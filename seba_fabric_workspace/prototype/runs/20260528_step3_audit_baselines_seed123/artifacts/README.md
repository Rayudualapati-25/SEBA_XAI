# Run 20260528_step3_audit_baselines_seed123

Purpose: Step 3 mutable-log and signed hash-chain audit baselines.

Input run: `20260528_step2_policy_oracle_seed123`

Audit events written: `1000`

## What This Run Contains

- `mutable_access_log.csv`
- `signed_hash_chain_log.csv`
- tampered copies of both logs
- tamper-verification results
- compact detection summary

## What This Run Does Not Contain

- No real police/CCTNS/ICJS/FIR data.
- No blockchain ledger or consensus.
- No Hyperledger Fabric deployment.
- No production-grade signing or key management.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/audit_baseline.py \
  --input-run-id 20260528_step2_policy_oracle_seed123 \
  --run-id 20260528_step3_audit_baselines_seed123
```
