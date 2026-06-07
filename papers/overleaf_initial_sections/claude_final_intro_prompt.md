# Claude Task: Final Professor-Level Introduction Draft for SEBA-XAI

You are acting as a top-level research professor and IEEE paper-writing mentor.
This is a writing-only task.

## Goal

Create the final initial version of the **Introduction** section for the
SEBA-XAI paper in Overleaf/IEEE LaTeX format.

The professor's instruction is:

> Please go through the previous papers to see the writing of the problem
> statement. Please start writing the introduction, related work first and then
> proposed methodology. Write the initial version then we will fine tune the
> problem statement and contribution. Till now all is in mind. We have to put
> in writing first. Please use Overleaf template for these parts.

Codex has already written the first Overleaf draft. Your job is to improve the
**Introduction only** so that it reads like a serious professor-level research
paper opening, while staying evidence-safe.

## Read These Files First

- `papers/overleaf_initial_sections/sections/introduction.tex`
- `papers/final_paper/introduction/introduction_draft_v2_deadline.md`
- `papers/overleaf_initial_sections/sections/related_work.tex`
- `papers/overleaf_initial_sections/sections/proposed_methodology.tex`
- `papers/overleaf_initial_sections/references.bib`
- `papers/final_paper/introduction/evidence_register.csv`
- `papers/final_paper/introduction/claim_source_table.csv`
- `01_literature_review.md`
- `02_literature_matrix.csv`
- `06_proposed_architecture.md`
- `results/FINDINGS.md`

If you inspect PDFs, focus only on writing pattern and problem-statement style.
Do not quote long passages from papers.

## Output Files To Create

Create:

1. `papers/overleaf_initial_sections/sections/introduction_final_professor.tex`
2. `papers/final_paper/introduction/introduction_final_professor.md`
3. `reports/iteration/iter_045_claude_professor_intro.md`

Do not overwrite `introduction.tex`; keep the existing draft intact.

## Required Introduction Structure

Write in IEEE-style prose, not report style.

The section should contain:

1. India digital policing context using CCTNS and ICJS.
2. The sensitive inter-agency access-governance problem.
3. A clearly written problem statement paragraph.
4. Why security/access control is necessary.
5. Why blockchain is useful only as a tamper-evident audit layer.
6. Why XAI is necessary as an audit/review artifact.
7. Why this is not ordinary crime prediction or suspect prediction.
8. What existing work covers and what gap remains.
9. SEBA-XAI proposed direction.
10. Contribution bullets.
11. Scope and non-claims.

## Hard Boundaries

Do not claim:

- CCTNS/ICJS replacement.
- live police deployment.
- actual police-record testing.
- raw records stored on-chain.
- legal compliance proof.
- privacy guarantee.
- SOTA or breakthrough.
- crime prediction superiority.
- suspect or criminal prediction.
- real Hyperledger Fabric deployment.

Correct framing:

> SEBA-XAI is a CCTNS/ICJS-compatible secure overlay for explainable,
> auditable access governance over sensitive inter-agency police records.

## Evidence-Safe Claims

You may use these claims:

- Official sources describe CCTNS and ICJS as existing Indian digital
  policing/criminal-justice infrastructure.
- CCTNS has national police-station coverage according to the official PIB
  source.
- ICJS connects police/CCTNS with courts, prisons, forensics, and prosecution.
- ABAC is suitable for contextual authorization because it uses subject,
  object, action, and environment attributes.
- Blockchain is useful for tamper-evident audit commitments across known
  agencies, but raw sensitive records should stay off-chain.
- XAI should be logged as an audit artifact, not just shown as a dashboard.
- Public NCRB data is aggregate reported/registered crime data, not a public
  individual FIR/access-control dataset.
- The prototype and benchmark are synthetic.

## Citation Rules

Use the existing BibTeX keys in:

- `papers/overleaf_initial_sections/references.bib`

Do not invent citation keys.
Do not add new references unless absolutely necessary.
Prefer these citations:

- `\cite{pib_cctns_2026}`
- `\cite{mha_icjs_2026}`
- `\cite{nist_abac_2014}`
- `\cite{nist_blockchain_access_2022}`
- `\cite{androulaki_fabric_2018}`
- `\cite{zhao_fabric_abac_2022}`
- `\cite{kim_two_level_2021,li_lechain_2021}`
- `\cite{rudin_2019}`
- `\cite{zocholl_xai_law_enforcement_2025}`
- `\cite{ensign_feedback_2018}`
- `\cite{ncrb_2023}`

## Style

- Use simple but strong academic English.
- Avoid robotic phrases.
- Avoid hype.
- Avoid too many adjectives.
- Make the problem statement clear and defensible.
- Write as if it is the first serious draft to send to a research supervisor.
- Around 1,200-1,600 words.

## Verification Before Finishing

In the iteration report, state:

- files created;
- what sources were used;
- any claims deliberately avoided;
- whether all citation keys used are present in `references.bib`;
- whether any unsupported claims remain.

Do not run experiments.
Do not edit source code.
Do not regenerate result tables.
