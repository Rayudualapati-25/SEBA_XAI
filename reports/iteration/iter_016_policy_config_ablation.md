# Iteration 016: Policy Configuration And Ablation

Date: 2026-05-28  
Status: Step 8 implementation complete  
Scope: formal PBAC/ABAC policy config and policy-dimension ablation experiment

## What Was Done

Implemented the next SEBA-XAI prototype step:

- added `prototype/synthetic_access_sim/policies/seba_xai_policy_v1.json`;
- added `prototype/synthetic_access_sim/policy_ablation.py`;
- moved policy dimensions into a structured JSON policy config;
- compared RBAC, full configured PBAC/ABAC, and rule-group ablations;
- measured false allows, false denies, false escalations, recall, and local decision latency;
- generated scenario-level error breakdowns;
- saved the run under `prototype/runs/20260528_step8_policy_config_ablation_seed42/`;
- saved summary tables under `prototype/results/tables/`, `results/tables/`, and `experiments/runs/`.

## Generated Artifacts

```text
prototype/runs/20260528_step8_policy_config_ablation_seed42/
  config.yaml
  logs/policy_ablation.log
  metrics.json
  artifacts/
    README.md
    data_dictionary.md
    dataset_manifest.json
    policy_config_snapshot.json
    policy_rule_group_summary.csv
    policy_ablation_predictions.csv
    policy_ablation_comparison.csv
    policy_ablation_by_scenario.csv
    policy_ablation_effects.csv
```

Additional result records:

```text
prototype/results/tables/policy_ablation_step8_comparison.csv
results/tables/policy_ablation_step8_comparison.csv
experiments/runs/20260528_step8_policy_config_ablation_seed42.json
```

## Result Summary

The comparison is against the deterministic Step 2 policy oracle, not real police access-control labels.

| Method | Accuracy | False allows | False denies | False escalations |
|---|---:|---:|---:|---:|
| RBAC role/action only | 0.2900 | 656 | 54 | 0 |
| Full configured PBAC/ABAC | 1.0000 | 0 | 0 | 0 |
| No approval rules | 0.9470 | 0 | 0 | 53 |
| No assignment rules | 0.9350 | 0 | 0 | 65 |
| No sealed-record rules | 0.8680 | 32 | 0 | 100 |
| No privacy rules | 0.9540 | 46 | 0 | 0 |
| No jurisdiction rules | 0.9920 | 8 | 0 | 0 |
| No sensitivity rules | 0.9560 | 19 | 0 | 25 |
| No emergency/network rules | 0.9990 | 1 | 0 | 0 |
| No context-review fallback | 0.9850 | 15 | 0 | 0 |

## Interpretation

RBAC role/action alone is weak for this synthetic workload because it ignores context such as jurisdiction, sensitivity, privacy flags, approval, sealed records, and emergency review. It produced 656 false allows and 54 false denies against the reference policy.

The full configured PBAC/ABAC policy matched the Step 2 oracle exactly. This confirms that the JSON config and the Step 8 evaluator are aligned with the earlier policy oracle for the current synthetic workload.

The most important ablation risks are:

- removing sealed-record rules: 32 false allows and 100 false escalations;
- removing privacy rules: 46 false allows;
- removing sensitivity rules: 19 false allows and 25 false escalations;
- removing jurisdiction rules: 8 false allows.

False allows are the highest-risk error because they represent access granted where the reference policy would deny or escalate.

## What Worked

- The security/access-control layer is now represented by a structured policy config, not only by hidden Python rules.
- The experiment gives an evidence-backed reason for using PBAC/ABAC instead of RBAC alone.
- The ablation table shows which policy dimensions matter under the synthetic workload.
- The run creates reproducible artifacts and a root experiment record.

## What Is Weak Or Missing

- The policy rules are synthetic and conservative; they are not official police policy.
- The evaluator is still local Python over JSON, not OPA, XACML, Hyperledger Fabric chaincode, or a production policy engine.
- The reference labels come from the Step 2 policy oracle, not human expert labels.
- No real CCTNS/ICJS integration exists.
- No legal compliance claim can be made from this experiment.

## Next Step

Create paper-ready experiment material:

- convert Step 3-8 result tables into concise paper tables;
- generate plots for false allows, tamper detection, metadata exposure, and latency;
- write a short evidence-safe experiment narrative;
- keep all claims limited to synthetic prototype evidence.
