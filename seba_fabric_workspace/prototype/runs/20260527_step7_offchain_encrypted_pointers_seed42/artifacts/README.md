# Run 20260527_step7_offchain_encrypted_pointers_seed42

Purpose: Step 7 off-chain encrypted storage/pointer simulation and metadata-leakage analysis.

Synthetic off-chain payloads: `900`

Request pointer commitments: `1000`

## What This Run Contains

- encrypted synthetic record payload envelopes;
- request-to-record pointer commitments;
- full metadata versus minimized commitment ledger views;
- metadata-exposure comparison;
- controlled payload and pointer tamper tests.

## What This Run Does Not Contain

- No real police, CCTNS, ICJS, FIR, victim, witness, or case records.
- No production encryption or key management.
- No legal-compliance proof.
- No deployed storage service or Hyperledger Fabric private data collection.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/offchain_storage.py \
  --run-id 20260527_step7_offchain_encrypted_pointers_seed42
```
