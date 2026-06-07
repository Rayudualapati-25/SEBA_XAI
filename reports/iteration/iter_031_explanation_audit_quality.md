# Iteration 031 — Explanation And Audit Quality Metrics

Date: 2026-05-29  
Status: completed and reproduced

## Goal

Measure whether the "explainable" part of SEBA-XAI is actually reviewable, rather than only being present in the architecture.

The previous experiments established the security side: normal integrity mechanisms catch ordinary tampering, NS-PI catches the validly re-signed `compromised_signer` attack in the synthetic benchmark, and grouped drift is needed for localized station/district corruption. This iteration adds the missing XAI evidence.

## Implementation

Added:

- `src/seba/xai_quality.py`
- `scripts/run_explanation_audit_quality.py`
- `tests/test_xai_quality.py`
- `results/tables/explanation_audit_quality.csv`
- `results/tables/explanation_audit_quality_summary.csv`

Updated:

- `Makefile`, so `make reproduce` regenerates the XAI/audit quality tables.

## Metrics

The script measures:

1. **Trace completeness**  
   Whether each request has decision, primary reason, matched rules, decisive attributes, explanation text, policy version, decision hash, explanation hash, and audit anchor hash.

2. **Decisive-attribute text coverage**  
   Whether decisive attributes in the structured trace are reflected in the rendered natural-language explanation text.

3. **Counterfactual coverage and validity**  
   Whether deny/escalate rows receive counterfactual suggestions, and whether applying those edits changes the learned NS-PI policy decision to `allow`.

4. **Duplicate-context stability**  
   Whether requests with identical policy-relevant attributes produce stable decision and primary-reason outputs.

5. **Audit reconstruction**  
   Whether an auditor can reconstruct request -> signed hash-chain event -> block index -> block commitment.

## Key Results

From `results/tables/explanation_audit_quality_summary.csv`:

| Metric | Mean | Std | Min | Max |
|---|---:|---:|---:|---:|
| Trace complete rate | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| Decisive attribute text coverage mean | 0.9310 | 0.0054 | 0.9231 | 0.9369 |
| Decisive attribute full text coverage rate | 0.7810 | 0.0208 | 0.7550 | 0.8090 |
| Counterfactual coverage rate | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| Counterfactual validity rate | 0.9964 | 0.0055 | 0.9876 | 1.0000 |
| Stable decision/reason row rate | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| Audit reconstruction rate | 1.0000 | 0.0000 | 1.0000 | 1.0000 |

## Interpretation

What worked:

- The structured XAI trace is complete for all tested synthetic requests.
- Counterfactual explanations are generated for all deny/escalate rows in the current workload.
- Counterfactual replay validity is high under the learned NS-PI policy.
- Audit reconstruction succeeds across the signed hash-chain and blockchain-style block index.
- Duplicate policy contexts have stable decision and primary-reason outputs in the tested data.

What is weak:

- Full natural-language coverage of decisive attributes is only 0.781 on average.
- This means the structured trace contains the needed information, but the rendered sentence does not always surface every decisive attribute.
- Counterfactual validity is measured against the learned NS-PI policy, not a human legal standard or real police review process.
- Audit reconstruction proves artifact linkage in the prototype, not production legal admissibility.

## Verification

Commands run:

```bash
python3 scripts/run_explanation_audit_quality.py
python3 -m ruff check scripts/run_explanation_audit_quality.py scripts/run_nspi_targeted_sensitivity.py src tests
make lint
make test
make reproduce
```

Observed status:

- Ruff checks passed.
- Test suite passed: `67 passed`.
- Full reproduction passed and regenerated the XAI/audit quality tables.

## Next Step

The next experiment should be workload and policy-mix stress testing:

1. Vary request count: 500, 1000, 2500, 5000.
2. Vary classified-record ratio.
3. Vary cross-jurisdiction ratio.
4. Vary revoked-credential ratio.
5. Vary approval-token missing/invalid ratio.
6. Recompute security, NS-PI, XAI, audit, and overhead metrics where feasible.

Recommended output:

`results/tables/workload_policy_stress_summary.csv`

This matters because the current results are still tied to one synthetic workload design.
