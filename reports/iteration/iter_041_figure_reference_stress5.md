# Iteration 041 — Figure/Table Pack, Reference Verification, and Five-Seed Stress

Date: 2026-05-30
Status: completed

## 1. Goal

Finish the reviewer-facing hardening step after the combined paper draft:

1. create a conservative figure/table pack;
2. verify high-priority bibliography metadata;
3. remove the old workload-stress seed-count mismatch by rerunning stress with
   five seeds;
4. update paper-facing docs without adding unsupported claims.

Claude was used only for review support. It returned a checklist recommending
source-path captions, avoiding production-latency graphics, avoiding AAS
leaderboard visuals, and prioritizing bibliography verification for the
blockchain evidence, Fabric+ABAC, XAI-law-enforcement, and close access-control
papers. Codex performed the repo edits and verification.

## 2. What Changed

Created:

- `papers/final_paper/figures_tables/figure_table_pack_v1.md`
- `papers/final_paper/references_verification_v1.md`

Updated:

- `scripts/run_workload_policy_stress.py`
- `results/tables/workload_policy_stress_raw.csv`
- `results/tables/workload_policy_stress_summary.csv`
- `results/tables/seed_confidence_raw.csv`
- `results/tables/seed_confidence_summary.csv`
- `results/FINDINGS.md`
- `CONTRIBUTION.md`
- `REPRODUCE.md`
- current paper drafts under `papers/final_paper/`
- `SESSION_HANDOFF.md`

## 3. Experiment Update

`scripts/run_workload_policy_stress.py` now defaults to the same five-seed set
used by the other headline experiments:

```text
{7, 21, 42, 99, 123}
```

The workload/policy-mix stress matrix now has 40 raw cells:

- size arm: N in `{500, 1000, 2500, 5000}` with five seeds;
- policy-mix arm: four mix overrides at N=1000 with five seeds.

The run completed successfully:

```text
Done: 40/40 cells ok
```

The seed-confidence summary now contains:

```text
139 metric/group rows
695 per-seed rows
```

## 4. Main Result After Rerun

The 25% compromised-signer asymmetry still holds across the stress matrix:

- signed-chain detection: 0.0;
- NS-PI global detection: 1.0;
- trusted raw-attribute oracle detection: 1.0.

The 10% compromised-signer case remains workload-size dependent:

| N | NS-PI global mean | NS-PI per-station mean |
|---:|---:|---:|
| 500 | 0.2 | 0.2 |
| 1000 | 1.0 | 0.6 |
| 2500 | 1.0 | 1.0 |
| 5000 | 1.0 | 1.0 |

Interpretation: the old three-seed reporting caveat is removed, but the
low-rate workload-size limitation remains and must stay visible in the paper.

## 5. Reference Work

The high-priority bibliography pass verified entries [6]-[8], [10],
[13]-[18], and [20]-[28] in `papers/final_paper/references_ieee_map.md`.

Important correction:

- [25] was corrected to `R. Sharma and U. Gupta, Computers and Electrical
  Engineering, vol. 109, 108761, 2023, doi: 10.1016/j.compeleceng.2023.108761`.

Remaining reference work is style-only:

- IEEE capitalization and punctuation;
- venue abbreviations;
- access dates for web-only sources;
- final order after the paper stops moving.

## 6. What Worked

- The five-seed stress run completed without errors.
- The seed-confidence aggregator handled the expanded stress raw table without
  code changes.
- The paper drafts now have one consistent five-seed language for the stress
  matrix.
- The reference map no longer contains unverified author-detail placeholders.

## 7. What Is Still Weak

- The stress matrix is still synthetic, so it supports reproducibility but not
  real-world police performance.
- NS-PI still misses 2% and 5% global corruption and 10% targeted
  station/district corruption.
- At 10% global corruption, N=500 remains unstable.
- Natural-language explanation text still does not surface every decisive
  attribute.
- The blockchain component remains a local file-backed permissioned-audit
  simulation, not a production Fabric network.

## 8. Verification

Commands run:

```bash
python3 scripts/run_workload_policy_stress.py
python3 scripts/run_seed_confidence_summary.py
make lint
make test
make reproduce
```

Observed status:

- `python3 scripts/run_workload_policy_stress.py`: 40/40 cells ok.
- `python3 scripts/run_seed_confidence_summary.py`: 139 summary rows and 695
  per-seed rows.
- `make lint`: passed.
- `make test`: 75 passed.
- `make reproduce`: passed and regenerated the full pipeline with the
  five-seed stress default.

## 9. Next Step

Convert the figure/table pack into actual paper visuals and run a final IEEE
bibliography style pass. Do not add new claims during that step unless a new
experiment is run and recorded.
