# Demonstration walkthrough

## Start

```bash
make down
make all
make backend
```

Open `http://localhost:3001`. Select an enrolled Fabric identity; there is no
application password. The screen explicitly labels this as a custodial local
development identity selector.

## Eight scenarios

| Identity | Action | Expected evidence |
|---|---|---|
| `io.krishnan` | request `REC-FIR-001` for investigation | `ALLOW / POLICY_SATISFIED` |
| `const.verma` | same request without assignment | `DENY / NOT_ASSIGNED` |
| `analyst.rao` | request victim-protected `REC-EVIDENCE-001` | `DENY / VICTIM_DATA_NOT_NECESSARY` |
| `insp.singh` | cross-district request | `ESCALATE / CROSS_JURISDICTION` |
| `insp.sharma` | request `REC-JUVENILE-001` | `DENY / JUVENILE_PROTECTED` |
| `judge.rana` | approve the cross-district escalation | linked Approval and payload release |
| `insp.rathore` | request with revoked certificate attribute | `DENY / CRED_NOT_ACTIVE` |
| `aud.qureshi` | inspect audit trail, then request raw content | full metadata reconstruction; raw content denied |

Each decision page should show its reason, decisive attributes, policy version,
counterfactual, decision hash, and Fabric transaction ID.

## Automated proof

Leave the backend running in one terminal, then:

```bash
make test-chaincode   # 92 deterministic chaincode tests
make test-backend     # 33 live API + explanation tests
make smoke            # 16 live end-to-end checks
make verify-log       # reads direct Fabric audit events
make measure          # role-only ablation versus contextual policy
make inspect          # interactive ledger/block/certificate inspection
```

`make verify-log` does not reconcile an external database. Authenticated access
events are Fabric transactions, so it reports the ledger mechanisms: endorsement,
ordering, block hashes, and key history.

## What to tell a reviewer

- The project did not put all data on-chain. That would replicate sensitive
  victim and juvenile data to every peer and make deletion difficult.
- It put governance state, integrity commitments, approvals, and audit evidence
  on-chain; raw content stays under agency control.
- The 2-second transaction times in the current local run are dominated by the
  configured orderer batch timeout and are not a distributed performance claim.
- The policy and data are synthetic. The prototype does not establish legal
  compliance, production security, or CCTNS/ICJS integration.
