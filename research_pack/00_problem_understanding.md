# 00 Problem Understanding

Generated: 2026-05-12  
Role: Senior AI research assistant review for an M.Tech/IEEE-level research direction.

## Core Problem

Indian police and criminal-justice agencies need to share information across police stations, districts, states, courts, prisons, forensic labs, and prosecution units. Some records are sensitive: FIR details, witness statements, victim records, juvenile information, forensic reports, cybercrime evidence, case diary material, and inter-agency intelligence. The research question is how to support **trusted, auditable, privacy-aware, and explainable access** to such records without pretending that India has no existing infrastructure.

India already has CCTNS and ICJS. A 2026 PIB release says all 17,798 police stations were using CCTNS as of 2026-02-01, with data replicated near-real-time to the National Data Centre and standardized master codes for states, districts, police stations, acts, and sections. MHA describes ICJS as integrating Police/CCTNS, Courts/e-Courts, Jails/e-Prisons, Forensics/e-Forensics, and Prosecution/e-Prosecution through a Data Sharing Matrix. Sources: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241 and https://www.mha.gov.in/en/commoncontent/icjsncrb-administration

## Research Interpretation

The project should be framed as an **intelligent secure overlay** on top of CCTNS/ICJS-style infrastructure:

- Blockchain is used for tamper-evident commitments, approvals, policy-version records, access events, explanation hashes, and audit reconstruction.
- Security and privacy are enforced through RBAC, ABAC/PBAC, encryption, credential revocation, off-chain storage, and misuse/anomaly monitoring.
- XAI explains model-supported and policy-supported decisions such as allow, deny, escalate, or require superior approval.

The research should not claim that blockchain stores all police data. That is weak technically and risky legally. Raw records should remain off-chain in authorized local/state systems or encrypted storage.

## Decision to Support

The first research prototype should support this decision:

> When Officer A from Station X requests Record R from Station Y, should the system allow access, deny access, or escalate to an authorized superior, and can the system later reconstruct why that decision was made?

This is stronger than a generic crime-prediction system because it binds the three pillars equally:

- Blockchain: immutable audit of request, policy, approval, and explanation commitments.
- Security/privacy/access control: deterministic policy enforcement and sensitive-record protection.
- XAI: understandable justification for the officer, approving superior, and auditor.

## In Scope

- Inter-police-station and inter-agency access-request workflows.
- Classified/sensitive record access simulation.
- Policy/versioned access decisions using RBAC and ABAC/PBAC.
- Permissioned blockchain audit layer, preferably Hyperledger Fabric for prototype realism.
- Off-chain encrypted payload pointers, not raw record storage on-chain.
- XAI explanations for access-risk scoring, anomaly detection, and aggregate trend models.
- Public India aggregate crime datasets and synthetic inter-agency workloads.

## Out of Scope for the First Paper

- Replacing CCTNS or ICJS.
- Deploying in real Indian police infrastructure.
- Individual suspect prediction from public NCRB data.
- Automatic sensitive-record disclosure without human approval.
- Legal-compliance claims without expert legal review.
- Claims that blockchain alone provides privacy, fairness, security, or correctness.

## Research Questions

RQ1. Does a permissioned blockchain plus ABAC/PBAC overlay improve audit completeness and tamper detection for inter-station access requests compared with centralized RBAC/ABAC logs and signed append-only logs?

RQ2. What latency, throughput, storage, and operational overhead does the audit overlay introduce under realistic multi-station request loads?

RQ3. Can XAI-backed access justifications improve reviewability of sensitive access decisions compared with raw policy outputs or opaque model scores?

RQ4. How much sensitive metadata is exposed by different designs: centralized logs, signed append-only logs, Fabric-only audit, Fabric plus encrypted off-chain storage, and Fabric plus privacy-preserving attribute handling?

RQ5. Which India public datasets can support aggregate crime-analysis experiments without making unsupported station-level or individual-level claims?

## Strict Supervisor Notes

- If the paper title says "crime prediction", reviewers will expect crime-prediction novelty and strong datasets. The current evidence does not support that as the main contribution.
- If the paper title says "blockchain for police data sharing", reviewers will ask why CCTNS/ICJS are insufficient. The answer must be "auditability, provenance, verifiable approvals, policy-version reconstruction, and explainable access governance", not "CCTNS does not exist".
- If the paper uses public NCRB data, it must say "reported/registered aggregate crime", not true crime incidence.
- The recommended paper should be a system/evaluation paper with a synthetic access-control workload plus public aggregate analysis, not a deployment paper.
