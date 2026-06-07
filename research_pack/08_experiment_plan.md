# 08 Experiment Plan

Generated: 2026-05-12  
Updated: 2026-06-05  
Status: active publication experiment plan. The original plan has been partially executed for the synthetic SEBA-XAI access-governance benchmark. Current results exist under `results/tables/`, `results/plots/`, `prototype/runs/`, `experiments/runs/`, and `results/FINDINGS.md`.

Important boundary: all completed experiments use synthetic access-governance workloads. No real CCTNS logs, ICJS logs, FIR records, police records, or live Hyperledger Fabric deployment have been used.

## Current Publication Framing

The first paper should be framed as a reproducible, synthetic benchmark and prototype for explainable policy-aware audit in sensitive inter-agency access governance.

It should not be framed as crime prediction, real police deployment, legal-compliance proof, or raw police data on blockchain.

## Completed Synthetic Benchmark Evidence

The following experiment families have already been implemented and recorded.

| Experiment Family | Main Artifacts | Current Evidence |
|---|---|---|
| Synthetic access-request generation | `prototype/runs/*`, `prototype/synthetic_access_sim/generate_synthetic_requests.py` | synthetic stations, officers, cases, records, and access requests |
| Policy oracle and XAI artifacts | `prototype/synthetic_access_sim/policy_oracle.py`, `results/tables/explanation_audit_quality*.csv` | allow/deny/escalate labels, reason codes, decisive attributes, explanation hashes |
| Mutable and signed audit baselines | `prototype/synthetic_access_sim/audit_baseline.py` | mutable log and signed hash-chain comparison |
| Permissioned blockchain-style audit simulation | `prototype/synthetic_access_sim/blockchain_audit.py` | local block/event commitments and tamper tests |
| Latency and storage overhead | `results/tables/paper_table_04_latency_storage.csv` | decision, audit, block build, and verification overhead |
| Metadata exposure study | `results/tables/paper_table_03_metadata_exposure.csv` | comparison of full metadata logging and minimized commitments |
| Policy ablation | `results/tables/policy_ablation_step8_comparison.csv` | component-removal effects |
| Multi-seed full grid | `results/tables/full_grid_*.csv` | five-seed comparison across defenses and attacks |
| NS-PI compromised-signer analysis | `results/tables/adaptive_attack_summary.csv`, `results/tables/nspi_ablation.csv` | log-only drift signal and failure cases |
| XAI and audit quality | `results/tables/explanation_audit_quality*.csv` | trace completeness, counterfactual validity, audit reconstruction, explanation-text weakness |
| Workload and policy stress | `results/tables/workload_policy_stress_*.csv` | workload-size and policy-mix stress behavior |
| Seed-confidence summary | `results/tables/seed_confidence_*.csv` | descriptive stability summary across five seeds |

Current interpreted findings are summarized in `results/FINDINGS.md`. That file is the controlling source for result claims until the next reproduction freeze.

## Experiment 1: Access-Control Correctness

Goal: verify that each design makes the expected allow/deny/escalate decision against the deterministic policy oracle.

Methods:

- centralized RBAC;
- centralized ABAC/PBAC;
- mutable audit log;
- signed append-only hash chain;
- permissioned blockchain-style audit simulation;
- Fabric/ABAC-style re-execution simulation;
- trusted raw-attribute policy oracle;
- NS-PI log-only policy-drift detection;
- XAI artifact logging.

Metrics:

- authorization agreement score;
- false allow rate;
- false deny rate;
- escalation behavior;
- policy coverage;
- reason-code completeness;
- explanation trace completeness;
- counterfactual validity.

Required scenarios:

- in-jurisdiction normal request;
- cross-jurisdiction sensitive request;
- revoked officer;
- stale case assignment;
- superior approval required;
- juvenile/witness/victim-sensitive record;
- emergency flag;
- court/prosecutor request;
- sealed record;
- expired approval token.

Current status:

- Completed for the synthetic benchmark with five seeds `{7, 21, 42, 99, 123}`.
- Evidence exists in `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv`, `results/tables/full_grid_raw.csv`, `results/tables/policy_ablation_step8_comparison.csv`, and `results/FINDINGS.md`.
- The policy oracle is a benchmark labeling function, not an official police policy source.

## Experiment 2: Audit Completeness and Tamper Detection

Goal: test whether the audit trail can reconstruct what happened and detect manipulation.

Tamper cases:

- delete centralized log row;
- alter decision reason;
- alter explanation artifact;
- alter payload pointer;
- replay approval token;
- backdate request timestamp;
- revoke credential after request and test reconstruction;
- remove superior approval event;
- simulate compromised signer or station-side policy corruption.

Metrics:

- audit completeness;
- tamper detection rate;
- audit reconstruction success;
- missing event rate;
- hash verification failure rate;
- false tamper alert rate;
- authorization agreement under attack.

Current evidence:

- Mutable logs are intentionally weak under tampering.
- Signed hash chains and blockchain-style logs detect ordinary post-write changes better than mutable logs.
- Ledger-only methods do not detect every validly re-signed compromised-signer case, because the corrupted decision can still be structurally valid.
- Trusted policy re-evaluation is strongest in the current synthetic benchmark, but it requires access to stronger raw attributes than a log-only auditor may have.
- NS-PI is useful as a complementary log-only drift signal, but it misses low-rate and some targeted corruption cases.

These statements must be cited from `results/FINDINGS.md` and the matching tables before they are used in the paper.

## Experiment 3: Latency, Throughput, and Storage Overhead

Goal: measure cost of auditability.

Load settings:

- 10, 50, 100, 500 simulated stations;
- 1, 5, 20, 100 concurrent requests per station;
- classified-record ratios of 5%, 20%, 50%;
- cross-jurisdiction request ratios of 5%, 20%, 50%.

Metrics:

- p50/p95/p99 decision latency;
- throughput requests per second;
- audit write latency;
- approval workflow latency;
- storage per request;
- block/event log size;
- explanation artifact size;
- failed request rate under load.

Current status:

- Initial latency and storage measurements exist in `results/tables/paper_table_04_latency_storage.csv`.
- Final submission still needs a reproduction freeze and a clear note that these are local prototype measurements, not production CCTNS/ICJS measurements.

Report negative results. If signed logs are faster and sufficient for some threat models, that is a useful result.

## Experiment 4: Metadata Leakage

Goal: measure how much sensitive context is exposed even when raw records stay off-chain.

Leakage features:

- station pair;
- officer rank;
- request frequency;
- sensitivity level;
- case type;
- timing pattern;
- approval/escalation frequency;
- model reason code.

Designs to compare:

- full metadata logging;
- hashed identifiers;
- coarse sensitivity categories;
- delayed/batched audit writes;
- private data collections or selective visibility if implemented.

Metrics:

- metadata leakage score;
- re-identification proxy risk;
- sensitive-attribute inference accuracy;
- audit utility loss.

Current status:

- Initial metadata exposure comparison exists in `results/tables/paper_table_03_metadata_exposure.csv`.
- This experiment estimates leakage under a synthetic threat model. It does not prove formal privacy.

## Experiment 5: XAI Reviewability

Goal: evaluate whether explanations are complete, stable, and useful for audit.

Explanation types:

- policy trace;
- model feature contribution;
- missing-attribute explanation;
- superior-approval explanation;
- human override explanation.

Metrics:

- explanation trace completeness;
- counterfactual coverage;
- counterfactual validity;
- explanation stability;
- role-specific explanation coverage;
- explanation hash verification;
- audit reconstruction rate;
- decisive-attribute natural-language coverage.

Current evidence:

- Structured traces and audit reconstruction are strong in current synthetic results.
- Natural-language decisive-attribute coverage is a measured weakness and must be reported honestly unless improved and rerun.
- No human-subject review study has been conducted.

First paper can avoid a human-subject study. Use structured checklist-based reviewability metrics unless ethics approval and participants are available.

## Experiment 6: Aggregate India Crime Trend Context

Goal: demonstrate careful India public-data use if a separate aggregate modeling section is later added.

Data:

- NCRB Crime in India 2023;
- NCRB Crime in India 2022 and prior years where compatible;
- BPRD DoPO for police-resource covariates.

Baselines:

- last observation carried forward;
- historical mean/median;
- Poisson or negative-binomial regression;
- regularized linear model;
- interpretable GAM/EBM if feasible;
- random forest/gradient boosting only after simple baselines.

Metrics:

- MAE/RMSE for counts/rates;
- Poisson deviance where suitable;
- temporal holdout error;
- per-state/per-region error;
- feature stability;
- explanation stability.

Current status:

- Deferred for the first SEBA-XAI paper.
- NCRB/BPRD should be used for India context and dataset-boundary discussion, not for individual prediction.

Hard boundary:

- no individual prediction;
- no operational police recommendation;
- no claim of true crime incidence.

## Experiment 7: Optional Security/Blockchain Benchmarks

Use only if time permits:

- UNSW-NB15 or CSE-CIC-IDS2018 for intrusion/anomaly detection;
- Elliptic Bitcoin graph for blockchain/security graph classification;
- Amazon Employee Access for access-control approval modeling.

Purpose:

- show that explanation artifact logging can generalize to cyber/security decisions;
- not central to the India police-sharing contribution.

Current status:

- Deferred for the first paper.
- These datasets should not be used to imply validation of the India police access-governance workflow.

## Publication-Critical Experiments Still Pending

These are not new claims yet. They are the next checks before journal submission.

1. **Reproducibility freeze**
   - Run `make test`, `make lint`, `make typecheck`, `make reproduce`, and `make figures`.
   - Save a new iteration report and document any result drift.

2. **Artifact-to-claim audit**
   - Map every quantitative manuscript claim to the exact CSV/JSON/log/plot artifact.
   - Do not leave any number supported only by prose.

3. **Low-rate compromised-signer boundary, if time permits**
   - Add finer flip fractions around `1%`, `2%`, `5%`, `7.5%`, `10%`, and `12.5%`.
   - Report the result as synthetic sensitivity, not a universal detection threshold.

4. **Grouped drift ablation clarity**
   - Ensure global-only, station-only, district-only, and combined NS-PI behavior is reported for targeted attacks.
   - Current evidence already shows grouped drift matters; final paper must explain where it fails.

5. **Explanation renderer improvement or explicit limitation**
   - Either improve decisive-attribute natural-language coverage and rerun XAI metrics, or keep the measured weakness in the final paper.

6. **Optional real Fabric validation**
   - Only if time and setup allow.
   - No "Fabric deployment" claim is allowed without real Fabric logs/artifacts.

## Run Record Requirements

Every run must save:

```text
experiments/runs/<run_id>/
  config.yaml
  logs/
  metrics.json
  artifacts/
  README.md
```

Every results table must be saved under `results/tables/`. Every plot must be saved under `results/plots/`. Every iteration must update `reports/iteration/iter_*.md`.

## Paper Gate

Results-section drafting is now allowed only from the completed synthetic artifacts listed above. Before final submission:

- rerun the reproduction pipeline;
- verify every result claim against an artifact;
- keep limitations and negative results in the paper;
- label all synthetic results clearly;
- do not claim real police deployment, legal compliance, crime prediction, or raw police data on-chain.
