# Iteration 001: Research Scoping

Date: 2026-04-24  
Status: completed scoping; no experiments run.

## Goal

Create an initial research base for an AI model/system on police and crime in India, treating blockchain, security, and explainable AI as equal pillars.

## What Worked

- Created the `codex research` folder with reproducible research subfolders.
- Identified the strongest official India context: CCTNS and ICJS already provide national criminal-justice information infrastructure.
- Verified that OGD has `Crime in India - 2023`, published 2026-02-10 and updated 2026-02-13.
- Identified public India datasets suitable for aggregate crime and public-safety modeling: NCRB Crime in India, ADSI, and BPRD DoPO.
- Identified global method benchmarks for incident-level crime, access control, cyber anomaly detection, and blockchain/security graph analysis.
- Built an experiment plan with baselines and ablations.

## What Failed or Is Weak

- No actual datasets were downloaded or profiled in this iteration.
- No model, blockchain prototype, or access-control simulator has been implemented yet.
- India public data appears mostly aggregate, not incident-level or station-level.
- Direct blockchain-for-Indian-police-station-sharing literature is sparse.
- Recent law-enforcement XAI and data-protection papers need full-text verification before strong claims.
- Legal analysis of DPDP Act, Bharatiya Sakshya Adhiniyam, CCTNS, ICJS, and operational policing rules requires expert review.

## Evidence Artifacts Created

- `sources/literature_matrix.md`
- `sources/dataset_inventory.md`
- `sources/source_log.md`
- `results/tables/literature_matrix.csv`
- `results/tables/dataset_shortlist.csv`
- `experiments/experiment_plan.md`

## Interpretation

The most defensible research direction is not "put all police data on blockchain." It is:

1. keep sensitive records off-chain and encrypted;
2. use permissioned blockchain for auditable commitments, policy versions, approvals, and access events;
3. use ABAC as the primary security baseline;
4. use XAI to explain model-supported access decisions and aggregate crime-analysis outputs;
5. compare against centralized RBAC/ABAC and signed-log baselines.

## Next Experiment

Build a small synthetic multi-station access-control simulator and compare:

1. centralized RBAC plus audit log;
2. centralized ABAC;
3. signed append-only logs;
4. basic Hyperledger Fabric;
5. Fabric plus ABAC plus off-chain encrypted payload pointers;
6. Fabric plus ABAC plus XAI explanation hash logging.

Required outputs:

- run configs;
- metrics JSON;
- comparison table;
- latency/throughput plot;
- tamper-detection test report;
- updated iteration report.

