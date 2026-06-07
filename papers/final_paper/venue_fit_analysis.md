# Venue Fit Analysis for SEBA-XAI

Date: 2026-06-05

## Research Framing Used

The paper is framed as a security and explainable-AI evaluation paper:

> SEBA-XAI is a secure, explainable, blockchain-audited access-governance framework for CCTNS/ICJS-style inter-agency police data sharing. It combines ABAC/PBAC policy checks, tamper-evident audit commitments, off-chain sensitive records, and XAI traces for allow, deny, and escalate access decisions.

The paper should not be submitted as a crime-prediction paper, a live CCTNS deployment paper, or a paper claiming that raw police records are stored on blockchain.

## Best Journal Targets

| Rank | Venue | Best Framing | Fit | Risk |
|---:|---|---|---|---|
| 1 | Journal of Information Security and Applications | Applied information-security and access-governance evaluation | Very strong | Needs clear security contribution, baselines, and reproducible results |
| 2 | IEEE Access | Interdisciplinary applied system with security, blockchain, XAI, and public-sector context | Strong and practical | Broad venue; paper must be polished and evidence-heavy |
| 3 | IEEE Transactions on Technology and Society | Governance, accountability, public-sector AI, technology-society impact | Strong if socio-technical framing is emphasized | Less suitable if the paper is mostly code/results |
| 4 | Forensic Science International: Digital Investigation | Digital evidence integrity, provenance, auditability, criminal-justice records | Strong if framed around audit/provenance | Less suitable if not connected clearly to digital investigation or evidence |
| 5 | IEEE Transactions on Privacy | Privacy engineering and access to sensitive records | Good if metadata leakage/privacy analysis is strengthened | Needs deeper privacy model than current prototype |
| 6 | Blockchain: Research and Applications | Permissioned blockchain audit and law-enforcement/public-sector blockchain application | Good | Blockchain contribution must be central and technically strong |
| 7 | Government Information Quarterly | Digital government, public-sector information flows, accountability, privacy | Good for policy/governance version | Needs stronger government-administration contribution, less technical prototype emphasis |
| 8 | AI and Ethics | AI accountability, XAI, law, privacy, security, governance | Good for ethics/XAI version | Weaker for experimental security paper unless ethical analysis is central |
| 9 | IEEE Transactions on Dependable and Secure Computing | Dependable and secure system evaluation | Ambitious | Needs much stronger formal/system-security novelty |
| 10 | IEEE Transactions on Information Forensics and Security | Information forensics/security and reproducible research | Ambitious | Likely too selective unless the forensic/audit method is technically novel |

## Safest Submission Path

1. Journal of Information Security and Applications
2. IEEE Access
3. Forensic Science International: Digital Investigation

These venues fit the current paper best because the current evidence is an applied security prototype with audit, access control, XAI, tamper testing, latency, and metadata-exposure evaluation.

## Ambitious Submission Path

1. IEEE Transactions on Dependable and Secure Computing
2. IEEE Transactions on Information Forensics and Security
3. Blockchain: Research and Applications

These should be attempted only if the paper is strengthened with a clearer formal threat model, stronger ablations, reproducible package, and sharper technical novelty.

## Conference Targets

| Venue | Fit | Recommended Use |
|---|---|---|
| IEEE ICBDS 2026 | Very strong for blockchain, distributed security, access control, provenance, experiments | Good India/IEEE conference target |
| IEEE ICDLT 2026 | Strong for DLT auditability, compliance, security, privacy, AI/blockchain integration | Good if blockchain angle is central |
| ICEGOV 2026 | Strong for digital governance, trustworthy AI, privacy, cybersecurity, public-sector infrastructure | Good if framed as public-sector digital governance |
| dg.o 2026 | Strong for digital government research, cybersecurity and public values, privacy | Good for management/policy + technical evaluation paper |

## Recommendation

The first submission should not target a pure AI journal or pure crime-prediction venue. The best framing is:

> A prototype-based information-security paper on explainable, policy-aware audit for sensitive inter-agency police data access.

The best first target is **Journal of Information Security and Applications**. The best IEEE-friendly practical target is **IEEE Access**. The strongest conference target is **IEEE ICBDS 2026**.

## Cost Sorting: Paid, Free, and Conditional

Important distinction:

- **Free for author** usually means subscription/traditional publishing. The paper may not be freely readable by everyone.
- **Open access** usually means the paper is freely readable by everyone, but the author/institution often pays an APC.
- Fees can change, so final APC must be checked again at submission time.

### Best Free-for-Author Journal Routes

| Venue | Cost Category | Notes |
|---|---|---|
| Journal of Information Security and Applications | Free if subscription route is chosen | Best overall target. Open access is optional and paid; subscription route has no open-access publication fee. |
| Forensic Science International: Digital Investigation | Free if subscription route is chosen | Good digital-forensics/audit target. Open access is optional and paid. |
| AI and Ethics | Free if subscription route is chosen | Good ethics/XAI governance backup. Open access is optional and paid. |
| Government Information Quarterly | Free if subscription route is chosen | Good governance backup, but the technical-security fit is weaker. Open access is optional and expensive. |
| IEEE Transactions on Technology and Society | Usually free under traditional/hybrid subscription route | Good IEEE governance target. Optional open access has APC; possible overlength charges must be checked. |
| IEEE Transactions on Dependable and Secure Computing | Usually free under traditional/hybrid subscription route | Very ambitious. Optional open access has APC; possible overlength charges must be checked. |
| IEEE Transactions on Information Forensics and Security | Usually free under traditional/hybrid subscription route | Very ambitious. Optional open access has APC; possible overlength charges must be checked. |

### Mandatory Paid / Open-Access Journal Routes

| Venue | Cost Category | Known/Current Fee Signal |
|---|---|---|
| IEEE Access | Mandatory APC | Gold open access; IEEE Access lists USD 2,160 plus applicable taxes. |
| IEEE Transactions on Privacy | Mandatory APC | Fully open access. IEEE source shows APC around USD 2,075-2,160 depending on page/list date; verify at submission. |
| AI and Ethics, if choosing open access | Optional APC | Current APC listed as GBP 2,390 / USD 3,290 / EUR 2,690. |
| Journal of Information Security and Applications, if choosing open access | Optional APC | Elsevier page lists USD 2,970 excluding taxes. |
| Forensic Science International: Digital Investigation, if choosing open access | Optional APC | Elsevier page lists USD 2,950 excluding taxes. |
| Government Information Quarterly, if choosing open access | Optional APC | Elsevier page lists USD 4,800 excluding taxes. |

### Conditional / Possibly Free Open-Access Routes

| Venue | Cost Category | Notes |
|---|---|---|
| Blockchain: Research and Applications | Sponsored open access at present | Elsevier page lists USD 1,600 for full articles, but also states the APC is covered by Zhejiang University Press for accepted articles. Verify before submission. |
| ACM Digital Government: Research and Practice | Conditional open access | ACM states all ACM publications are open access from 2026. If the corresponding author is at an ACM Open institution, publication can be at no cost; otherwise 2026 APC applies. |

### Conferences

Conferences are not "free" in the same sense as journals. Even if there is no APC, accepted papers usually require at least one author registration.

| Venue | Expected Cost Category |
|---|---|
| IEEE ICBDS 2026 | Paid author registration expected |
| IEEE ICDLT 2026 | Paid author registration expected |
| ICEGOV 2026 | Paid author registration expected |
| dg.o 2026 | Paid author registration expected; ACM open-access APC may depend on ACM Open/institutional eligibility |

### Practical Recommendation If Budget Is Low

Submit first to **Journal of Information Security and Applications** using the subscription route. It is the best fit and does not require an open-access publication fee under the traditional route.

If an IEEE venue is required and budget is low, avoid IEEE Access because it is mandatory paid open access. Prefer a hybrid IEEE Transactions venue only if the supervisor agrees the paper is strong enough and if overlength charges can be avoided.

## Source Notes

- IEEE Access describes itself as a multidisciplinary, online-only, open-access IEEE journal for original research and development across IEEE fields, with rapid peer review and APC-supported publishing: https://ieeeaccess.ieee.org/
- IEEE Transactions on Technology and Society publishes research on interactions among technology, science, and society, including ethical, professional, social responsibility, policy, regulation, public impact, and evidence-supported interdisciplinary work: https://technologyandsociety.org/transactions/scope/
- Journal of Information Security and Applications covers original research and practice-driven information-security applications, including authentication/access control, anonymity/privacy, cryptographic protection, digital forensics, and security management/policies: https://www.sciencedirect.com/journal/journal-of-information-security-and-applications
- Computers & Security is security/audit/control focused, but its current scope explicitly excludes blockchain as a principal cryptology component and has a moratorium on AI/ML-significant submissions, so it is not recommended for this paper: https://www.sciencedirect.com/journal/computers-and-security
- Forensic Science International: Digital Investigation covers crime/security in the computerized world, especially digital evidence, provenance, integrity, and authenticity: https://www.sciencedirect.com/journal/forensic-science-international-digital-investigation
- Government Information Quarterly focuses on policy, information technology, government, public information flows, privacy, security, transparent/accountable government, and digital government practice: https://www.sciencedirect.com/journal/government-information-quarterly
- Blockchain: Research and Applications covers blockchain theory/applications, security/privacy, permissioned blockchains, regulation/law enforcement, usability, and legal/ethical/societal aspects: https://www.sciencedirect.com/journal/blockchain-research-and-applications
- AI and Ethics covers ethical, regulatory, policy, law, legal technology, privacy/security, and society-facing AI issues: https://link.springer.com/journal/43681/aims-and-scope
- IEEE Transactions on Privacy covers privacy and data protection, including design, implementation, testing, validation, architectures, infrastructures, case studies, and applied privacy problems: https://ieeesystemscouncil.org/publication/transactions-privacy
- IEEE Transactions on Dependable and Secure Computing covers design, modeling, evaluation, measurement, and simulation for dependable and secure systems without compromising performance: https://www.computer.org/digital-library/journals/tq/cfp-dependable-secure-computing
- IEEE Transactions on Information Forensics and Security covers technologies and applications relating to information forensics, information security, biometrics, surveillance, and related systems, and encourages reproducible research: https://signalprocessingsociety.org/publications-resources/ieee-transactions-information-forensics-and-security/about-transactions
- ICEGOV 2026 focuses on trustworthy digital governance, responsible AI, privacy, cybersecurity, digital public infrastructure, and measurable governance outcomes: https://www.icegov.org/2026/workflow/
- dg.o 2026 accepts research papers on digital government topics and includes tracks on cybersecurity, public values, resilient technologies, privacy, and digital autonomy: https://dgsociety.org/dgo-2026/call-for-papers/
- IEEE ICDLT 2026 covers DLT/blockchain security, privacy, auditability, compliance, benchmarking, and AI/blockchain integration: https://blockchainconfluence.pt/
- IEEE ICBDS 2026 includes blockchain, distributed systems security, access control, provenance with blockchain, AI/ML for privacy and security, and experiments/simulation/tools: https://icbds.ieeepunesection.org/
