# Experiment Plan

Generated: 2026-04-24  
Updated: 2026-06-05  
Status: active publication experiment plan. The original plan has been partially executed for the synthetic SEBA-XAI access-governance benchmark. Current results exist under `results/tables/`, `results/plots/`, `prototype/runs/`, `experiments/runs/`, and `results/FINDINGS.md`.

Important boundary: all completed experiments use synthetic access-governance workloads. No real CCTNS logs, ICJS logs, FIR records, police records, or live Hyperledger Fabric deployment have been used.

## Current Publication Framing

The first paper should be framed as:

> SEBA-XAI as a reproducible, synthetic benchmark and prototype for explainable policy-aware audit in sensitive inter-agency access governance.

It should not be framed as crime prediction, real police deployment, legal-compliance proof, or raw police data on blockchain.

## Reproducibility Requirements

- Use deterministic seeds where possible.
- Save every run config under `experiments/runs/<run_id>/config.yaml`.
- Save logs under `experiments/runs/<run_id>/logs/`.
- Save metrics under `experiments/runs/<run_id>/metrics.json`.
- Save tables under `results/tables/`.
- Save plots under `results/plots/`.
- Record dataset version, source URL, download date, preprocessing hash, and known limitations.
- Never claim superiority without baseline and ablation results.

## Completed Synthetic Benchmark Evidence

The following experiment families have already been implemented and recorded:

| Experiment Family | Main Scripts/Artifacts | Current Evidence |
|---|---|---|
| Synthetic access-request generation | `prototype/synthetic_access_sim/generate_synthetic_requests.py`, `prototype/runs/*step1*/` | synthetic stations, officers, cases, records, and access requests |
| Policy oracle and XAI artifacts | `prototype/synthetic_access_sim/policy_oracle.py`, `prototype/runs/*step2*/` | `allow`/`deny`/`escalate` labels, reason codes, decisive attributes, explanation hashes |
| Mutable and signed audit baselines | `prototype/synthetic_access_sim/audit_baseline.py`, `prototype/runs/*step3*/` | mutable log and signed hash-chain comparisons |
| Permissioned blockchain-style audit simulation | `prototype/synthetic_access_sim/blockchain_audit.py`, `prototype/runs/*step4*/` | local block/event commitments and tamper tests |
| Latency and storage overhead | `prototype/synthetic_access_sim/measure_overhead.py`, `prototype/runs/*step5*/`, `results/tables/paper_table_04_latency_storage.csv` | decision/audit/build/verify overhead tables |
| Experiment-mode comparison | `prototype/synthetic_access_sim/experiment_modes.py`, `prototype/runs/*step6*/` | method comparison outputs |
| Off-chain record and metadata leakage study | `prototype/synthetic_access_sim/offchain_storage.py`, `prototype/runs/*step7*/`, `results/tables/paper_table_03_metadata_exposure.csv` | full-metadata vs minimized commitment ledgers |
| Policy ablation | `prototype/synthetic_access_sim/policy_ablation.py`, `results/tables/policy_ablation_step8_comparison.csv` | component-removal effects |
| Multi-seed full grid | `scripts/run_full_grid.py`, `results/tables/full_grid_*.csv` | five-seed comparison across defenses and attacks |
| NS-PI ablation and compromised-signer analysis | `scripts/run_ablations.py`, `results/tables/adaptive_attack_summary.csv`, `results/tables/nspi_ablation.csv` | compromised-signer asymmetry and NS-PI variants |
| Global sensitivity | `scripts/run_nspi_sensitivity.py`, `results/tables/nspi_compromised_signer_sensitivity_*.csv` | 2%-50% global flip sensitivity |
| Targeted sensitivity | `scripts/run_nspi_targeted_sensitivity.py`, `results/tables/nspi_targeted_compromised_signer_*.csv` | station/district-targeted corruption results |
| XAI and audit reconstruction quality | `scripts/run_explanation_audit_quality.py`, `results/tables/explanation_audit_quality*.csv` | trace completeness, counterfactual validity, audit reconstruction |
| Workload/policy-mix stress | `scripts/run_workload_policy_stress.py`, `results/tables/workload_policy_stress_*.csv` | workload size and policy-mix stress results |
| Seed-confidence summary | `scripts/run_seed_confidence_summary.py`, `results/tables/seed_confidence_*.csv` | descriptive stability summary across seeds |

Current interpreted findings are summarized in `results/FINDINGS.md`. That file is the authoritative claim source until the next reproduction freeze.

## Experiment 1: Multi-Station Access-Control and Audit Workload

Goal: test the blockchain/security/XAI core without requiring restricted police data.

Dataset/workload:

- Synthetic police-station records and access requests.
- Entities: station, district, state, officer, superior officer, case, data object, approval token.
- Data-object attributes: sensitivity level, case type, jurisdiction, victim/witness flag, juvenile flag, evidence type, retention state.
- Subject attributes: role, rank, station, jurisdiction, active credential, case assignment, training status.
- Environment attributes: emergency flag, time window, purpose, court/prosecutor request, network status.

Baselines:

1. Centralized RBAC plus database audit log.
2. Centralized ABAC using NIST-style policies.
3. Federated local databases plus signed append-only logs.
4. Basic Hyperledger Fabric with MSP identities and simple chaincode authorization.

Proposed methods:

1. Fabric plus ABAC.
2. Fabric plus ABAC plus off-chain encrypted storage.
3. Fabric plus ABAC plus DID/VC-style authorization credentials.
4. Fabric plus ABAC plus XAI audit artifact logging.

Metrics:

- authorization accuracy against labeled policy tests;
- false allow and false deny rates;
- access latency p50/p95/p99;
- throughput under concurrent station requests;
- audit completeness;
- tamper detection rate;
- metadata leakage score;
- revocation delay;
- policy-update consistency;
- node outage behavior.

Ablations:

- remove blockchain audit;
- remove ABAC and use RBAC only;
- remove off-chain encryption;
- remove DID/VC credentials;
- remove XAI explanation logging;
- remove superior-approval requirement;
- vary classified-record percentage;
- vary station outage and network partition rates.

Minimum result required before claims:

- one run per baseline and proposed method;
- one ablation per substantive component;
- saved config, logs, metrics, and comparison table.

Current status:

- Completed for the synthetic benchmark with multiple baselines and five-seed evaluation.
- Evidence exists in `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv`, `results/tables/full_grid_raw.csv`, `results/tables/policy_ablation_step8_comparison.csv`, and `results/FINDINGS.md`.
- The blockchain layer is a local permissioned-audit simulation, not a live Hyperledger Fabric deployment.
- The policy oracle is a benchmark labeling function, not official police policy.

## Experiment 2: India Aggregate Crime Trend Modeling

Goal: produce an honest India-focused AI baseline from public data.

Candidate data:

- NCRB Crime in India 2023 and previous years where schema aligns;
- BPRD Data on Police Organizations;
- population denominators from official sources;
- optional ADSI context for non-crime public safety, kept separate from crime targets.

Possible targets:

- state/UT-year or district-year crime-rate trend;
- crime-head level counts;
- police disposal or chargesheet-rate outcomes;
- cybercrime aggregate trend.

Baselines:

1. last-observation carried forward;
2. historical mean/median by region and crime head;
3. Poisson or negative-binomial regression;
4. regularized linear/logistic model;
5. interpretable GAM or Explainable Boosting Machine;
6. tree/rule-list baseline;
7. random forest or gradient boosting with SHAP, only after simple baselines.

Metrics:

- MAE/RMSE for counts/rates;
- Poisson deviance where suitable;
- calibration for risk buckets;
- per-state and per-region error;
- temporal holdout performance;
- feature stability;
- explanation stability.

Ablations:

- remove police-capacity covariates;
- remove population normalization;
- remove lag features;
- remove sensitive-category targets;
- compare interpretable model versus post-hoc SHAP explanation;
- compare pre-2023 and 2023 schema continuity.

Critical limitation:

NCRB public data supports aggregate modeling. It does not support individual suspect prediction, station-level operational recommendations, or claims about true crime incidence.

Current status:

- Deferred for the first SEBA-XAI access-governance paper.
- NCRB/BPRD should be used for India context and dataset-boundary discussion unless a separate aggregate-modeling experiment is implemented.
- Do not mix aggregate crime-trend modeling claims into the current access-governance results.

## Experiment 3: Security and Blockchain-Anomaly Benchmarks

Goal: give the security pillar its own measurable experiments.

Candidate datasets:

- UNSW-NB15 or CSE-CIC-IDS2018 for intrusion/anomaly detection;
- Elliptic Bitcoin Transaction Dataset for blockchain transaction graph classification;
- Amazon Employee Access Challenge for access-control classification if terms permit.

Baselines:

- logistic regression;
- decision tree/rule list;
- random forest;
- gradient boosting;
- graph baseline for Elliptic;
- interpretable model where feasible.

Proposed methods:

- anomaly detector plus XAI explanation artifacts;
- access-control risk model plus ABAC policy override;
- graph model plus explanation method for illicit transaction classification;
- audit log of model input digest, model version, explanation hash, and human review.

Metrics:

- precision, recall, F1, AUROC, AUPRC;
- false positive rate at operational thresholds;
- explanation fidelity/stability;
- audit reconstruction rate;
- tamper-detection rate for altered artifacts.

Current status:

- Deferred for the first paper.
- These datasets may support a future general cybersecurity paper, but they are not needed to support the current SEBA-XAI police access-governance contribution.

## Publication-Critical Experiments Still Pending

These are not new claims yet. They are the next technical checks before journal submission.

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

## Paper Gate

Results-section drafting is now allowed only from the completed synthetic artifacts listed above. Before final submission:

- rerun the reproduction pipeline;
- verify every result claim against an artifact;
- keep limitations and negative results in the paper;
- label all synthetic results clearly;
- do not claim real police deployment, legal compliance, crime prediction, or raw police data on-chain.
