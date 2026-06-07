# Iteration 029: NS-PI Compromised-Signer Sensitivity

Date: 2026-05-29

## Goal

Measure how much compromised-signer corruption is needed before NS-PI drift detection fires in the current synthetic workload.

## What Worked

- Added `scripts/run_nspi_sensitivity.py`.
- Added the sensitivity stage to `make reproduce`.
- Generated:
  - `results/tables/nspi_compromised_signer_sensitivity_raw.csv`
  - `results/tables/nspi_compromised_signer_sensitivity_summary.csv`

## Evidence

Verification:

- `make lint`: passed.
- `make test`: `63 passed`.
- `make reproduce`: passed.

Summary result:

| Flip fraction | NS-PI any detection | Trusted oracle detection |
|---:|---:|---:|
| 0.02 | 0.0 | 1.0 |
| 0.05 | 0.0 | 1.0 |
| 0.10 | 1.0 | 1.0 |
| 0.15 | 1.0 | 1.0 |
| 0.20 | 1.0 | 1.0 |
| 0.25 | 1.0 | 1.0 |
| 0.35 | 1.0 | 1.0 |
| 0.50 | 1.0 | 1.0 |

## Interpretation

This result makes the research more honest. NS-PI is not a detector for tiny corruption rates in the current workload. It becomes reliable at about 10% global compromised-signer corruption and above. The trusted raw-attribute oracle catches every tested flip fraction because it checks individual events against the original request view.

## What Failed Or Is Weak

- NS-PI misses 2% and 5% corruption.
- This script only tests global compromised-signer corruption. It does not yet test station-specific or district-specific corruption.
- The current workload size is fixed to the existing seed artifacts.

## Next Step

Add a targeted sensitivity test for per-station and per-district compromised-signer corruption, then report where global drift fails and grouped drift helps.
