# Off-Chain Storage And Metadata Leakage Data Dictionary

This file describes Step 7 outputs.

## Important Boundary

The encrypted store is a deterministic prototype simulation using a demo key.
It is not production encryption, key management, legal compliance, or a real
police data store.

## Core Files

- `offchain_record_store.jsonl`: encrypted synthetic record payload envelopes.
- `offchain_pointer_table.csv`: request-to-record pointer commitments.
- `full_metadata_ledger.csv`: intentionally overexposed ledger design for comparison.
- `minimized_commitment_ledger.csv`: commitment-based minimized ledger design.
- `metadata_leakage_comparison.csv`: schema-level metadata exposure comparison.
    - `offchain_tamper_test_results.csv`: controlled payload/pointer tamper tests, including recomputed pointer-commitment cases.
- `storage_overhead_offchain.csv`: local artifact sizes.

## Key Fields

| Field | Meaning |
|---|---|
| `record_pointer_id` | Synthetic pointer to an off-chain payload envelope. |
| `payload_hash` | Hash of the decrypted synthetic payload. |
| `ciphertext_hash` | Hash of the encrypted payload bytes. |
| `pointer_commitment_hash` | Hash binding the request, payload hash, XAI hash, decision hash, and audit block reference. |
| `explanation_hash` | Hash of the Step 2 XAI artifact. Raw explanation text is not stored in the ledger views. |
| `metadata_exposure_score` | Fraction of predefined sensitive metadata columns visible in clear text. This is not a formal privacy metric. |

## Correct Interpretation

    Step 7 supports the architecture claim that SEBA-XAI can keep raw records
    off-chain while logging verifiable commitments. Pointer verification checks
    local consistency and anchors decision/XAI/block references to the generated
    Step 2 and Step 4 artifacts. It also shows why metadata minimization matters:
    a ledger that stores only hashes can still verify integrity with less direct
    exposure than a ledger containing clear role, station, sensitivity, purpose,
    action, decision, and reason-code fields.
