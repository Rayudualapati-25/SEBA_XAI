# Iteration 051: Publication Sprint Results Section

Status: completed on 2026-06-07.

## What worked

- Re-ran the full reproduction pipeline with deterministic seeds
  `{7, 21, 42, 99, 123}`.
- Regenerated multi-seed results, adversarial grid results, ablations,
  NS-PI sensitivity, targeted sensitivity, XAI/audit-quality metrics,
  workload-policy stress results, and seed-confidence summaries.
- Updated the IEEE Overleaf manuscript so the paper now has a dedicated
  `Results and Discussion` section.
- Rebuilt the Overleaf upload zip after validation.

## Evidence used

- `results/tables/paper_table_01_method_comparison.csv`
- `results/tables/full_grid_aas_by_defense.csv`
- `results/tables/full_grid_per_attack.csv`
- `results/tables/nspi_compromised_signer_sensitivity_summary.csv`
- `results/tables/nspi_targeted_compromised_signer_summary.csv`
- `results/tables/workload_policy_stress_summary.csv`
- `results/tables/explanation_audit_quality_summary.csv`
- `results/tables/paper_table_03_metadata_exposure.csv`
- `results/tables/paper_table_04_latency_storage.csv`

## What is weak

- The workload is synthetic and does not validate performance on real CCTNS,
  ICJS, FIR, or police access-log data.
- The blockchain layer is still a local permissioned blockchain-style
  simulation, not a deployed Hyperledger Fabric network.
- NS-PI detects the compromised-signer case under measurable conditions, but
  it misses low-rate global corruption and small targeted corruption.
- The structured XAI trace is strong, but the natural-language explanation
  text does not always mention every decisive attribute.

## Next refinement

- Ask the professor to check whether the problem statement should emphasize
  access governance, compromised-signer detection, or XAI audit review as the
  main novelty.
- Improve table formatting after Overleaf compile because local TeX tools are
  unavailable in this environment.
- Keep future manuscript claims tied to the generated result tables and avoid
  deployment, legal-compliance, or real police-data claims.
