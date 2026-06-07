# Iteration 032 — Workload And Policy-Mix Stress Test

Date: 2026-05-29
Status: completed and reproduced

## Goal

Answer the standing reviewer question:

> Do the SEBA-XAI results — especially the `compromised_signer` asymmetry and
> NS-PI drift behaviour — survive changes in workload size and policy mix, or
> are they only true for the single 1000-request synthetic setting?

This is a deliberate attempt to break the prior results, not to confirm them.

## Implementation

Added:

- `scripts/run_workload_policy_stress.py`
- `results/tables/workload_policy_stress_raw.csv` (one row per cell, 24 cells)
- `results/tables/workload_policy_stress_summary.csv` (aggregated per arm/size)
- `tests/test_workload_policy_stress.py`

Updated:

- `Makefile` (`make reproduce` now regenerates the stress tables)
- `REPRODUCE.md`, `results/FINDINGS.md`, `CONTRIBUTION.md`, `SESSION_HANDOFF.md`

### Honest knob design

The generator (`generate_synthetic_requests.py`) exposes a real
`--num-requests` size knob but **no per-ratio CLI flags**. Rather than fake
ratios, the stress script:

- varies **size** with the real `--num-requests` argument (500/1000/2500/5000);
- varies **policy mix** by overriding the generator's module-level
  `SCENARIO_WEIGHTS` in-process and re-running the real, tested generation
  logic. No rows are fabricated.

Scenario-weight proxies (documented in the script):

- cross-jurisdiction ratio  <- `cross_jurisdiction_sensitive` weight
- revoked-credential ratio  <- `revoked_credential` weight
- approval missing/invalid  <- `expired_approval_token` weight
- classified-record ratio   <- **indirect** proxy (boost cross-jurisdiction +
  juvenile + sealed scenarios, which pull sensitive records)

Every cell reports the **realized** ratios measured from the generated
workload, so the reader can confirm the knob actually moved the distribution.

Determinism: fixed seeds {7, 42, 123}. Per-cell run directories are deleted
after metrics are extracted; only the two result tables persist.

## Matrix

- Size arm: num_requests ∈ {500, 1000, 2500, 5000}, baseline mix, 3 seeds = 12 cells.
- Mix arm: {high_cross_jurisdiction, high_revoked_credential, high_approval_missing,
  high_classified_proxy} at N=1000, 3 seeds = 12 cells.
- Total: 24 cells, all completed (24/24 ok, 0 errors, 0 duplicate cells).
  Latest reproduced total compute was ~86 s; per-cell runtime 2.5 s (N=500) to
  6.7 s (N=5000), so
  5000 was feasible and is included.

`cs_f25` = compromised_signer at 25% flip; `cs_f10` = at 10% flip. Detection
values are means over 3 seeds (0.0 = never, 1.0 = always).

## Results — Size Arm (baseline mix, mean over 3 seeds)

| N | classified | cross-juris | revoked | appr-missing | NS-PI train acc | cs25 signed | cs25 NS-PI global | cs25 oracle | cs10 NS-PI global | cs10 per-station | CF validity | runtime |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 500  | 0.256 | 0.761 | 0.101 | 0.453 | 0.909 | 0.0 | 1.0 | 1.0 | **0.0** | 0.333 | 1.000 | 2.50s |
| 1000 | 0.240 | 0.773 | 0.091 | 0.442 | 0.942 | 0.0 | 1.0 | 1.0 | 1.0 | 0.333 | 1.000 | 2.93s |
| 2500 | 0.247 | 0.781 | 0.090 | 0.451 | 0.968 | 0.0 | 1.0 | 1.0 | 1.0 | 1.000 | 1.000 | 4.39s |
| 5000 | 0.254 | 0.786 | 0.087 | 0.456 | 0.974 | 0.0 | 1.0 | 1.0 | 1.0 | 1.000 | 1.000 | 6.67s |

## Results — Policy-Mix Arm (N=1000, mean over 3 seeds)

Baseline N=1000 for reference: classified 0.240, cross-juris 0.773, revoked 0.091, appr-missing 0.442.

| Arm | classified | cross-juris | revoked | appr-missing | cs25 signed | cs25 NS-PI global | cs25 oracle | cs10 NS-PI global | CF validity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| high_cross_jurisdiction | 0.259 | **0.820** | 0.071 | 0.475 | 0.0 | 1.0 | 1.0 | 1.0 | 1.000 |
| high_revoked_credential | 0.254 | 0.795 | **0.252** | 0.550 | 0.0 | 1.0 | 1.0 | 1.0 | 1.000 |
| high_approval_missing | 0.249 | 0.803 | 0.073 | **0.558** | 0.0 | 1.0 | 1.0 | 1.0 | 1.000 |
| high_classified_proxy | **0.313** | 0.883 | 0.071 | 0.490 | 0.0 | 1.0 | 1.0 | 1.0 | 1.000 |

Bold = the intended knob moved relative to baseline.

## What Survives

1. **The headline `compromised_signer` asymmetry is robust.** At a 25% flip,
   the cryptographic/integrity detector stays blind (0.0) and NS-PI global
   drift + trusted oracle both detect (1.0) at **every** workload size
   (500–5000) and **every** policy-mix arm. This was the main risk to the
   paper and it held.
2. **Counterfactual validity is stable** (1.000 in the latest regenerated
   stress summary) across all sizes and mixes.
3. **NS-PI rule-list fit improves with size**, train accuracy 0.909 (N=500) →
   0.974 (N=5000): more data gives the depth-8 rule list a better fit to the
   deterministic oracle.
4. **The knobs are real**: realized ratios moved as intended — revoked
   0.091 → 0.252, approval-missing 0.442 → 0.558, classified 0.240 → 0.313.

## What Is Weak (report honestly)

1. **NS-PI low-rate sensitivity is workload-size dependent.** At a 10% flip,
   NS-PI global drift **misses at N=500** (0.0) and only becomes reliable at
   N ≥ 1000. The earlier "≈10% detection threshold" finding therefore holds
   only for workloads of ~1000+ requests; smaller workloads weaken it.
2. **Per-station drift is data-hungry.** At a 10% flip, per-station detection
   is 0.333 at N=500 and N=1000, reaching 1.0 only at N ≥ 2500. Consistent
   with the earlier targeted-corruption finding: grouped drift needs enough
   rows per group.
3. **The cross-jurisdiction knob has limited headroom.** The baseline workload
   is already ~77% cross-jurisdiction, so the "high_cross_jurisdiction" arm
   only reaches 0.82. The cross-jurisdiction axis cannot be stress-pushed far
   in the current generator design; this is a generator limitation, stated
   rather than hidden.
4. **`cs25 signed` is 0.0 by construction, not a failure.** The compromised
   signer re-signs a valid log, so integrity detectors are *designed* to be
   blind here; the 0.0 column is the expected control, included for honesty.

## Boundaries

- Synthetic workload only; no real police data, deployment, legal-compliance,
  or SOTA claim.
- The classified-ratio knob is indirect (via sensitive-scenario weights);
  reported realized ratios make the effect auditable.
- Only the 25% and 10% flip fractions and 3 seeds were used in the stress
  matrix to bound runtime; the dedicated sensitivity sweep
  (`scripts/run_nspi_sensitivity.py`) remains the finer-grained reference.

## Verification

```bash
python3 scripts/run_workload_policy_stress.py
make lint
make test
```

Status:

- 24/24 cells ok, 0 duplicate cells, latest full matrix ~86 s.
- `make lint`: passed.
- `make test`: passed.

## Next Step

Either:

1. Begin the paper results section (the security, sensitivity, XAI-quality,
   and now workload/policy-mix robustness evidence are all in place), or
2. Add a seed-level confidence table for the final paper as flagged in
   `CONTRIBUTION.md` "Required Next Evidence".
