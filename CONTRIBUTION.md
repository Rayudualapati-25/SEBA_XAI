# Contribution Statement and Novelty Boundary

Revised: 2026-08-09
Status: aligned to the implemented system in `seba_fabric_workspace/crime-records-network/`.

This document states what SEBA-XAI is, what it claims, and what it must not
claim. Every architectural claim below cites the code that implements it.
Claims that are not implemented are listed separately as open work.

---

## 1. What SEBA-XAI is

SEBA-XAI is a permissioned-blockchain system for governing access to sensitive
criminal-justice records shared between departments. It is implemented on
Hyperledger Fabric 2.5.16 with five organisations — Police, Forensics,
Prosecution, Court, and Audit — each operating its own certificate authority
and its own CouchDB-backed peer, transacting on the channel `crimechannel`
under a `MAJORITY` (3-of-5) endorsement policy.

Two properties define the design, and both are architectural rather than
procedural.

**Access decisions are evaluated inside the ledger, not recorded by it.** The
policy engine is chaincode. When an officer requests a record, the decision is
computed within the endorsed transaction, executed independently by three of
five organisations, and committed as the transaction itself. The system does
not compute a decision in an application tier and then write a log entry
describing it.

**The grounds of a decision are committed atomically with the decision.** The
same evaluation that produces the outcome produces the reason code, the
decisive attributes, and the counterfactual. All are hashed and written in one
state update, so a decision cannot exist in the ledger without the reasoning
that produced it, and the two cannot be made to disagree.

SEBA-XAI is not a modification, extension, or improvement of any existing
system. CCTNS and ICJS appear in this work only as the operational environment
that makes inter-agency record requests possible; they are never a baseline,
and no claim in this project is measured against them.

---

## 2. Contribution statement

> We present SEBA-XAI, a permissioned-blockchain system for inter-agency
> criminal-justice record access governance in which the authorisation decision
> is itself the endorsed on-chain computation. Subject attributes are bound to
> X.509 certificates issued by each department's own certificate authority, so
> a requester cannot assert their own authority; object attributes are read from
> ledger state; and only the requested action and declared purpose originate
> with the requester. Each decision is committed atomically with a
> machine-checkable explanation artifact — reason code, decisive attributes,
> counterfactual, and policy version — hash-linked to the decision event, while
> raw records remain in agency-controlled off-chain storage under a SHA-256
> commitment. We further show that endorsement consensus establishes agreement
> on a transaction but not the integrity of the premises it was evaluated
> against, and we characterise the resulting class of attacks.

---

## 3. Architectural claims and their implementing code

| # | Claim | Implementation |
|---|---|---|
| C1 | Authorisation is an endorsed on-chain computation, not an off-chain decision that is logged | `chaincode/crimerecords/lib/accessContract.js` — `RequestAccess` evaluates policy within the transaction |
| C2 | Subject attributes are unforgeable by the requester | `lib/util/identity.js` — `getCaller` reads role, rank, station, jurisdiction, badge, clearance, credential status and case assignments from the signing X.509 certificate |
| C3 | Object attributes are read from committed ledger state, never from the request | `accessContract.js` — record metadata fetched by composite key before evaluation |
| C4 | Requester-supplied input is confined to action and environment, and is allow-listed | `accessContract.js` `ENV_SCHEMA` with `lib/util/validate.js` `validateAllowList` |
| C5 | Decision and explanation are produced by one code path and committed atomically | `lib/policy/policyEngine.js` returns decision, reason code, decisive attributes and counterfactual together; `accessContract.js` hashes and stores them in a single state write |
| C6 | Policy is deterministic and versioned, so evaluation is reproducible | `lib/policy/policyV1.js` — `POLICY_VERSION`, frozen RBAC/ABAC/PBAC tables; no randomness, no clock dependence, no model inference |
| C7 | No single organisation can produce a decision | `network/configtx/configtx.yaml` — `Endorsement: MAJORITY Endorsement` over five org MSPs |
| C8 | Escalation enforces separation of duties | `accessContract.js` `_resolveEscalation` rejects an approver sharing the requester's MSP and role; approver roles restricted to `ESCALATION_APPROVERS` |
| C9 | Secrets are committed, not stored | `accessContract.js` stores `sha256(approvalToken)`, never the token |
| C10 | Verification compares ledger state against a caller's artifact, never claim against claim | `lib/auditContract.js` `VerifyExplanation`, `VerifyRecordPayload` |
| C11 | Reads and searches are accountable despite generating no transactions | off-chain hash chain in `backend/src/audit/accessLog.js`, anchored on-chain by `auditContract.js` `AnchorAccessLog` under `AuditMSP` with monotonic sequence per epoch |
| C12 | Raw records never reach the shared ledger | `lib/recordContract.js` stores metadata plus `payloadHash`; evidence detail is confined to the `evidenceDetails` private data collection |
| C13 | Caller input cannot reach the state database as a query | `recordContract.js` `SEARCH_SCHEMA` allow-list |
| C14 | Generated natural language cannot influence a decision | `backend/src/llm/` runs only after commitment and reads the decision back from the ledger; output is validated and never written on-chain |

---

## 4. Evidence base

Two distinct bodies of evidence exist. They must never be merged in a claim,
because they were produced by different artifacts under different assumptions.

### 4.1 The implemented system — `seba_fabric_workspace/crime-records-network/`

| Evidence | Result | Source |
|---|---|---|
| Chaincode unit tests | 70 passing, ~97% line coverage | `make test-chaincode` |
| API tests against the running network | 48 passing, real certificates | `make test-backend` |
| End-to-end walkthrough | 11 steps | `make smoke` |
| Ledger inspection | 9 sections over real blocks, signatures, certificates | `make inspect` |
| Attack replay | 6 of 6 blocked | `scripts/smoke-test.sh` |
| Decision commit latency | 72.69 ms marginal | `experiments/results/live_fabric_measurements.json` |
| Verification latency | 3.99 ms | same |
| Storage per decision | 857 B | same |

Two measurement caveats are mandatory wherever these numbers appear.

The end-to-end commit latency is 2072 ms, of which 2000 ms is the orderer's
configured `BatchTimeout`. Across all 50 measurements the spread was under
83 ms, which is the signature of a fixed wait rather than variable computation.
The figure representing system work is the marginal **72.69 ms**. Quoting
2072 ms as the cost of the design is incorrect.

The 857 B per decision is not comparable to the earlier prototype's 353.50 B,
because this implementation commits the full explanation artifact inline.

A further scope limit: the network runs on a single host under Docker with one
ordering node. The latencies are valid measurements of this configuration and
are not projections of a geographically distributed deployment.

### 4.2 The prior research package — `src/seba/`

This is a **synthetic simulation study**, and must always be labelled as one.
It preceded the implemented system and does not describe it. It contributes a
five-seed adversarial benchmark over a generated workload, with an attack
catalogue, a severity-weighted scorer, and re-implemented comparison defences.

Its principal result is an asymmetry: across five seeds, every integrity-based
defence detected ordinary tampering but obtained 0.00 detection against a
validly re-signed decision log, while a distribution-level drift detector and a
trusted attribute oracle each obtained 1.00 detection under stronger visibility
assumptions. Detailed figures are in `results/FINDINGS.md`.

The drift detector's boundaries are part of the honest result: it misses 2% and
5% global corruption, misses 10% targeted station or district corruption, and
its threshold varies with workload size.

---

## 5. Threat model position

The system's security rests on the assumption that each organisation's
certificate authority issues attributes truthfully. That assumption is load
bearing, and its failure defines the sharpest finding available to this work.

Because subject attributes live inside certificates, a compromised departmental
certificate authority can issue an identity carrying any clearance or case
assignment it chooses. Three endorsing organisations then execute the policy
correctly against that identity, agree unanimously, and commit an `allow`.
Every signature verifies, every endorsement is valid, and the ledger is
consistent — yet the decision was never authorised by real policy.

The general statement is that **endorsement consensus establishes agreement on
a transaction, not the integrity of the premises the transaction was evaluated
against.** Integrity and correctness are separate properties, and a
tamper-evidence check cannot distinguish them.

This is currently an analytical result for the implemented system. It has been
demonstrated experimentally only in the synthetic study of §4.2, where the
corresponding attack is log re-signing. Replaying it against the live network
requires compromising an organisation's CA or MSP administrator, which is a
strictly stronger assumption and is not yet implemented. This gap must be
stated wherever the result is presented.

---

## 6. Novelty boundary

The project claims:

- a system in which authorisation is the endorsed on-chain computation rather
  than an off-chain decision subsequently logged;
- certificate-bound subject attributes, removing the requester's ability to
  assert their own authority;
- atomic commitment of decision and machine-checkable justification by a single
  deterministic code path;
- accountability for reads and searches, which generate no ledger transactions,
  via an anchored off-chain hash chain;
- a characterisation of what endorsement consensus does and does not establish
  about a committed decision.

The project does **not** claim:

- invention of attribute-based access control, permissioned ledgers, or
  explainable AI, each of which is established prior work;
- improvement over CCTNS, ICJS, or any deployed system, none of which is used
  as a baseline;
- deployment readiness, legal compliance, or admissibility as evidence;
- validation on real police records or real access logs;
- formal privacy guarantees — metadata exposure is measured by a schema-level
  proxy, not proved;
- performance representative of a distributed multi-site deployment;
- any form of crime, suspect, or risk prediction.

---

## 7. Open work

1. Replay the CA-compromise attack of §5 against the live network, which
   requires modelling a compromised MSP administrator.
2. Evaluate under a multi-host orderer configuration so latency reflects a
   distributed deployment.
3. Reduce `BatchTimeout` and re-measure, so the reported end-to-end figure is
   not dominated by a configured wait.
4. Strengthen the natural-language explanation layer: decisive-attribute text
   coverage is 0.781 in the synthetic study, meaning structured traces are
   complete while rendered text is not.
5. Replace the schema-level metadata-exposure proxy with a defensible privacy
   analysis.
