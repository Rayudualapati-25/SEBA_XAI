# Iteration 049 - Paper Draft v2 Assembly

Date: 2026-06-06

## Scope

Assembled the aligned Introduction, Methodology, and Results material into a
single supervisor-review draft:

- `papers/final_paper/paper_draft_v2.md`

This iteration did not run new experiments and did not introduce new numerical
claims. The draft uses the existing evidence boundary from:

- `papers/final_paper/research_master_dashboard.md`
- `papers/final_paper/claim_control_memo.md`
- `papers/final_paper/artifact_to_claim_table.csv`
- `results/FINDINGS.md`
- `results/tables/`

## What Worked

- The draft now states the central claim clearly: SEBA-XAI is a synthetic
  benchmark and research prototype for explainable, policy-aware audit of
  sensitive inter-agency access decisions.
- The Introduction, Methodology, and Results sections use the same claim
  boundary: no real police-data claim, no deployment claim, no legal-compliance
  claim, no crime-prediction claim, and no live Fabric-performance claim.
- The Results section keeps NS-PI in the correct role: complementary log-only
  drift detection, not a replacement for ABAC/PBAC, blockchain-style audit, or
  trusted raw-attribute policy checking.

## What Is Still Weak

- The draft is not yet a final IEEE manuscript. Related Work, Threat Model,
  Limitations, Conclusion, and bibliography formatting still need to be merged
  after supervisor feedback.
- The reproduction freeze has not been run for this exact draft.
- The current metadata-exposure metric is a schema-level proxy, not a formal
  privacy proof.

## Next Step

Send `paper_draft_v2.md` for supervisor review. After the claim boundary is
accepted, sync the wording into the Overleaf/IEEE manuscript and run the
reproduction-freeze checklist in
`papers/final_paper/reproduction_freeze_prep.md`.
