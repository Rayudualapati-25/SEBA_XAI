# Dataset Inventory

Generated: 2026-04-24  
Scope: datasets useful for AI research on police/crime in India, plus global benchmarks for methods that India public data cannot support yet.

## India-Specific Datasets and Official Systems

| Dataset/System | URL | Content | Granularity | Access/License | Suitability |
|---|---|---|---|---|---|
| NCRB Crime in India 2023 | https://www.data.gov.in/catalog/crime-india-2023 | Cognizable crimes, IPC crimes, SLL cases, violent crimes, murder, victims, firearms, unidentified bodies, cybercrime, crimes against women/children/SC/ST/senior citizens, human trafficking, police/court disposal, arrests, convictions, recidivism-related tables. | Mostly annual state/UT, district, and metropolitan-city tables depending on resource. | OGD catalog, NDSAP/Government Open Data context. Published 2026-02-10, updated 2026-02-13. | Best current public India crime source for aggregate trend analysis. Not incident-level or station-level public data. |
| NCRB Crime in India 2022 | https://www.data.gov.in/catalog/crime-india-2022 | Similar NCRB annual crime tables for 2022. | Mostly annual aggregate tables. | OGD/NDSAP context. | Useful for building time series and validating schema continuity before 2023. |
| NCRB Accidental Deaths and Suicides in India 2023 | https://www.data.gov.in/catalog/accidental-deaths-suicides-india-adsi-2023 | Natural and unnatural accidents, traffic accidents, suicides, causes, means, age/gender/profession distributions. | Annual national, state/UT, and city tables depending on resource. | OGD catalog; search result states Government Open Data License - India. Published 2025-11-28, updated 2025-12-19. | Adjacent public-safety dataset. Use with strict ethics; suicide is not a crime-prediction target. |
| BPRD Data on Police Organizations | https://bprd.nic.in/page/data_on_police_organization_dopo | Police manpower, infrastructure, vehicles, police stations, and related state/UT/CPO/CAPF organizational data. | State/UT and organization-level reports. | Public reports; exact PDF license must be checked before redistribution. | Strong covariate source for policing capacity, station counts, and normalization. |
| CCTNS operational status | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241 | Official statement of CCTNS coverage, FIR digitization counts, data replication, standardized investigation forms, and master codes. | National and state/UT coverage. | Official press release, not a research dataset. | Critical baseline context for system design. Not public raw CCTNS data. |
| ICJS official description | https://www.mha.gov.in/en/commoncontent/inter-operable-criminal-justice-system-icjs | Integration of CCTNS, e-Courts, e-Prisons, e-Forensics, and e-Prosecution; Data Sharing Matrix; analytics/AI/ML mention. | System-level description. | Official MHA page. | Defines existing criminal-justice interoperability context. Not a downloadable dataset. |
| Police station geolocation examples | https://www.data.gov.in/resource/police-stations-faridabad and https://jk.data.gov.in/resource/police-stations-2021 | City-specific police station names, addresses, and sometimes latitude/longitude. | City-level fragments. | OGD resources. | Useful for prototype maps, not a verified national police-station geocoding dataset. |
| CERT-In annual reports | https://www.cert-in.org.in/s2cMainServlet?pageid=PUBANULREPRT | Cyber incident trends, advisories, response activity, vulnerabilities, training, and coordination information. | Mostly national aggregate/report level. | Public reports; redistribution terms should be checked. | Security context for cybercrime/anomaly research; too aggregate for rich ML alone. |

## Global Benchmarks

| Dataset | URL | Content | Best Use | Limitations |
|---|---|---|---|---|
| UK Police Open Data | https://data.police.uk/ | Street-level crime, outcomes, stop-and-search, approximate location, month, force, crime category. | Spatiotemporal crime forecasting and XAI on open incident-like data. | UK legal/reporting context differs from India. |
| Chicago Crimes 2001 to Present | https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2 | Incident records with type, date/time, block-level location, arrest flag, domestic flag, beat/district/ward/community area, coordinates. | Classic crime forecasting benchmark. | U.S. city data does not transfer directly to India. |
| NYPD Complaint Data Historic | https://catalog.data.gov/dataset/nypd-complaint-data-historic | Complaint records with offense, date, precinct, borough, location, and some demographic fields. | XAI/fairness and incident-level crime modeling benchmark. | Policing-bias and reporting-bias risks. |
| FBI Crime Data API/NIBRS | https://www.fbi.gov/how-we-can-help-you/more-fbi-services-and-information/ucr/nibrs and https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi | Incident/offense/victim/offender/arrestee/property data where agencies report via NIBRS. | Rich incident-level criminal-justice data modeling. | U.S. reporting rules and completeness vary. |
| UCI Communities and Crime | https://archive.ics.uci.edu/dataset/183/communities+and+crime | Socioeconomic, demographic, law-enforcement variables, and crime rates. | Lightweight interpretable regression/fairness baseline. | Old U.S. aggregate data; many missing values. |
| ProPublica COMPAS | https://github.com/propublica/compas-analysis | Broward County criminal-justice records, COMPAS scores, demographics, and recidivism labels. | XAI/fairness benchmark. | Not a crime-prediction dataset; not India-representative. |
| Elliptic Bitcoin Transaction Dataset | https://www.kaggle.com/datasets/ellipticco/elliptic-data-set and https://www.elliptic.co/blog/elliptic-dataset-cryptocurrency-financial-crime | Bitcoin transaction graph with licit/illicit/unknown labels and anonymized features. | Blockchain/security graph ML and XAI experiments. | Feature meanings are anonymized; Kaggle license is restrictive/noncommercial. |
| UNSW-NB15 | https://research.unsw.edu.au/projects/toniot-datasets | Network flow features and attack labels from a cyber range. | Intrusion/anomaly detection baseline. | Lab/testbed data; split and leakage issues must be controlled. |
| CSE-CIC-IDS2018 | https://www.unb.ca/cic/datasets/ids-2018.html | PCAP/log/flow features for multiple attack families. | Security anomaly detection and XAI. | Large; computationally heavier; testbed data. |
| CICIDS2017 | https://www.unb.ca/cic/datasets/ids-2017.html | PCAPs and flow features with benign and attack traffic. | Legacy IDS benchmark. | Known quality and leakage cautions in literature; use carefully. |
| ToN-IoT | https://research.unsw.edu.au/projects/toniot-datasets | IoT/IIoT telemetry, logs, network traffic, and attack classes. | Heterogeneous security anomaly detection. | Not policing-specific. |
| Amazon Employee Access Challenge | https://www.kaggle.com/c/amazon-employee-access-challenge/data | Categorical employee/resource/role attributes and approved/denied access decisions. | Access-control ML and XAI baseline. | Kaggle access and license constraints; not law-enforcement data. |

## Ranked Shortlist for First Experiments

1. NCRB Crime in India 2023 plus BPRD DoPO for India aggregate trend and police-capacity modeling.
2. Synthetic multi-station access-control workload based on CCTNS/ICJS concepts and NIST ABAC.
3. NCRB cybercrime tables plus CERT-In reports for India cyber/security context.
4. Elliptic Bitcoin dataset for blockchain/security graph anomaly detection.
5. UK Police Open Data or Chicago Crimes for incident-level spatiotemporal method development.
6. UNSW-NB15 or CSE-CIC-IDS2018 for security anomaly/XAI baselines.
7. Amazon Employee Access Challenge for access-control XAI if license/access terms are acceptable.

## Dataset Risks

- NCRB public data records reported/registered cases, not true crime incidence.
- FIR registration, underreporting, state practices, and policing intensity can dominate the apparent signal.
- Public NCRB tables are aggregate; do not claim incident-level prediction from them.
- Post-2024 Indian criminal-law category changes may affect time-series continuity.
- Sensitive categories require strong ethical guardrails: women, children, caste/tribe, trafficking, cyber victims, senior citizens, suicide, and custody-related data.
- Global datasets are method benchmarks, not evidence that a model will work in India.

