# Iteration 014: Explicit Experiment Modes

Date: 2026-05-27  
Status: Step 6 implementation complete  
Scope: baseline/proposed method comparison for the synthetic SEBA-XAI prototype

## What Was Done

Implemented a consolidated experiment-mode harness:

- added `prototype/synthetic_access_sim/experiment_modes.py`;
- compared five explicit methods;
- used Step 2 policy-oracle labels as deterministic expected labels;
- generated per-request predictions for each method;
- generated a method comparison table with correctness, tamper detection, latency, storage, and XAI-hash availability;
- generated a decision-confusion table;
- saved the run under `prototype/runs/20260527_step6_experiment_modes_seed42/`;
- saved the summary table under `prototype/results/tables/experiment_modes_step6_comparison.csv`.

## Methods Compared

| Method ID | Meaning | Status |
|---|---|---|
| `rbac_mutable_log` | RBAC + mutable log | baseline |
| `abac_pbac_mutable_log` | ABAC/PBAC + mutable log | baseline |
| `abac_pbac_signed_hash_chain` | ABAC/PBAC + signed hash-chain log | baseline |
| `abac_pbac_blockchain_style` | ABAC/PBAC + blockchain-style audit | baseline |
| `seba_xai_full` | ABAC/PBAC + blockchain-style audit + XAI hash | proposed |

## Generated Artifacts

```text
prototype/runs/20260527_step6_experiment_modes_seed42/
  config.yaml
  logs/experiment_modes.log
  metrics.json
  artifacts/
    README.md
    data_dictionary.md
    dataset_manifest.json
    method_definitions.json
    experiment_mode_predictions.csv
    experiment_mode_comparison.csv
    decision_confusion_by_method.csv
```

## Result Summary

The comparison is against the deterministic Step 2 policy oracle, not real police access-control labels.

| Method | Accuracy | False allow | False deny | False escalate | Audit tamper detection | XAI hash logged |
|---|---:|---:|---:|---:|---:|---|
| RBAC + mutable log | 0.2900 | 656 | 54 | 0 | 0.0000 | false |
| ABAC/PBAC + mutable log | 1.0000 | 0 | 0 | 0 | 0.0000 | false |
| ABAC/PBAC + signed hash-chain log | 1.0000 | 0 | 0 | 0 | 1.0000 | false |
| ABAC/PBAC + blockchain-style audit | 1.0000 | 0 | 0 | 0 | 1.0000 | false |
| SEBA-XAI full | 1.0000 | 0 | 0 | 0 | 1.0000 | true |

Local estimated build latency:

| Method | Estimated build p50 ms |
|---|---:|
| RBAC + mutable log | 8.298958 |
| ABAC/PBAC + mutable log | 21.745625 |
| ABAC/PBAC + signed hash-chain log | 31.270333 |
| ABAC/PBAC + blockchain-style audit | 42.527958 |
| SEBA-XAI full | 42.527958 |

## Interpretation

RBAC performs poorly because it cannot represent jurisdiction, sensitivity, sealed-record status, juvenile/victim/witness flags, emergency review, approval tokens, or escalation.

ABAC/PBAC methods reach 1.0000 accuracy because the Step 2 policy oracle defines the expected synthetic policy label. This should be described as **policy-oracle consistency**, not real-world accuracy.

The SEBA-XAI full method differs from the blockchain-style audit baseline by logging the XAI explanation hash, which supports later explanation-integrity verification.

## What Worked

- The prototype now has explicit baselines and a proposed method.
- The RBAC baseline demonstrates why role-only access is weak for sensitive inter-agency police record requests.
- The table now connects correctness, audit tamper detection, latency, storage, and XAI logging in one place.
- The proposed SEBA-XAI method is clearly separated from intermediate baselines.

## What Is Weak Or Missing

- ABAC/PBAC correctness is measured against the synthetic oracle, not external labels.
- No real user, officer, auditor, or legal-review study exists.
- No off-chain encrypted storage/pointer simulation exists yet.
- No metadata-leakage analysis has been run yet.
- No concurrent load test exists.
- No real Hyperledger Fabric implementation exists.

## Next Step

Implement off-chain encrypted storage/pointer simulation:

- keep synthetic raw payload placeholders off-chain;
- store only payload hashes/pointers in audit events;
- compare metadata exposure with and without minimization;
- measure whether explanation and payload hashes can still be verified after tampering.
