# 06 Proposed System Architecture

Generated: 2026-05-12

## System Name

**SEBA-XAI: Secure Explainable Blockchain-Audited Access Overlay**

## Architecture Principle

SEBA-XAI is an overlay. It does not replace CCTNS, ICJS, state data centers, court systems, forensic systems, or prison/prosecution systems. It sits above or beside them as an auditable authorization and explanation layer.

## High-Level Components

1. **Existing agency systems**
   - Police station/state CCTNS-like record systems.
   - ICJS-connected court, prison, forensic, and prosecution systems.
   - Local/state storage remains authoritative for raw records.

2. **Access request gateway**
   - Receives record-access requests from officers or agency systems.
   - Normalizes subject, object, action, and environment attributes.
   - Checks authentication, credential status, role, station, rank, jurisdiction, case assignment, purpose, and emergency flag.

3. **Policy decision layer**
   - RBAC baseline for role/rank rules.
   - ABAC/PBAC engine for fine-grained policies.
   - Superior-approval rule for sensitive/classified data.
   - Revocation and time-window checks.

4. **AI risk and anomaly layer**
   - Access-risk score for unusual or sensitive requests.
   - Insider-misuse anomaly detection on request history.
   - Optional aggregate crime trend model for public NCRB/BPRD analysis.
   - AI never becomes final authority for sensitive disclosure.

5. **XAI layer**
   - Generates explanation for allow, deny, or escalate recommendation.
   - Produces role-specific explanations for requesting officer, approving superior, auditor, and court/prosecutor reviewer.
   - Stores explanation artifact off-chain if sensitive.
   - Writes explanation hash, model version, policy version, and input digest to audit log.

6. **Blockchain audit layer**
   - Permissioned ledger, preferably Hyperledger Fabric in prototype.
   - Stores request ID, policy ID/version, decision type, approval proof hash, model version, explanation hash, payload hash/pointer, timestamp, and actor credentials.
   - Does not store raw FIRs, witness statements, evidence media, or personal data.

7. **Encrypted off-chain storage**
   - Raw payload remains in authorized local/state/agency storage.
   - Encrypted copies or references can be stored in approved object storage if needed.
   - Blockchain stores only commitment hashes and access metadata needed for audit.

8. **Audit and review dashboard**
   - Reconstructs a decision from request attributes, policy version, model version, explanation hash, and final approval.
   - Flags tampered logs, missing explanations, stale credentials, abnormal request sequences, and policy/version mismatches.

## Data Flow: Sensitive Record Request

1. Officer submits request: subject ID, role/rank, station, jurisdiction, case ID, requested object, purpose, and urgency.
2. Gateway validates credential status and creates request ID.
3. Policy layer evaluates RBAC and ABAC/PBAC rules.
4. AI layer optionally scores access risk and anomaly likelihood.
5. XAI layer creates decision explanation:
   - allowed because case assignment, jurisdiction, purpose, and time window matched;
   - denied because credential was revoked or jurisdiction mismatch occurred;
   - escalated because sensitivity level requires superior approval.
6. For sensitive records, superior officer reviews policy result, AI risk score, and explanation before final approval.
7. Blockchain audit layer records hashes and metadata.
8. If approved, gateway releases access token or encrypted pointer to authorized storage.
9. Auditor can later reconstruct the event and verify hashes.

## Officer Permission Workflow

Minimum subject attributes:

- officer ID;
- role;
- rank;
- station;
- district/state jurisdiction;
- active credential status;
- assigned case IDs;
- training/clearance flag;
- superior officer ID if approval is required.

Minimum object attributes:

- record ID;
- record type;
- case ID;
- station of origin;
- jurisdiction;
- sensitivity level;
- victim/witness/juvenile flag;
- evidence type;
- retention status;
- sealed/restricted flag.

Minimum environment attributes:

- timestamp;
- purpose;
- emergency flag;
- court/prosecutor request flag;
- network/node status;
- policy version;
- approval token status.

## Classified Data Request Workflow

Decision logic:

- **Allow:** all policy conditions match and sensitivity does not require higher approval.
- **Deny:** credential revoked, station/jurisdiction mismatch without exception, purpose invalid, case assignment missing, or record sealed.
- **Escalate:** request may be legitimate but record sensitivity, juvenile/witness flag, emergency override, cross-state request, or abnormal pattern requires superior review.

Approval record:

- approval token ID;
- approving officer credential hash;
- policy version;
- request ID;
- explanation hash;
- expiration time;
- revocation status;
- final human decision.

## Blockchain Layer Design

Recommended first prototype:

- Fabric organization per simulated state/district/agency group.
- Chaincode function for `submitRequest`, `recordDecision`, `recordApproval`, `recordAccess`, `revokeCredential`, and `verifyAuditTrail`.
- Ledger stores hashes and metadata only.
- Private data collections may be tested, but the first paper should not depend on them for the core claim.

What goes on-chain:

- request hash;
- decision summary;
- policy version hash;
- approval proof hash;
- model version;
- explanation artifact hash;
- encrypted object pointer hash;
- actor credential hash;
- timestamps and event type.

What stays off-chain:

- raw FIRs;
- witness/victim identities;
- case diary text;
- forensic media;
- full explanation text if it exposes sensitive attributes;
- personal data not needed for audit.

## XAI Layer Design

Use interpretable-first models where possible:

- decision tree or rule list for access-risk scoring;
- logistic regression or Explainable Boosting Machine for aggregate trend models;
- SHAP only as a secondary explanation for black-box benchmarks;
- deterministic policy explanation for ABAC/PBAC decisions.

Explanation types:

- policy explanation: which attributes passed/failed;
- risk explanation: which request features increased risk score;
- missing-data explanation: which required attribute was unavailable;
- override explanation: why a human approved or rejected a model/policy recommendation.

## Threat Model

Test at least these cases:

- officer outside jurisdiction requests classified record;
- stale case assignment;
- revoked credential;
- emergency override abuse;
- curious insider repeatedly queries unrelated records;
- compromised station node attempts to alter local logs;
- deleted centralized audit log;
- altered explanation artifact;
- replayed approval token;
- delayed revocation propagation;
- metadata inference from audit logs.

## Architecture Claim That Can Be Defended

If implemented and evaluated, the architecture can claim to improve **audit reconstruction and tamper evidence** compared with centralized logs. It cannot claim complete privacy, legal admissibility, or operational superiority without additional evidence.
