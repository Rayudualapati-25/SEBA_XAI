# Run 20260528_step2_policy_oracle_seed21

Purpose: Step 2 deterministic policy oracle and basic XAI explanation generation.

Input run: `20260528_step1_synthetic_requests_seed21`

Requests evaluated: `1000`

## What This Run Contains

- `labeled_access_requests.csv` with `allow`, `deny`, or `escalate` decisions.
- `policy_summary.csv` with decision and reason-code counts.
- `explanation_artifacts.jsonl` with one structured explanation artifact per request.
- `policy_rules.json` with the rule IDs used by the oracle.
- Decision, explanation, and audit-anchor hashes for later blockchain testing.

## What This Run Does Not Contain

- No real police/CCTNS/ICJS/FIR data.
- No trained ML model.
- No SHAP/LIME explanation.
- No blockchain ledger write.
- No deployment or legal-compliance claim.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/policy_oracle.py \
  --input-run-id 20260528_step1_synthetic_requests_seed21 \
  --run-id 20260528_step2_policy_oracle_seed21
```
