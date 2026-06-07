# Reproducing SEBA-XAI Results

End-to-end reproduction takes ~5 minutes on a 2024 M-series laptop. No GPU required, no network access required, deterministic seed in every step.

## 1. Environment

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Python ≥3.11. The pinned dependency ranges in `pyproject.toml` are tested against numpy 2.x, pandas 2.x, scikit-learn 1.8.x.

Verify the install:

```bash
make test
```

Expected: **75 passed** after the seed-confidence helper tests are present.

## 2. Multi-seed sweep (~30 s)

Generates the synthetic workload + policy-oracle labels + audit logs for seeds 7, 21, 99, 123. Seed 42 already exists in `prototype/runs/`. Re-running is safe — output dirs are seed-tagged.

```bash
bash scripts/run_multi_seed.sh
```

Outputs: `prototype/runs/20260528_step{1,2,3,4}_*_seed{7,21,99,123}/`.

## 3. Multi-seed aggregation (~1 s)

Reads all five seeds' `metrics.json`, emits mean ± std + 95% bootstrap CI for every numeric metric.

```bash
python3 scripts/aggregate_seeds.py
```

Output: [results/tables/multi_seed_summary.csv](results/tables/multi_seed_summary.csv).

## 4. Full evaluation grid (~30 s)

Runs every defense × attack × seed cell. Includes the NS-PI drift detector trained on each seed's labeled requests.

```bash
python3 scripts/run_full_grid.py
```

Outputs:
- [results/tables/full_grid_raw.csv](results/tables/full_grid_raw.csv) — one row per (seed, defense, attack).
- [results/tables/full_grid_per_attack.csv](results/tables/full_grid_per_attack.csv) — aggregated per (defense, attack).
- [results/tables/full_grid_aas_by_defense.csv](results/tables/full_grid_aas_by_defense.csv) — AAS mean/std per defense across seeds.

## 5. Adaptive attacks + ablation (~10 s)

```bash
python3 scripts/run_ablations.py
```

Outputs:
- [results/tables/adaptive_attack_summary.csv](results/tables/adaptive_attack_summary.csv).
- [results/tables/nspi_ablation.csv](results/tables/nspi_ablation.csv).

## 6. Compromised-signer sensitivity

```bash
python3 scripts/run_nspi_sensitivity.py
python3 scripts/run_nspi_targeted_sensitivity.py
```

Outputs:
- [results/tables/nspi_compromised_signer_sensitivity_summary.csv](results/tables/nspi_compromised_signer_sensitivity_summary.csv).
- [results/tables/nspi_targeted_compromised_signer_summary.csv](results/tables/nspi_targeted_compromised_signer_summary.csv).

## 7. Explanation and audit quality

```bash
python3 scripts/run_explanation_audit_quality.py
```

Outputs:
- [results/tables/explanation_audit_quality.csv](results/tables/explanation_audit_quality.csv).
- [results/tables/explanation_audit_quality_summary.csv](results/tables/explanation_audit_quality_summary.csv).

## 8. Workload and policy-mix stress test

```bash
python3 scripts/run_workload_policy_stress.py
```

Outputs:
- [results/tables/workload_policy_stress_summary.csv](results/tables/workload_policy_stress_summary.csv).
- [results/tables/workload_policy_stress_raw.csv](results/tables/workload_policy_stress_raw.csv).

This regenerates the 40-cell stress matrix over workload size and policy-mix
arms. It is slower than the smaller metric scripts because it re-runs the
synthetic generation and policy/audit pipeline for each cell.

## 9. Seed-level confidence / stability table

```bash
python3 scripts/run_seed_confidence_summary.py
```

Outputs:
- [results/tables/seed_confidence_summary.csv](results/tables/seed_confidence_summary.csv) — mean/std/min/max per metric group.
- [results/tables/seed_confidence_raw.csv](results/tables/seed_confidence_raw.csv) — long-form per-seed values used for the summary.

This script does not run new experiments. It only consolidates existing
seed-level raw CSVs so paper claims can report stability instead of isolated
mean values.

## 10. Read the honest interpretation

Before quoting any number from the tables above, read [results/FINDINGS.md](results/FINDINGS.md). It documents which results support the locked contribution sentence and which do not.

## 11. Generate paper figures

```bash
python3 scripts/generate_paper_figures.py
```

Outputs:
- [papers/final_paper/figures_tables/fig_01_seba_xai_architecture.svg](papers/final_paper/figures_tables/fig_01_seba_xai_architecture.svg).
- [papers/final_paper/figures_tables/fig_02_detector_visibility.svg](papers/final_paper/figures_tables/fig_02_detector_visibility.svg).
- [papers/final_paper/figures_tables/fig_03_compromised_signer_detection.svg](papers/final_paper/figures_tables/fig_03_compromised_signer_detection.svg).
- [papers/final_paper/figures_tables/fig_04_nspi_sensitivity.svg](papers/final_paper/figures_tables/fig_04_nspi_sensitivity.svg).
- [papers/final_paper/figures_tables/fig_05_xai_audit_quality.svg](papers/final_paper/figures_tables/fig_05_xai_audit_quality.svg).
- [papers/final_paper/figures_tables/fig_06_workload_stress_detection.svg](papers/final_paper/figures_tables/fig_06_workload_stress_detection.svg).

The figure script reads the regenerated CSVs; it does not invent result
numbers.

## 12. Everything in one command

```bash
make reproduce
```

Equivalent to steps 2 through 9 above.

## 13. Verifying reproducibility

After running `make reproduce`, re-run it. Deterministic result columns should
match across runs. Runtime fields such as `runtime_seconds` in the workload
stress tables can vary because they measure local wall-clock execution time,
and timestamps inside `prototype/runs/*/config.yaml` are run-time metadata. If
a non-runtime result metric differs, that's a bug — file an issue.

## 14. Cleaning up

```bash
make clean
```

Removes Python build artifacts and caches. Does **not** remove `prototype/runs/` or `results/tables/` — those are intentional inputs/outputs you want to keep.
