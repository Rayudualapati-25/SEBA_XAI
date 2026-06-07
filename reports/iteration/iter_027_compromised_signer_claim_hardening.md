# Iteration 027: Compromised-Signer Claim Hardening

Date: 2026-05-29

## Goal

Make the SEBA-XAI research claim more solid by reconciling the NS-PI contribution with current multi-seed experiment evidence.

## What Worked

- The `compromised_signer` attack is implemented in `src/seba/attacks/compromised_signer.py`.
- The attack flips deny/escalate decisions to allow and marks the affected events as validly re-signed and policy-output compromised.
- Current integrity and ABAC-style baselines are intentionally blind under this attacker model.
- NS-PI detects `compromised_signer` in 5/5 seeds in the full-grid result table.
- `make lint` now passes across `src/` and `tests/`.
- `make test` passes with `62 passed`.
- `scripts/run_full_grid.py` and `scripts/run_ablations.py` regenerated the main result tables.

## Evidence

Primary tables:

- `results/tables/full_grid_per_attack.csv`
- `results/tables/full_grid_aas_by_defense.csv`
- `results/tables/adaptive_attack_summary.csv`
- `results/tables/nspi_ablation.csv`

Key result:

| Attack | Baselines | NS-PI |
|---|---:|---:|
| `compromised_signer` | 0/5 seeds detected | 5/5 seeds detected |

Overall AAS still shows that NS-PI is not a general tamper-detection replacement:

| Defense group | Interpretation |
|---|---|
| Signed-chain / CT / blockchain-style / Fabric+ABAC / ABAC re-exec | Strong for ordinary log edits |
| NS-PI drift | Useful for policy-distribution drift under compromised-signer logs |

## What Failed Or Is Weak

- The old contribution sentence was too broad because NS-PI does not beat integrity and ABAC baselines overall.
- The current `abac_reexec` and `fabric_abac` baselines share the compromised canonical policy output in the `compromised_signer` experiment. A stronger independent raw-attribute policy-oracle baseline is still needed.
- The workload is synthetic, so claims must be about reproducible controlled evaluation, not real-world police deployment.
- Explanation-quality metrics are not yet finalized.

## Claim Update

Updated:

- `CONTRIBUTION.md`
- `results/FINDINGS.md`
- `16_make_seba_xai_solid_research.md`

New claim:

> NS-PI is a complementary interpretable policy-drift detector that catches validly re-signed compromised-signer logs in the synthetic benchmark. It does not replace cryptographic audit or ABAC/PBAC.

## Next Experiment

Implement an independent raw-attribute policy-oracle baseline that evaluates the original request attributes from a separate trusted view. This will test whether the NS-PI advantage remains when compared against a stronger external ABAC verifier.
