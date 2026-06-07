# Iteration 035 - Paper Sections v1 (Threat Model + Results)

Date: 2026-05-30
Status: documentation/writing only - no experiments run, no tables regenerated

## Goal

Turn the evidence-safe scaffold from iteration 034 into the first actual
paper-draft prose for two sections: Threat Model and Results.

This is a writing step. It produces no new metrics. Every quantitative
statement in the drafts is copied from an existing artifact under
`results/tables/` and cites that artifact path inline. Interpretation
statements are tagged `[INTERPRETATION]`.

## Files created

- `papers/final_paper/threat_model/threat_model_draft_v1.md`
- `papers/final_paper/results/results_draft_v1.md`

## Files updated

- `reports/iteration/iter_035_paper_sections_v1.md` (this report)

## Files intentionally left unchanged

- `papers/final_paper/results/experiment_results_narrative.md` (older
  narrative kept as-is, per task instruction).
- All `results/tables/*.csv` and all source code (no regeneration).

## Source-to-claim coverage

The two drafts cover the required content and cite these artifacts:

| Draft content | Backing artifact |
|---|---|
| Attacker model, trust assumptions, visibility | `reports/iteration/iter_034_threat_model_results_notes.md` |
| AAS ranking | `results/tables/full_grid_aas_by_defense.csv` |
| Ordinary tamper detection | `results/tables/full_grid_per_attack.csv`, `results/tables/full_grid_raw.csv` |
| Compromised-signer asymmetry + stability | `results/tables/seed_confidence_summary.csv`, `results/tables/adaptive_attack_summary.csv` |
| Global sensitivity | `results/tables/nspi_compromised_signer_sensitivity_summary.csv` |
| Targeted sensitivity | `results/tables/nspi_targeted_compromised_signer_summary.csv` |
| XAI / audit reviewability | `results/tables/explanation_audit_quality_summary.csv`, `results/tables/seed_confidence_summary.csv` |
| Workload / policy-mix stress | `results/tables/workload_policy_stress_summary.csv` |
| Seed-level stability | `results/tables/seed_confidence_summary.csv`, `results/tables/seed_confidence_raw.csv` |
| Limitations | `results/FINDINGS.md` Section 8 |

## Honesty controls applied

- No claim of SOTA, deployment readiness, legal compliance, real police-data
  performance, real CCTNS/ICJS performance, or production Fabric latency.
- No fabricated metric: every number matches a value already in the cited
  table (verified for the seed-confidence figures in iteration 034).
- Non-table statements are tagged `[INTERPRETATION]`.
- The compromised-signer attacker is explicitly described as a synthetic
  modeling assumption, and the trusted raw-attribute oracle is explicitly
  described as a strong-assumption baseline.

## Verification

- No experiments were run in this iteration.
- No result tables were regenerated.
- Only documentation files under `papers/final_paper/` and this iteration
  report were written.
- A forbidden-phrase check was run with `rg` over the two new draft files
  (SOTA, deployment-ready, legal compliance proof, real police data
  performance, production Fabric latency, guarantee); see the session log.

## Next step

Draft the remaining paper sections (Introduction is already scaffolded under
`papers/final_paper/introduction/`; Methodology and Related Work remain) using
the same source-to-claim discipline. Decide the target-venue framing recorded
in `CONTRIBUTION.md` before camera-ready polishing.
