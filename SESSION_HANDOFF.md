# Session Handoff — SEBA-XAI Research Hardening

Handoff updated: 2026-05-30
For: next Codex / Claude Code session picking up this repo cold.

Read first:

1. `CONTRIBUTION.md`
2. `results/FINDINGS.md`
3. `16_make_seba_xai_solid_research.md`
4. `reports/iteration/iter_031_explanation_audit_quality.md`
5. `reports/iteration/iter_032_workload_policy_stress.md`
6. `reports/iteration/iter_033_seed_confidence_summary.md`
7. `reports/iteration/iter_034_threat_model_results_notes.md`
8. `reports/iteration/iter_035_paper_sections_v1.md`
9. `reports/iteration/iter_036_methodology_related_work_v1.md`
10. `reports/iteration/iter_037_limitations_conclusion_skeleton.md`
11. `reports/iteration/iter_038_introduction_v1.md`
12. `reports/iteration/iter_039_reference_map_intro_citations.md`
13. `reports/iteration/iter_040_related_work_citations_and_paper_draft.md`
14. `reports/iteration/iter_041_figure_reference_stress5.md`
15. `reports/iteration/iter_042_figures_and_final_references.md`

## 0. Current Research Identity

SEBA-XAI is now best framed as:

> A CCTNS/ICJS-compatible research prototype for explainable, blockchain-audited access governance over sensitive police/criminal-justice records, evaluated with synthetic inter-agency access workloads and adversarial audit attacks.

Do **not** frame it as crime prediction, real police deployment, legal compliance, or "put police data on blockchain."

## 1. Current Defensible Claim

The old broad NS-PI claim was too strong. The current evidence-backed claim is:

> NS-PI is a complementary interpretable policy-drift detector. It detects validly re-signed compromised-signer logs in the synthetic benchmark while ledger-only integrity and audit-only baselines are blind under that attacker model. A trusted raw-attribute policy oracle also detects the attack, so NS-PI should be framed as a log-only drift signal rather than the strongest possible verifier.

The newest sensitivity result adds:

> Global NS-PI can miss localized station/district corruption because the overall changed share of the workload is small. Grouped station/district drift is the right detector for localized compromised-signer attacks, but it still misses very small target-group corruption.

The newest XAI-quality result adds:

> The XAI layer is now measurable: complete structured traces, counterfactual replay validity, duplicate-context stability, and signed-log-to-block audit reconstruction have been evaluated across five synthetic seeds. The main XAI weakness is that not every decisive attribute is fully rendered in the natural-language explanation text.

The workload/policy-mix stress result (iter 032, extended in iter 041) adds:

> The compromised_signer asymmetry (integrity blind 0.0 / NS-PI global 1.0 / trusted oracle 1.0 at a 25% flip) and counterfactual validity (1.0 in the latest regenerated stress summary) hold across workload sizes N∈{500,1000,2500,5000} and across high-classified, high-cross-jurisdiction, high-revoked-credential, and high-approval-missing policy mixes over five seeds. The NS-PI low-rate threshold is workload-size dependent: at a 10% flip, global drift is inconsistent at N=500 and stable from N≥1000, while per-station drift reaches full detection from N≥2500. The cross-jurisdiction knob has limited headroom because the baseline workload is already about 78% cross-jurisdiction.

The newest seed-confidence result (iter 033, updated in iter 041) adds:

> The final-paper stability table now exists. `results/tables/seed_confidence_summary.csv` contains 139 metric/group rows and `results/tables/seed_confidence_raw.csv` contains 695 per-seed values. The table confirms the compromised-signer asymmetry across five seeds (NS-PI drift and trusted oracle mean 1.0/std 0.0; ledger/audit baselines mean 0.0/std 0.0), while preserving the known low-rate, targeted, and workload-size sensitivity weaknesses.

The newest paper-notes result (iter 034) adds:

> A paper-facing threat-model and results-notes scaffold now exists. It maps each safe Results/Threat Model claim to a backing table, separates strong findings, weak findings, and not-proven claims, and labels non-table statements as interpretation. This is not the final IEEE section yet; it is the guardrail for writing it without overstating the evidence.

The newest paper-draft result (iter 035) adds:

> First IEEE-style draft sections now exist for Threat Model and Results. They are located at `papers/final_paper/threat_model/threat_model_draft_v1.md` and `papers/final_paper/results/results_draft_v1.md`. The older `papers/final_paper/results/experiment_results_narrative.md` was intentionally left unchanged as earlier prototype context; the v1 Results draft is the current multi-seed paper-facing draft.

The newest paper-draft result (iter 036) adds:

> First IEEE-style draft sections now exist for Methodology and Related Work. They are located at `papers/final_paper/methodology/methodology_draft_v1.md` and `papers/final_paper/related_work/related_work_draft_v1.md`. Claude created the draft files; Codex reviewed them, removed scan-sensitive wording, created the iteration report, and updated the paper index/handoff.

The newest paper-draft result (iter 037) adds:

> Draft sections now exist for Limitations and Conclusion, plus a combined paper skeleton. They are located at `papers/final_paper/limitations/limitations_draft_v1.md`, `papers/final_paper/conclusion/conclusion_draft_v1.md`, and `papers/final_paper/paper_skeleton_v1.md`. Claude was checked first but remained unavailable due the usage limit until 06:10 IST, so Codex completed this bounded documentation step from local evidence.

The newest paper-draft result (iter 038) adds:

> The Introduction has been revised into a current v1 aligned with the narrowed SEBA-XAI / NS-PI contribution. It is located at `papers/final_paper/introduction/introduction_draft_v1.md`. The older v0 scaffold remains for comparison.

The newest reference-cleanup result (iter 039) adds:

> A working IEEE-style reference map now exists at `papers/final_paper/references_ieee_map.md`, and Introduction v1 uses numeric placeholders. Author details missing from local evidence are explicitly marked for verification instead of guessed.

The newest paper-assembly result (iter 040) adds:

> Related Work citations have been converted from raw URLs and CSV-row references into the shared numeric reference map, now extended through `[28]`. A first combined manuscript draft exists at `papers/final_paper/paper_draft_v1.md`. Claude provided a review-only citation-cleanup checklist; Codex performed the edits and verification.

The newest hardening result (iter 041) adds:

> A paper-facing figure/table pack now exists at `papers/final_paper/figures_tables/figure_table_pack_v1.md`, high-priority reference metadata has been verified and documented in `papers/final_paper/references_verification_v1.md`, and the workload/policy-mix stress matrix has been rerun over five seeds with 40/40 cells successful. The current paper drafts and `results/FINDINGS.md` have been updated to remove the old three-seed stress caveat.

The newest paper-asset result (iter 042) adds:

> Six paper SVG figures now exist in `papers/final_paper/figures_tables/`, generated by `scripts/generate_paper_figures.py` and reproducible with `make figures`. A figure manifest with source paths and caption guardrails exists at `papers/final_paper/figures_tables/paper_figures_manifest.md`. A cleaned IEEE-style reference list for supervisor review exists at `papers/final_paper/references_ieee_final_v1.md`, and both the generated figures and full reference list have been inserted into `papers/final_paper/paper_draft_v1.md`.

The supervisor-review memo adds:

> `papers/final_paper/supervisor_review_memo_v1.md` summarizes the current claim, what not to claim, which figures should stay in the main paper, what should move to appendix, current weaknesses, and questions to ask the supervisor.

Evidence:

- `results/tables/full_grid_per_attack.csv`
- `results/tables/full_grid_aas_by_defense.csv`
- `results/tables/adaptive_attack_summary.csv`
- `results/tables/nspi_ablation.csv`
- `results/tables/nspi_compromised_signer_sensitivity_summary.csv`
- `results/tables/nspi_targeted_compromised_signer_summary.csv`
- `results/tables/explanation_audit_quality.csv`
- `results/tables/explanation_audit_quality_summary.csv`
- `results/tables/workload_policy_stress_summary.csv`
- `results/tables/workload_policy_stress_raw.csv`
- `results/tables/seed_confidence_summary.csv`
- `results/tables/seed_confidence_raw.csv`
- `reports/iteration/iter_034_threat_model_results_notes.md`
- `papers/final_paper/threat_model/threat_model_draft_v1.md`
- `papers/final_paper/results/results_draft_v1.md`
- `reports/iteration/iter_035_paper_sections_v1.md`
- `papers/final_paper/methodology/methodology_draft_v1.md`
- `papers/final_paper/related_work/related_work_draft_v1.md`
- `reports/iteration/iter_036_methodology_related_work_v1.md`
- `papers/final_paper/limitations/limitations_draft_v1.md`
- `papers/final_paper/conclusion/conclusion_draft_v1.md`
- `papers/final_paper/paper_skeleton_v1.md`
- `reports/iteration/iter_037_limitations_conclusion_skeleton.md`
- `papers/final_paper/introduction/introduction_draft_v1.md`
- `reports/iteration/iter_038_introduction_v1.md`
- `papers/final_paper/references_ieee_map.md`
- `reports/iteration/iter_039_reference_map_intro_citations.md`
- `papers/final_paper/paper_draft_v1.md`
- `reports/iteration/iter_040_related_work_citations_and_paper_draft.md`
- `papers/final_paper/figures_tables/figure_table_pack_v1.md`
- `papers/final_paper/references_verification_v1.md`
- `reports/iteration/iter_041_figure_reference_stress5.md`
- `scripts/generate_paper_figures.py`
- `papers/final_paper/figures_tables/paper_figures_manifest.md`
- `papers/final_paper/references_ieee_final_v1.md`
- `papers/final_paper/supervisor_review_memo_v1.md`
- `reports/iteration/iter_042_figures_and_final_references.md`

Key result:

| Attack | Integrity/ABAC baselines | NS-PI |
|---|---:|---:|
| `compromised_signer` | 0/5 seeds detected | 5/5 seeds detected |

Additional baseline:

| Baseline | `compromised_signer` result |
|---|---:|
| `trusted_policy_oracle` | 5/5 seeds detected |

Important boundary:

NS-PI does **not** beat cryptographic audit overall, and it does not beat the trusted raw-attribute oracle. Its value is as an interpretable log-only drift detector under weaker auditor visibility.

Sensitivity boundary:

- Global NS-PI misses 2% and 5% global compromised-signer corruption.
- For targeted station corruption, grouped NS-PI reaches full detection at 50% of targeted eligible rows in the current workload.
- For targeted district corruption, grouped NS-PI reaches full detection at 25% of targeted eligible rows in the current workload.
- NS-PI misses 10% targeted station/district corruption.
- The trusted raw-attribute oracle detects all tested sensitivity cases because it has an independent uncompromised request view.

XAI/audit quality boundary:

- Trace completeness: 1.0 mean.
- Counterfactual coverage: 1.0 mean.
- Counterfactual validity: 0.9964 mean.
- Stable decision/reason row rate for duplicate policy contexts: 1.0 mean.
- Audit reconstruction rate: 1.0 mean.
- Decisive-attribute full text coverage: 0.781 mean, so the natural-language explanation renderer is still imperfect.

Seed-confidence boundary:

- The seed-confidence table is descriptive across-seed stability evidence.
- It is not a formal confidence interval and does not prove operational robustness.
- Stress rows now use five seeds like the full-grid, sensitivity, and XAI rows.
- The 10% compromised-signer stress result remains workload-size dependent.

## 2. Verification Status

Latest checked commands:

```bash
make lint
make test
make reproduce
python3 scripts/run_full_grid.py
python3 scripts/run_ablations.py
python3 scripts/run_nspi_sensitivity.py
python3 scripts/run_nspi_targeted_sensitivity.py
python3 scripts/run_explanation_audit_quality.py
python3 scripts/run_workload_policy_stress.py
python3 scripts/run_seed_confidence_summary.py
```

Status:

- `make lint`: passed.
- `make test`: `75 passed`.
- `make reproduce`: passed after changing workload stress to the five-seed default.
- Full-grid tables regenerated.
- Adaptive attack and NS-PI ablation tables regenerated.
- Global and targeted compromised-signer sensitivity tables regenerated.
- XAI and audit reconstruction quality tables regenerated.
- Workload and policy-mix stress tables regenerated (40/40 cells ok).
- Seed-confidence summary and raw tables regenerated (139 summary rows, 695 per-seed rows).

## 3. What Exists

| Area | Location |
|---|---|
| Revised contribution | `CONTRIBUTION.md` |
| Current results interpretation | `results/FINDINGS.md` |
| Solid research blueprint | `research_pack/16_make_seba_xai_solid_research.md` |
| Attack catalog | `src/seba/attacks/` |
| Compromised-signer attack | `src/seba/attacks/compromised_signer.py` |
| Scoring detectors | `src/seba/scoring/detectors.py` |
| Baselines | `src/seba/baselines/` |
| Trusted raw policy oracle | `src/seba/baselines/trusted_oracle.py` |
| NS-PI learner/drift/counterfactuals | `src/seba/nspi/` |
| Full evaluation grid | `scripts/run_full_grid.py` |
| Ablations | `scripts/run_ablations.py` |
| Global compromised-signer sensitivity | `scripts/run_nspi_sensitivity.py` |
| Targeted station/district sensitivity | `scripts/run_nspi_targeted_sensitivity.py` |
| XAI/audit quality metrics | `scripts/run_explanation_audit_quality.py` |
| XAI/audit quality implementation | `src/seba/xai_quality.py` |
| Workload/policy-mix stress test | `scripts/run_workload_policy_stress.py` |
| Seed-confidence summary | `scripts/run_seed_confidence_summary.py` |
| Research papers | `sources/downloaded_research_papers_2026-05-29/` local-only folder |
| Paper draft guardrail | `papers/final_paper/README.md` |
| Introduction draft | `papers/final_paper/introduction/introduction_draft_v1.md` |
| Related Work draft | `papers/final_paper/related_work/related_work_draft_v1.md` |
| Methodology draft | `papers/final_paper/methodology/methodology_draft_v1.md` |
| Threat Model draft | `papers/final_paper/threat_model/threat_model_draft_v1.md` |
| Results draft | `papers/final_paper/results/results_draft_v1.md` |
| Limitations draft | `papers/final_paper/limitations/limitations_draft_v1.md` |
| Conclusion draft | `papers/final_paper/conclusion/conclusion_draft_v1.md` |
| Combined paper skeleton | `papers/final_paper/paper_skeleton_v1.md` |
| Reference map | `papers/final_paper/references_ieee_map.md` |
| Cleaned IEEE references | `papers/final_paper/references_ieee_final_v1.md` |
| Paper figure generator | `scripts/generate_paper_figures.py` |
| Generated paper figures | `papers/final_paper/figures_tables/` |
| Supervisor memo | `papers/final_paper/supervisor_review_memo_v1.md` |
| Iteration records | `reports/iteration/` |

## 4. Next Best Step

Send the current manuscript pack to the supervisor for direction before adding
new claims or experiments.

Reason:

The security, sensitivity, XAI-reviewability, workload-stress, and
seed-confidence evidence now exist, and iterations 034-042 have converted it
into Introduction, Threat Model, Results, Methodology, Related Work,
Limitations, Conclusion, a combined skeleton, a combined manuscript draft, a
figure/table plan, generated SVG figures, verified reference metadata notes,
and a cleaned IEEE-style reference list. The generated figures and full
reference list are now inserted in the combined manuscript, and the
supervisor-review memo records the figure-placement decision. The next
reviewer-facing need is supervisor feedback, not new evidence generation.

Minimum tasks:

1. Share `paper_draft_v1.md`, `supervisor_review_memo_v1.md`, and
   `figures_tables/paper_figures_manifest.md`.
2. Ask whether to target applied security, public-safety AI, or
   blockchain/access-control framing.
3. Do not add new claims until supervisor feedback or a new experiment exists.

## 5. Research Rules

- Do not claim deployment readiness.
- Do not claim legal compliance.
- Do not claim real police data was used.
- Do not claim SOTA.
- Do not claim NS-PI replaces blockchain or ABAC.
- Every result claim must point to a table, script, log, or source note.

## 6. Professor Explanation

Simple version:

> I narrowed the broad topic into explainable and auditable access governance for sensitive police records. The prototype now simulates inter-agency access requests, evaluates policy decisions, logs audit commitments, and tests attacks. The important result is that normal audit mechanisms catch normal log tampering, NS-PI catches a compromised-signer case from log-distribution drift, and a trusted raw-attribute oracle catches the same case when a separate trusted request view exists. I am now stress-testing how strong the NS-PI signal remains under smaller or more targeted corruption.

Updated version:

> I also completed the targeted station/district sensitivity test. It shows global drift can miss localized attacks, so grouped station/district drift is necessary. The next step is to measure whether the XAI layer is actually reviewable by adding explanation completeness, counterfactual validity, explanation stability, and audit reconstruction metrics.

Latest version:

> I also completed the XAI-quality measurement. It shows that structured explanation traces and audit reconstruction are complete in the synthetic benchmark, counterfactual explanations are almost always valid under replay, and the remaining weakness is that the natural-language explanation text does not always mention every decisive attribute. The next step is workload and policy-mix stress testing.

Current version:

> I completed the combined manuscript draft, figure/table planning, reference metadata verification, and five-seed workload/policy-mix stress rerun. The paper evidence now supports a conservative SEBA-XAI claim: blockchain-style audit, ABAC/PBAC policy checks, trusted policy re-evaluation, and NS-PI log-only drift monitoring catch different failure modes under different visibility assumptions. The next writing step is to convert the planned figures/tables into final paper visuals and do the final IEEE bibliography style pass.

Latest shareable version:

> I generated the paper figures and cleaned the IEEE-style reference list. The paper folder now has the combined draft, figure/table plan, six SVG figures, source-path manifest, verified reference notes, and a cleaned reference list. The next step is normal manuscript assembly: insert the selected figures, replace the reference placeholder, and polish the writing for supervisor review.

Current latest version:

> I inserted the generated figures and full cleaned reference list into the combined paper draft. The remaining work is no longer evidence generation; it is paper editing: decide main-paper versus appendix figures and polish the wording for supervisor review without adding new claims.

Final current version:

> I prepared the supervisor-review pack: combined draft with figures and references, generated SVG figures, source manifest, verified references, cleaned IEEE reference list, reproduction evidence, and a supervisor memo. The next action is to show this pack to the professor and get direction on venue/framing before expanding the paper.
