# 07 Methodology

Generated: 2026-05-12

## Methodology Overview

The methodology is a staged systems evaluation, not a deployment study.

Stage 1 builds a reproducible synthetic inter-station access-control workload. Stage 2 compares baseline and proposed access/audit designs. Stage 3 adds XAI artifact logging and ablations. Stage 4 optionally validates related AI components using public aggregate India crime data and cybersecurity/access-control benchmarks.

## Stage 1: Synthetic Multi-Station Workload

Create deterministic synthetic data with a fixed random seed. Each run must save the generator config.

Entities:

- state;
- district;
- police station;
- officer;
- superior officer;
- case;
- record object;
- approval token;
- access request;
- audit event.

Subject attributes:

- officer role;
- rank;
- station;
- district/state jurisdiction;
- active/revoked credential;
- case assignment;
- clearance/training status;
- prior request count;
- recent denied/escalated requests.

Object attributes:

- record type;
- case type;
- originating station;
- jurisdiction;
- sensitivity level;
- victim/witness flag;
- juvenile flag;
- evidence-media flag;
- sealed/restricted flag;
- retention status.

Environment attributes:

- timestamp;
- purpose;
- time window;
- emergency flag;
- court/prosecutor request flag;
- node/network status;
- policy version.

## Stage 2: Policy Oracle

Build a deterministic policy oracle before training or evaluating any model. The oracle defines the ground-truth expected decision for each request:

- allow;
- deny;
- escalate.

Minimum rules:

- revoked credentials deny;
- sealed records deny unless court/prosecutor flag and authorized approval exist;
- juvenile/witness/victim-sensitive records escalate;
- cross-jurisdiction classified records escalate;
- valid case assignment plus role/rank plus purpose plus time window allow for non-classified records;
- emergency override escalates unless policy explicitly permits temporary access;
- stale assignment or expired approval deny.

The oracle is necessary because "accuracy" has no meaning without a known expected decision.

## Stage 3: Baselines

Baseline A: centralized RBAC plus mutable database audit log.

Baseline B: centralized ABAC/PBAC plus mutable database audit log.

Baseline C: centralized ABAC/PBAC plus signed append-only log.

Baseline D: basic Hyperledger Fabric-style audit with simple chaincode authorization.

These baselines prevent the paper from comparing the proposed design only against weak strawmen.

## Stage 4: Proposed Designs

Proposed P1: Fabric-style audit plus ABAC/PBAC.

Proposed P2: P1 plus off-chain encrypted payload pointers and payload hash commitments.

Proposed P3: P2 plus superior-approval token commitments.

Proposed P4: P3 plus XAI explanation artifact logging.

Optional P5: P4 plus privacy-preserving attribute treatment, such as hashed attributes, selective disclosure, or hidden-policy experiments. Keep this optional unless implementation time permits.

## Stage 5: AI and XAI Methods

Use deterministic policies for final access decisions. AI is decision support:

- access-risk scoring;
- anomaly detection for suspicious request patterns;
- aggregate crime trend modeling from public data;
- explanation generation and logging.

Recommended first models:

- rule list or decision tree for access-risk model;
- logistic regression or Explainable Boosting Machine for interpretable risk scoring;
- isolation forest or one-class baseline for anomaly detection;
- last-observation, historical mean, Poisson/negative-binomial regression, and regularized linear models for aggregate NCRB trend baselines.

XAI methods:

- policy-reason trace for ABAC/PBAC;
- feature contribution table for interpretable model;
- SHAP only for tree/boosting baselines;
- explanation-stability check under small non-sensitive perturbations.

## Stage 6: Ablations

Run at least these ablations:

- remove blockchain audit;
- remove ABAC/PBAC and use RBAC only;
- remove off-chain encryption;
- remove superior approval;
- remove XAI explanation logging;
- remove anomaly/risk scoring;
- vary classified-record percentage;
- vary cross-jurisdiction request percentage;
- vary credential revocation rate;
- vary station outage/network partition rate.

## Stage 7: India Aggregate Crime Context

Use NCRB Crime in India 2023/2022 and BPRD DoPO only for aggregate analysis:

- state/UT-year crime rates;
- crime-head counts;
- cybercrime aggregate trend;
- police capacity covariates;
- basic trend and interpretability demonstration.

Do not use this stage to claim individual prediction, station recommendations, or policing effectiveness.

## Stage 8: Reproducibility Package

Every experiment must save:

- `config.yaml`;
- random seed;
- generator version/hash;
- policy version/hash;
- model version/hash;
- metrics JSON;
- logs;
- audit events;
- explanation artifacts or hashes;
- plots;
- known limitations.

Suggested future run path:

```text
experiments/runs/<run_id>/
  config.yaml
  logs/
  metrics.json
  artifacts/
  README.md
```

## Research Hypotheses

H1. Fabric plus ABAC/PBAC will improve tamper detection and audit reconstruction compared with centralized mutable logs.

H2. Signed append-only logs will be a strong non-blockchain baseline and may be faster than blockchain. If so, report it honestly.

H3. XAI artifact logging will improve reviewability and audit completeness, but may increase storage and latency overhead.

H4. Off-chain encryption will reduce raw-data exposure but may not fully solve metadata leakage.

H5. Public NCRB/BPRD data can support aggregate trend analysis but not individual-level prediction.

## Minimum Publishable Method

The minimum credible paper needs:

- at least one run per baseline and proposed method;
- at least one ablation for blockchain, ABAC/PBAC, off-chain encryption, superior approval, and XAI logging;
- a comparison table;
- latency/throughput plots;
- tamper-detection results;
- metadata-leakage discussion;
- limitations and negative results.
