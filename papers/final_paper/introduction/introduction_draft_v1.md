# Introduction Draft v1

Created: 2026-05-30
Status: current evidence-bounded introduction draft; not final camera-ready prose.
Evidence basis: `papers/final_paper/introduction/evidence_register.csv`,
`papers/final_paper/introduction/claim_source_table.csv`, `CONTRIBUTION.md`,
`results/FINDINGS.md`, and the section drafts under `papers/final_paper/`.

## Introduction

India's police and criminal-justice information systems are already operating
at national scale. The Crime and Criminal Tracking Network and Systems (CCTNS)
provides a digital backbone for police processes, and an official Press
Information Bureau release reports that all 17,798 police stations were using
CCTNS as of 2026-02-01 [1]. The same source describes CCTNS
support for digitizing police processes including FIRs and chargesheets,
state-hosted application deployment, near-real-time replication to a National
Data Centre, search of crime, criminal, and property information, standardized
Integrated Investigation Forms, and master codes for states, districts, police
stations, acts, and sections [1]. The Inter-Operable Criminal
Justice System (ICJS) further connects the police/CCTNS pillar with courts,
prisons, forensics, and prosecution through a Data Sharing Matrix
[2]. This paper therefore starts from a baseline of existing
digital infrastructure. The research problem is not replacing CCTNS or ICJS,
but studying how an additional access-governance overlay can make sensitive
inter-agency record requests more auditable, explainable, and measurable.

Inter-agency access to police and criminal-justice records is not an ordinary
database query problem. Records may include FIR details, witness and victim
information, juvenile records, forensic reports, cybercrime complaints, case
diary material, evidence references, and court or prosecution-linked records.
A requester's organization or broad role is not enough to justify disclosure.
The decision may depend on role, rank, station, jurisdiction, case assignment,
purpose, record sensitivity, credential status, approval state, time window,
emergency context, and whether the request is connected to court, prosecution,
or forensic workflow. These factors create a contextual authorization problem:
the system must decide whether to allow, deny, or escalate a request, and an
auditor must later reconstruct what was requested, which policy version was
used, which attributes mattered, what explanation was generated, and who
approved or reviewed the event.

SEBA-XAI treats blockchain audit, security/access control, and explainable AI
as equal pillars of this access-governance problem. Blockchain is useful here
only in a limited role: it can support tamper-evident audit commitments across
known agencies, not store raw sensitive records or make records private by
itself. NISTIR 8403 discusses blockchain access-control systems in terms of
decentralization, high confidence, and tamper resistance while also emphasizing
implementation considerations [4]. Hyperledger Fabric is a
relevant reference point because it is a modular system for permissioned
blockchains among known organizations [5]. However, security and
privacy still require contextual policy enforcement, off-chain storage,
minimization, encryption, and careful metadata handling. NIST SP 800-162
defines attribute-based access control (ABAC) using subject, object, action,
and environmental attributes evaluated against policy rules or relationships,
and frames ABAC as useful for information sharing within and across
organizations while maintaining control of information [3].

The explainability pillar is equally central because access recommendations in
public-safety workflows must be reviewable by officers, superiors, auditors,
and possibly court or prosecution stakeholders. In this paper, XAI is not a
decorative dashboard layer. It is a logged artifact: the system should preserve
the decision label, reason code, decisive policy attributes, policy version,
model or rule version, counterfactual information where applicable, and hashes
that bind explanations to audit events. This framing follows high-stakes AI
arguments for interpretable models where feasible [9] and recent
law-enforcement XAI work emphasizing stakeholder needs, AI literacy, and
automation-bias risk [10]. It also avoids individual predictive
policing as the primary problem. Prior work on feedback loops in predictive
policing shows why reported or observed policing data can reinforce future
model attention [11], and public NCRB crime data is aggregate
reported/registered crime context rather than public individual police-record
access data [12].

Existing research covers parts of this problem but not the full workflow
evaluated here. Blockchain has been proposed for digital crime evidence
management and lawful evidence chain-of-custody workflows [7], [8].
Fabric-based ABAC and encrypted off-chain data sharing have been studied in
generic data-sharing contexts [6]. XAI and
fairness research has identified high-stakes explanation needs and the risks
of overclaiming criminal-justice prediction systems [9], [11], [10]. The gap is narrower than "AI for police data":
there is limited reproducible work on a CCTNS/ICJS-compatible access-governance
overlay that jointly evaluates contextual authorization, superior-review style
escalation, off-chain sensitive-record commitments, blockchain-style audit,
explanation artifact logging, adversarial audit attacks, and explanation
reviewability. This integration matters because the components fail in different ways. A
signed or blockchain-style audit log can reveal ordinary event edits, but it
does not by itself know whether a validly signed decision was the correct
policy output. ABAC re-execution can detect changes when the recorded canonical
inputs remain trustworthy, but it can also inherit corruption if the canonical
decision trace has already been laundered through a compromised enforcement
point. A trusted raw-attribute policy oracle can provide the strongest
row-level comparison when an independent request view exists, but that
assumption may be unavailable to an auditor who only receives the signed log.
The research question is therefore not which single layer is universally best;
it is how audit, policy re-evaluation, and interpretable drift monitoring can
be compared under explicit visibility assumptions.

To address this gap, we propose SEBA-XAI, a Secure, Explainable,
Blockchain-Audited access-governance overlay for sensitive inter-agency police
record sharing. The implemented research prototype uses synthetic
CCTNS/ICJS-style access requests, a deterministic declared policy oracle, a
file-backed permissioned-chain audit simulation, signed hash-chain and
CT-style log baselines, ABAC/Fabric-style re-execution baselines, a trusted
raw-attribute policy oracle baseline, and NS-PI, an interpretable
neuro-symbolic policy-induction and drift-detection component. Raw sensitive
records remain off-chain; the audit layer stores commitments and metadata for
requests, decisions, policies, approvals, model or rule versions, and
explanation artifacts. The evaluation is intentionally synthetic so that
attack cases and detector visibility assumptions can be controlled and
reproduced. The current evidence leads to a conservative contribution. Across the full
attack catalog, NS-PI is not the best overall tamper detector; the trusted
raw-attribute policy oracle is strongest, and integrity/ABAC-style baselines
are stronger for ordinary record edits (`results/tables/full_grid_aas_by_defense.csv`).
The useful NS-PI result is specific to the validly re-signed
`compromised_signer` attacker. In that setting, ledger-only and audit-only
baselines detect 0/5 seeds, while NS-PI and the trusted raw-attribute oracle
detect 5/5 seeds (`results/tables/seed_confidence_summary.csv`). This supports
framing NS-PI as a complementary log-only policy-drift signal when auditors do
not have an independent raw request view, not as a replacement for
cryptographic audit or trusted policy re-evaluation.

This paper makes five contributions. First, it formulates a CCTNS/ICJS-
compatible access-governance problem for sensitive inter-agency police and
criminal-justice records. Second, it implements a SEBA-XAI research prototype
combining off-chain records, contextual access policy, blockchain-style audit
commitments, and logged XAI artifacts. Third, it introduces an adversarial
audit benchmark covering ordinary tamper attacks, metadata-inference style
checks, and validly re-signed compromised-signer attacks. Fourth, it evaluates
NS-PI against ledger-only, ABAC/Fabric-style, and trusted raw-attribute oracle
baselines, showing both its useful compromised-signer signal and its
low-rate/targeted sensitivity limits. Fifth, it measures XAI and audit
reviewability through trace completeness, decisive-attribute text coverage,
counterfactual coverage and validity, duplicate-context stability, and
signed-log-to-block audit reconstruction.

The scope is deliberately limited. The paper does not claim live CCTNS/ICJS
integration, use actual police records, store raw sensitive data on-chain,
predict crime or criminals, or establish statutory compliance. The blockchain
component is a file-backed permissioned-audit simulation, not a live Fabric
network. The results support a reproducible benchmark and a narrow
architecture claim: integrity audit, contextual policy re-evaluation, and
interpretable log-only drift monitoring catch different failure modes under
different visibility assumptions. The remainder of the paper reviews related
work, defines the methodology and threat model, presents the evaluation, and
states limitations and future work.

## Citation Map

Numeric references are mapped in `papers/final_paper/references_ieee_map.md`.
