# SEBA-XAI Prototype

This folder contains the runnable prototype work for the research project.

Current prototype:

| Prototype | Purpose | Status |
|---|---|---|
| `synthetic_access_sim` | Generate synthetic police-style access requests, label them with deterministic policy decisions, create rule-trace explanations, test audit-log baselines, simulate permissioned blockchain-style audit, measure local overhead, compare explicit experiment modes, test off-chain storage/pointer metadata exposure, and run configured policy ablations. | Step 8 complete |

## What Is Inside

```text
prototype/
  synthetic_access_sim/
    README.md
    generate_synthetic_requests.py
    policy_oracle.py
    audit_baseline.py
    blockchain_audit.py
    measure_overhead.py
    experiment_modes.py
    offchain_storage.py
    policy_ablation.py
    policies/
      seba_xai_policy_v1.json
  runs/
    20260527_step1_synthetic_requests_seed42/
    20260527_step2_policy_oracle_seed42/
    20260527_step3_audit_baselines_seed42/
    20260527_step4_permissioned_blockchain_audit_seed42/
    20260527_step5_latency_storage_overhead/
    20260527_step6_experiment_modes_seed42/
    20260527_step7_offchain_encrypted_pointers_seed42/
    20260528_step8_policy_config_ablation_seed42/
  results/
    tables/
      synthetic_request_step1_profile.csv
      policy_oracle_step2_summary.csv
      audit_baseline_step3_summary.csv
      blockchain_audit_step4_summary.csv
      latency_storage_step5_summary.csv
      experiment_modes_step6_comparison.csv
      offchain_storage_step7_summary.csv
      policy_ablation_step8_comparison.csv
```

## Important Boundary

The current prototype uses synthetic data only. It does not yet implement:

- trained AI or SHAP/LIME explanations;
- real blockchain deployment;
- distributed consensus or Hyperledger Fabric;
- production encryption/key management;
- real CCTNS/ICJS integration.

No real CCTNS, ICJS, FIR, police, victim, witness, or case data is included.

## Completed Decision And XAI Step

The deterministic policy oracle reads `access_requests.csv` and outputs:

- `allow`;
- `deny`;
- `escalate`;
- reason code;
- rule-trace explanation;
- decision hash;
- explanation hash;
- audit anchor hash;
- policy version.

## Completed Audit Baseline Step

The first audit baseline now compares:

- mutable centralized log;
- signed append-only hash-chain log;
- tamper verification script.

It injects:

- changed decision;
- deleted event;
- changed explanation hash;
- reordered events.

## Completed Blockchain-Style Audit Step

The permissioned blockchain-style audit simulation now:

- groups signed audit events into blocks;
- stores event commitment hashes, not raw records;
- computes Merkle roots;
- links blocks using previous block hashes;
- signs blocks with synthetic agency validators;
- requires a 3-of-4 synthetic validator quorum;
- detects controlled chain tampering.

## Completed Overhead Measurement Step

The local overhead measurement now records:

- policy/XAI decision latency;
- mutable-log creation and schema verification time;
- signed hash-chain creation and verification time;
- blockchain-style block creation and verification time;
- storage size per request/event.

## Completed Experiment Mode Step

The prototype now compares explicit baseline/proposed modes:

- RBAC + mutable log;
- ABAC/PBAC + mutable log;
- ABAC/PBAC + signed hash-chain log;
- ABAC/PBAC + blockchain-style audit;
- SEBA-XAI full: ABAC/PBAC + blockchain-style audit + XAI hash.

## Completed Off-Chain Storage And Metadata Step

The prototype now simulates:

- encrypted synthetic record payload envelopes kept off-chain;
- per-request pointer commitments;
- a full metadata ledger view for comparison;
- a minimized commitment ledger view;
- schema-level metadata exposure metrics;
- controlled payload and pointer tamper tests.

Step 7 result:

| Metric | Value |
|---|---:|
| Synthetic off-chain record payloads | 900 |
| Request pointer commitments | 1000 |
| Full metadata clear sensitive columns | 19 |
| Minimized metadata clear sensitive columns | 0 |
| Controlled tamper cases detected | 7/7 |

## Completed Policy Configuration And Ablation Step

The prototype now has a structured policy config:

- `prototype/synthetic_access_sim/policies/seba_xai_policy_v1.json`

Step 8 compares:

- RBAC role/action baseline;
- full configured PBAC/ABAC policy;
- approval-rule ablation;
- assignment-rule ablation;
- sealed-record-rule ablation;
- privacy-rule ablation;
- jurisdiction-rule ablation;
- sensitivity-rule ablation;
- emergency/network-rule ablation;
- fallback-review ablation.

Step 8 result:

| Method | Accuracy vs policy oracle | False allows | False denies | False escalations |
|---|---:|---:|---:|---:|
| RBAC role/action only | 0.2900 | 656 | 54 | 0 |
| Full configured PBAC/ABAC | 1.0000 | 0 | 0 | 0 |
| No sealed-record rules | 0.8680 | 32 | 0 | 100 |
| No privacy rules | 0.9540 | 46 | 0 | 0 |
| No jurisdiction rules | 0.9920 | 8 | 0 | 0 |

## Next Coding Step

Add paper-ready plots/tables and a short experiment narrative for the prototype results.
