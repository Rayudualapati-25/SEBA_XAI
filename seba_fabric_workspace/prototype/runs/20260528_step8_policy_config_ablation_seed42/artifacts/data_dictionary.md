# Policy Ablation Data Dictionary

This file describes Step 8 outputs.

## Important Boundary

The Step 2 policy oracle is used as the deterministic reference label. The
reported accuracy values mean agreement with the synthetic oracle, not real
police access-control accuracy.

## Core Files

- `policy_config_snapshot.json`: policy configuration used for this run.
- `policy_rule_group_summary.csv`: configured rule groups and rule IDs.
- `policy_ablation_predictions.csv`: per-request prediction for every method.
- `policy_ablation_comparison.csv`: one row per baseline/proposed/ablation method.
- `policy_ablation_by_scenario.csv`: per-scenario error breakdown.
- `policy_ablation_effects.csv`: error deltas relative to full configured PBAC.

## Key Fields

| Field | Meaning |
|---|---|
| `false_allow_count` | Method allowed a request that the reference policy did not allow. |
| `false_deny_count` | Method denied a request that the reference policy did not deny. |
| `false_escalate_count` | Method escalated a request that the reference policy did not escalate. |
| `disabled_rule_groups` | Policy dimensions removed for the ablation. |
| `accuracy_drop_from_full` | Difference from the full configured policy row. |
| `decision_latency_ms_p50_total` | Local median total time to evaluate all synthetic requests. |

## Correct Interpretation

This step helps justify the security/access-control pillar by showing the
effect of removing approval, assignment, sealed-record, privacy, jurisdiction,
sensitivity, emergency/network, and fallback-review rules.
