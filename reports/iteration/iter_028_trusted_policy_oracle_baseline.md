# Iteration 028: Trusted Raw-Attribute Policy Oracle Baseline

Date: 2026-05-29

## Goal

Add the stronger reviewer baseline that checks perturbed audit events against an independent trusted view of the original raw request attributes.

## What Worked

- Added `TrustedRawPolicyOracle` in `src/seba/baselines/trusted_oracle.py`.
- Added the baseline to `src/seba/scoring/grid.py` as `trusted_policy_oracle`.
- Added a unit test showing the trusted oracle detects `compromised_signer`.
- Updated `tests/test_grid.py` for the larger defense set.
- Regenerated the full-grid and ablation tables.

## Evidence

Verification:

- `make lint`: passed.
- `make test`: `63 passed`.
- `python3 scripts/run_full_grid.py`: regenerated `results/tables/full_grid_*.csv`.
- `python3 scripts/run_ablations.py`: regenerated `adaptive_attack_summary.csv` and `nspi_ablation.csv`.

Key table evidence from `results/tables/full_grid_per_attack.csv`:

| Defense | `compromised_signer` detection rate |
|---|---:|
| `trusted_policy_oracle` | 1.0 |
| `nspi_drift` | 1.0 |
| `signed_chain` | 0.0 |
| `blockchain_style` | 0.0 |
| `ct_log` | 0.0 |
| `fabric_abac` | 0.0 |
| `abac_reexec` | 0.0 |
| `mutable_log` | 0.0 |

## Interpretation

The result is stricter and more honest than the previous claim. NS-PI is not uniquely able to detect `compromised_signer`; a trusted raw-attribute oracle also detects it. The distinction is the trust assumption:

- `trusted_policy_oracle` needs a separate uncompromised raw-request view.
- `nspi_drift` works from the signed decision trace as a log-only distribution alarm.

## What Is Still Weak

- NS-PI still has weak overall AAS because it is not designed for single-row tamper detection.
- The trusted oracle is a strong baseline and may be unrealistic if the auditor cannot access raw request attributes.
- The paper now needs workload sensitivity tests to show when NS-PI drift is reliable under lower-rate or targeted corruption.

## Next Step

Run a workload sensitivity grid varying compromised-signer flip fraction, request volume, and corruption scope.
