# Iteration 039 - Reference Map and Introduction Citation Cleanup

Date: 2026-05-30
Status: documentation/writing only - no experiments run, no tables regenerated

## Goal

Begin reference cleanup by creating a numeric IEEE-style reference map and
converting the Introduction v1 placeholder citations into numeric placeholders.

## Files created

- `papers/final_paper/references_ieee_map.md`
- `reports/iteration/iter_039_reference_map_intro_citations.md`

## Files updated

- `papers/final_paper/introduction/introduction_draft_v1.md`
- `papers/final_paper/README.md`
- `papers/final_paper/paper_skeleton_v1.md`
- `SESSION_HANDOFF.md`

## Files intentionally left unchanged

- All source code.
- All result tables.
- Related Work citations are not converted yet; that remains the next cleanup
  task.

## Honesty controls applied

- Author details that are not available in the local evidence files are marked
  "Author details to verify" instead of being guessed.
- Numeric references are mapped to existing source IDs from
  `papers/final_paper/introduction/evidence_register.csv`.
- Local artifact citations in Methodology, Results, and Limitations were left
  untouched.

## Verification

- No experiments were run.
- No result tables were regenerated.
- No source code was changed.
- Documentation checks were run after writing:
  - forbidden overclaim phrase scan on the new reference/report and Introduction
    draft;
  - local cited-path existence check for literal paths in the new files;
  - Introduction word/paragraph check remained within the target structure.

## Next step

Convert Related Work citations into the same reference map, then create a
combined manuscript draft from `papers/final_paper/paper_skeleton_v1.md`.
