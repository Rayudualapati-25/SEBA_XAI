# 12 Five-Day Learning Plan

Generated: 2026-05-12  
Goal: prepare for an M.Tech/IEEE-level paper direction in five focused days.

## Day 1: Understand the Problem and Indian Context

### Read

- PIB CCTNS operational status: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241
- MHA ICJS page: https://www.mha.gov.in/en/commoncontent/icjsncrb-administration
- NCRB Crime in India 2023 catalog: https://www.data.gov.in/catalog/crime-india-2023
- BPRD DoPO page: https://bprd.nic.in/en/page/data_on_police_organization_dopo

### Learn

- What CCTNS does.
- What ICJS connects.
- Why a blockchain overlay must not replace existing systems.
- Difference between public aggregate NCRB data and restricted operational police records.

### Deliverable

Write one page answering:

1. What problem does CCTNS/ICJS already solve?
2. What problem remains for sensitive access governance?
3. Why is "put all police data on blockchain" a weak idea?
4. What should stay off-chain?

### Supervisor Check

You pass Day 1 only if you can explain the project without saying "CCTNS does not exist" or "blockchain stores FIRs".

## Day 2: Literature Review Across Three Equal Pillars

### Read: Blockchain

- Hyperledger Fabric paper: https://arxiv.org/abs/1801.10228
- Two-Level Blockchain System for Digital Crime Evidence Management: https://www.mdpi.com/1424-8220/21/9/3051
- LEChain: https://doi.org/10.1016/j.future.2020.09.038
- Blockchain access-control survey: https://arxiv.org/abs/1908.08503

### Read: Security/Privacy

- NIST SP 800-162 ABAC: https://csrc.nist.gov/pubs/sp/800/162/upd2/final
- Fabric ABAC paper: https://doi.org/10.1016/j.jisa.2022.103182
- Privacy-preserving ML survey: https://arxiv.org/abs/2108.04417

### Read: XAI/Fairness

- Rudin high-stakes interpretable models: https://doi.org/10.1038/s42256-019-0048-x
- Ensign predictive-policing feedback loops: https://proceedings.mlr.press/v81/ensign18a.html
- XAI in law enforcement: https://doi.org/10.3389/fpos.2025.1605619

### Deliverable

Update a literature table with:

- what each paper solves;
- what it does not solve;
- what gap remains for SEBA-XAI.

### Supervisor Check

You pass Day 2 only if each pillar has equal weight. Do not let blockchain dominate the paper.

## Day 3: Dataset Discovery and Rejection Discipline

### Study

- `03_datasets.md`
- `04_dataset_matrix.csv`
- NCRB Crime in India 2023 and 2022 catalogs.
- UK Police Open Data: https://data.police.uk/about/
- Chicago Crimes dataset.
- UNSW-NB15 and CSE-CIC-IDS2018.
- Elliptic Bitcoin dataset.
- Amazon Employee Access Challenge.

### Learn

- Why NCRB supports aggregate modeling only.
- Why FIR/NLP is not ready without a proper dataset.
- Why synthetic workload is valid for access-control benchmarking if documented.
- Why global datasets are method benchmarks, not India evidence.

### Deliverable

Write a dataset decision memo:

- accepted for core experiment;
- accepted for context;
- accepted for optional benchmark;
- rejected and why.

### Supervisor Check

You pass Day 3 only if you reject at least one tempting but weak dataset due to provenance, licensing, or mismatch.

## Day 4: Architecture and Methodology

### Study

- `06_proposed_architecture.md`
- `07_methodology.md`
- `08_experiment_plan.md`
- `09_evaluation_metrics.md`

### Learn

- RBAC vs ABAC/PBAC.
- Why policy oracle is required.
- Why signed append-only logs are a serious baseline.
- What should be hashed on-chain.
- What explanation artifacts should contain.
- What ablations prove.

### Deliverable

Draw or describe:

1. access-request workflow;
2. blockchain audit workflow;
3. XAI artifact workflow;
4. baseline/proposed-method comparison;
5. threat model.

### Supervisor Check

You pass Day 4 only if your methodology includes baselines and ablations. A proposed system without ablations is not enough.

## Day 5: Paper Preparation

### Study

- `05_research_gap.md`
- `10_ethics_security_legal.md`
- `11_paper_outline.md`

### Write

- final title;
- 250-word abstract;
- problem statement;
- objectives;
- contribution list;
- limitations;
- experiment table;
- expected paper outline.

### Learn

- How to phrase novelty without overclaiming.
- How to separate facts, interpretation, and recommendation.
- How to write limitations before results.
- How to make negative results publishable.

### Deliverable

Produce a two-page mini-proposal:

1. title;
2. abstract;
3. research gap;
4. architecture summary;
5. experiment plan;
6. evaluation metrics;
7. risks and limitations;
8. target venue.

### Supervisor Check

You pass Day 5 only if the mini-proposal contains no fake results, no SOTA claim, no deployment claim, and no individual crime-prediction claim.

## What to Learn Next

- Hyperledger Fabric chaincode basics.
- ABAC policy modeling and XACML/Rego-style policy expression.
- Cryptographic hashing, signatures, and append-only logs.
- Basic threat modeling: STRIDE and misuse cases.
- Interpretable ML: decision trees, rule lists, logistic regression, Explainable Boosting Machines.
- XAI limits: SHAP/LIME stability and explanation leakage.
- Privacy basics: differential privacy, federated learning, secure multiparty computation, homomorphic encryption.
- Responsible AI in public-sector and high-stakes settings.

## Weekly Continuation After the Five Days

Week 2: implement synthetic workload generator and RBAC/ABAC baselines.  
Week 3: implement signed-log and Fabric-style audit prototype.  
Week 4: add XAI artifact logging and threat/tamper tests.  
Week 5: run ablations and create plots/tables.  
Week 6: write first IEEE-style draft with real results only.
