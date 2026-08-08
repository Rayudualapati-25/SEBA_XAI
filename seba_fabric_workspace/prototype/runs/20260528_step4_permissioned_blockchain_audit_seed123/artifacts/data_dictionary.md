# Permissioned Blockchain-Style Audit Output Data Dictionary

This file describes Step 4 outputs.

## Important Boundary

This step is a local permissioned blockchain-style simulation. It is not Hyperledger Fabric, not a deployed blockchain, not PoW, and not PoS.

## Core Files

- `permissioned_audit_blocks.jsonl`: simulated permissioned audit-chain blocks.
- `block_event_index.csv`: maps audit events to block numbers and commitment hashes.
- `validator_set.json`: synthetic validator set and quorum rule.
- `tampered_chains/`: controlled tampered chain files.
- `blockchain_tamper_test_results.csv`: verification result for original and tampered chains.
- `blockchain_detection_summary.csv`: compact chain-detection summary.
- `comparison_with_step3_signed_log.csv`: comparison with Step 3 mutable and signed-log baselines.

## Key Block Fields

| Field | Meaning |
|---|---|
| `block_number` | Sequential block number. |
| `previous_block_hash` | Hash link to previous block. |
| `event_commitment_hashes` | Hash commitments to signed audit events. |
| `merkle_root` | Merkle root over event commitments. |
| `validator_id` | Permissioned validator that proposes/signs the block. |
| `block_payload_hash` | Hash of block content before signatures. |
| `validator_signature` | Demo validator HMAC signature over block payload hash. |
| `quorum_endorsements` | Demo quorum signatures from known validators. |
| `block_hash` | Final block hash binding payload and signatures. |

## Correct Interpretation

This layer gives a blockchain-style audit structure for the prototype. It stores audit commitments only. Raw police records and raw explanation text stay off-chain.
