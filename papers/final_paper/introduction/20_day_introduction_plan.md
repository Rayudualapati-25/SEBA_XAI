# 20-Day Introduction Research And Writing Plan

Created: 2026-05-16  
Deadline: 2026-06-15  
Daily workload: 2 hours per day  
Target section: IEEE-style Introduction, 1200-1600 words

## Outcome

By 2026-06-15, produce an evidence-safe introduction for the SEBA-XAI paper. The introduction must answer:

1. Why the problem matters in India.
2. What CCTNS/ICJS already solve.
3. What gap remains.
4. Why blockchain, security/privacy/access control, and XAI are all necessary.
5. Why this is not ordinary crime prediction.
6. What the paper contributes.
7. What the paper does not claim.

## Daily Work Block Template

Use the same structure every day:

1. 15 minutes: reread yesterday's notes and today's objective.
2. 45 minutes: source reading or evidence extraction.
3. 45 minutes: write or revise one introduction component.
4. 15 minutes: update claim-source table and daily log.

Do not spend the whole session reading. Every day must leave behind a written artifact.

## Day 1, 2026-05-16: Build Control Document

Objective: set the paragraph map and writing rules.

Tasks:

- Read `research_pack/00_problem_understanding.md`, `research_pack/01_literature_review.md`, `research_pack/05_research_gap.md`, and `research_pack/11_paper_outline.md`.
- Confirm the paper identity: SEBA-XAI as the testable system, PAX-ICJS++ as future ecosystem framing only.
- Create the paragraph slots:
  1. India digital policing context.
  2. Sensitive inter-agency data-sharing problem.
  3. CCTNS/ICJS as baseline.
  4. Remaining audit/access governance gap.
  5. Blockchain role and limits.
  6. ABAC/PBAC/security role.
  7. XAI role.
  8. Fragmented related work gap.
  9. Proposed SEBA-XAI direction.
  10. Contributions.
  11. Scope boundaries.

Deliverable:

- `introduction_control_document.md`
- `introduction_skeleton.md`

Acceptance check:

- You can explain the paper in five sentences without saying "replace CCTNS".

## Day 2, 2026-05-17: CCTNS And ICJS Evidence

Objective: ground the opening in official India sources.

Sources:

- PIB CCTNS operational police stations: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241
- MHA ICJS/NCRB administration page: https://www.mha.gov.in/en/commoncontent/icjsncrb-administration

Extract:

- all 17,798 police stations using CCTNS as of 2026-02-01;
- FIRs, chargesheets, and related process digitized in CCTNS;
- State Data Centres and National Data Centre replication;
- search facility for crime, criminal, and property information;
- standardized Integrated Investigation Forms;
- master codes for state, district, police station, acts, and sections;
- ICJS components: Police/CCTNS, courts, prisons, forensics, prosecution;
- ICJS 2.0 upgrades where MHA states them.

Deliverable:

- 6-8 verified bullets in `evidence_register.csv`.
- Draft paragraph 1.

Acceptance check:

- Do not claim that CCTNS data is public.
- Do not claim universal full real-time interoperability unless the source says it.

## Day 3, 2026-05-18: Sensitive Data And Access Governance

Objective: define the problem at record-request level.

Tasks:

- List sensitive record types: FIR details, witness statements, victim data, juvenile records, forensic reports, cybercrime complaints, case diary material, evidence media, court/prosecution records.
- Define request actors: requesting officer, record-owning station, approving superior, auditor, prosecutor/court user.
- Define what must be recorded: request ID, subject attributes, object attributes, purpose, policy version, decision, approval, explanation hash, timestamp.
- Draft paragraph 2.

Acceptance check:

- Paragraph must be about access governance, not generic crime prediction.

## Day 4, 2026-05-19: Blockchain Literature

Objective: state blockchain's useful role and hard limits.

Sources:

- Hyperledger Fabric: https://arxiv.org/abs/1801.10228
- NISTIR 8403: https://doi.org/10.6028/NIST.IR.8403
- Two-Level Blockchain System for Digital Crime Evidence Management: https://www.mdpi.com/1424-8220/21/9/3051
- LEChain: https://doi.org/10.1016/j.future.2020.09.038
- Blockchain access-control survey: https://arxiv.org/abs/1908.08503

Deliverable:

- For each source: what it proves, what it does not prove, one sentence usable in introduction.
- Draft paragraph 3.

Acceptance check:

- Paragraph must say raw sensitive data stays off-chain.

## Day 5, 2026-05-20: Framing Decision Gate

Objective: freeze the paper identity.

Decision:

- Use SEBA-XAI as the paper identity.
- Keep PAX-ICJS++ as a future direction only.

Tasks:

- Freeze title.
- Write 100-word problem statement.
- Write 3-sentence elevator pitch.
- Draft paragraph 4 on the gap between existing infrastructure and auditable explainable access governance.

Acceptance check:

- The gap must be stateable in one sentence.

## Day 6, 2026-05-21: Security And ABAC/PBAC

Objective: prove access control is central, not an implementation detail.

Sources:

- NIST SP 800-162: https://csrc.nist.gov/pubs/sp/800/162/upd2/final
- Fabric ABAC paper: https://doi.org/10.1016/j.jisa.2022.103182

Tasks:

- Define RBAC, ABAC, PBAC, credential revocation, superior approval, and policy versioning.
- Explain subject, object, action, and environment attributes.
- Draft paragraph 5.

Acceptance check:

- ABAC/PBAC must appear before blockchain hype in the argument.

## Day 7, 2026-05-22: XAI Evidence

Objective: justify XAI as procedural accountability.

Sources:

- Rudin 2019: https://doi.org/10.1038/s42256-019-0048-x
- XAI in law enforcement 2025: https://doi.org/10.3389/fpos.2025.1605619
- Predictive-policing feedback loops: https://proceedings.mlr.press/v81/ensign18a.html
- Fair prediction: https://doi.org/10.1089/big.2016.0047

Tasks:

- Extract explanation audiences: officer, superior, auditor, court/prosecutor, affected person where applicable.
- Draft paragraph 6 on XAI for allow/deny/escalate justification.

Acceptance check:

- Do not claim XAI solves trust.

## Day 8, 2026-05-23: Crime Prediction Boundary

Objective: prevent the introduction from becoming a weak predictive-policing paper.

Sources:

- NCRB Crime in India 2023: https://www.data.gov.in/catalog/crime-india-2023
- BPRD DoPO: https://bprd.nic.in/en/page/data_on_police_organization_dopo

Tasks:

- Write boundary note: public NCRB data is aggregate and reported/registered.
- Draft paragraph 7 explaining why the paper is not individual suspect prediction.

Acceptance check:

- No "predict criminals" language.

## Day 9, 2026-05-24: Related Work Compression

Objective: compress related work into introduction-friendly form.

Clusters:

1. Indian digital policing infrastructure.
2. Blockchain/evidence/access-control systems.
3. Security/privacy/access-control methods.
4. XAI/fairness/high-stakes law enforcement.

Deliverable:

- 2 sentences per cluster: what exists, what remains missing.
- Draft paragraph 8.

Acceptance check:

- Keep literature detail for Related Work section, not Introduction.

## Day 10, 2026-05-25: Contribution Design

Objective: produce contribution bullets that are honest before experiments.

Contribution wording:

1. Formulate a CCTNS/ICJS-compatible access-governance problem.
2. Propose SEBA-XAI as a blockchain-audited ABAC/PBAC and XAI artifact overlay.
3. Define a reproducible synthetic multi-station workload and evaluation plan.
4. Identify metrics for audit completeness, tamper detection, false allows/denies, metadata leakage, latency, and explanation stability.

Deliverable:

- Draft paragraph 9 and contribution bullets.

Acceptance check:

- Contributions must not claim completed results unless experiments exist.

## Day 11, 2026-05-26: Non-Claims And Scope

Objective: make the introduction impossible to misread as hype.

Non-claims:

- not replacing CCTNS/ICJS;
- not storing raw records on-chain;
- not legal compliance proof;
- not deployment;
- not SOTA crime prediction;
- not individual prediction from public data.

Deliverable:

- Short non-claims paragraph.

Acceptance check:

- Reviewer cannot reasonably accuse the paper of predictive-policing overclaim.

## Day 12, 2026-05-27: Rough Introduction

Objective: assemble full rough draft.

Target:

- 1800-2200 words.
- Keep citation placeholders.
- Do not polish yet.

Structure:

1. Opening context.
2. Infrastructure baseline.
3. Sensitive access problem.
4. Three-pillar need.
5. Literature gap.
6. Proposed system.
7. Contributions.
8. Scope boundaries.

Acceptance check:

- Every paragraph has a function.

## Day 13, 2026-05-28: Evidence Audit

Objective: make each factual sentence defensible.

Tasks:

- For every factual claim, mark: source exists, source missing, inference, or remove.
- Update `claim_source_table.csv`.
- Remove unsupported claims.

Acceptance check:

- No unsupported factual claim remains.

## Day 14, 2026-05-29: Citation Strengthening

Objective: replace weak references with authoritative ones.

Citation targets:

- 12-18 high-quality introduction citations.
- Official India sources for CCTNS/ICJS.
- NIST for ABAC and blockchain access control.
- Fabric systems paper.
- Blockchain evidence/access-control papers.
- XAI/high-stakes law-enforcement papers.
- NCRB/BPRD for data boundaries.

Acceptance check:

- No citation stuffing.

## Day 15, 2026-05-30: Argument Flow Revision

Objective: make the logic unavoidable.

Flow:

1. India has infrastructure.
2. Infrastructure creates sharing opportunity and governance risk.
3. Sensitive records require contextual authorization.
4. Audit must be tamper-evident across agencies.
5. AI decisions require explanation.
6. Existing work treats these separately.
7. SEBA-XAI combines them in a measurable overlay.

Acceptance check:

- Reader knows why all three pillars are needed by paragraph 5.

## Day 16, 2026-05-31: IEEE Compression

Objective: reduce to a clean IEEE introduction.

Target:

- 1200-1600 words.
- 8 paragraphs.
- 4 contribution bullets.

Acceptance check:

- It reads like a paper introduction, not a project report.

## Day 17, 2026-06-01: Reviewer Attack

Objective: anticipate objections.

Reviewer questions:

- Why blockchain instead of signed logs?
- Where is real police data?
- How is this different from Fabric ABAC?
- What exactly does XAI explain?
- Is this legal or deployable?
- Why India-specific if the data is synthetic?
- Why not just use CCTNS logs?

Deliverable:

- Update `reviewer_objection_checklist.md`.

Acceptance check:

- Introduction anticipates objections without becoming defensive.

## Day 18, 2026-06-02: Freeze Core Wording

Objective: lock terms.

Freeze:

- problem statement;
- research gap;
- contribution bullets;
- non-claims;
- key terms.

Required terminology:

- SEBA-XAI;
- CCTNS/ICJS-compatible overlay;
- ABAC/PBAC;
- permissioned blockchain audit;
- XAI artifact logging;
- off-chain encrypted records.

Acceptance check:

- No random switching among SEBA-XAI, PAX-CCTNS, and PAX-ICJS++.

## Day 19, 2026-06-03: Final Introduction Draft v1

Objective: produce supervisor-sendable v1.

Target:

- 8 paragraphs.
- 1200-1600 words.
- IEEE-style citation placeholders.
- 4 contribution bullets.

Acceptance check:

- No fake results.
- No deployment claim.
- No legal-compliance claim.

## Day 20, 2026-06-04: Quality Gate

Objective: produce v2 and supervisor memo.

Tasks:

- Read aloud once.
- Classify each sentence as fact, interpretation, contribution, or limitation.
- Remove vague phrases: very useful, highly secure, fully transparent, guarantees privacy, revolutionary, SOTA.
- Prepare supervisor memo.

Acceptance check:

- v2 is evidence-safe and ready for polishing.

## 2026-06-05 To 2026-06-15 Buffer

June 5-6: citation cleanup.  
June 7-8: style cleanup.  
June 9-10: peer/supervisor review.  
June 11-12: feedback revision.  
June 13: technical consistency check.  
June 14: final language pass.  
June 15: freeze introduction, claim-source table, citation list, and open-risk memo.
