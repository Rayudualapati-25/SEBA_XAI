# Run 20260528_step1_synthetic_requests_seed7

Purpose: Step 1 synthetic access-request data generation for SEBA-XAI.

Seed: `7`

Requests generated: `1000`

## What This Run Contains

- Synthetic stations, officers, cases, records, and access requests.
- Dataset profile and manifest.
- No real police/CCTNS/ICJS/FIR data.
- No RBAC/ABAC/PBAC decision output.
- No XAI output.
- No blockchain audit result.

## How To Reproduce

```bash
python3 prototype/synthetic_access_sim/generate_synthetic_requests.py \
  --run-id 20260528_step1_synthetic_requests_seed7 \
  --seed 7 \
  --num-requests 1000
```

## Correct Interpretation

This run is a dataset/workload-generation artifact only. It can support future policy-oracle, audit, and XAI experiments, but it is not itself an experiment result.
