# 03 Dataset Discovery

Generated: 2026-05-12  
Evidence status: discovery and suitability review. No dataset has been downloaded or profiled in this folder yet.

## Dataset Suitability Rule

A dataset is suitable for publication only if the paper's claim matches what the dataset actually contains. Public NCRB tables can support aggregate trend modeling. They do not support individual suspect prediction, station-level operational recommendations, or claims about true crime incidence. Synthetic data can support access-control and audit-workflow experiments only if generation rules, seeds, distributions, and limitations are fully documented.

## Recommended Dataset Stack

Use a three-part dataset stack:

1. **Synthetic multi-station access-control workload** for the core blockchain/security/XAI experiment.
2. **NCRB Crime in India plus BPRD DoPO** for India aggregate crime and police-resource context.
3. **UNSW-NB15/CSE-CIC-IDS2018, Elliptic, and Amazon Employee Access** as optional method benchmarks for cybersecurity, blockchain-graph, and access-control ML tasks.

This stack is stronger than relying only on public crime prediction datasets because the main contribution is access governance and auditability.

## India-Specific Sources

### NCRB Crime in India 2023

Source: https://www.data.gov.in/catalog/crime-india-2023

Content: cognizable crimes, IPC crimes, SLL cases, violent crimes, murder, cybercrime, crimes against women/children/SC/ST/senior citizens, human trafficking, police/court disposal, arrests, convictions, and related aggregate tables.

Usability: best current public India crime source for state/UT, district, city, and crime-head aggregate analysis where tables permit.

Limitations: reported/registered cases only; not true incidence; not public incident-level FIR records; not enough for individual prediction; schema continuity must be checked across years, especially around the transition from IPC/CrPC/Evidence Act terminology to new criminal laws.

Publication suitability: **strong for aggregate descriptive modeling and trend baselines; unsuitable for individual or station-level prediction claims.**

### NCRB Crime in India 2022 and Earlier

Source: https://www.data.gov.in/catalog/crime-india-2022

Content: similar annual aggregate crime tables.

Usability: necessary for time-series baselines, temporal holdout, and schema-continuity checks.

Limitations: same reporting-bias and aggregation limitations as 2023. Older tables may require harmonization.

Publication suitability: **strong for aggregate trend analysis if preprocessing is documented.**

### BPRD Data on Police Organizations

Source: https://bprd.nic.in/en/page/data_on_police_organization_dopo

Content: manpower, infrastructure, vehicles, police stations, state/UT and organization-level policing capacity statistics. BPRD says DoPO has been an annual publication since 1986 and is used by government agencies, NITI Aayog, and MHA.

Usability: police-capacity covariates, station counts, manpower normalization, and context for workload simulation.

Limitations: not a crime incident dataset; capacity variables can reflect reporting capacity, not public safety.

Publication suitability: **strong as covariates/context; not a target dataset.**

### NCRB ADSI 2023

Source: https://www.data.gov.in/catalog/accidental-deaths-suicides-india-adsi-2023

Content: accidental deaths, traffic accidents, suicides, causes, means, and demographic aggregate tables.

Usability: public-safety context and cautionary comparison, not crime prediction.

Limitations: ethically sensitive; suicide should not be treated as a policing target; aggregate only.

Publication suitability: **moderate for context with strict ethics; not recommended for core experiments.**

### CCTNS Operational Status

Source: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241

Content: national CCTNS coverage, state/UT police-station coverage, FIR digitization counts, near-real-time replication to NDC, standardized investigation forms and master codes.

Usability: baseline context for system assumptions and synthetic workload design.

Limitations: not an open operational dataset.

Publication suitability: **strong as official context; not suitable as experiment data.**

### ICJS Official Description

Source: https://www.mha.gov.in/en/commoncontent/icjsncrb-administration

Content: integration of CCTNS, e-Courts, e-Prisons, e-Forensics, and e-Prosecution; Data Sharing Matrix.

Usability: inter-agency workflow model and motivation.

Limitations: no public transaction logs or request-level access data.

Publication suitability: **strong as architecture context.**

### I4C National Cybercrime Reporting Portal

Source: https://i4c.mha.gov.in/ncrp.aspx

Content: official portal features for cybercrime reporting, monitoring dashboards, online tracking, and citizen financial cyber fraud reporting workflow.

Usability: cybercrime workflow context and possible synthetic scenario inspiration.

Limitations: no public raw complaint dataset.

Publication suitability: **moderate as context only.**

### NJDG/eCourts Public Judicial Data

Source: https://doj.gov.in/the-national-judicial-data-grid-njdg/

Content: civil/criminal case data, orders, judgments, and case details across computerized courts, according to Department of Justice descriptions.

Usability: downstream criminal-justice context; legal NLP only if public judgments are used with privacy safeguards.

Limitations: court records are not police FIR data; scraping/API legality and terms must be checked.

Publication suitability: **moderate for legal NLP; not a substitute for CCTNS/FIR data.**

## FIR/NLP Dataset Reality Check

There is no clear official open national FIR-text dataset suitable for police-record NLP. Kaggle or scraped "Indian crime" datasets may exist, but many lack provenance, licensing clarity, or field definitions. For an IEEE-level paper, do not make FIR NLP the core experiment unless a legally reusable, documented dataset is obtained.

Indian legal NLP datasets such as IndianBailJudgments-1200 and ILDC are useful for court-text modeling, explanation, and fairness experiments, but they are not FIR datasets and do not represent police access requests. Sources: https://arxiv.org/abs/2507.02506 and https://arxiv.org/abs/2105.13562

## Global Method Benchmarks

### UK Police Open Data

Source: https://data.police.uk/about/

Content: street-level crime and anti-social behaviour incidents, approximate location, month, crime category, outcomes, stop-and-search data, and Open Government Licence v3.0.

Use: incident-like crime forecasting and XAI method testing.

Limitation: UK context does not transfer directly to India.

Publication suitability: **strong as external benchmark; weak for India claims.**

### Chicago Crimes 2001 to Present

Source: https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2

Content: incident records with date, type, block-level location, arrest flag, domestic flag, beat, district, ward, community area, and coordinates.

Use: standard spatiotemporal crime benchmark.

Limitation: US city data, reporting bias, not India.

Publication suitability: **strong for method comparison; not for India deployment claims.**

### FBI NIBRS / Crime Data API

Source: https://www.fbi.gov/services/cjis/ucr/

Content: incident/offense/victim/offender/arrestee/property data where agencies report via NIBRS.

Use: rich incident-level criminal-justice benchmark.

Limitation: US reporting rules and completeness vary; not India.

Publication suitability: **moderate to strong for incident-level method testing; not for India conclusions.**

### Elliptic Bitcoin Transaction Dataset

Source: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set/data

Content: Bitcoin transaction graph with licit, illicit, and unknown labels; 203,769 nodes, 234,355 edges, and 166 anonymized features according to the dataset description.

Use: blockchain/security graph anomaly detection and XAI.

Limitation: cryptocurrency AML, not police data sharing; feature meanings are anonymized.

Publication suitability: **moderate as optional security/blockchain benchmark.**

### UNSW-NB15

Source: https://research.unsw.edu.au/projects/unsw-nb15-dataset

Content: network traffic generated in a cyber range with normal and attack traffic.

Use: cyber/anomaly detection and explanation tests.

Limitation: lab/testbed data; leakage and split design matter.

Publication suitability: **strong for cybersecurity benchmark; not policing-specific.**

### CSE-CIC-IDS2018

Source: https://registry.opendata.aws/cse-cic-ids2018/

Content: collaborative CSE/CIC cyber defense dataset on AWS using profiles to generate realistic cybersecurity data.

Use: intrusion/anomaly detection and security XAI.

Limitation: large, computationally heavy, testbed-generated.

Publication suitability: **strong for security benchmark; optional for first paper.**

### Amazon Employee Access Challenge

Source: https://www.kaggle.com/c/amazon-employee-access-challenge/data

Content: historical employee/resource/role access approval records from 2010 and 2011.

Use: access-control classification and XAI baseline.

Limitation: corporate access control, not law enforcement; Kaggle terms must be checked.

Publication suitability: **moderate if license allows; not India-specific.**

## Final Dataset Recommendation

For the first publishable paper:

1. Main benchmark: synthetic multi-station access-control workload with deterministic seed and documented policy oracle.
2. India context: NCRB Crime in India 2023/2022 plus BPRD DoPO for aggregate trend and capacity covariates.
3. Optional extension: UNSW-NB15 for security anomaly XAI or Amazon Employee Access for access-control ML baseline.

Do not center the paper on FIR NLP unless a proper official or legally reusable FIR dataset is obtained.
