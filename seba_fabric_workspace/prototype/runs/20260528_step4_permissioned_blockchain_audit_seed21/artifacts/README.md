# Run 20260528_step4_permissioned_blockchain_audit_seed21

Purpose: Step 4 permissioned blockchain-style audit simulation.

Input run: `20260528_step3_audit_baselines_seed21`

Audit events committed: `1000`

Blocks created: `20`

## What This Run Contains

- permissioned audit blocks;
- event-to-block index;
- synthetic validator set;
- controlled tampered chain files;
- chain verification results;
- comparison with Step 3 log baselines.

## What This Run Does Not Contain

- No real police/CCTNS/ICJS/FIR data.
- No raw record content on-chain.
- No raw XAI explanation text on-chain.
- No Hyperledger Fabric deployment.
- No real network consensus.
- No PoW or PoS.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/blockchain_audit.py \
  --input-run-id 20260528_step3_audit_baselines_seed21 \
  --run-id 20260528_step4_permissioned_blockchain_audit_seed21
```
