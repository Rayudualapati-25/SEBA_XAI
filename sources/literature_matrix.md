# Literature and Standards Matrix

Generated: 2026-04-24  
Selection rule: include sources that directly inform blockchain, security, XAI, criminal-justice data sharing, or reproducible baselines. Venue details should be rechecked before final citation formatting.

## Blockchain and Data-Sharing Sources

| ID | Source | Year | Type | Relevance |
|---|---:|---:|---|---|
| B1 | Two-Level Blockchain System for Digital Crime Evidence Management, Sensors. https://www.mdpi.com/1424-8220/21/9/3051 | 2021 | paper | Direct crime-evidence management source. Useful for hot/cold blockchain separation, evidence lifecycle, identity, and investigation data. |
| B2 | LEChain: A blockchain-based lawful evidence management scheme for digital forensics. https://doi.org/10.1016/j.future.2020.09.038 | 2021 | paper | Direct digital-forensics and lawful evidence workflow source. Relevant to chain of custody, access control, and privacy. |
| B3 | Design and Implementation of a Digital Evidence Management Model Based on Hyperledger Fabric. https://doi.org/10.3745/JIPS.04.0178 | 2020 | paper | Practical Hyperledger Fabric evidence-management baseline. Useful for implementation architecture and distributed evidence management. |
| B4 | Hyperledger Fabric: A Distributed Operating System for Permissioned Blockchains. https://doi.org/10.1145/3190508.3190538 | 2018 | systems paper | Foundational Fabric source. Supports choosing permissioned blockchain over public chain for known law-enforcement organizations. |
| B5 | Attribute-based access control scheme for data sharing on Hyperledger Fabric. https://doi.org/10.1016/j.jisa.2022.103182 | 2022 | paper | Directly relevant to Fabric plus fine-grained ABAC and encrypted off-chain storage. |
| B6 | Towards Supporting Attribute-Based Access Control in Hyperledger Fabric Blockchain. https://doi.org/10.1007/978-3-031-06975-8_21 | 2022 | paper | Relevant for evaluating Fabric native controls versus stronger ABAC. |
| B7 | Blockchain Based Auditable Access Control for Distributed Business Processes. https://doi.org/10.1109/ICDCS47774.2020.00015 | 2020 | paper | Not policing-specific, but strong for cross-organization auditable access-control design. |
| B8 | Towards accountable and privacy-preserving blockchain-based access control for data sharing. https://doi.org/10.1016/j.jisa.2024.103866 | 2024 | paper | Useful for accountable privacy and deanonymization-under-oversight design patterns. |
| B9 | Blockchain based access control systems: State of the art and challenges. https://doi.org/10.1145/3350546.3352561 and https://arxiv.org/abs/1908.08503 | 2019 | survey | Grounds novelty and open challenges for blockchain access control. |
| B10 | W3C Decentralized Identifiers v1.0. https://www.w3.org/TR/did-1.0/ | 2022 | standard | Relevant to officer, station, device, or agency identity architecture. |
| B11 | W3C Verifiable Credentials Data Model v2.0. https://www.w3.org/TR/vc-data-model/ | 2025 | standard | Relevant to verifiable rank, assignment, authorization, or temporary approval credentials. |

## Security, Privacy, and Governance Sources

| ID | Source | Year | Type | Relevance |
|---|---:|---:|---|---|
| S1 | NIST SP 800-162: Guide to Attribute Based Access Control. https://doi.org/10.6028/NIST.SP.800-162 | 2014, updated 2019 | standard | Authoritative ABAC baseline. Important for non-blockchain comparison. |
| S2 | CJIS Security Policy v5.9.4. https://le.fbi.gov/file-repository/cjis_security_policy_v5-9-4_20231220.pdf/view | 2023 | policy | U.S. criminal-justice security benchmark. Use as requirements inspiration, not India law. |
| S3 | Privacy-Preserving Machine Learning: Methods, Challenges and Directions. https://arxiv.org/abs/2108.04417 | 2021 | survey | Helps distinguish FL, DP, HE, SMPC, access control, and audit logging. |
| S4 | Privacy-preserving attribute-based access control using homomorphic encryption. https://doi.org/10.1186/s42400-024-00323-8 | 2024 | paper | Relevant if access attributes themselves are sensitive. |
| S5 | Digital Personal Data Protection Act, 2023. https://www.indiacode.nic.in/handle/123456789/22037?view_type=browse | 2023 | India law | Governs personal-data handling context. A legal expert must interpret policing exemptions and obligations. |
| S6 | Bharatiya Sakshya Adhiniyam, 2023. https://www.indiacode.nic.in/handle/123456789/20063 | 2023 | India law | Important for electronic evidence and trial context. Requires legal interpretation before system claims. |
| S7 | MHA ICJS page. https://www.mha.gov.in/en/commoncontent/inter-operable-criminal-justice-system-icjs | current page | official system context | Establishes existing integration of police, courts, prisons, forensics, and prosecution. |
| S8 | PIB CCTNS operational police stations release. https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241 | 2026 | official status | States all 17,798 police stations use CCTNS as of 2026-02-01. Critical baseline context. |

## XAI, Fairness, and Policing Sources

| ID | Source | Year | Type | Relevance |
|---|---:|---:|---|---|
| X1 | Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. https://doi.org/10.1038/s42256-019-0048-x | 2019 | paper | Core justification for interpretable baselines in high-stakes policing/criminal justice. |
| X2 | The accuracy, fairness, and limits of predicting recidivism. https://doi.org/10.1126/sciadv.aao5580 | 2018 | paper | Demonstrates importance of simple baselines and careful claims in criminal-justice prediction. |
| X3 | Fair Prediction with Disparate Impact. https://doi.org/10.1089/big.2016.0047 | 2017 | paper | Key fairness impossibility/metric tradeoff source for recidivism-like settings. |
| X4 | Inherent Trade-Offs in the Fair Determination of Risk Scores. https://arxiv.org/abs/1609.05807 | 2017 | paper | Shows fairness criteria tradeoffs when base rates differ. |
| X5 | To Predict and Serve? https://doi.org/10.1111/j.1740-9713.2016.00960.x | 2016 | paper/commentary | Important warning about biased policing data and feedback loops. |
| X6 | Runaway Feedback Loops in Predictive Policing. https://proceedings.mlr.press/v81/ensign18a.html | 2018 | paper | Directly supports feedback-loop ablation and cautious interpretation of reported crime. |
| X7 | Algorithmic prediction in policing: assumptions, evaluation, and accountability. https://doi.org/10.1080/10439463.2016.1253695 | 2016 | paper | Grounds evaluation beyond predictive accuracy. |
| X8 | Dialogue-based XAI for Predictive Policing: a Field Study. https://ceur-ws.org/Vol-4017/paper_03.pdf | 2025 | workshop/field study | Useful for role-specific and dialogue-based explanations with police analysts. |
| X9 | Fundamental considerations for the use of explainable AI in law enforcement. https://doi.org/10.3389/fpos.2025.1605619 | 2025 | paper | Direct law-enforcement XAI source, including stakeholder and automation-bias concerns. |
| X10 | A Secure and Privacy-Preserving Blockchain-Based XAI-Justice System. https://doi.org/10.3390/info14090477 | 2023 | paper | Architecture combining blockchain, privacy, and XAI in justice context. Treat as inspiration until replicated. |
| X11 | Blockchain-based auditing of legal decisions supported by explainable AI and generative AI tools. https://doi.org/10.1016/j.engappai.2023.107666 | 2024 | paper | Relevant to hashing/logging legal decision-support artifacts and XAI outputs. |
| X12 | Data Protection Challenges in AI-Driven Criminal Justice in the EU and India. https://link.springer.com/article/10.1007/s44196-025-01037-6 | 2026 | paper | Strong topic fit for India/EU governance; verify full text before detailed claims. |

## Evidence Gaps

- Direct India-specific blockchain-for-police-station-sharing papers are sparse.
- Most blockchain policing literature is digital evidence, judicial evidence, or generic access control, not operational CCTNS replacement.
- India-specific empirical AI policing evaluations are much thinner than U.S./EU recidivism and predictive-policing literature.
- XAI sources support accountability and reviewability, but they do not prove operational benefit without experiments.

