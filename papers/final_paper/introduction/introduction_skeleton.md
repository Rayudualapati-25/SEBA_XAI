# Introduction Skeleton

Created: 2026-05-16  
Target length: 1200-1600 words after compression

## Working Title

SEBA-XAI: A Secure, Explainable, Blockchain-Audited Access Overlay for Inter-Agency Police Data Sharing in India

## Paragraph 1: Opening Context

India's police and criminal-justice information systems are already digitized at national scale. Use CCTNS and ICJS facts to establish that this is not a greenfield problem. End by saying digital interconnection increases the importance of controlled, accountable data access.

Citation placeholders:

- [PIB-CCTNS-2026]
- [MHA-ICJS-2026]

## Paragraph 2: Baseline Infrastructure

Explain what CCTNS/ICJS already provide: FIR/chargesheet digitization, state data centers, National Data Centre replication, standardized forms/master codes, and ICJS links across police, courts, prisons, forensics, and prosecution. State clearly that the proposed paper complements this infrastructure.

Citation placeholders:

- [PIB-CCTNS-2026]
- [MHA-ICJS-2026]

## Paragraph 3: Sensitive Access Problem

Move from infrastructure to sensitive-record governance. Explain that record requests may involve victim/witness records, juvenile information, cybercrime complaints, forensic reports, and case diary material. A legitimate request depends on role, rank, jurisdiction, case assignment, sensitivity, purpose, time, approval, and credential status.

Citation placeholders:

- [NIST-ABAC-2014]

## Paragraph 4: Three Pillars

Explain the equal role of blockchain, security/access control, and XAI. Blockchain gives tamper-evident audit commitments. ABAC/PBAC gives contextual policy enforcement. XAI gives reviewable allow/deny/escalate justification for officers, approving superiors, and auditors.

Citation placeholders:

- [NIST-BC-AC-2022]
- [FABRIC-2018]
- [NIST-ABAC-2014]
- [XAI-LE-2025]

## Paragraph 5: What Existing Work Misses

Compress related work. Blockchain evidence management exists. Fabric ABAC exists. XAI in high-stakes/law enforcement settings exists. India aggregate crime analytics exists. The missing piece is a reproducible, CCTNS/ICJS-compatible, explainable access-governance overlay evaluated across audit, policy, privacy, and explanation criteria.

Citation placeholders:

- [EVIDENCE-BC-2021]
- [LECHAIN-2021]
- [FABRIC-ABAC-2022]
- [RUDIN-2019]
- [XAI-LE-2025]

## Paragraph 6: Proposed SEBA-XAI

Introduce SEBA-XAI. State that raw records stay off-chain. The ledger stores request, policy, approval, payload-pointer, model, and explanation commitments. ABAC/PBAC evaluates access conditions. XAI artifacts explain model-supported or policy-supported decisions. Human approval remains required for sensitive disclosures.

Citation placeholders:

- design proposal, no citation required except supporting technologies.

## Paragraph 7: Contributions

Use exact bullets:

1. Formulate a CCTNS/ICJS-compatible access-governance problem for sensitive inter-agency police record sharing.
2. Propose SEBA-XAI, an overlay combining permissioned blockchain audit commitments, ABAC/PBAC, off-chain encrypted storage, and XAI artifact logging.
3. Define a reproducible synthetic multi-station workload and evaluation plan for allow, deny, and escalate decisions.
4. Identify evaluation metrics for audit completeness, tamper detection, false allows and denies, metadata leakage, latency, and explanation stability.

## Paragraph 8: Scope And Paper Roadmap

State boundaries: not CCTNS replacement, not deployment, not legal-compliance proof, not raw records on-chain, not individual prediction from public NCRB data. Close with paper organization.

Citation placeholders:

- [NCRB-2023] if mentioning public aggregate data boundary.

## One-Sentence Gap

Existing research has studied digital-policing infrastructure, blockchain evidence management, blockchain access control, ABAC, crime analytics, and XAI separately, but limited work jointly evaluates a CCTNS/ICJS-compatible overlay for auditable, privacy-aware, and explainable sensitive-record access across inter-agency police workflows.

## One-Sentence Contribution

This paper proposes SEBA-XAI, a secure and explainable blockchain-audited overlay that keeps sensitive records off-chain while logging verifiable commitments for requests, policies, approvals, model versions, and explanation artifacts.
