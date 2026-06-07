# 05 Research Gap Analysis

Generated: 2026-05-12

## What Reviewers Will Consider Already Known

1. India already has digital policing and justice infrastructure through CCTNS/ICJS. Source: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241 and https://www.mha.gov.in/en/commoncontent/icjsncrb-administration
2. Blockchain has already been proposed for digital evidence management and chain of custody. Sources: https://www.mdpi.com/1424-8220/21/9/3051 and https://doi.org/10.1016/j.future.2020.09.038
3. Hyperledger Fabric is already a known permissioned blockchain platform. Source: https://arxiv.org/abs/1801.10228
4. ABAC is already a mature access-control model. Source: https://csrc.nist.gov/pubs/sp/800/162/upd2/final
5. Fabric-plus-ABAC and blockchain access-control research already exist. Source: https://doi.org/10.1016/j.jisa.2022.103182
6. XAI/fairness/predictive-policing limitations are well documented. Sources: https://doi.org/10.1038/s42256-019-0048-x and https://proceedings.mlr.press/v81/ensign18a.html
7. NCRB aggregate crime analytics already exists in India-focused research. Source: https://doi.org/10.1016/j.compenvurbsys.2023.108761

## Weak Research Angles to Reject

### Weak Angle 1: "Put Police Data on Blockchain"

Reject. Blockchain does not automatically provide privacy, correctness, legal admissibility, or data quality. Storing raw FIRs, witness records, victim identities, juvenile records, or forensic records on-chain creates serious confidentiality and retention problems.

### Weak Angle 2: "AI Crime Prediction for India Using NCRB"

Reject as the main contribution. Public NCRB data is aggregate and based on reported/registered cases. It cannot justify individual suspect prediction, station-level operational recommendations, or true-crime-incidence claims.

### Weak Angle 3: "CCTNS Replacement"

Reject. Official evidence shows CCTNS/ICJS are already operational at national scale. A replacement claim is unrealistic for an M.Tech paper and would require access, governance approval, and operational evaluation far beyond this project.

### Weak Angle 4: "XAI Solves Trust"

Reject. XAI can improve reviewability, but explanations can be incomplete, misleading, or sensitive. Recent XAI law-enforcement literature warns that explanation needs differ by stakeholder and automation bias remains a risk. Source: https://doi.org/10.3389/fpos.2025.1605619

## Strong Gap

The publishable gap is:

> Existing work has studied digital policing infrastructure, blockchain evidence management, blockchain access control, ABAC, crime prediction, and XAI largely as separate threads. There is limited reproducible work on a CCTNS/ICJS-compatible secure overlay that jointly evaluates permissioned blockchain audit, ABAC/PBAC enforcement, superior approval, off-chain encryption, XAI explanation artifacts, and tamper/metadata-leakage tests for inter-station and inter-agency sensitive-record access.

## Novel Research Problem Formulation

**Problem statement:**  
How can an intelligent secure overlay support auditable, privacy-aware, and explainable access to sensitive police/criminal-justice records across Indian police stations and agencies, while preserving existing CCTNS/ICJS-style infrastructure and avoiding exposure of raw sensitive records on-chain?

## Proposed Title

**SEBA-XAI: A Secure, Explainable, Blockchain-Audited Access Overlay for Inter-Agency Police Data Sharing in India**

Alternative titles:

1. **An Explainable Permissioned-Blockchain Overlay for Secure Inter-Police Data Sharing in India**
2. **Auditable and Explainable Access Control for Sensitive Criminal-Justice Data: A CCTNS-Compatible Overlay**
3. **Blockchain-Audited ABAC with XAI Justifications for Cross-Station Police Record Access**

## Research Objectives

O1. Design a CCTNS/ICJS-compatible overlay architecture where raw sensitive data stays off-chain and only commitments, approvals, policy versions, and explanation hashes are logged on-chain.

O2. Implement a reproducible synthetic multi-station workload representing officers, stations, jurisdictions, cases, sensitivity levels, approvals, purposes, credentials, and time windows.

O3. Compare centralized RBAC, centralized ABAC/PBAC, signed append-only logs, basic Fabric audit, and Fabric plus ABAC/PBAC plus XAI artifact logging.

O4. Measure authorization correctness, false allows, false denies, latency, throughput, audit completeness, tamper detection, metadata leakage, revocation delay, and explanation stability.

O5. Use public NCRB/BPRD data only for aggregate crime-analysis context and optional XAI demonstration, not for unsupported individual prediction.

## Claimed Novelty Boundaries

The project may claim, if implemented and evaluated:

- A reproducible benchmark for inter-station sensitive-record access decisions inspired by Indian CCTNS/ICJS workflows.
- A combined architecture linking Fabric-style audit commitments, ABAC/PBAC decisions, superior approval, off-chain encryption, and XAI explanation hashes.
- A comparison against centralized and signed-log baselines.
- A structured evaluation of tamper detection, audit reconstruction, metadata leakage, and explanation stability.

The project must not claim yet:

- better crime prediction;
- legal compliance;
- real-world deployability;
- privacy preservation in a formal cryptographic sense;
- fairness;
- SOTA;
- operational benefit to police.

## Final Recommendation

Build the first paper as a **secure systems plus responsible AI paper**, not a pure ML crime-prediction paper. The best venue framing is "trusted AI-enabled access governance for public-safety data." The strongest evaluation is a synthetic but reproducible access-control workload plus public India aggregate context, not a weak proprietary or unverified FIR dataset.
