# Introduction - Aligned Professor Draft

Status: evidence-aligned Markdown draft for supervisor review. This file is
now controlled by `papers/final_paper/research_master_dashboard.md`,
`papers/final_paper/claim_control_memo.md`, and
`papers/final_paper/artifact_to_claim_table.csv`. It is no longer guaranteed
to be an exact mirror of the older LaTeX section until the Overleaf files are
updated.

Evidence basis: `papers/final_paper/introduction/evidence_register.csv`,
`papers/final_paper/introduction/claim_source_table.csv`,
`papers/final_paper/research_master_dashboard.md`,
`papers/final_paper/claim_control_memo.md`,
`papers/final_paper/artifact_to_claim_table.csv`,
`research_pack/01_literature_review.md`, `research_pack/02_literature_matrix.csv`,
`06_proposed_architecture.md`, `results/FINDINGS.md`,
`papers/final_paper/introduction/introduction_draft_v2_deadline.md`,
`papers/overleaf_initial_sections/sections/introduction.tex`,
`papers/overleaf_initial_sections/sections/related_work.tex`, and
`papers/overleaf_initial_sections/sections/proposed_methodology.tex`.

## Introduction

India's police and criminal-justice information systems already operate at
national scale. The Crime and Criminal Tracking Network and Systems (CCTNS)
provides a digital backbone for police-station processes, and an official
Press Information Bureau release reports that all 17,798 police stations
were using CCTNS as of February 1, 2026 [pib_cctns_2026]. The same source
describes CCTNS support for First Information Reports, chargesheets,
state-hosted applications, replication to a National Data Centre, search of
crime, criminal, and property information, standardized
Integrated Investigation Forms, and master codes for states, districts,
police stations, acts, and sections [pib_cctns_2026]. The Inter-Operable
Criminal Justice System (ICJS) further connects the police pillar with
courts, prisons, forensics, and prosecution through a Data Sharing Matrix
[mha_icjs_2026]. The present work therefore does not treat the Indian
context as a missing-infrastructure problem; it starts from the position
that CCTNS- and ICJS-style infrastructure already exists and studies how a
secure overlay can be evaluated for the governance of sensitive
inter-agency access decisions over such records.

Within this digital environment, a distinct sub-problem deserves dedicated
study: controlled access to sensitive police and criminal-justice records
across agencies. Such records may include FIR details, witness and victim
information, juvenile records, forensic reports, cybercrime complaints,
case-diary material, evidence references, and court- or prosecution-linked
information. Their disclosure can affect privacy, the integrity of ongoing
investigations, victim protection, and the accountability of public
institutions. A request from a person with the broad role of "police
officer" or "agency user" is not, by itself, sufficient justification for
release. The decision typically depends on the requester's role, rank,
station, jurisdiction, case assignment, purpose of access, record
sensitivity, credential status, approval state, time window, emergency
context, and connection to court, prosecution, or forensic workflows. Each
of these attributes can flip the same request between legitimate and
inappropriate.

**Problem statement.** Given an inter-agency request for a sensitive police
or criminal-justice record, the system should decide whether to allow, deny,
or escalate the request using contextual policy rules, and should preserve
an auditable, explainable record of how that decision was reached. The
record should be sufficient for an independent reviewer to reconstruct what
was requested, which policy version was applied, which attributes were
decisive, what explanation was produced for the decision, and which approval
or review event was bound to the request. This must be achieved without
placing raw sensitive records on a shared or public ledger, and without
assuming that any single technical layer delivers confidentiality,
correctness, and accountability on its own.

The evidence-backed claim of this paper is therefore narrow: SEBA-XAI is
evaluated as a reproducible synthetic benchmark and prototype for
policy-aware audit in sensitive inter-agency access governance. It compares
ledger-only integrity checks, ABAC/Fabric-style policy re-execution,
trusted policy re-evaluation, and log-only interpretable policy-drift
detection under explicit visibility assumptions. This wording follows the
claim boundary in `papers/final_paper/claim_control_memo.md` and should not
be expanded into claims about operational deployment, legal compliance, or
crime prediction.

Three technical pillars support this problem in equal measure. The first is
security and access control. Static role-based access control is useful but
too coarse for many sensitive inter-agency record-sharing scenarios. The
NIST guide to Attribute-Based Access Control (ABAC) defines authorization
in terms of subject, object, action, and environmental attributes evaluated
against policy rules or relationships, and notes the suitability of ABAC
for information sharing across organizational boundaries [nist_abac_2014].
Building on this, the proposed overlay combines ABAC with policy-based
access-control ideas such as policy versioning, purpose constraints,
credential revocation, approval requirements, and superior review.
Authorization remains in a contextual policy layer; the audit layer is not
asked to carry that responsibility.

The second pillar is permissioned blockchain-style auditing. Blockchain is
not used here to provide privacy and is not used to store raw records.
NISTIR 8403 describes blockchain-based access-control systems in terms of
decentralization, high confidence, and tamper resistance, and also notes
practical implementation considerations such as governance and scalability
[nist_blockchain_access_2022]. Hyperledger Fabric is a relevant reference
point because it provides a modular permissioned blockchain platform
intended for known organizations rather than open anonymous participation
[androulaki_fabric_2018]. In the proposed design, sensitive records remain
off-chain under agency control while the permissioned audit layer stores
only minimized metadata and commitments, such as request identifiers,
policy identifiers, approval events, model or rule versions, explanation
hashes, and record commitments.

The third pillar is explainable AI (XAI). Access decisions in public-safety
workflows must be understandable to officers, supervisors, auditors, and
potentially court or prosecution stakeholders. In this work, XAI is not
treated as a visual dashboard added after the decision; it is treated as a
logged audit artifact. Each decision preserves the decision label, reason
code, decisive subject/object/action/environment attributes, policy
version, model or rule version, counterfactual information where
applicable, and a hash that binds the explanation to the audit event. This
position follows Rudin's argument that high-stakes decisions should prefer
interpretable models where feasible [rudin_2019] and the recent
law-enforcement XAI literature that emphasizes stakeholder-specific
explanations, AI literacy, and automation-bias risk
[zocholl_xai_law_enforcement_2025].

This scope is deliberately narrower than predictive policing or individual
suspect modelling. Predictive policing research has shown that feedback
loops can arise when observed or reported crime data is itself shaped by
earlier policing activity, so models trained on such data risk reinforcing
their own attention patterns [ensign_feedback_2018]. Public crime
statistics from the National Crime Records Bureau are useful as aggregate
reported and registered crime context, but they are not a public
individual-level CCTNS or FIR access-decision dataset [ncrb_2023]. For
these reasons, the paper does not claim to predict criminals, identify
suspects, or replace police judgement. Aggregate crime context motivates
the domain; the technical contribution is focused on secure, explainable,
and auditable access governance.

Existing research supports parts of this direction, but the integrated
workflow remains underexplored. Blockchain has been studied for digital
crime evidence management and lawful evidence chain-of-custody workflows
[kim_two_level_2021, li_lechain_2021], and Fabric combined with ABAC
together with encrypted off-chain storage has been studied in generic
data-sharing settings [zhao_fabric_abac_2022]. The XAI and fairness
literature has raised cautions specific to high-stakes criminal-justice
systems [rudin_2019, ensign_feedback_2018, zocholl_xai_law_enforcement_2025].
However, these threads are usually evaluated separately. The remaining gap
is a CCTNS- and ICJS-compatible access-governance overlay that jointly
considers contextual authorization, superior-review style escalation,
off-chain sensitive-record commitments, permissioned blockchain-style
audit, XAI artifact logging, and adversarial audit attacks within a single
reproducible benchmark.

To address this gap, the paper proposes SEBA-XAI, a Secure, Explainable,
Blockchain-Audited access-governance overlay for sensitive inter-agency
police record sharing. SEBA-XAI is designed to sit above existing agency
systems rather than replace them. The implemented research prototype
evaluates synthetic CCTNS- and ICJS-style access requests with a
deterministic declared policy oracle, records policy decisions and
explanation artifacts with hash commitments, and stores audit metadata
through signed hash-chain and permissioned blockchain-style logs. It also
compares these mechanisms against ledger-only baselines, ABAC and Fabric
re-execution baselines [zhao_fabric_abac_2022, nist_abac_2014], a trusted
raw-attribute policy oracle that assumes an independent view of the
original requests, and an interpretable neuro-symbolic policy induction
and drift-detection component referred to as NS-PI. The evaluation is
synthetic by design because actual police access logs and sensitive records
are not publicly available and should not be assumed in a first-stage
academic prototype.

The paper makes five initial contributions:

- It formulates a CCTNS- and ICJS-compatible access-governance problem
  for sensitive inter-agency police and criminal-justice records, with a
  clearly stated decision space of allow, deny, or escalate.
- It presents the SEBA-XAI architecture, combining RBAC, ABAC, and
  PBAC-style contextual policy enforcement, off-chain sensitive-record
  commitments, permissioned blockchain-style audit commitments, and logged
  XAI artifacts that are bound to audit events by hash.
- It defines a reproducible synthetic benchmark for access-request
  decisions, including ordinary tamper attacks and a validly re-signed
  compromised-signer attack model.
- It evaluates multiple audit and policy-checking strategies under explicit
  visibility assumptions, namely ledger-only integrity checks, ABAC- and
  Fabric-style policy re-execution, trusted raw-attribute policy
  re-evaluation, and log-only interpretable drift detection.
- It measures reviewability of the overlay through audit reconstruction,
  trace completeness, decisive-attribute coverage, explanation stability,
  counterfactual coverage, metadata exposure, and local latency and storage
  overhead.

The scope of the paper is intentionally limited. It does not claim live
deployment inside CCTNS or ICJS, does not use actual police records, does
not place raw sensitive records on-chain, does not prove legal compliance,
and does not claim improved crime-prediction performance. The blockchain
component in the prototype is a permissioned-audit simulation rather than a
live Hyperledger Fabric network. The results should therefore be read as
reproducible benchmark evidence for a research architecture, not as
operational validation. The remainder of the paper reviews related work in
Section II, describes the SEBA-XAI methodology and threat model in Section
III, presents the synthetic evaluation, discusses limitations, and outlines
the future work that would be required before any real-world pilot could be
considered.
