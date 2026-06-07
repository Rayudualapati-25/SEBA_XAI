# Iteration 038 - Introduction Draft v1

Date: 2026-05-30
Status: documentation/writing only - no experiments run, no tables regenerated

## Goal

Revise the older Introduction scaffold into a current evidence-bounded v1 that
matches the narrowed SEBA-XAI / NS-PI contribution and the section drafts from
iterations 035-037.

Claude was still unavailable due the active usage limit, so Codex completed
this writing step from local evidence.

## Files created

- `papers/final_paper/introduction/introduction_draft_v1.md`
- `reports/iteration/iter_038_introduction_v1.md`

## Files updated

- `papers/final_paper/README.md`
- `papers/final_paper/paper_skeleton_v1.md`
- `SESSION_HANDOFF.md`

## Files intentionally left unchanged

- `papers/final_paper/introduction/introduction_draft_v0.md` remains as the
  older scaffold for comparison.
- All source code and result tables.

## Source-to-claim coverage

| Introduction content | Backing artifact |
|---|---|
| CCTNS and ICJS baseline facts | `papers/final_paper/introduction/evidence_register.csv`, `papers/final_paper/introduction/claim_source_table.csv` |
| ABAC/PBAC rationale | `papers/final_paper/introduction/evidence_register.csv`, `01_literature_review.md` |
| Blockchain role and limits | `papers/final_paper/introduction/evidence_register.csv`, `papers/final_paper/methodology/methodology_draft_v1.md` |
| XAI role and predictive-policing boundary | `papers/final_paper/introduction/evidence_register.csv`, `papers/final_paper/related_work/related_work_draft_v1.md` |
| SEBA-XAI prototype scope | `papers/final_paper/methodology/methodology_draft_v1.md`, `06_proposed_architecture.md` |
| NS-PI narrowed contribution | `CONTRIBUTION.md`, `results/FINDINGS.md`, `results/tables/seed_confidence_summary.csv` |
| Scope boundaries | `papers/final_paper/limitations/limitations_draft_v1.md`, `papers/final_paper/threat_model/threat_model_draft_v1.md` |

## Honesty controls applied

- The introduction says CCTNS/ICJS already exist and SEBA-XAI is an overlay,
  not a replacement.
- The key NS-PI result is stated as a complementary log-only signal, not an
  overall detector win.
- The trusted raw-attribute oracle remains visible as the stronger baseline.
- The introduction states that the prototype uses synthetic requests and no
  actual police records.
- The blockchain layer is described as a file-backed permissioned-audit
  simulation, not a live Fabric network.

## Verification

- No experiments were run.
- No result tables were regenerated.
- No source code was changed.
- Documentation checks were run after writing:
  - forbidden overclaim phrase scan on the new introduction/report;
  - local cited-path existence check for literal paths in the new files.

## What worked

The introduction now reflects the current paper identity:
SEBA-XAI as a benchmarked architecture for explainable policy-drift detection
and trusted policy re-evaluation in blockchain-audited police access
governance.

## What is weak

Citation placeholders still need conversion into IEEE numeric references. The
draft is evidence-safe but still needs final compression and style polishing
before supervisor submission.

## Next step

Create an IEEE-style reference map and convert placeholder citations in the
Introduction and Related Work into consistent numeric references.
