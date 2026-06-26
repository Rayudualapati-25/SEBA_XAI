# Iteration 053: Supervisor Introduction Comments

Status: completed locally on 2026-06-26.

## What worked

- Addressed the supervisor's comment to avoid an India-only framing by adding
  recent international work on accountable blockchain access control,
  privacy-preserving ABAC, and law-enforcement XAI in the introduction.
- Added a concrete police-data governance example using the PSNI breach and
  ICO action to show why police metadata and access evidence need careful
  handling.
- Added realistic access-request roles: investigating police officer,
  ranked/supervisory officer, forensic expert, laboratory specialist,
  prosecutor or court-linked authority, and auditor.
- Replaced the older combined "Challenges and Contributions" subsection with
  separate "Practical Challenges" and "Research Contributions" subsections.
- Replaced "CCTNS/ICJS-style" wording with "CCTNS/ICJS-compatible" in the
  introduction and related work.
- Recompiled the Overleaf project and verified that the PDF preview now shows
  the corrected headings and wording.

## What is verified

- Local LaTeX compilation succeeds with `tectonic -X compile main.tex`.
- No remaining `TS:`, `\notets`, `Challenges and Contributions`, or
  `CCTNS/ICJS-style` markers remain in the local Overleaf source folder.
- Overleaf PDF preview shows `A. Practical Challenges`,
  `B. Research Contributions`, and `CCTNS/ICJS-compatible`.

## What remains weak

- The paper still needs a supervisor review for the exact final problem
  statement and contribution wording.
- Local compilation reports layout warnings, mainly underfull/overfull boxes,
  but no citation or LaTeX build errors.
- GitHub terminal push is blocked because HTTPS credentials are not available
  in the current shell session.

## Next refinement

- Push the local commit to GitHub after GitHub authentication is available.
- Ask the supervisor to review whether the four challenges map cleanly to the
  four contributions.
- Continue polishing the introduction for readability without adding new claims
  unless there is evidence in the repository.
