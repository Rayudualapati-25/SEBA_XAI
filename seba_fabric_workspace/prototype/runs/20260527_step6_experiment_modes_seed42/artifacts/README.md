# Run 20260527_step6_experiment_modes_seed42

Purpose: Step 6 explicit baseline/proposed experiment-mode comparison.

## Methods Compared

1. RBAC + mutable log
2. ABAC/PBAC + mutable log
3. ABAC/PBAC + signed hash-chain log
4. ABAC/PBAC + permissioned blockchain-style audit
5. SEBA-XAI full: ABAC/PBAC + permissioned blockchain-style audit + XAI hash

## Important Boundary

The Step 2 policy oracle is used as deterministic ground-truth policy label for the synthetic workload. This is not real police decision ground truth.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/experiment_modes.py \
  --run-id 20260527_step6_experiment_modes_seed42
```
