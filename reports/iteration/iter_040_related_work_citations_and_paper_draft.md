# Iteration 040 - Related Work Citations and Combined Paper Draft

Date: 2026-05-30

## Goal

Resume from `SESSION_HANDOFF.md` and complete the next documentation step:
convert Related Work citations into the working IEEE-style reference map and
assemble a single manuscript draft from the current paper sections.

## Files Updated

- `papers/final_paper/references_ieee_map.md`
- `papers/final_paper/related_work/related_work_draft_v1.md`
- `papers/final_paper/paper_draft_v1.md`

## Claude / Codex Coordination

Claude was checked through the desktop app. A stale older workflow restarted
after retry, so it was stopped to avoid overlapping edits. Claude was then
given a review-only citation-cleanup prompt and returned a checklist without
editing files. Codex performed the actual file edits and verification.

Claude's suggested numbering order differed from the handoff plan. The final
map uses the local matrix/handoff order:

- `[13]` Fabric-based digital evidence management
- `[14]` blockchain auditable access control for distributed business processes
- `[15]` blockchain access-control survey
- `[16]` accountable/privacy-preserving blockchain access control
- `[17]` privacy-preserving ML survey
- `[18]` differential privacy deep learning
- `[19]` recidivism prediction limits
- `[20]` disparate-impact fairness
- `[21]` fair risk-score trade-offs
- `[22]` dialogue-based XAI for predictive policing
- `[23]` blockchain audit of AI-supported legal decisions
- `[24]` blockchain-XAI-justice architecture
- `[25]` India aggregate crime analytics
- `[26]` India murder-motive forecasting and XAI
- `[27]` CriX crime demographics and XAI
- `[28]` IndianBailJudgments-1200

## Citation Cleanup

`papers/final_paper/related_work/related_work_draft_v1.md` no longer uses raw
URLs or `02_literature_matrix.csv` row references as paper citations. The
section now cites numeric placeholders `[1]` through `[28]` where needed.

The reference map now includes working entries through `[28]`. Bibliographic
metadata missing from local evidence is explicitly marked as "Author details to
verify" instead of guessed. This is especially important for entries derived
from the local literature matrix without full publisher metadata.

## Combined Draft

Created `papers/final_paper/paper_draft_v1.md` as a first combined manuscript
draft with:

- title
- abstract
- keywords
- Introduction
- Related Work
- Methodology
- Threat Model
- Results
- Limitations and Future Work
- Conclusion
- reference-map pointer

The draft is intentionally compact and evidence-bound. Quantitative claims are
tied to local artifacts such as:

- `results/tables/full_grid_aas_by_defense.csv`
- `results/tables/full_grid_per_attack.csv`
- `results/tables/seed_confidence_summary.csv`
- `results/tables/nspi_compromised_signer_sensitivity_summary.csv`
- `results/tables/nspi_targeted_compromised_signer_summary.csv`
- `results/tables/explanation_audit_quality_summary.csv`
- `results/tables/workload_policy_stress_summary.csv`

## Verification

Commands run:

```bash
rg -n 'https?://|`02_literature_matrix\.csv` row|row [0-9]+' papers/final_paper/related_work/related_work_draft_v1.md
rg -n '<overclaiming phrase pattern>' papers/final_paper/paper_draft_v1.md papers/final_paper/related_work/related_work_draft_v1.md papers/final_paper/references_ieee_map.md
rg -o '\[[0-9]+\]' papers/final_paper/paper_draft_v1.md papers/final_paper/related_work/related_work_draft_v1.md | sed 's/^.*://' | sort -u
rg -o '^\[[0-9]+\]' papers/final_paper/references_ieee_map.md | sort -u
wc -w papers/final_paper/paper_draft_v1.md papers/final_paper/related_work/related_work_draft_v1.md papers/final_paper/references_ieee_map.md
```

Results:

- Related Work raw URL / row-citation scan: clean (`rg` exit 1).
- Overclaim phrase scan on the updated paper surfaces: clean (`rg` exit 1).
- Numeric placeholders used by the combined draft and Related Work are covered
  by the reference map.
- `paper_draft_v1.md` word count: 2889.

No experiments were run. No result tables were regenerated. No source code was
changed.

## What Worked

The paper now has one combined draft file instead of only separate section
drafts. Related Work citations are also integrated into the same numeric map as
the Introduction.

## What Is Weak

Several bibliography entries still need author, venue, and publisher-page
verification before final IEEE formatting. The combined draft is compact and
will need figures, table formatting, and reference cleanup before supervisor or
conference submission.

## Next Step

Prepare a paper-facing figure/table pack and final-reference cleanup plan:

1. create a small architecture figure from `06_proposed_architecture.md`;
2. create a Results table plan using existing `results/tables/*.csv`;
3. verify author/venue metadata for entries marked "Author details to verify";
4. decide whether to extend the workload/policy-mix stress matrix from three
   seeds to five seeds or retain the caveat explicitly.
