# Manual Demo Steps For Professor Discussion

Use this as the practical walkthrough.

## 1. Explain The Scenario

A forensic expert requests access to a sensitive cybercrime evidence reference
from another agency. The system should not decide only from the role
`forensic expert`. It should check purpose, jurisdiction, sensitivity,
approval, credential status, and case relationship.

## 2. Run The Existing SEBA-XAI Decision Step

The current prototype already produces:

- `allow`, `deny`, or `escalate`;
- primary reason code;
- decisive attributes;
- decision hash;
- explanation hash;
- audit anchor hash.

## 3. Prepare Fabric Audit Events

```bash
bash prototype/fabric_audit_chain/scripts/03_prepare_events.sh
```

This creates:

```text
prototype/fabric_audit_chain/runs/20260702_fabric_audit_event_prep/artifacts/fabric_audit_events.jsonl
```

## 4. Start Fabric Network

Docker Desktop is required.

```bash
bash prototype/fabric_audit_chain/scripts/00_check_prereqs.sh
bash prototype/fabric_audit_chain/scripts/01_bootstrap_fabric.sh
bash prototype/fabric_audit_chain/scripts/02_start_network.sh
```

## 5. Submit Audit Events

```bash
bash prototype/fabric_audit_chain/scripts/04_submit_events.sh
```

## 6. Query One Event

Copy one `requestIdHash` from the JSONL file.

```bash
bash prototype/fabric_audit_chain/scripts/05_query_event.sh <requestIdHash>
```

## 7. What To Say

The actual sensitive record is still off-chain. Fabric only stores the audit
commitment. If someone later changes the off-chain decision or explanation
artifact, the hash will not match the committed ledger evidence.

## 8. What Not To Claim

Do not claim:

- real CCTNS integration;
- legal compliance;
- production security;
- real police data testing;
- crime prediction;
- public blockchain deployment.
