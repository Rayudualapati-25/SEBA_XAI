# Paper Draft Guardrail

Updated: 2026-06-06

Baseline, proposed-method, and ablation artifacts now exist in the repository, so evidence-backed paper drafting can begin.

Allowed at this stage:

- problem statement;
- related-work notes;
- dataset inventory;
- methodology;
- result tables derived from saved artifacts;
- cautious experiment narrative;
- limitations and failure modes.

Not allowed:

- claims of SOTA;
- deployment claims;
- legal-compliance claims;
- production security claims;
- real police/CCTNS/ICJS performance claims;
- unsupported novelty claims.

Paper text must cite generated artifacts in `results/tables/`, `results/plots/`, `prototype/runs/`, `experiments/runs/`, and `reports/iteration/`.

## Current Draft Sections

- `research_master_dashboard.md` - start-here dashboard for title, problem statement, claims, evidence, weaknesses, and next steps.
- `claim_control_memo.md` - strict allowed/forbidden claim boundary for publication drafting.
- `artifact_to_claim_table.csv` - major paper claims mapped to exact evidence artifacts and safe wording.
- `result_metric_dictionary.md` - simple definitions for the main metrics used in the Results section.
- `reproduction_freeze_prep.md` - freeze checklist and 2026-06-06 verification result after paper claims were aligned.
- `introduction/introduction_draft_v0.md` - early introduction draft.
- `introduction/introduction_draft_v1.md` - current evidence-bounded introduction draft.
- `introduction/introduction_final_professor.md` - current aligned professor-review Introduction draft.
- `related_work/related_work_draft_v1.md` - current evidence-bounded related-work draft.
- `methodology/methodology_draft_v1.md` - current aligned script- and artifact-grounded methodology draft.
- `threat_model/threat_model_draft_v1.md` - current evidence-bounded threat model draft.
- `results/results_draft_v1.md` - current aligned multi-seed, evidence-bounded results draft.
- `limitations/limitations_draft_v1.md` - current evidence-bounded limitations and future-work draft.
- `conclusion/conclusion_draft_v1.md` - current conservative conclusion draft.
- `paper_skeleton_v1.md` - current combined-paper assembly scaffold.
- `paper_draft_v1.md` - first combined manuscript draft assembled from the current section drafts.
- `paper_draft_v2.md` - current aligned supervisor-review draft with Introduction, Methodology, Results, scope boundaries, and reproduction-freeze status.
- `references_ieee_map.md` - current working reference map for numeric citations.
- `references_verification_v1.md` - verification notes for the current reference map.
- `references_ieee_final_v1.md` - cleaned IEEE-style reference list for supervisor review.
- `figures_tables/figure_table_pack_v1.md` - current figure/table plan for the combined draft.
- `figures_tables/paper_figures_manifest.md` - generated figure file list and caption guardrails.
- `supervisor_review_memo_v1.md` - short review memo with claim boundary, figure placement decision, and questions for the supervisor.
- `results/experiment_results_narrative.md` - older prototype narrative kept for context; do not treat it as the latest results section.

Next priority: upload or sync `papers/overleaf_ieee_journal/` into Overleaf,
then refine the IEEE journal draft with supervisor feedback.
