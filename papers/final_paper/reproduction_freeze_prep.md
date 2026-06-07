# Reproduction Freeze Preparation

Date: 2026-06-06  
Status: freeze completed on 2026-06-06 after aligned draft v2 assembly.

## Purpose

The reproduction freeze should be run only after the paper claims are aligned
with the dashboard, claim-control memo, and artifact-to-claim table. The goal
is to confirm that the current results can be regenerated and that the paper
does not depend on stale or unsupported numbers.

This checklist was run for `papers/final_paper/paper_draft_v2.md` on
2026-06-06.

## Preconditions

Before running the freeze:

1. Introduction, Methodology, and Results must use the evidence boundary in
   `papers/final_paper/claim_control_memo.md`.
2. Major claims must appear in
   `papers/final_paper/artifact_to_claim_table.csv`.
3. Result terminology must match
   `papers/final_paper/result_metric_dictionary.md`.
4. No section should claim real CCTNS/ICJS deployment, real police records,
   legal compliance, production security, SOTA, or crime prediction.

## Freeze Commands

Run these from the repository root:

```bash
make test
make lint
make typecheck
make reproduce
make figures
```

## 2026-06-06 Freeze Result

| Command | Status | Notes |
|---|---|---|
| `make test` | Passed | `75 passed` |
| `make lint` | Passed | Ruff checks passed after removing one unused import |
| `make typecheck` | Passed | Initial typing issues were fixed; mypy then passed over 26 source files |
| `make reproduce` | Passed | Multi-seed pipeline, full grid, ablations, sensitivities, XAI/audit quality, workload stress, and seed-confidence summaries regenerated |
| `make figures` | Passed | Paper SVG figures regenerated under `papers/final_paper/figures_tables/` |

No paper-claim drift was found in the checked headline values for AAS,
`compromised_signer`, NS-PI sensitivity, XAI/audit quality, metadata exposure,
or local latency/storage tables.

## Expected Output Areas

After the freeze, inspect these artifacts:

| Area | Files To Check |
|---|---|
| Consolidated findings | `results/FINDINGS.md` |
| Full-grid comparison | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv`, `results/tables/full_grid_raw.csv` |
| NS-PI sensitivity | `results/tables/nspi_compromised_signer_sensitivity_summary.csv`, `results/tables/nspi_targeted_compromised_signer_summary.csv` |
| XAI/audit quality | `results/tables/explanation_audit_quality_summary.csv` |
| Workload stress | `results/tables/workload_policy_stress_summary.csv` |
| Metadata and overhead | `results/tables/paper_table_03_metadata_exposure.csv`, `results/tables/paper_table_04_latency_storage.csv` |
| Figures | `results/plots/`, `papers/final_paper/figures_tables/` |

## Pass Criteria

The freeze is acceptable only if:

- all commands complete successfully;
- regenerated metrics match the claims used in the paper, or any drift is
  documented before the paper is updated;
- figures regenerate without missing source tables;
- no final manuscript claim lacks an artifact path;
- the limitations still report the synthetic-only boundary and known NS-PI/XAI
  weaknesses.

## If Results Drift

If any table changes:

1. do not hide the change;
2. update `results/FINDINGS.md` if the regenerated pipeline intentionally
   changes the interpreted findings;
3. update `papers/final_paper/artifact_to_claim_table.csv`;
4. update the Results and Limitations sections;
5. add a new iteration report explaining the drift.

## Current Next Action

The next writing action is to sync the accepted `paper_draft_v2.md` wording
into the Overleaf/IEEE manuscript and merge the Related Work, Threat Model,
Limitations, Conclusion, references, and figures without adding unsupported
claims.
