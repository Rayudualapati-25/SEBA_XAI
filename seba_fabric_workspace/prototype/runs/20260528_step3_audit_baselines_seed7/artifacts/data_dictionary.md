# Audit Baseline Output Data Dictionary

This file describes Step 3 audit-baseline outputs.

## Important Boundary

This step compares local log designs. It does not implement blockchain, consensus, or Hyperledger Fabric.

## Core Files

- `mutable_access_log.csv`: centralized mutable audit log baseline.
- `signed_hash_chain_log.csv`: append-only-style audit log with previous hashes and demo HMAC signatures.
- `tampered_logs/`: controlled changed, deleted, hash-modified, and reordered log files.
- `tamper_test_results.csv`: verification result for each original and tampered log.
- `audit_detection_summary.csv`: compact detection-rate table.

## Key Fields

| Field | Meaning |
|---|---|
| `event_sequence` | Position of the event in the audit log. |
| `event_id` | Deterministic synthetic event identifier. |
| `request_id` | Request being audited. |
| `decision` | Policy-oracle decision. |
| `request_content_hash` | Hash of Step 1 request content. |
| `decision_hash` | Hash of Step 2 decision-critical fields. |
| `explanation_hash` | Hash of Step 2 explanation artifact. |
| `audit_anchor_hash` | Combined hash prepared for later blockchain anchoring. |
| `event_payload_hash` | Hash of the audit event payload in the signed log. |
| `previous_event_hash` | Previous event hash in the signed log. |
| `event_hash` | Hash linking payload hash, previous hash, and sequence. |
| `log_signature` | Demo HMAC signature over `event_hash`. |

## Correct Interpretation

Mutable logs can be compared against an external reference file hash, but they cannot prove internal tampering by themselves. Signed hash-chain logs can detect the injected tampering through recomputed hashes and signatures.
