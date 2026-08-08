# Experiment Mode Comparison Data Dictionary

This file describes Step 6 outputs.

## Core Files

- `experiment_mode_predictions.csv`: per-request predictions for every method.
- `experiment_mode_comparison.csv`: one row per method with correctness, audit, latency, storage, and XAI availability.
- `decision_confusion_by_method.csv`: oracle decision versus predicted decision counts.
- `method_definitions.json`: method definitions and scope notes.

## Important Fields

| Field | Meaning |
|---|---|
| `accuracy` | Exact match with Step 2 policy-oracle label. |
| `false_allow_count` | Method allowed a request that the oracle did not allow. |
| `false_deny_count` | Method denied a request that the oracle did not deny. |
| `false_escalate_count` | Method escalated a request that the oracle did not escalate. |
| `audit_tamper_detection_rate` | Detection rate read from matching Step 3/Step 4 tamper-test artifacts. |
| `explanation_available_rate` | Whether the method exposes XAI explanation for requests. |
| `xai_hash_logged` | Whether the method logs explanation hash in the proposed audit layer. |
| `explanation_hash_tamper_detection` | Detection rate read from Step 7 explanation-hash pointer tamper tests when XAI hashes are logged. |
| `estimated_total_build_latency_ms_p50` | Local additive estimate using measured decision and audit build times. |

## Correct Interpretation

This is a synthetic workload comparison. The ABAC/PBAC oracle defines expected labels. Do not treat this as real police access-control accuracy.
