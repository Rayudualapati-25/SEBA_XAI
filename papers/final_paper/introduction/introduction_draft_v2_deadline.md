# Introduction Draft v2 - Deadline Version

Created: 2026-06-01  
Status: supervisor-ready introduction draft for discussion; still needs final venue formatting.  
Evidence basis: `evidence_register.csv`, `claim_source_table.csv`, `results/FINDINGS.md`,
`references_ieee_final_v1.md`, and the current SEBA-XAI prototype artifacts.

## Introduction

India's police and criminal-justice information systems already operate at a
large national scale. The Crime and Criminal Tracking Network and Systems
(CCTNS) provides the digital backbone for several police-station processes,
and an official Press Information Bureau release reports that all 17,798
police stations were using CCTNS as of 2026-02-01 [1]. The same source states
that CCTNS supports digitisation of police processes such as FIRs and
chargesheets, state-hosted application deployment, near-real-time replication
to a National Data Centre, search of crime, criminal, and property information,
standardised Integrated Investigation Forms, and master codes for states,
districts, police stations, acts, and sections [1]. The Inter-Operable
Criminal Justice System (ICJS) extends this digital context by linking the
police/CCTNS pillar with courts, prisons, forensics, and prosecution through a
Data Sharing Matrix [2]. Therefore, this work does not treat Indian policing
as a blank technical space. It starts from the fact that CCTNS and ICJS-style
infrastructure already exist, and studies how a secure overlay can strengthen
the governance of sensitive inter-agency access requests.

The central problem is not ordinary crime prediction. It is controlled access
to sensitive police and criminal-justice records. Such records may include FIR
details, witness and victim information, juvenile records, forensic reports,
cybercrime complaints, case diary material, evidence references, and court or
prosecution-linked information. A broad role such as "police officer" or
"agency user" is not sufficient to decide whether a record should be released.
The decision may depend on the requester's role, rank, station, jurisdiction,
case assignment, purpose of access, record sensitivity, credential status,
approval state, time window, emergency context, and connection to court,
prosecution, or forensic workflow. This creates a contextual authorization
problem. The system must decide whether to allow, deny, or escalate a request,
and an auditor must later be able to reconstruct what was requested, which
policy version was applied, which attributes affected the decision, what
explanation was generated, and who approved or reviewed the event.

Security and access control are therefore the first core requirement. Static
role-based access control is useful, but it is too coarse for many sensitive
inter-agency record-sharing situations. Attribute-Based Access Control (ABAC)
is a stronger fit because it evaluates subject, object, action, and
environmental attributes against policy rules or relationships [3]. In this
research, ABAC is combined with policy-based access control (PBAC) ideas such
as policy versioning, approval requirements, revocation state, and purpose
constraints. This framing keeps the security layer at the centre of the
architecture. Blockchain is not used as a substitute for authorization,
encryption, or privacy. Instead, authorization is performed by a contextual
policy layer, while the audit layer records commitments about the decision and
its evidence.

The blockchain component has a deliberately limited role. NISTIR 8403
describes blockchain-based access-control systems as offering properties such
as decentralization, high confidence, and tamper resistance, while also noting
implementation considerations [4]. Hyperledger Fabric is also relevant because
it is a modular permissioned blockchain system intended for known
organizations rather than open anonymous participation [5]. These properties
make a permissioned blockchain-style audit layer suitable for recording
tamper-evident commitments across police stations or criminal-justice
agencies. However, raw police records should not be placed on-chain. In the
proposed design, sensitive records remain off-chain under agency control, and
the audit layer stores only request identifiers, policy identifiers, approval
events, model or rule versions, explanation hashes, record commitments, and
other minimized metadata required for review.

Explainable AI is the third equal pillar because access decisions in
public-safety workflows must be understandable to different stakeholders.
Officers need to know why a request was allowed, denied, or escalated.
Supervisors need enough explanation to review exceptional or sensitive
requests. Auditors need to reconstruct whether the decision followed the
declared policy. Prosecutors, courts, or oversight bodies may need a traceable
record of why access was granted. In this work, XAI is not treated as a
visual dashboard added after the decision. It is treated as an audit artifact.
Each decision should preserve the decision label, reason code, decisive policy
attributes, policy version, model or rule version, counterfactual information
where applicable, and hashes that bind the explanation to the logged event.
This position follows high-stakes AI arguments that interpretable models are
preferable where feasible [9], and recent law-enforcement XAI work that
emphasizes stakeholder needs, AI literacy, and automation-bias risk [10].

This scope is important because many AI-policing proposals become weak when
they are framed as individual crime or criminal prediction. Predictive
policing research has shown that feedback loops can occur when observed or
reported crime data is shaped by earlier policing activity [11]. Public NCRB
Crime in India data is useful for aggregate reported/registered crime context,
but it is not a public individual-level CCTNS/FIR access-decision dataset
[12]. For that reason, this paper does not claim to predict criminals,
identify suspects, or replace police judgement. Aggregate crime data may help
motivate the domain, but the technical contribution is focused on explainable,
auditable, and secure access governance.

Existing research supports parts of this direction, but the complete workflow
remains underexplored. Blockchain has been studied for digital crime evidence
management and lawful evidence chain-of-custody workflows [7], [8].
Fabric-based ABAC and encrypted off-chain sharing have also been studied in
generic data-sharing settings [6]. XAI and fairness research has raised
important cautions for high-stakes criminal-justice applications [9]-[11].
However, these threads are usually studied separately. The gap addressed here
is narrower and more practical: there is limited reproducible work on a
CCTNS/ICJS-compatible access-governance overlay that jointly evaluates
contextual authorization, superior-review style escalation, off-chain
sensitive-record commitments, permissioned blockchain-style audit,
explanation artifact logging, adversarial audit attacks, and explanation
reviewability.

To address this gap, this paper proposes SEBA-XAI, a Secure, Explainable,
Blockchain-Audited access-governance overlay for sensitive inter-agency police
record sharing. SEBA-XAI is designed to sit above existing agency systems
rather than replace them. In the implemented research prototype, synthetic
CCTNS/ICJS-style access requests are evaluated by a deterministic declared
policy oracle. The prototype records policy decisions, explanation artifacts,
hash commitments, and audit metadata using signed hash-chain and
permissioned-blockchain-style logs. It also compares these mechanisms with
ledger-only baselines, ABAC/Fabric-style policy re-execution, a trusted
raw-attribute policy oracle, and an interpretable neuro-symbolic policy
induction and drift-detection component called NS-PI. The evaluation is
synthetic by design, because synthetic workloads make it possible to control
policy rules, attack types, visibility assumptions, and repeatable seeds.

This paper makes five contributions. First, it formulates a CCTNS/ICJS-
compatible access-governance problem for sensitive inter-agency police and
criminal-justice records. Second, it presents the SEBA-XAI architecture,
combining contextual access policy, off-chain sensitive records,
permissioned-blockchain-style audit commitments, and logged XAI artifacts.
Third, it implements a reproducible synthetic benchmark for allow, deny, and
escalate access decisions, including ordinary tamper attacks and validly
re-signed compromised-signer attacks. Fourth, it evaluates multiple audit and
policy-checking approaches under explicit visibility assumptions, including
ledger-only integrity checks, ABAC/Fabric-style re-execution, trusted
raw-attribute policy re-evaluation, and log-only interpretable drift
detection. Fifth, it measures reviewability through audit reconstruction,
trace completeness, decisive-attribute coverage, explanation stability,
counterfactual coverage, and latency/storage overhead.

The paper has clear limits. It does not claim live deployment inside CCTNS or
ICJS, does not use actual police records, does not store raw sensitive records
on-chain, does not prove legal compliance, and does not claim state-of-the-art
crime prediction. The blockchain layer in the prototype is a file-backed
permissioned-audit simulation rather than a live Hyperledger Fabric network.
The results should therefore be read as reproducible benchmark evidence for a
research architecture, not as operational validation. The remainder of the
paper reviews related work, describes the SEBA-XAI methodology and threat
model, presents the synthetic evaluation, discusses limitations, and outlines
future work required before any real-world pilot could be considered.

## Immediate Deadline Notes

- This version is suitable to send to a professor for feedback on problem
  framing, scope, and contribution wording.
- The strongest sentence to defend is: "The research problem is not replacing
  CCTNS/ICJS or predicting criminals; it is secure, explainable, auditable
  access governance for sensitive inter-agency records."
- The most important non-claim is that the prototype is synthetic and not a
  live police deployment.
- Before final submission, convert this section into the target paper template
  and ensure references [1]-[12] match the final bibliography exactly.
