# SEBA-XAI Fabric Audit Event Schema

This schema defines the commitment-only event submitted to Hyperledger Fabric.

## Required Fields

| Field | Meaning | Example Source |
|---|---|---|
| `requestIdHash` | SHA-256 hash of synthetic request identifier | Built locally from `request_id` |
| `policyVersion` | Policy version used for decision | `policy_version_evaluated` |
| `decision` | `allow`, `deny`, or `escalate` | Policy oracle output |
| `primaryReasonCode` | Main rule that drove the decision | `primary_reason_code` |
| `decisionHash` | Hash of decision payload | Policy oracle output |
| `explanationHash` | Hash of XAI explanation artifact | Policy oracle output |
| `recordCommitment` | Hash/pointer commitment to the target record | `target_record_hash` |
| `auditAnchorHash` | Combined request-decision-explanation anchor | Policy oracle output |
| `approvalReferenceHash` | Hash of required approval label | Built locally |
| `attributeSetHash` | Hash of decisive attributes | Built locally |
| `sourcePrototypeRun` | Local synthetic run ID | Builder config |
| `createdAtUtc` | Synthetic request timestamp | `timestamp_utc` |

## Fields That Must Not Go On-Chain

- raw record payload;
- FIR text;
- requester/officer name;
- requester officer ID;
- target record ID;
- target case ID;
- natural-language explanation text;
- victim, witness, or juvenile names;
- any real police record.

## Why The Explanation Text Is Not Stored Directly

The XAI explanation may reveal sensitive context. The chain stores
`explanationHash` so an auditor can later verify that the explanation artifact
has not been changed. The artifact itself should remain in controlled off-chain
storage.

## Ledger Verification Logic

The Fabric chaincode checks:

1. all required fields are present;
2. decision is one of `allow`, `deny`, or `escalate`;
3. hash fields are valid SHA-256 hex values;
4. forbidden raw/sensitive fields are absent;
5. the request hash has not already been recorded.

It then writes one immutable audit event under:

```text
audit:<requestIdHash>
```
