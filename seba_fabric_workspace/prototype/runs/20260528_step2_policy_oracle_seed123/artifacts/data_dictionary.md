# Policy Oracle Output Data Dictionary

This file describes the Step 2 policy-oracle output.

## Important Boundary

The output is based on synthetic access requests and deterministic policy assumptions. It is not a real police access-control decision log.

## Core Files

- `labeled_access_requests.csv`: Step 1 request fields plus policy and XAI fields.
- `explanation_artifacts.jsonl`: one structured explanation artifact per request.
- `policy_rules.json`: rule IDs and decision precedence.
- `policy_summary.csv`: counts for decisions, reason codes, approvals, and sensitivity groups.

## Added Fields

| Field | Meaning |
|---|---|
| `decision` | Policy oracle decision: `allow`, `deny`, or `escalate`. |
| `primary_reason_code` | Main rule responsible for the decision. |
| `matched_rule_ids` | Rule IDs used for the final decision. |
| `all_triggered_rule_ids` | All triggered rules before final precedence. |
| `decisive_attributes` | Request attributes that influenced the decision. |
| `failed_or_review_rules` | Deny or escalation rules triggered by the request. |
| `required_approval` | Approval category required if escalated. |
| `xai_explanation` | Human-readable rule-trace explanation. |
| `xai_supporting_factors` | Positive contextual factors found in the request. |
| `policy_version_evaluated` | Policy version used by the oracle. |
| `decision_hash` | SHA-256 hash of decision-critical fields. |
| `explanation_hash` | SHA-256 hash of the structured explanation artifact. |
| `audit_anchor_hash` | Hash combining request, decision, explanation, and policy version for future audit logging. |
