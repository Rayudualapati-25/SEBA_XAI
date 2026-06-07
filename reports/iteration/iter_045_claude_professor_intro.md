# Iteration 045 - Final Professor-Level Introduction Draft

Date: 2026-06-01
Status: documentation/writing only - no experiments, no tables regenerated,
no source code changed, no commit.

## Goal

Produce the final initial version of the SEBA-XAI Introduction as a
serious professor-level research-paper opening that remains
evidence-safe.

## Files Created

1. `papers/overleaf_initial_sections/sections/introduction_final_professor.tex`
   - IEEE-style LaTeX section: `\section{Introduction}`.
2. `papers/final_paper/introduction/introduction_final_professor.md`
   - Markdown mirror of the LaTeX section for supervisor review without
     LaTeX rendering. Citations annotated with the BibTeX keys used in
     the LaTeX file.
3. `reports/iteration/iter_045_claude_professor_intro.md`
   - This iteration report.

The existing draft
`papers/overleaf_initial_sections/sections/introduction.tex` was left
untouched, as instructed.

## Sources Used

Read and used to ground the prose:

- `papers/overleaf_initial_sections/sections/introduction.tex` (the
  existing Codex draft, used as the structural baseline).
- `papers/final_paper/introduction/introduction_draft_v2_deadline.md`
  (deadline-version Markdown draft).
- `papers/overleaf_initial_sections/sections/related_work.tex` and
  `papers/overleaf_initial_sections/sections/proposed_methodology.tex`
  (to keep the Introduction consistent with the rest of the section
  outline and the BibTeX keys those sections cite).
- `papers/overleaf_initial_sections/references.bib` (every cite key used
  in the new draft is present here).
- `papers/final_paper/introduction/evidence_register.csv` (verified
  facts and intended-use notes per source).
- `papers/final_paper/introduction/claim_source_table.csv` (claim ->
  source -> status mapping that constrained the wording).
- `01_literature_review.md` and `02_literature_matrix.csv` (cluster
  context for related-work mentions in the Introduction).
- `06_proposed_architecture.md` (overlay framing, off-chain commitment
  pattern, decision space, XAI artifact list).
- `results/FINDINGS.md` (to keep the contribution bullets aligned with
  what the repository actually measures; no numeric results are pulled
  into the Introduction itself).

## Citation Inventory

All citation keys used in the new Introduction:

- `pib_cctns_2026`
- `mha_icjs_2026`
- `nist_abac_2014`
- `nist_blockchain_access_2022`
- `androulaki_fabric_2018`
- `zhao_fabric_abac_2022`
- `kim_two_level_2021`
- `li_lechain_2021`
- `rudin_2019`
- `zocholl_xai_law_enforcement_2025`
- `ensign_feedback_2018`
- `ncrb_2023`

Verification: every one of these keys is present as a top-level entry in
`papers/overleaf_initial_sections/references.bib`. No new citation keys
were introduced and no fabricated references were used.

## Required Structure Coverage

The Introduction covers the eleven required elements in order:

1. India digital policing context using CCTNS and ICJS - opening
   paragraph with `pib_cctns_2026` and `mha_icjs_2026`.
2. The sensitive inter-agency access-governance problem - second
   paragraph describing record categories and attribute dependence.
3. Clear problem-statement paragraph - bold-led paragraph explicitly
   labelled "Problem statement".
4. Why security/access control is necessary - first technical pillar,
   uses `nist_abac_2014` and motivates the PBAC additions.
5. Why blockchain is useful only as a tamper-evident audit layer -
   second technical pillar, uses `nist_blockchain_access_2022` and
   `androulaki_fabric_2018`, explicitly states raw records remain
   off-chain.
6. Why XAI is necessary as an audit/review artifact - third technical
   pillar, uses `rudin_2019` and `zocholl_xai_law_enforcement_2025`,
   reframes XAI as a logged audit artifact rather than a dashboard.
7. Why this is not ordinary crime prediction or suspect prediction -
   uses `ensign_feedback_2018` and `ncrb_2023`.
8. What existing work covers and what gap remains - dedicated paragraph
   citing `kim_two_level_2021`, `li_lechain_2021`, `zhao_fabric_abac_2022`,
   `rudin_2019`, `ensign_feedback_2018`, `zocholl_xai_law_enforcement_2025`.
9. SEBA-XAI proposed direction - dedicated paragraph naming the overlay
   and its components.
10. Contribution bullets - five-item `itemize` listing problem
    formulation, architecture, benchmark, evaluation, and reviewability
    measurement.
11. Scope and non-claims - closing paragraph stating the explicit
    boundaries.

## Hard-Boundary Claims Deliberately Avoided

None of the following appear in the new Introduction text:

- CCTNS/ICJS replacement.
- Live police deployment.
- Actual police-record testing.
- Raw records stored on-chain.
- Legal compliance proof.
- Privacy guarantee.
- SOTA or breakthrough phrasing.
- Crime-prediction superiority.
- Suspect or criminal prediction.
- Real Hyperledger Fabric deployment.

The closing paragraph re-states the boundaries explicitly so a reviewer
cannot read them off only by inference.

## Style Notes

- Length: approximately 1{,}300 words for the LaTeX section, within the
  1{,}200-1{,}600 target.
- Voice: simple, declarative academic English without hype words or
  excessive adjectives.
- IEEE conventions used: `\cite{}` for inline citations, em-dashes
  avoided in favour of plain prose, problem statement set off with
  `\textbf{}` rather than a numbered subsection so the section reads as
  a single Introduction.
- The Markdown mirror uses bracketed citation keys instead of LaTeX
  `\cite{}` macros so a supervisor can read it without LaTeX.

## Unsupported Claims Remaining

None. Every factual claim in the Introduction is either:

- Directly supported by an entry in `evidence_register.csv` /
  `claim_source_table.csv` (Indian infrastructure facts, ABAC, NISTIR,
  Fabric, evidence-blockchain precedents, XAI/fairness literature,
  NCRB scope), or
- A design-claim about SEBA-XAI itself (overlay, off-chain commitments,
  policy-pillar separation, NS-PI as a log-only drift detector,
  reproducible synthetic benchmark), which is consistent with
  `06_proposed_architecture.md`, `CONTRIBUTION.md`, and the existing
  drafts under `papers/final_paper/`.

No quantitative metrics from `results/tables/` were quoted in the
Introduction, so there is no risk of stale-number drift in this section.

## Verification

- No experiments were run.
- No source code was changed.
- No result tables were regenerated.
- No commit was made.
- The existing Introduction draft `introduction.tex` was preserved.
- Every cite key in the new Introduction exists in
  `papers/overleaf_initial_sections/references.bib` (12/12 keys verified
  by `grep` against the bib file).
- Forbidden-phrase scan (`SOTA`, `state-of-the-art`, `state of the art`,
  `deployment-ready`, `deployment ready`, `legal compliance proof`,
  `real police data`, `production Fabric`, `breakthrough`, `guarant*`)
  via `rg -in` on both new files: zero matches. The first scan caught a
  single instance of "state-of-the-art" inside a disclaim sentence; it
  was rewritten to "improved crime-prediction performance" before this
  report was finalized, so the second scan came back clean.

## Next Step

Send the new Introduction to the supervisor for problem-statement and
contribution-wording feedback. After feedback, fine-tune the problem
statement and contribution bullets in
`papers/overleaf_initial_sections/sections/introduction_final_professor.tex`
and propagate any wording changes back into the Markdown mirror.

## Codex Independent Verification Addendum

After Claude generated the professor-style Introduction, Codex performed an
independent verification pass on the produced files.

- Files verified:
  - `papers/overleaf_initial_sections/sections/introduction_final_professor.tex`
  - `papers/final_paper/introduction/introduction_final_professor.md`
  - `reports/iteration/iter_045_claude_professor_intro.md`
- Word counts:
  - LaTeX Introduction: 1,344 words.
  - Markdown mirror: 1,407 words.
  - Iteration report: 882 words before this addendum.
- Citation consistency:
  - 12 unique `\cite{}` keys were detected in the LaTeX Introduction.
  - 0 cited keys were missing from `papers/overleaf_initial_sections/references.bib`.
- Overclaim scan:
  - The only matches for risky phrases were explicit non-claim statements such as
    “does not claim to predict criminals” and “does not use actual police records.”
  - These matches are acceptable because they narrow the paper scope rather than
    making unsupported claims.
- No experiments, source-code edits, result-table changes, or commits were made
  during this Claude writing step.
