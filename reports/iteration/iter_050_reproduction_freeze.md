# Iteration 050 - Reproduction Freeze

Date: 2026-06-06

## Scope

Implemented the reproduction-freeze step for the aligned SEBA-XAI paper draft.
The goal was to verify that the current paper claims in
`papers/final_paper/paper_draft_v2.md` are backed by regenerated artifacts and
that the prototype passes basic engineering checks.

## Commands Run

| Command | Result |
|---|---|
| `make test` | Passed: 75 tests |
| `make lint` | Passed |
| `make typecheck` | Passed after fixing static typing issues |
| `make reproduce` | Passed |
| `make figures` | Passed |

## Implementation Fixes

The first `make typecheck` run failed with typing errors in four source files.
The fixes were type-surface changes only:

- cast registered attack functions to the `Attack` protocol in
  `src/seba/attacks/catalog.py`;
- typed `per_group_drift(**kwargs)` in `src/seba/nspi/drift.py`;
- avoided a reused variable type in `src/seba/nspi/counterfactual.py`;
- typed defense callables and the aggregate return value in
  `src/seba/scoring/grid.py`.

No scoring formula, attack behavior, or result interpretation was intentionally
changed by these fixes.

## Regenerated Evidence

The freeze regenerated the main evidence files used by the draft:

- `results/tables/full_grid_aas_by_defense.csv`
- `results/tables/full_grid_per_attack.csv`
- `results/tables/adaptive_attack_summary.csv`
- `results/tables/nspi_compromised_signer_sensitivity_summary.csv`
- `results/tables/nspi_targeted_compromised_signer_summary.csv`
- `results/tables/explanation_audit_quality_summary.csv`
- `results/tables/workload_policy_stress_summary.csv`
- `results/tables/seed_confidence_summary.csv`
- `results/tables/paper_table_03_metadata_exposure.csv`
- `results/tables/paper_table_04_latency_storage.csv`
- `papers/final_paper/figures_tables/fig_01_seba_xai_architecture.svg`
- `papers/final_paper/figures_tables/fig_02_detector_visibility.svg`
- `papers/final_paper/figures_tables/fig_03_compromised_signer_detection.svg`
- `papers/final_paper/figures_tables/fig_04_nspi_sensitivity.svg`
- `papers/final_paper/figures_tables/fig_05_xai_audit_quality.svg`
- `papers/final_paper/figures_tables/fig_06_workload_stress_detection.svg`

## Claim Drift Check

No headline drift was found against `paper_draft_v2.md`:

- trusted policy oracle AAS remains `1.0000`;
- ABAC/Fabric/blockchain/CT/signed-chain AAS remains `0.7917`;
- mutable log AAS remains `0.5000`;
- NS-PI AAS remains `0.2500` with std about `0.0932`;
- `compromised_signer` remains undetected by ledger-only/ABAC-style baselines
  and detected by NS-PI/trusted oracle in the five-seed full-grid setting;
- NS-PI still misses 2% and 5% global corruption and detects 10% global
  corruption in the sensitivity table;
- 10% targeted station/district corruption is still missed;
- XAI/audit quality values remain aligned with the draft, including
  counterfactual validity around `0.9964` and decisive-attribute full text
  coverage around `0.7810`;
- metadata exposure remains `1.0000` for the full-metadata ledger and `0.0000`
  for the minimized-commitment ledger under the schema-level proxy.

## What Worked

The reproduction pipeline is now executable end to end, and the aligned paper
draft is not depending on stale headline numbers.

## What Is Still Weak

The freeze does not remove the core research limitations: synthetic workload,
declared policy oracle, local blockchain-style simulation, schema-level privacy
proxy, and no real CCTNS/ICJS deployment evidence.

## Next Step

Sync `paper_draft_v2.md` into the Overleaf/IEEE manuscript and merge Related
Work, Threat Model, Limitations, Conclusion, references, and generated figures.
Do not add new claims unless a new experiment is first added and recorded.
