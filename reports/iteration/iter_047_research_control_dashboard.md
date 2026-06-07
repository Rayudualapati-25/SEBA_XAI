# Iteration 047: Research Control Dashboard and Artifact-To-Claim Table

Date: 2026-06-05

## Scope

This iteration created easier research-control artifacts for writing and supervising the SEBA-XAI paper.

No new experiments were run. No new benchmark numbers, deployment claims, legal claims, or dataset claims were added.

## Files Created Or Updated

| File | Purpose |
|---|---|
| `papers/final_paper/research_master_dashboard.md` | Start-here dashboard for paper identity, problem statement, completed work, supported findings, weaknesses, and next steps. |
| `papers/final_paper/artifact_to_claim_table.csv` | Claim-to-evidence table mapping major paper claims to exact artifacts, metrics, limits, and safe wording. |
| `papers/final_paper/result_metric_dictionary.md` | Simple dictionary of the main metrics used in the Results section. |
| `papers/final_paper/README.md` | Updated to list the new research-control files first. |

## What Worked

- The project now has a clear start point for paper writing.
- Major claims are mapped to concrete artifacts such as `results/FINDINGS.md`, `results/tables/full_grid_per_attack.csv`, and `results/tables/explanation_audit_quality_summary.csv`.
- The metric dictionary should make it easier to explain the Results section to a supervisor without changing the technical meaning.
- The dashboard keeps the paper focused on synthetic access governance, not broad crime prediction or unsupported deployment claims.

## What Is Still Weak

- The artifact-to-claim table is a major-claim audit, not a sentence-by-sentence final manuscript audit.
- The final reproduction freeze still needs to be run before submission.
- Real Fabric validation, real police data, formal privacy proof, and domain-validated policy rules are still outside the current evidence boundary.
- Natural-language explanation coverage remains a reported weakness unless the renderer is improved and rerun.

## Next Step

Use the dashboard and claim table to revise the final manuscript sections in this order:

1. Abstract
2. Introduction
3. Methodology
4. Results
5. Limitations

After the claims are aligned, run the reproduction freeze:

```bash
make test
make lint
make typecheck
make reproduce
make figures
```

Then update the claim table with final manuscript paragraph references.
