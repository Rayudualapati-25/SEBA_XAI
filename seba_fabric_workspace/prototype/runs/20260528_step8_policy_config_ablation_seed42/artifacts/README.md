# Run 20260528_step8_policy_config_ablation_seed42

Purpose: Step 8 configured PBAC/ABAC policy ablation.

Policy version: `P-2026-05-CONFIG-V1`

Synthetic requests evaluated: `1000`

Methods compared: `10`

## What This Run Contains

- configured policy snapshot;
- rule-group summary;
- per-request predictions;
- method comparison table;
- scenario-level error table;
- ablation effects relative to full configured PBAC.

## What This Run Does Not Contain

- No real CCTNS, ICJS, FIR, police, victim, witness, or case data.
- No official Indian police access-control policy.
- No legal-compliance proof.
- No production policy engine.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/policy_ablation.py \
  --run-id 20260528_step8_policy_config_ablation_seed42
```
