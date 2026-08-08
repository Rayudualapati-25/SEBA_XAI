# Architecture

## Layers

```
web interface  ──►  REST API  ──►  chaincode on 5 peers  ──►  ledger
   (frontend)      (backend)      (decision + explanation)
                        │
                        ├──►  SQLite: record payloads, accounts, access log
                        └──►  Ollama: rewords a committed decision (display only)
```

Two separations are load-bearing:

1. **Records are off-chain, commitments are on-chain.** The ledger holds record
   metadata, a SHA-256 of the payload, and an off-chain URI. The payload itself
   is in agency storage. Replicating narratives to all five organisations would
   weaken privacy rather than improve it, and would make erasure impossible.

2. **Decisions are made in chaincode, not in the application.** The API cannot
   grant access; it can only submit a request and record what the chaincode
   decided. The model can only reword that decision after the fact.

## Access decision

Implemented in `chaincode/crimerecords/lib/policy/policyEngine.js`. Inputs are
assembled in `accessContract.js` from three sources:

| Input | Source | Client-controlled |
|---|---|---|
| subject (role, rank, station, jurisdiction, clearance, credential status, case assignments) | caller's X.509 certificate | no |
| object (record type, sensitivity, juvenile/witness flags, sealed status, jurisdiction, case) | ledger state | no |
| action | request argument | yes |
| environment (purpose, time window, emergency flag, court link, approval token) | request argument | yes |

Eight rules are evaluated in order; the first that matches returns.

| # | Condition | Outcome | Reason code |
|---|---|---|---|
| 1 | credential not active | deny | `CRED_NOT_ACTIVE` |
| 2 | purpose absent or undeclared | deny | `INVALID_PURPOSE` |
| 3 | RBAC matrix has no role/action/type entry | deny | `RBAC_NO_PERMISSION` |
| 4 | record sealed, caller not `CourtMSP` | escalate | `SEALED_RECORD` |
| 5 | juvenile flag, role not privileged | escalate | `JUVENILE_PROTECTED` |
| 6 | jurisdiction mismatch | escalate, or allow with emergency + token | `CROSS_JURISDICTION` / `EMERGENCY_CROSS_JURISDICTION` |
| 7 | requester not assigned to the case | deny | `NOT_ASSIGNED` |
| 8 | clearance below record sensitivity | escalate | `INSUFFICIENT_CLEARANCE` |
| — | all gates passed | allow | `POLICY_SATISFIED` |

Rule order is significant: assignment (7) precedes clearance (8), so an
unassigned requester receives `NOT_ASSIGNED` rather than a clearance reason.
Changing the order changes the reason-code distribution that the evaluation
reports.

Each rule returns the decision, a reason code, the decisive attribute names, and
a counterfactual. The explanation is produced by the same code path as the
decision and therefore cannot contradict it, which is why trace completeness is
1.0000 by construction.

The engine is deterministic: no randomness, no model, no dependence on wall-clock
time. Identical inputs yield identical decisions and identical reasons.

## Contracts

`chaincode/crimerecords/lib/`

| Contract | Responsibility |
|---|---|
| `recordContract.js` | Record registry: create, attach evidence commitments, seal/unseal, query, history |
| `accessContract.js` | Access requests, policy evaluation, explanation commitment, escalation resolution |
| `auditContract.js` | Explanation and payload verification, trail reconstruction, access-log anchoring |

Shared helpers in `lib/util/`: `identity.js` reads certificate attributes and
enforces MSP and role checks; `validate.js` provides allow-list validation and
canonical hashing.

## Two integrity mechanisms

**Payload commitment.** `payloadHash` is written when a record is filed.
`VerifyRecordPayload` recomputes the hash of what agency storage currently holds
and compares it with the ledger value, which detects post-hoc edits to the
off-chain store.

**Access-log anchoring.** Reads and searches are Fabric queries and produce no
transaction. They are appended to a hash chain in SQLite, where each entry
commits the previous entry's hash. The head hash is committed on-chain every
`ANCHOR_EVERY` entries by `AnchorAccessLog`. Editing or deleting an entry breaks
the chain and contradicts an anchor already on the ledger. A per-log `epoch`
records log recreation so that a legitimate rebuild does not read as tampering,
while remaining permanently visible in the anchor history.

## Explanation wording

`backend/src/llm/`. The module reads the committed decision back from the ledger,
builds a prompt from an allow-listed set of fields, calls the local model at
temperature 0 with a fixed seed, and validates the response before displaying it.

Validation distinguishes two severities: *problems* mean the text asserts
something false, and the deterministic template is shown instead; *warnings* mean
the text is correct but incomplete, and it is shown with the gap recorded.
Generated text is cached by explanation hash and is never written to the ledger,
so the ledger does not depend on a non-deterministic component.

The prompt excludes the case narrative, complainant reference, badge number,
approval token, and evidence detail. A unit test enforces this with canary
strings.

## Web interface

`frontend/` uses native ES modules with no build step. Features are registered as
modules in `js/modules/index.js`; navigation, routing and role filtering are
derived from the registry. See `frontend/README.md` for the procedure to add one.

The role lists in `frontend/js/core/access.js` mirror the backend and control only
what appears in the navigation. Authorisation is enforced by the backend and the
chaincode.
