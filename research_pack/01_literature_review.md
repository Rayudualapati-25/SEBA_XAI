# 01 Literature Review

Generated: 2026-05-12  
Evidence status: source-grounded review for research direction. Some cited papers still need full-text extraction before final IEEE references.

## 1. Existing Indian Digital Policing Context

The baseline is not a manual or disconnected policing system. India has CCTNS and ICJS-style infrastructure. PIB reported on 2026-03-11 that all 17,798 police stations were using CCTNS as of 2026-02-01, with FIRs, chargesheets, and related police data entered in state data centers, replicated near-real-time to the National Data Centre, and searchable for crime, criminal, and property information. The same release notes standardized investigation forms and master codes for states, districts, police stations, acts, and sections. Source: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241

MHA describes ICJS as integrating Police/CCTNS, Courts/e-Courts, Jails/e-Prisons, Forensics/e-Forensics, and Prosecution/e-Prosecution with a Data Sharing Matrix. Source: https://www.mha.gov.in/en/commoncontent/icjsncrb-administration

**Implication:** the paper must position the contribution as an overlay for auditable authorization, provenance, privacy, and explainable review. It must not claim to create the first national data-sharing system for Indian policing.

## 2. Blockchain for Evidence and Access Governance

The most relevant blockchain literature is about digital evidence management, chain of custody, and auditable access control. Two-Level Blockchain System for Digital Crime Evidence Management (Sensors, 2021) and LEChain (Future Generation Computer Systems, 2021) support the idea that blockchain can record evidence lifecycle events and make tampering harder to hide. They do not prove that raw police records should be placed on-chain. Sources: https://www.mdpi.com/1424-8220/21/9/3051 and https://doi.org/10.1016/j.future.2020.09.038

Hyperledger Fabric is a strong implementation candidate because Fabric is designed for permissioned organizations, modular consensus, and membership identities rather than anonymous public-chain participation. Source: https://arxiv.org/abs/1801.10228

Blockchain-based access-control surveys and NISTIR 8403 show that blockchain can help with auditability, tamper resistance, and decentralization, but it also creates challenges around scalability, privacy, governance, and policy complexity. Sources: https://arxiv.org/abs/1908.08503 and https://doi.org/10.6028/NIST.IR.8403

**Gap:** many papers cover digital evidence or generic blockchain access control, but few evaluate a CCTNS/ICJS-compatible inter-station access workflow with ABAC, superior approval, off-chain encryption, and XAI explanation logging as equal components.

## 3. Security, Privacy, and Access Control

NIST SP 800-162 defines ABAC as authorization based on subject, object, action, and environmental attributes evaluated against policies. It explicitly fits information-sharing scenarios where control must be maintained across organizational boundaries. Source: https://csrc.nist.gov/pubs/sp/800/162/upd2/final

Fabric plus ABAC papers show that chaincode can enforce fine-grained access policies and that encrypted off-chain storage, such as IPFS-style storage with on-chain hashes, is a common pattern. Source: https://doi.org/10.1016/j.jisa.2022.103182

Newer privacy-preserving blockchain access-control work, including accountable/privacy-preserving frameworks, tries to reduce exposure of permissions, identities, and attributes. Source: https://doi.org/10.1016/j.jisa.2024.103866

Privacy-preserving ML literature separates differential privacy, federated learning, secure multiparty computation, homomorphic encryption, and trusted execution. Source: https://arxiv.org/abs/2108.04417. Differentially private deep learning is technically possible but adds accuracy/privacy trade-offs and is not automatically suitable for every police workflow. Source: https://arxiv.org/abs/1607.00133

**Gap:** most access-control papers evaluate technical access logic but not police-specific sensitive-record workflows, explanation artifacts, superior approval, and audit reconstruction under realistic threat cases.

## 4. XAI in Policing and High-Stakes Decisions

Rudin argues that high-stakes decisions should prefer interpretable models where possible rather than black-box models plus fragile post-hoc explanations. Source: https://doi.org/10.1038/s42256-019-0048-x

Criminal-justice risk tools have known limitations. Dressel and Farid showed that simple baselines can rival more complex recidivism tools under some conditions, which is a warning against overclaiming AI sophistication. Source: https://doi.org/10.1126/sciadv.aao5580

Fairness literature shows that accuracy, calibration, false-positive rates, and false-negative rates can conflict when base rates differ. Sources: https://doi.org/10.1089/big.2016.0047 and https://arxiv.org/abs/1609.05807

Predictive-policing literature warns that reported police data can create feedback loops: policing more in an area can generate more observed incidents, which then reinforces model attention to that area. Source: https://proceedings.mlr.press/v81/ensign18a.html

Recent law-enforcement XAI work emphasizes stakeholder-specific explanations, AI literacy, automation-bias risk, and collaboration among law enforcement, academia, and industry. Source: https://doi.org/10.3389/fpos.2025.1605619

**Gap:** XAI is usually discussed for crime prediction or investigative support, not as a first-class logged artifact in an auditable inter-agency access-control workflow.

## 5. India-Specific Crime Analytics Literature

India public crime-analysis work commonly uses NCRB aggregate data. Examples include spatial/regression analysis of crimes against women using NCRB data and recent India-focused forecasting/XAI studies. Sources: https://doi.org/10.1016/j.compenvurbsys.2023.108761 and https://doi.org/10.1109/UPCON62832.2024.10983398

These studies are useful baselines for aggregate trend modeling, but they do not solve access governance, classified-record disclosure, inter-station approvals, or privacy-preserving audit.

**Gap:** the proposed contribution should not compete mainly with crime forecasting papers. It should use aggregate crime modeling only as a secondary demonstration of XAI and careful public-data use.

## 6. What Is Already Published

- Blockchain has been applied to digital evidence lifecycle and chain of custody.
- Hyperledger Fabric has been evaluated as a permissioned blockchain platform.
- ABAC and Fabric-plus-ABAC designs already exist.
- XAI and fairness concerns in criminal justice are well established.
- India NCRB-based aggregate crime analyses already exist.
- CCTNS/ICJS already provide official Indian criminal-justice interoperability context.

## 7. Remaining Publishable Gap

The gap is a **CCTNS/ICJS-compatible overlay architecture and reproducible benchmark** that jointly evaluates:

- permissioned blockchain audit commitments;
- ABAC/PBAC access decisions;
- superior-approval workflow for sensitive records;
- off-chain encrypted sensitive data;
- XAI artifacts hashed into the audit log;
- tamper, revocation, insider misuse, metadata leakage, and explanation-stability tests.

This gap is credible because it is narrower than "AI policing", more realistic than "blockchain replaces CCTNS", and measurable without access to restricted real police records.

## Source Quality Notes

- Strong: official India sources, NIST standards, peer-reviewed systems/security/XAI papers.
- Moderate: recent conference/workshop law-enforcement XAI papers and domain-specific applied papers.
- Weak: Kaggle mirrors without provenance, private legal-data APIs, current-affairs summaries, and generic crime-prediction papers without reproducibility.
- Rejected as primary evidence: blogs, political commentary, Reddit claims, and any paper that reports performance without reproducible dataset/split details.
