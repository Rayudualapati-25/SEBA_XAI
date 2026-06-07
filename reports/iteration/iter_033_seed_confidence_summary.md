# Iteration 033 - Seed-Level Confidence Summary

Date: 2026-05-30
Status: completed and locally verified

## Goal

Prepare the final paper evidence base before drafting results text by
consolidating across-seed stability for the headline SEBA-XAI metrics.

The purpose of this step is not to run a new experiment. It is to prevent
single-number reporting. Every summary value is computed from existing
seed-level raw CSV artifacts.

## Implementation

Added:

- `scripts/run_seed_confidence_summary.py`
- `results/tables/seed_confidence_summary.csv`
- `results/tables/seed_confidence_raw.csv`
- `tests/test_seed_confidence_summary.py`

Updated:

- `Makefile` so `make reproduce` now regenerates the workload stress tables
  and then the seed-confidence tables.
- `REPRODUCE.md` so the reproduction path documents workload stress and
  seed-confidence generation.

## Source Tables

The aggregator reads only raw tables that contain seed-level rows:

| Source table | Main use |
|---|---|
| `full_grid_raw.csv` | `compromised_signer` detection by defense |
| `adaptive_attack_summary.csv` | adaptive compromised-signer detection |
| `explanation_audit_quality.csv` | XAI trace, counterfactual, and audit quality |
| `nspi_compromised_signer_sensitivity_raw.csv` | global flip-fraction sensitivity |
| `nspi_targeted_compromised_signer_raw.csv` | station/district targeted sensitivity |
| `workload_policy_stress_raw.csv` | size and policy-mix stress stability |

The summary table contains 139 metric/group rows. The raw table contains 567
per-seed values used to compute those rows.

## Method

For each metric group, the script computes:

- number of seeds
- seed list
- mean
- sample standard deviation when at least two seeds exist
- min
- max

If a metric has only one seed, the script sets `std=0.0` but marks
`std_defined=False`. This prevents a single observation from being reported as
measured stability.

## Key Results From The Summary Table

### Compromised-Signer Asymmetry

From `results/tables/seed_confidence_summary.csv`:

| Defense | n_seeds | Detection mean | Std | Min | Max |
|---|---:|---:|---:|---:|---:|
| `signed_chain` | 5 | 0.0 | 0.0 | 0.0 | 0.0 |
| `blockchain_style` | 5 | 0.0 | 0.0 | 0.0 | 0.0 |
| `ct_log` | 5 | 0.0 | 0.0 | 0.0 | 0.0 |
| `fabric_abac` | 5 | 0.0 | 0.0 | 0.0 | 0.0 |
| `abac_reexec` | 5 | 0.0 | 0.0 | 0.0 | 0.0 |
| `mutable_log` | 5 | 0.0 | 0.0 | 0.0 | 0.0 |
| `nspi_drift` | 5 | 1.0 | 0.0 | 1.0 | 1.0 |
| `trusted_policy_oracle` | 5 | 1.0 | 0.0 | 1.0 | 1.0 |

Interpretation: the main compromised-signer result is stable across the five
available full-grid seeds. It still must be framed carefully: ledger integrity
baselines are blind by construction under this attack because the event is
validly re-signed, while NS-PI and the trusted raw-attribute oracle use
different evidence assumptions.

### XAI And Audit Quality

| Metric | n_seeds | Mean | Std | Min | Max |
|---|---:|---:|---:|---:|---:|
| trace completeness | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| counterfactual coverage | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| counterfactual validity | 5 | 0.996413 | 0.005470 | 0.987627 | 1.000000 |
| stable decision/reason row rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| audit reconstruction rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| decisive-attribute full text coverage | 5 | 0.781000 | 0.020833 | 0.755000 | 0.809000 |

Interpretation: the structured explanation and audit artifacts are stable in
this synthetic benchmark. The known weakness remains the natural-language
explanation text: the structured trace is complete, but not every decisive
attribute is fully rendered into the explanation text.

### Global Sensitivity Boundary

| Flip fraction | NS-PI global mean | NS-PI per-station mean | Trusted oracle mean |
|---:|---:|---:|---:|
| 0.02 | 0.0 | 0.0 | 1.0 |
| 0.05 | 0.0 | 0.0 | 1.0 |
| 0.10 | 1.0 | 0.6 | 1.0 |
| 0.15 | 1.0 | 1.0 | 1.0 |
| 0.25 | 1.0 | 1.0 | 1.0 |

Interpretation: NS-PI misses small 2% and 5% global corruption in the current
benchmark. The 10% point is reliable for global drift but still variable for
per-station drift (`std=0.547723`).

### Targeted Sensitivity Boundary

| Target | Flip fraction | Grouped detector mean | Std | Trusted oracle mean |
|---|---:|---:|---:|---:|
| station | 0.10 | 0.0 | 0.0 | 1.0 |
| station | 0.50 | 1.0 | 0.0 | 1.0 |
| district | 0.10 | 0.0 | 0.0 | 1.0 |
| district | 0.25 | 1.0 | 0.0 | 1.0 |

Interpretation: grouped NS-PI becomes useful only when the targeted corruption
is large enough within the selected group. It is not a row-level verifier and
does not replace the trusted raw-attribute oracle.

### Workload Stress Stability

At `compromised_signer` 25% flip, all size and policy-mix stress arms keep the
same pattern across three stress seeds:

| Metric | Result |
|---|---|
| signed-chain detection | 0.0 mean, 0.0 std |
| NS-PI global detection | 1.0 mean, 0.0 std |
| trusted oracle detection | 1.0 mean, 0.0 std |

At a 10% flip, workload size still matters:

| N | NS-PI global mean | Per-station mean | Per-station std |
|---:|---:|---:|---:|
| 500 | 0.0 | 0.333333 | 0.577350 |
| 1000 | 1.0 | 0.333333 | 0.577350 |
| 2500 | 1.0 | 1.000000 | 0.000000 |
| 5000 | 1.0 | 1.000000 | 0.000000 |

Interpretation: the stronger 25% compromised-signer result is stable in the
stress matrix, but low-rate/grouped drift needs enough workload volume.

## Boundaries

- This table is across-seed descriptive evidence, not a formal confidence
  interval or deployment guarantee.
- Stress rows currently use three seeds, while the full-grid, sensitivity, and
  XAI tables use five seeds.
- All workloads are synthetic. No real police record or operational deployment
  is evaluated.
- Timing values are local Python-script runtimes, not production Hyperledger
  Fabric or CCTNS/ICJS latency measurements.

## Verification

```bash
python3 scripts/run_seed_confidence_summary.py
python3 -m ruff check scripts/run_seed_confidence_summary.py tests/test_seed_confidence_summary.py
python3 -m pytest tests/test_seed_confidence_summary.py
```

Status:

- `seed_confidence_summary.csv`: 139 metric/group rows.
- `seed_confidence_raw.csv`: 567 per-seed values.
- Focused lint and tests passed locally after implementation.

## Next Step

Begin the paper Results and Threat Model sections from the evidence now in
`results/tables/`, `results/FINDINGS.md`, and the iteration reports. The first
draft must not introduce any new performance or deployment claims.
