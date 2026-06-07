# Two-Month Paper Submission Schedule

Start date: 2026-06-05  
Target submission date: 2026-08-05  
Primary target: Journal of Information Security and Applications  
Backup target: IEEE Access  
Conference backup: IEEE ICBDS 2026

## Working Paper Position

The paper should be submitted as an applied information-security research paper:

> SEBA-XAI: Explainable Policy-Aware Audit for Secure Inter-Agency Police Data Access Governance

The contribution is not "AI for crime prediction" and not "blockchain replaces CCTNS/ICJS." The contribution is a reproducible security and XAI evaluation of sensitive access-governance workflows using policy checks, tamper-evident audit commitments, off-chain sensitive records, and explanation traces.

## Non-Negotiable Rules

- Do not claim real CCTNS/ICJS deployment.
- Do not claim real police-data performance.
- Do not claim legal compliance proof.
- Do not claim crime prediction.
- Do not store raw police records on-chain in the framing.
- Every result in the paper must come from a saved artifact under `results/`, `prototype/runs/`, or `experiments/runs/`.
- Every major component must have a baseline or ablation.

## Week 1: Freeze Scope and Problem Statement

Dates: 2026-06-05 to 2026-06-11

Goal: lock the exact problem statement, title, contribution, and venue.

Tasks:

- Choose final target venue: Journal of Information Security and Applications unless supervisor prefers IEEE Access.
- Freeze title.
- Freeze problem statement.
- Freeze research questions.
- Freeze contribution bullets.
- Rewrite the abstract based on the final framing.
- Check that the Introduction, Related Work, Methodology, Results, and Limitations all use the same terminology.

Deliverables:

- Final problem statement.
- Final contribution list.
- Final research questions.
- One-page supervisor memo.
- Updated Introduction draft.

Acceptance check:

- The paper can be explained in five sentences without saying "crime prediction."
- The paper clearly explains why blockchain alone is insufficient.
- The paper clearly explains what XAI explains.

## Week 2: Reproduce and Freeze Experiments

Dates: 2026-06-12 to 2026-06-18

Goal: rerun all experiments and freeze the result artifacts.

Tasks:

- Run the full reproducibility pipeline.
- Run tests.
- Confirm deterministic seeds.
- Confirm every result table has a corresponding script or run artifact.
- Confirm every plot is generated from a saved table.
- Record environment assumptions.
- Check whether the current results still match the paper draft.

Commands:

```bash
make test
make reproduce
```

Deliverables:

- Frozen `results/tables/`.
- Frozen `results/plots/`.
- Updated `results/FINDINGS.md`.
- Updated iteration report.
- Reproducibility note.

Acceptance check:

- No table in the paper is manually invented.
- No result is described unless it appears in a saved CSV/JSON/log/plot.
- All tests pass or failures are documented honestly.

## Week 3: Strengthen the Experimental Story

Dates: 2026-06-19 to 2026-06-25

Goal: make the experiments look like a real paper evaluation, not a demo.

Tasks:

- Build a clean experiment matrix:
  - mutable log baseline;
  - signed hash-chain baseline;
  - blockchain-style audit;
  - ABAC/PBAC policy re-execution;
  - trusted policy-oracle baseline;
  - NS-PI policy-drift detector;
  - SEBA-XAI full system.
- Ensure every method has a short definition.
- Ensure every attack has a short definition:
  - ordinary tampering;
  - record edit;
  - deletion;
  - replay;
  - compromised signer;
  - policy-corrupted valid signature.
- Clarify what is synthetic and why.
- Improve explanation-quality metrics.
- Add one table that maps each research question to experiments and metrics.

Deliverables:

- Final experiment setup section.
- Final method-comparison table.
- Final threat-model table.
- Research-question-to-metric table.

Acceptance check:

- A reviewer can see exactly what was tested.
- The paper does not hide weak results.
- Synthetic data is presented as a controlled benchmark, not fake real police data.

## Week 4: Finish Related Work and Novelty Comparison

Dates: 2026-06-26 to 2026-07-02

Goal: prove that the paper knows existing work and clearly separates itself.

Tasks:

- Review and compress related work into four clusters:
  - Indian digital-policing context: CCTNS/ICJS.
  - Blockchain audit and digital evidence management.
  - Access control: RBAC, ABAC, PBAC, policy re-execution.
  - XAI, auditability, and high-stakes public-sector decision support.
- Add "what exists vs what remains missing" paragraph.
- Add a related-work comparison table if venue length allows.
- Check every citation.
- Remove weak or irrelevant papers.

Deliverables:

- Final Related Work section.
- Final literature comparison table.
- Clean reference list.

Acceptance check:

- The paper does not claim novelty by ignoring existing ABAC/blockchain/XAI papers.
- The gap is specific: validly signed but policy-corrupted access decisions are hard for ledger-only audit.

## Week 5: Write Full Paper Draft v2

Dates: 2026-07-03 to 2026-07-09

Goal: assemble a complete readable paper.

Tasks:

- Merge all section drafts into one full paper.
- Write transitions between sections.
- Make all terminology consistent:
  - SEBA-XAI;
  - access governance;
  - policy-aware audit;
  - XAI traces;
  - compromised signer;
  - off-chain sensitive records;
  - blockchain-style audit commitments.
- Insert figures and tables.
- Rewrite Results as evidence-based claims.
- Rewrite Discussion as interpretation, not exaggeration.
- Keep limitations visible.

Deliverables:

- Full paper draft v2.
- Complete figure/table list.
- Complete references.

Acceptance check:

- The paper is readable from start to finish.
- Every contribution is supported by a method/result/limitation.
- Results and limitations do not contradict each other.

## Week 6: Supervisor Review and Hard Revision

Dates: 2026-07-10 to 2026-07-16

Goal: get supervisor feedback and revise the technical story.

Tasks:

- Send draft v2 to supervisor.
- Ask only focused questions:
  - Is the problem statement strong enough?
  - Are the contributions believable?
  - Is the synthetic evaluation acceptable?
  - Is the venue target suitable?
  - Are claims too broad?
- Revise problem statement and contribution wording.
- Fix unclear diagrams.
- Add missing citations.
- Remove unsupported claims.

Deliverables:

- Supervisor-feedback memo.
- Full paper draft v3.
- Updated abstract.
- Updated contribution paragraph.

Acceptance check:

- The supervisor can identify the exact contribution.
- The paper is no longer "all in mind"; it is fully written.

## Week 7: Journal Formatting and Reproducibility Package

Dates: 2026-07-17 to 2026-07-23

Goal: prepare the submission package.

Tasks:

- Convert the paper to the selected venue format.
- If targeting Journal of Information Security and Applications, follow Elsevier template requirements.
- If targeting IEEE Access, follow IEEE template requirements.
- Prepare anonymized/reproducible code package if needed.
- Prepare data availability statement.
- Prepare ethics statement.
- Prepare conflict-of-interest statement.
- Prepare cover letter draft.
- Verify citation style.
- Verify figure resolution.

Deliverables:

- Venue-formatted manuscript.
- Reproducibility package checklist.
- Data/code availability statement.
- Cover letter draft.

Acceptance check:

- The paper compiles or exports cleanly.
- The references are complete.
- The result artifacts are traceable.

## Week 8: Final Quality Gate and Submission

Dates: 2026-07-24 to 2026-08-05

Goal: submit the paper.

Tasks:

- Run final tests.
- Run final reproduce command if needed.
- Run final overclaim scan.
- Check all citations.
- Check all tables and figures.
- Proofread line by line.
- Remove tutorial-style writing.
- Remove repeated claims.
- Confirm venue formatting.
- Submit manuscript.

Commands:

```bash
make test
make reproduce
```

Suggested overclaim scan:

```bash
rg -n "SOTA|state-of-the-art|breakthrough|guarantee|fully secure|legal compliance proof|deployment-ready|real police data|predict criminals|replace CCTNS|replace ICJS" papers/final_paper
```

Deliverables:

- Submitted manuscript.
- Submitted cover letter.
- Final source package.
- Final reproducibility package.
- Submission confirmation screenshot or email.

Acceptance check:

- Manuscript submitted by 2026-08-05.
- Every non-obvious claim is supported.
- The paper clearly states synthetic-workload limitations.

## Daily Workload Plan

Minimum daily workload: 2 hours.

Recommended split:

- 30 minutes: read/review one section or one result table.
- 60 minutes: write or revise.
- 20 minutes: citation/result verification.
- 10 minutes: update progress note.

On experiment days:

- 30 minutes: run commands.
- 30 minutes: inspect logs.
- 40 minutes: update tables/figures/results wording.
- 20 minutes: document limitations.

## Final Submission Checklist

- Title fixed.
- Abstract fixed.
- Problem statement fixed.
- Contributions fixed.
- Research questions fixed.
- Related work complete.
- Methodology complete.
- Threat model complete.
- Experiment setup complete.
- Results complete.
- Discussion complete.
- Limitations complete.
- Ethics/legal scope complete.
- References verified.
- Tables verified.
- Figures verified.
- Reproducibility package ready.
- Cover letter ready.
- Supervisor approval received.

## Preferred Paper Framing

Use this sentence everywhere:

> This paper evaluates SEBA-XAI as a reproducible, policy-aware audit framework for sensitive inter-agency access governance, showing how access-control decisions, tamper-evident audit commitments, and explanation traces can be combined and evaluated under controlled compromised-signer and policy-corruption scenarios.

Avoid this sentence:

> This paper predicts crime using blockchain and explainable AI for Indian police data.

## Final Two-Month Outcome

By 2026-08-05, the target outcome is a submitted journal paper or, at minimum, a complete submission-ready manuscript with frozen experiments, verified figures, verified references, supervisor feedback, and a prepared cover letter.
