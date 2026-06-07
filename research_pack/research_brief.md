# Research Brief: Police and Crime AI in India

Generated: 2026-04-24  
Evidence status: literature and dataset scoping only. No model, benchmark, or ablation result exists yet.

## 1. Interpreted Research Intent

The rough brief points to a system where many police stations across India can cooperate through an AI-supported data-sharing model while preserving confidentiality. A station may need information from another station, but some records are classified or sensitive and require superior-officer approval. Blockchain is considered for inter-station trust and auditability, security for protected access and privacy, and explainable AI for showing why a model or policy recommends allowing, denying, escalating, or prioritizing a request.

This should not be reduced to "crime prediction with blockchain." A stronger research framing is:

> Can a permissioned, audit-ready, explainable, and privacy-aware architecture improve cross-station criminal-justice information sharing compared with conventional centralized access-control and logging systems?

The AI model can support multiple tasks:

- access-risk scoring for a data request;
- crime trend forecasting from aggregate NCRB data;
- anomaly detection in access logs or cyber/network traffic;
- explanation generation for why a request is approved, denied, or escalated;
- human-in-the-loop review for classified data release.

## 2. Existing Indian Context

Fact: India already operates CCTNS and ICJS. A 2026-03-11 PIB release states that all 17,798 police stations are using CCTNS as of 2026-02-01, with FIRs, chargesheets, and related records digitized in state data centers, replicated near-real-time to the National Data Centre, and searchable for crime, criminal, and property information. Source: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241

Fact: MHA describes ICJS as integrating Police/CCTNS, Courts/e-Courts, Jails/e-Prisons, Forensics/e-Forensics, and Prosecution/e-Prosecution, with "One Data Once Entry" and a Data Sharing Matrix. Source: https://www.mha.gov.in/en/commoncontent/inter-operable-criminal-justice-system-icjs

Interpretation: the research should benchmark against centralized CCTNS-like access and audit assumptions, not against a fictional no-system baseline.

## 3. Equal Pillars

### Blockchain Pillar

Best-supported role: permissioned, tamper-evident audit and authorization infrastructure.

Candidate design:

- Keep raw FIRs, witness records, evidence media, and personal data off-chain.
- Store hashes, policy IDs, approval proofs, request IDs, model version IDs, explanation hashes, and event metadata on-chain.
- Use local/state storage, encrypted object storage, or IPFS-like storage only for encrypted payloads.
- Use permissioned blockchain, likely Hyperledger Fabric, because law-enforcement participants are known organizations.
- Use channels/private data collections carefully; they improve confidentiality but can fragment cross-jurisdiction auditability.

What blockchain does not prove:

- it does not make data private by itself;
- it does not make AI fair or accurate;
- it does not solve bad data quality;
- it does not remove legal obligations around correction, retention, expungement, or sealed records.

### Security Pillar

Best-supported role: policy enforcement, confidentiality, authentication, revocation, and misuse detection.

Minimum security design:

- RBAC baseline: role/rank based access.
- ABAC baseline: subject, object, action, and environment attributes.
- Required attributes: officer rank, station, district/state jurisdiction, case assignment, record sensitivity, purpose, approval status, time window, active credential, and emergency override flag.
- Superior approval should be represented as a verifiable policy event, not as a free-text note.
- All allow/deny/escalate decisions should be reproducible from a stored policy version and request attributes.
- Sensitive raw records and explanations must remain encrypted and off-chain.

Threat cases to test:

- officer outside jurisdiction requests classified data;
- stale case assignment;
- revoked credential;
- compromised station node;
- curious insider repeatedly querying unrelated records;
- collusion between two stations;
- altered explanation artifact;
- deleted centralized audit log;
- replayed approval token.

### Explainable AI Pillar

Best-supported role: human-reviewable reasoning for model-supported decisions, not automatic authority.

Candidate design:

- Prefer interpretable models for high-stakes decisions where performance is acceptable.
- Use post-hoc explanation methods only with limitations clearly reported.
- Separate explanation audiences: requesting officer, approving superior, auditor, court/prosecutor, and affected person.
- Log explanation artifact hash, model version, input digest, policy version, reviewing officer credential, and final human decision.
- Treat XAI outputs as sensitive because explanations can leak protected or classified attributes.

XAI should explain:

- why an access request was allowed, denied, or escalated;
- what policy attributes mattered;
- what data is missing;
- why a crime-risk or anomaly score was high;
- whether the final human decision overrode the model or policy suggestion.

## 4. Research Questions

RQ1: Does a permissioned blockchain plus ABAC design improve audit completeness and tamper detection for inter-station data sharing compared with centralized RBAC/ABAC and signed append-only logs?

RQ2: What latency, throughput, storage, and operational costs are introduced by permissioned blockchain in a multi-station workload?

RQ3: Can role-specific XAI reduce incorrect sensitive-data disclosures or inappropriate denials compared with non-explained model scores or raw policy outputs?

RQ4: Do privacy-preserving controls reduce sensitive metadata exposure without unacceptable latency or usability costs?

RQ5: Which India crime datasets can support aggregate crime-analysis experiments without implying unsupported individual-level prediction?

## 5. Candidate Contributions

These are hypotheses, not results:

- A Fabric-plus-ABAC design may improve tamper-evident audit trails over centralized logs.
- XAI-backed approval workflows may improve reviewability of sensitive access decisions.
- Off-chain encrypted storage plus on-chain commitments may reduce leakage compared with on-chain record storage.
- India aggregate crime data can support state/district/city trend analysis, but not incident-level prediction unless restricted official data is available.

## 6. Claims That Must Not Be Made Yet

Do not claim:

- state-of-the-art crime prediction;
- deployability in Indian policing;
- legal compliance;
- privacy preservation;
- fairness;
- security;
- operational benefit;
- publication readiness.

Each of those needs experiments, audit artifacts, or legal analysis not yet present in this folder.

## 7. Stakeholder Questions

These questions should be answered before implementation beyond a prototype:

- What exact decision is the AI model supporting: crime trend analysis, access approval, investigation prioritization, or cyber/anomaly detection?
- Which records are in scope: aggregate NCRB tables, FIR metadata, case diaries, evidence media, cybercrime complaints, forensic reports, or access logs?
- Who can approve sensitive sharing: SHO, DSP/ACP, SP/DCP, court, prosecutor, or designated data protection officer?
- What legal retention, correction, sealing, juvenile-record, and court-disclosure rules apply?
- Can any real CCTNS/ICJS data be accessed for research, or must experiments use public aggregate data plus synthetic workloads?

