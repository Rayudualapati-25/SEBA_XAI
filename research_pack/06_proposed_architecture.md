# 06 System Architecture

Revised: 2026-08-09
Status: describes the implemented system in
`seba_fabric_workspace/crime-records-network/`. Every element below exists in
code; nothing here is aspirational. Where a component is planned but not built,
it is listed in §10.

---

## 1. System identity

**SEBA-XAI** is a permissioned-blockchain system for governing access to
sensitive criminal-justice records held by different departments.

It is a system, not an overlay: the authorisation decision is executed by
chaincode inside the endorsed transaction, and the ledger is where the decision
is *made*, not where a decision made elsewhere is filed. It is not a
simulation: it runs on Hyperledger Fabric 2.5.16 with five organisations, real
certificate authorities, per-user transaction signing, and CouchDB state
databases.

SEBA-XAI does not replace, extend, or improve CCTNS, ICJS, or any other
deployed system. Those systems establish that records are reachable across
agency boundaries; SEBA-XAI governs whether a specific request for one should
be granted, and preserves reviewable evidence of that judgement.

---

## 2. Network topology

| Element | Configuration |
|---|---|
| Platform | Hyperledger Fabric 2.5.16 |
| Organisations | Police, Forensics, Prosecution, Court, Audit |
| Per organisation | own Fabric CA, own peer, own CouchDB state database |
| Channel | `crimechannel` |
| Endorsement policy | `MAJORITY Endorsement` — 3 of 5 organisations |
| Ordering service | `etcdraft`, single node, `BatchTimeout: 2s` |
| Chaincode | `crimerecords` — RecordContract, AccessContract, AuditContract |
| Private data | `evidenceDetails` collection, restricted to Police, Forensics, Court |

Defined in `network/configtx/configtx.yaml` and
`chaincode/collections-config.json`.

The single ordering node and single Docker host are deliberate scope limits for
a research deployment, and every latency figure produced by this network must
be qualified by them.

---

## 3. The trust boundary

The architecture's central decision is which facts the requester is permitted
to assert. Three sources feed every evaluation, and they are not equally
trusted.

| Fact class | Origin | Requester can influence? |
|---|---|---|
| Identity: role, rank, station, jurisdiction, badge, clearance, credential status, case assignments | the requester's signed X.509 certificate, issued by their own department CA | **No** |
| Object: record type, sensitivity, juvenile and witness flags, sealed status, jurisdiction, case | committed ledger state | **No** |
| Action: view, export, annotate | the request | Yes |
| Environment: purpose, time window, emergency flag, court link, approval token | the request | Yes |

`lib/util/identity.js` reads the identity class through
`ctx.clientIdentity.getAttributeValue()`, so an officer cannot claim a rank,
clearance, or case assignment they were not issued. A missing attribute becomes
`null`, and policy treats `null` as not granted rather than as unrestricted.

The two requester-controlled classes are constrained before they reach the
policy engine: `ENV_SCHEMA` in `lib/accessContract.js` is an allow-list with
per-field types, enumerations, and patterns, enforced by `validateAllowList` in
`lib/util/validate.js`. A field outside the schema is rejected rather than
ignored.

This is the property that distinguishes the design from an access-control
service that receives attributes in a request payload: the requester supplies
their *intent*, never their *authority*.

---

## 4. The three contracts

`chaincode/crimerecords/lib/`

| Contract | Responsibility |
|---|---|
| `recordContract.js` | Record registration, evidence commitments, sealing and unsealing, allow-listed search |
| `accessContract.js` | Access requests, policy evaluation, explanation commitment, escalation resolution |
| `auditContract.js` | Explanation and payload verification, audit-trail reconstruction, access-log anchoring |

Supported by `util/identity.js` (certificate attribute extraction and MSP/role
gates) and `util/validate.js` (schema validation and hashing).

---

## 5. The policy engine

`lib/policy/policyEngine.js`, with declarative tables in `lib/policy/policyV1.js`.

Evaluation is an ordered rule list. The first rule that matches is terminal;
nothing after it executes.

| # | Condition | Outcome | Reason code |
|---|---|---|---|
| 1 | Credential is not active | deny | `CRED_NOT_ACTIVE` |
| 2 | Purpose missing or not a declared purpose | deny | `INVALID_PURPOSE` |
| 3 | Role lacks this action on this record type | deny | `RBAC_NO_PERMISSION` |
| 4 | Record sealed and caller is not the Court | escalate | `SEALED_RECORD` |
| 5 | Juvenile record and role not permitted | escalate | `JUVENILE_PROTECTED` |
| 6 | Jurisdiction mismatch | escalate, or allow with emergency flag plus approval token | `CROSS_JURISDICTION` / `EMERGENCY_CROSS_JURISDICTION` |
| 7 | Caller not assigned to the case | deny | `NOT_ASSIGNED` |
| 8 | Clearance below record sensitivity | escalate | `INSUFFICIENT_CLEARANCE` |
| — | All gates passed | allow | `POLICY_SATISFIED` |

The layering is explicit: rule 3 is the RBAC base matrix, rules 4 to 8 are
attribute-based constraints, and revocation, versioning, and the approval-token
exception are policy-based. Rule order is itself a design decision — assignment
is tested before clearance, so an unassigned officer is told they are not on
the case rather than that their clearance is insufficient. Reordering would
change the reason codes in every result.

Evaluation is deterministic: no randomness, no clock dependence, no model
inference. The same request yields the same decision and the same reason on
every peer, which is what permits three organisations to endorse independently
and agree.

Every rule returns four values, not one: the outcome, the reason code, the
attributes that were decisive, and the counterfactual describing what would
have changed the result.

---

## 6. Request lifecycle

1. An authenticated user's request reaches the backend, which holds one Fabric
   Gateway connection per logged-in user (`backend/src/fabric/gateway.js`), so
   the transaction is signed by that individual's own key.
2. `AccessContract.RequestAccess` extracts the caller's certificate attributes,
   loads record metadata from ledger state, and validates the environment
   against `ENV_SCHEMA`.
3. The policy engine evaluates and returns decision, reason code, decisive
   attributes, and counterfactual.
4. An explanation artifact is assembled from that result and hashed.
5. A single state write commits the decision event: identifiers, a minimised
   subject snapshot, the environment with the approval token reduced to
   `sha256`, the explanation, the explanation hash, and the policy version.
6. Three of five organisations endorse; the transaction is ordered and
   committed.
7. If the outcome is `escalate`, the request stands as `pending-escalation`
   until an approver resolves it.

The decision and its justification are written in the same state update. There
is no interval in which one exists without the other, and no path by which they
can be made to disagree.

---

## 7. Escalation and separation of duties

`_resolveEscalation` in `lib/accessContract.js` enforces three conditions: the
approver's role must appear in `ESCALATION_APPROVERS`; the decision must still
be pending; and the approver must not share both MSP and role with the
requester, so a request cannot be approved by its own originator's position.
The resolution records the approving organisation, role, note, timestamp, and
transaction identifier, and is committed as a further state update — the
original decision remains in the key's history.

---

## 8. What is on-chain and what is not

Committed to the ledger: record metadata, the SHA-256 commitment of the record
payload, the off-chain location reference, access decision events, explanation
artifacts and their hashes, policy versions, approval-token commitments,
escalation resolutions, and access-log anchors.

Never committed: case narratives, first information report text, witness and
victim identities, case-diary contents, forensic media, badge numbers, raw
approval tokens, and generated natural-language text.

The reasoning is that a permissioned ledger replicates every write to all five
organisations permanently. Placing case content there would give every
department an indelible copy of every file — worse for confidentiality than the
status quo — and would make the deletion required for juvenile protection and
court-ordered erasure impossible.

Verification therefore compares a payload held off-chain against its on-chain
commitment (`AuditContract.VerifyRecordPayload`) and an explanation artifact
held by a reviewer against the committed hash
(`AuditContract.VerifyExplanation`). In both cases the reference value is read
from ledger state and only the artifact under test comes from the caller, so a
verification can never degenerate into comparing a claim with itself.

---

## 9. Read accountability

Writes generate transactions; reads and searches do not. Without additional
machinery, who *looked* at a case would leave no durable trace — an inversion
of the operational reality, in which who read a file is frequently more
sensitive than who wrote one.

`backend/src/audit/accessLog.js` maintains an off-chain hash chain over read
and search events, where `entryHash(n) = sha256(entryHash(n-1) ‖
canonical(entry n))`. Altering or removing any entry invalidates every entry
after it.

`backend/src/audit/anchor.js` commits the head of that chain to the ledger
every `ANCHOR_EVERY` entries (default 25) through
`AuditContract.AnchorAccessLog`. Anchoring is restricted to `AuditMSP`, and the
sequence number must strictly advance within an epoch, so an older head cannot
be re-anchored to conceal later reads. Fabric retains the full history of the
anchor key, so a reviewer can test the chain against every anchor ever written,
not merely the newest.

An epoch identifier marks a deliberate rebuild of the off-chain log. Without
it, a legitimate reconstruction would be indistinguishable from tampering. The
epoch is visible in ledger history, so a rebuild is permitted but never
concealed.

---

## 10. Explanation rendering

`backend/src/llm/` renders a committed decision into plain language using a
locally hosted model.

The ordering is a security property, not a convenience. The chaincode decides
and commits first. The backend then reads that decision *back from the ledger*
rather than from the browser, so no one can obtain an explanation for a
decision they invented. A prompt is constructed from a fixed field list that
excludes case narrative, complainant details, badge numbers, approval tokens,
and evidence descriptions, with a test that plants marker strings and asserts
they never appear. The generated text is validated against the committed
decision: contradictions are discarded in favour of deterministic template
wording, while incomplete-but-accurate text is shown with the omission
recorded. Generated text is never written on-chain, because a permanent record
must not depend on output that can vary between runs.

The model explains; it never decides.

---

## 11. Known limits of the current build

1. One ordering node on one Docker host. Latency figures characterise this
   configuration only.
2. `BatchTimeout` of 2 s dominates end-to-end commit latency; the figure
   representing system work is the marginal 72.69 ms.
3. The CA-compromise threat in `CONTRIBUTION.md` §5 is analysed but not
   replayed against the live network.
4. Metadata exposure is assessed by a schema-level proxy, not a formal privacy
   analysis.
5. Explanation text does not surface every decisive attribute in all cases;
   the structured artifact is complete, the rendering is not.
6. All records and identities are synthetic. No real case data is used.
