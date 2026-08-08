# Iteration 059 - Introduction Prose Rewrite

Date: 2026-07-28

## What Was Requested

Improve the writing quality of the Introduction in
`papers/overleaf_ieee_journal/sections/introduction.tex` without changing the
paper's claims.

## What Changed

Rewritten as connected IEEE-style argument rather than short declarative
sentences. Content preserved; structure and prose reworked.

- Opening funnel rewritten: connectivity is solved, governance is not. The
  after-the-fact reviewer (inquiry or court) is introduced in the first
  paragraph as the party the design must serve.
- Added `\IEEEPARstart` for IEEEtran journal format.
- Merged the redundant PSNI framing ("This example is outside India, but it
  illustrates the same governance risk") into a single sentence that uses the
  out-of-jurisdiction status as the argument rather than as an apology.
- Promoted the integrity-vs-semantics gap out of Contribution 4 into its own
  motivating paragraph before the problem statement. This is the paper's
  sharpest hook and was previously buried in a bullet.
- Strengthened the roles paragraph with the point that the auditor is separated
  in time from the decision, so evidence not recorded at decision time cannot be
  recovered at review time. This motivates the audit-artifact design.
- Split the trailing disclaimer text into two labelled subsections:
  `Design Scope of Each Layer` and `Scope of Claims`.
- Added a headline-result preview to `Scope of Claims`: integrity defences at
  0.0 detection on the compromised-signer attack, NS-PI drift and trusted oracle
  detecting it under stronger visibility assumptions. The previous introduction
  never previewed the main finding.
- Added the missing "remainder of this paper is organised as follows"
  paragraph with resolved cross-references.
- Added `\label{sec:related}`, `sec:methodology`, `sec:results`,
  `sec:limitations`, `sec:conclusion` to the corresponding section files.
- Refreshed `papers/seba_xai_ieee_journal_overleaf.zip`.

## What Was Deliberately Preserved

- Every citation key; no new references introduced.
- All supervisor-mandated items from iterations 053/054: non-India-only framing,
  the five recent international works, the PSNI/ICO example, the realistic role
  descriptions, and the explicit challenge-to-contribution mapping.
- All honesty hedges: synthetic workload, no live CCTNS/ICJS deployment claim,
  no legal-compliance claim, no real-record validation, no production security,
  no formal privacy, no SOTA performance.
- "CCTNS/ICJS-compatible" wording.

## Verification

- `tectonic -X compile main.tex` succeeds; `main.pdf` written.
- `main.log` contains no undefined references or undefined citations. The only
  "undefined" entries are pre-existing `TU/ptm` font-shape substitution
  warnings.
- Rendered PDF checked: `\IEEEPARstart` drop cap, subsections A-C, and numeric
  citations all resolve correctly.
- Remaining warnings are underfull/overfull hbox layout warnings, mostly in
  methodology, results, and the bibliography. Unchanged from before this
  iteration.

## What Is Still Weak

- Result numbers stated in the introduction are quoted from the synthetic
  benchmark and must stay synchronised with Section~IV if the workload is
  re-run.
- Layout warnings still need a formatting pass before final submission.
- Supervisor has not yet reviewed this revision.

## Next Step

- Sync the refreshed zip to Overleaf, or paste `introduction.tex` plus the five
  one-line `\label` additions into the live project.
- Ask the supervisor whether the promoted integrity-vs-semantics paragraph is
  the framing they want for the contribution.
