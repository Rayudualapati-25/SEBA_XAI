# Iteration 030 — Targeted Station/District Sensitivity

Date: 2026-05-29  
Status: completed and reproduced

## Goal

Test whether NS-PI still detects a `compromised_signer` attack when corruption is localized inside one station or one district instead of spread across the full workload.

This was needed because the previous global sensitivity result showed a clear weakness: NS-PI detected 10%+ global corruption in the current workload but missed 2% and 5% global corruption.

## Implementation

Added:

- `scripts/run_nspi_targeted_sensitivity.py`
- `results/tables/nspi_targeted_compromised_signer_raw.csv`
- `results/tables/nspi_targeted_compromised_signer_summary.csv`

The script:

1. Loads each existing seed run.
2. Learns the clean NS-PI policy model.
3. Selects the station or district with the most eligible deny/escalate rows.
4. Flips a fraction of that target group's deny/escalate decisions to allow.
5. Marks the attack as validly re-signed and policy-output compromised.
6. Compares global NS-PI, per-station NS-PI, per-district NS-PI, and the trusted raw-attribute policy oracle.

## Key Results

From `results/tables/nspi_targeted_compromised_signer_summary.csv`:

| Target scope | Target flip fraction | Mean global flip fraction | NS-PI global | NS-PI grouped/any | Trusted oracle |
|---|---:|---:|---:|---:|---:|
| station | 0.10 | 0.0042 | 0.0 | 0.0 | 1.0 |
| station | 0.25 | 0.0114 | 0.0 | 0.6 | 1.0 |
| station | 0.50 | 0.0234 | 0.0 | 1.0 | 1.0 |
| station | 1.00 | 0.0468 | 0.2 | 1.0 | 1.0 |
| district | 0.10 | 0.0102 | 0.0 | 0.0 | 1.0 |
| district | 0.25 | 0.0264 | 0.0 | 1.0 | 1.0 |
| district | 0.50 | 0.0532 | 0.2 | 1.0 | 1.0 |
| district | 1.00 | 0.1066 | 1.0 | 1.0 | 1.0 |

## Interpretation

What worked:

- The experiment confirms that global NS-PI is not enough for localized corruption.
- Grouped station/district drift is the correct way to use NS-PI for local attacks.
- The result is more realistic than only testing global corruption because an attacker may focus on one station, one district, or one jurisdiction.

What is weak:

- NS-PI still misses very small target-group corruption at 10%.
- The target selection uses the largest eligible group, so this is not a complete study of all station/district sizes.
- The trusted raw-attribute policy oracle remains stronger whenever an uncompromised raw request view is available.
- The workload is still synthetic.

## Verification

Commands run:

```bash
python3 scripts/run_nspi_targeted_sensitivity.py
python3 -m ruff check scripts/run_nspi_targeted_sensitivity.py src tests
make lint
make test
make reproduce
```

Observed status:

- Ruff checks passed.
- Test suite passed: `63 passed`.
- Full reproduction passed and regenerated the targeted sensitivity tables.

## Next Step

The next experiment should measure the XAI layer itself:

1. Explanation completeness.
2. Counterfactual validity.
3. Explanation stability.
4. Audit reconstruction quality.

The recommended output table is:

`results/tables/explanation_audit_quality.csv`

This matters because the current security evidence is now reasonably bounded, but the paper still needs evidence that the "explainable" part of SEBA-XAI is measurable and useful for audit review.
