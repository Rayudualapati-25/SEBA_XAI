# Iteration 037 - Limitations, Conclusion, and Paper Skeleton

Date: 2026-05-30
Status: documentation/writing only - no experiments run, no tables regenerated

## Goal

Continue the paper assembly after iterations 035 and 036 by drafting the
remaining paper-facing Limitations and Conclusion sections, then creating a
combined paper skeleton that shows how the existing section drafts should be
merged.

Claude was checked first because the active goal requires continued Claude +
Codex collaboration. Claude was unavailable due the active usage limit until
06:10 IST, so Codex completed this bounded documentation step from local
evidence.

## Files created

- `papers/final_paper/limitations/limitations_draft_v1.md`
- `papers/final_paper/conclusion/conclusion_draft_v1.md`
- `papers/final_paper/paper_skeleton_v1.md`
- `reports/iteration/iter_037_limitations_conclusion_skeleton.md`

## Files updated

- `papers/final_paper/README.md`
- `SESSION_HANDOFF.md`

## Files intentionally left unchanged

- All source code under `src/`, `scripts/`, `prototype/`, and `tests/`.
- All result tables under `results/tables/`.
- Existing section drafts for Introduction, Related Work, Methodology, Threat
  Model, and Results.

## Source-to-claim coverage

| Draft content | Backing artifact |
|---|---|
| Synthetic benchmark boundary | `papers/final_paper/methodology/methodology_draft_v1.md`, `prototype/synthetic_access_sim/generate_synthetic_requests.py` |
| Declared policy oracle boundary | `prototype/synthetic_access_sim/policy_oracle.py`, `papers/final_paper/methodology/methodology_draft_v1.md` |
| Compromised-signer limitation | `papers/final_paper/threat_model/threat_model_draft_v1.md`, `src/seba/attacks/compromised_signer.py`, `results/tables/seed_confidence_summary.csv` |
| Trusted raw-attribute oracle assumption | `papers/final_paper/threat_model/threat_model_draft_v1.md`, `results/tables/full_grid_aas_by_defense.csv` |
| NS-PI global sensitivity misses | `results/tables/nspi_compromised_signer_sensitivity_summary.csv` |
| NS-PI targeted sensitivity misses | `results/tables/nspi_targeted_compromised_signer_summary.csv` |
| Workload-size dependence | `results/tables/workload_policy_stress_summary.csv`, `results/tables/seed_confidence_summary.csv` |
| XAI text coverage weakness | `results/tables/explanation_audit_quality_summary.csv`, `papers/final_paper/results/results_draft_v1.md` |
| Blockchain simulation boundary | `prototype/synthetic_access_sim/blockchain_audit.py`, `papers/final_paper/methodology/methodology_draft_v1.md` |
| Seed-count caveat | `results/FINDINGS.md`, `results/tables/seed_confidence_summary.csv`, `results/tables/seed_confidence_raw.csv` |

## Honesty controls applied

- The Limitations draft explicitly says all evaluation is synthetic.
- The Conclusion repeats the narrow contribution only: complementary log-only
  policy-drift detection, not replacement of audit or trusted policy
  re-evaluation.
- The skeleton tells future writing passes not to add metrics during prose
  polishing.
- The stress matrix seed-count mismatch remains visible.

## Verification

- No experiments were run.
- No result tables were regenerated.
- No source code was changed.
- Documentation checks were run after writing:
  - forbidden overclaim phrase scan on the new draft files;
  - local cited-path existence check for literal paths in the new draft/report
    files.

## What worked

The paper now has all major draft-section slots represented: Introduction,
Related Work, Methodology, Threat Model, Results, Limitations, Conclusion, and
a combined skeleton.

## What is weak

The Introduction is still an older v0 scaffold, and references are not yet in
final IEEE numbering. The combined skeleton is an assembly guide, not a polished
single manuscript.

## Next step

Compress and revise the Introduction into a final v1 that matches the current
evidence-backed framing, then convert references into IEEE style.
