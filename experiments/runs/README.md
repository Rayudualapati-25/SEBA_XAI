# Experiment Runs

This folder stores reproducible run records.

Current run records:

| Run ID | Date | Type | Status |
|---|---:|---|---|
| `20260527_step1_synthetic_requests_seed42` | 2026-05-27 | Synthetic access-request generation | Moved to `prototype/runs/`; complete; not an experiment result |

Every future run should create:

```text
experiments/runs/<run_id>/
  config.yaml
  logs/
  metrics.json
  artifacts/
  README.md
```

Required run metadata:

- run ID;
- date/time;
- code commit or file hash if not using git;
- dataset source URLs and download date;
- random seed;
- baseline/proposed/ablation label;
- environment;
- known limitations.

Important boundary:

- The current Step 1 run generated a synthetic workload only and has been organized under `prototype/runs/`.
- It does not contain RBAC, ABAC/PBAC, XAI, blockchain audit, baseline comparison, or experimental results.
