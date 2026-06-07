# 11 Final Paper Outline

Generated: 2026-05-12

## Recommended Paper Direction

Write a secure systems and responsible AI paper:

**SEBA-XAI: A Secure, Explainable, Blockchain-Audited Access Overlay for Inter-Agency Police Data Sharing in India**

Do not write a generic "crime prediction using AI and blockchain" paper.

## Title Options

1. **SEBA-XAI: A Secure, Explainable, Blockchain-Audited Access Overlay for Inter-Agency Police Data Sharing in India**
2. **Auditable and Explainable Access Control for Sensitive Criminal-Justice Data: A CCTNS-Compatible Overlay**
3. **Blockchain-Audited ABAC with Explainable Access Decisions for Cross-Station Police Record Sharing**
4. **An Explainable Permissioned-Blockchain Overlay for Secure Inter-Police Data Sharing in India**
5. **Secure and Explainable Inter-Agency Police Data Access Using Permissioned Blockchain and ABAC**

Best choice: option 1. It signals security, XAI, audit, and India without claiming deployment.

## Draft Abstract

India's CCTNS and ICJS initiatives provide a national digital foundation for police and criminal-justice information exchange, but sensitive inter-station and inter-agency data sharing still raises questions of authorization, auditability, privacy, and explainability. This paper proposes SEBA-XAI, a CCTNS/ICJS-compatible secure overlay for sensitive police-record access. The design keeps raw records off-chain, enforces role- and attribute/policy-based access control, records permissioned-blockchain audit commitments for requests, policies, approvals, model versions, and explanation artifacts, and provides role-specific explanations for allow, deny, and escalate decisions. The proposed evaluation uses a reproducible synthetic multi-station workload inspired by Indian policing workflows, compares centralized RBAC, centralized ABAC/PBAC, signed append-only logs, basic permissioned blockchain audit, and blockchain-audited ABAC/PBAC with XAI logging, and measures false allows, false denies, audit completeness, tamper detection, latency, throughput, metadata leakage, and explanation stability. Public NCRB and BPRD datasets are used only for aggregate contextual analysis, not individual prediction. The expected contribution is a measurable architecture and benchmark for auditable, privacy-aware, explainable access governance in public-safety data sharing.

## Problem Statement

Existing India police and justice infrastructure supports large-scale digitization and inter-agency integration, but a research gap remains in auditable, explainable, privacy-aware access governance for sensitive cross-station and cross-agency record requests. The problem is to design and evaluate an overlay that can reconstruct who requested what, under which policy, with what model/explanation support, who approved it, and whether the audit trail was tampered with.

## Objectives

- Design a CCTNS/ICJS-compatible overlay, not a replacement.
- Keep sensitive raw records off-chain.
- Enforce RBAC and ABAC/PBAC access decisions.
- Record tamper-evident audit commitments on a permissioned blockchain.
- Add XAI artifacts for access decisions and human approval.
- Compare against centralized and signed-log baselines.
- Evaluate tamper detection, false allow/deny, latency, metadata leakage, and explanation stability.

## Novelty Claims

Potentially claim after implementation:

- A reproducible benchmark for sensitive inter-station access-request workflows.
- An integrated overlay combining permissioned blockchain audit, ABAC/PBAC, off-chain encryption, superior approval, and XAI explanation hashes.
- A comparative evaluation against centralized RBAC/ABAC and signed append-only logs.
- A structured audit-reconstruction and metadata-leakage evaluation for public-safety access governance.

Do not claim:

- CCTNS replacement;
- real deployment;
- legal compliance;
- SOTA crime prediction;
- formal privacy;
- fairness;
- operational policing benefit.

## IEEE-Style Paper Structure

### I. Introduction

- Motivation: sensitive inter-agency police data sharing.
- India context: CCTNS/ICJS exist.
- Problem: auditability, privacy, access governance, and explainability.
- Contributions and non-claims.

### II. Background and Related Work

- CCTNS/ICJS and Indian digital policing context.
- Blockchain for digital evidence and access control.
- ABAC/PBAC and privacy-preserving access control.
- XAI/fairness in law enforcement and high-stakes decisions.
- India aggregate crime analytics and dataset limitations.

### III. Problem Formulation and Threat Model

- Actors: officers, superiors, stations, agencies, auditors, attackers.
- Access decisions: allow, deny, escalate.
- Sensitive records and approval workflows.
- Threats: insider misuse, tampering, revoked credentials, replay, metadata leakage.

### IV. SEBA-XAI Architecture

- Existing systems layer.
- Access gateway.
- Policy decision layer.
- AI risk/anomaly layer.
- XAI layer.
- Blockchain audit layer.
- Off-chain encrypted storage.
- Audit dashboard.

### V. Methodology

- Synthetic workload generator.
- Policy oracle.
- Baselines.
- Proposed variants.
- Ablations.
- Public aggregate NCRB/BPRD contextual analysis.

### VI. Evaluation

- Authorization correctness.
- Audit completeness and tamper detection.
- Latency/throughput/storage overhead.
- Metadata leakage.
- XAI completeness/stability.
- Ablation results.

### VII. Ethics, Security, and Legal Discussion

- DPDP and Bharatiya Sakshya context.
- No raw data on-chain.
- No individual prediction from public aggregate data.
- Human approval and accountability.
- Misuse risks and limitations.

### VIII. Limitations and Future Work

- Synthetic workload limitations.
- No real CCTNS/ICJS access.
- No legal compliance proof.
- No formal privacy proof.
- Need user study for explanation usefulness.
- Need real stakeholder validation.

### IX. Conclusion

- Summarize measured findings only.
- Re-state safe, narrow contribution.

## Recommended Figures

1. CCTNS/ICJS-compatible overlay architecture.
2. Sensitive access-request workflow.
3. Blockchain audit event schema.
4. Baseline vs proposed variants.
5. Threat/tamper injection flow.
6. XAI artifact lifecycle.

## Recommended Tables

1. Literature matrix.
2. Dataset suitability matrix.
3. Security requirements and design mapping.
4. Baselines and proposed variants.
5. Metrics definitions.
6. Ablation matrix.
7. Risk and mitigation table.

## Recommended Venues

Realistic M.Tech/IEEE-level targets:

- IEEE International Conference on Blockchain and Cryptocurrency (ICBC), if the implementation emphasizes blockchain/audit.
- IEEE International Conference on Distributed Ledger Technologies (ICDLT), if the blockchain layer is strong.
- IEEE COINS, because its scope covers IoT, cybersecurity, AI, and next-generation systems.
- Privacy, Security and Trust (PST), if the paper emphasizes access control, privacy, and trust.
- IEEE BigData workshops/special sessions, if the aggregate NCRB/BPRD analysis becomes stronger.
- IEEE Technology and Society Magazine or IEEE Transactions on Technology and Society, if the contribution is framed around responsible public-safety technology and governance.
- Journal of Information Security and Applications, if the access-control/security evaluation is rigorous.

Avoid top-tier security venues for the first version unless there is a genuinely novel protocol or formal proof. The current best path is a strong applied systems paper with transparent limitations.

## What Must Be Completed Before Writing Results

- Implement synthetic workload generator.
- Implement at least RBAC, ABAC/PBAC, signed-log, basic Fabric-style audit, and Fabric+ABAC/PBAC+XAI variants.
- Run ablations.
- Save configs, logs, metrics, tables, and plots.
- Update iteration report.
- Write limitations and negative results.

## Final Supervisor Recommendation

Proceed with **SEBA-XAI as an auditable access-governance overlay**. Keep crime prediction secondary and aggregate only. The strongest research contribution is the integration and evaluation of blockchain audit, access control, privacy-aware storage, and explanation artifacts in a realistic Indian public-safety data-sharing context.
