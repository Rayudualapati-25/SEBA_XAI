# Iteration 010: Policy Oracle And Rule-Trace XAI

Date: 2026-05-27  
Status: Step 2 implementation complete  
Scope: deterministic policy validation and basic XAI explanations for synthetic access requests

## What Was Done

Implemented Step 2 of the SEBA-XAI prototype:

- added `prototype/synthetic_access_sim/policy_oracle.py`;
- read Step 1 synthetic requests from `prototype/runs/20260527_step1_synthetic_requests_seed42/artifacts/access_requests.csv`;
- applied deterministic access-governance rules;
- generated `allow`, `deny`, and `escalate` labels;
- generated rule-trace XAI explanations;
- generated `decision_hash`, `explanation_hash`, and `audit_anchor_hash` fields for future blockchain/audit testing;
- saved a reproducible run record under `prototype/runs/20260527_step2_policy_oracle_seed42/`;
- saved summary table under `prototype/results/tables/policy_oracle_step2_summary.csv`.

## Generated Artifacts

```text
prototype/runs/20260527_step2_policy_oracle_seed42/
  config.yaml
  logs/policy_oracle.log
  metrics.json
  artifacts/
    README.md
    data_dictionary.md
    dataset_manifest.json
    explanation_artifacts.jsonl
    labeled_access_requests.csv
    policy_rules.json
    policy_summary.csv
```

## Policy Logic

Decision precedence:

1. `deny`
2. `escalate`
3. `allow`

Hard-deny examples:

- inactive or revoked credential;
- expired approval token;
- stale case assignment;
- sealed record without court/prosecution context;
- training purpose for sensitive records;
- approval action without supervisor rank;
- sensitive update by low-rank requester;
- classified share without valid approval.

Escalation examples:

- emergency access;
- juvenile, victim, or witness-sensitive record;
- cross-jurisdiction sensitive record;
- classified record requiring approval;
- missing approval for sensitive record;
- sealed record even with court/prosecution context;
- degraded station-node status.

Allow condition:

- active credential;
- recognized purpose;
- routine action;
- low or medium sensitivity;
- assigned case, same jurisdiction, or court/prosecution context;
- no deny or escalation rule triggered.

## Run Result Summary

This is a policy-labeling artifact, not a performance result.

| Decision | Count |
|---|---:|
| `allow` | 113 |
| `deny` | 409 |
| `escalate` | 478 |

Validation checks:

- 1000 requests evaluated;
- 1000 explanation artifacts written;
- no empty `xai_explanation` fields;
- no empty `decision_hash`, `explanation_hash`, or `audit_anchor_hash` fields;
- no sealed record was directly allowed;
- Python syntax check passed with `python3 -m py_compile`.

## What Worked

- The policy oracle gives reproducible labels for the Step 1 synthetic workload.
- Each decision has a reason code and a human-readable explanation.
- Each decision now has stable hashes that can be anchored in the future audit layer.
- The oracle separates facts, policy output, explanation artifact, and audit anchor hash.

## What Is Weak Or Missing

- This is not a trained AI model.
- This is not SHAP, LIME, counterfactual explanation, or feature-attribution XAI.
- These labels come from synthetic rules and synthetic data, not from real police access decisions.
- No RBAC/ABAC/PBAC baseline comparison has been run yet.
- No blockchain ledger or signed append-only log has been implemented yet.
- No latency, throughput, tamper-detection, or metadata-leakage experiment has been run yet.

## Next Step

Implement the first audit baseline:

- write a mutable centralized access log;
- write a signed append-only hash-chain log;
- verify the hash chain;
- inject tampering cases such as changed decision, deleted row, changed explanation hash, and reordered events.

This will prepare the comparison with the later blockchain-style audit layer.
