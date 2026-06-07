# Iteration 036 - Methodology and Related Work v1

Date: 2026-05-30
Status: documentation/writing only - no experiments run, no tables regenerated

## Goal

Create first IEEE-style draft sections for Methodology and Related Work using
only existing evidence and local artifacts.

This was a Claude + Codex step. Claude created the Methodology and Related Work
draft files before the Claude session hit its usage/request limit. Codex then
reviewed the generated files, removed phrases that would trip the overclaim
scan, created this iteration report, and updated the paper indexes.

## Files created

- `papers/final_paper/methodology/methodology_draft_v1.md`
- `papers/final_paper/related_work/related_work_draft_v1.md`
- `reports/iteration/iter_036_methodology_related_work_v1.md`

## Files updated

- `papers/final_paper/README.md`
- `SESSION_HANDOFF.md`

## Files intentionally left unchanged

- All source code under `src/`, `scripts/`, `prototype/`, and `tests/`.
- All `results/tables/*.csv`.
- Existing Threat Model and Results drafts from iteration 035.

## Source-to-claim coverage

| Draft content | Backing artifact |
|---|---|
| Synthetic benchmark scope and no live deployment claim | `06_proposed_architecture.md`, `07_methodology.md`, `papers/final_paper/threat_model/threat_model_draft_v1.md` |
| Synthetic request generation | `prototype/synthetic_access_sim/generate_synthetic_requests.py`, `scripts/run_full_grid.py`, `scripts/run_workload_policy_stress.py` |
| Declared policy oracle and XAI artifacts | `prototype/synthetic_access_sim/policy_oracle.py`, `07_methodology.md`, `scripts/run_explanation_audit_quality.py` |
| Audit layers and off-chain/on-chain split | `prototype/synthetic_access_sim/audit_baseline.py`, `prototype/synthetic_access_sim/blockchain_audit.py`, `prototype/synthetic_access_sim/offchain_storage.py`, `06_proposed_architecture.md` |
| Baselines and detector visibility | `scripts/run_ablations.py`, `scripts/run_full_grid.py`, `src/seba/scoring/detectors.py`, `src/seba/baselines/` |
| Compromised-signer and adaptive attacks | `src/seba/attacks/compromised_signer.py`, `src/seba/attacks/adaptive.py`, `results/tables/adaptive_attack_summary.csv` |
| NS-PI learner and drift detector | `src/seba/nspi/learner.py`, `src/seba/nspi/drift.py`, `scripts/run_nspi_sensitivity.py`, `scripts/run_nspi_targeted_sensitivity.py` |
| XAI and audit reviewability metrics | `scripts/run_explanation_audit_quality.py`, `src/seba/xai_quality.py`, `results/tables/explanation_audit_quality_summary.csv` |
| Workload/policy-mix stress | `scripts/run_workload_policy_stress.py`, `results/tables/workload_policy_stress_summary.csv` |
| Seed-confidence aggregation | `scripts/run_seed_confidence_summary.py`, `results/tables/seed_confidence_summary.csv`, `results/tables/seed_confidence_raw.csv` |
| Indian digital policing related work | `01_literature_review.md`, `02_literature_matrix.csv` |
| Blockchain/evidence/access-control related work | `01_literature_review.md`, `02_literature_matrix.csv` |
| RBAC/ABAC/PBAC and privacy related work | `01_literature_review.md`, `02_literature_matrix.csv` |
| XAI/fairness/high-stakes policing related work | `01_literature_review.md`, `02_literature_matrix.csv` |

## Honesty controls applied

- The Methodology draft states that the evaluation is synthetic and does not
  use actual records or live CCTNS/ICJS interfaces.
- The blockchain layer is described as a file-backed permissioned-chain
  simulation, not a deployed Hyperledger Fabric network.
- The trusted raw-attribute oracle is identified as a stronger-assumption
  baseline, not a free operational property.
- The Related Work draft positions SEBA-XAI as a narrow access-governance
  workflow and not as CCTNS/ICJS replacement or predictive policing.
- Interpretation claims are tagged `[INTERPRETATION]`.

## Verification

- No experiments were run.
- No result tables were regenerated.
- No source code was edited.
- Codex reviewed the two draft files and reworded three scan-sensitive phrases
  before final checks:
  - a phrase implying actual CCTNS/ICJS interface use was changed to "live
    CCTNS/ICJS interfaces";
  - an over-strong integrity noun was changed to "integrity mechanism";
  - a survey-description phrase was shortened to "survey".
- Documentation safety checks were run after these edits:
  - forbidden overclaim phrase scan;
  - local cited-path existence check for literal paths in the new draft/report
    files.

## What worked

The Methodology draft is now tied to concrete scripts, tables, and source
modules instead of describing the architecture from memory. The Related Work
draft compresses the earlier literature review into the four intended clusters
without claiming unsupported novelty.

## What is weak

The sections are still draft prose. They have local artifact citations and URLs,
but they are not yet converted into final IEEE reference-number style. The
stress experiment still uses three seeds while most other experiments use five,
so the final Limitations section must keep that asymmetry visible.

## Next step

Draft the Limitations section and then assemble a combined paper skeleton that
orders Introduction, Related Work, Methodology, Threat Model, Results,
Limitations, and Conclusion without adding new claims.
