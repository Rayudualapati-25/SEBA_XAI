# Introduction Control Document

Created: 2026-05-16  
Target: IEEE-style Introduction, 1200-1600 words  
Working title: SEBA-XAI: A Secure, Explainable, Blockchain-Audited Access Overlay for Inter-Agency Police Data Sharing in India

## Five-Sentence Explanation

India already has national-scale police and criminal-justice digital infrastructure through CCTNS and ICJS. The research problem is not how to replace these systems, but how to add auditable, privacy-aware, and explainable access governance for sensitive inter-station and inter-agency record requests. SEBA-XAI proposes an overlay where raw records remain off-chain, ABAC/PBAC evaluates contextual access conditions, a permissioned blockchain records audit commitments, and XAI artifacts explain allow, deny, or escalate recommendations. The paper is not an individual crime-prediction paper and does not claim legal compliance or deployment readiness. Its contribution is a measurable architecture and evaluation plan for trustworthy access governance in Indian public-safety data sharing.

## Framing Decision

Use **SEBA-XAI** as the paper identity.

Reason:

- Narrow enough to evaluate within an M.Tech/IEEE paper.
- Directly balances blockchain, security/access control, and XAI.
- Avoids overbroad "entire criminal justice AI governance" claims.

Use **PAX-ICJS++** only in future-work language:

> SEBA-XAI can be viewed as one implementable component of a broader PAX-ICJS++ vision for procedurally accountable AI across interoperable criminal-justice systems.

Do not use PAX-ICJS++ in the title or main contribution list unless the paper scope expands substantially.

## Introduction Paragraph Plan

### Paragraph 1: Opening Motivation

Purpose:

- Establish that India has large-scale digital policing and criminal-justice infrastructure.
- Show why information sharing is a real and current problem.

Evidence:

- PIB CCTNS operational status.
- MHA ICJS page.

Tone:

- Calm, factual, no alarmism.

### Paragraph 2: CCTNS/ICJS As Baseline

Purpose:

- Make clear that the paper complements CCTNS/ICJS.
- Prevent reviewer objection that the paper ignores existing infrastructure.

Must say:

- CCTNS digitizes police processes including FIRs and chargesheets.
- Data is replicated to the National Data Centre.
- ICJS connects police, courts, prisons, forensics, and prosecution.

Must not say:

- CCTNS is absent.
- CCTNS data is public.
- The proposed system replaces CCTNS.

### Paragraph 3: Sensitive Access Governance Problem

Purpose:

- Move from general digitization to the specific research problem.

Core idea:

- Sensitive records need contextual authorization and reviewable disclosure.

Examples:

- FIR details.
- victim/witness information.
- juvenile records.
- forensic reports.
- cybercrime complaints.
- case diary and evidence material.

### Paragraph 4: Three-Pillar Need

Purpose:

- Explain why blockchain, security/access control, and XAI must be treated equally.

Must include:

- Blockchain for tamper-evident audit commitments.
- ABAC/PBAC/security for policy enforcement and confidentiality.
- XAI for reasoned allow/deny/escalate explanations.

### Paragraph 5: Literature Gap

Purpose:

- Show that the pieces exist separately but the combined problem remains open.

Clusters:

- blockchain evidence management;
- blockchain access control;
- ABAC/PBAC;
- XAI in law enforcement;
- India aggregate crime analytics.

Gap sentence:

> Existing work has studied these components separately, but there is limited reproducible work on a CCTNS/ICJS-compatible overlay that jointly evaluates blockchain audit, contextual access control, superior approval, off-chain sensitive storage, XAI artifact logging, and tamper/metadata-leakage risks for inter-agency police data sharing.

### Paragraph 6: Proposed System

Purpose:

- Introduce SEBA-XAI.

Must say:

- raw records stay off-chain;
- ledger stores request, policy, approval, model, and explanation commitments;
- ABAC/PBAC evaluates access conditions;
- XAI explains access decision support;
- final sensitive disclosure remains human-authorized.

### Paragraph 7: Contributions

Contribution bullets:

1. We formulate a CCTNS/ICJS-compatible access-governance problem for sensitive inter-agency police record sharing.
2. We propose SEBA-XAI, an overlay combining permissioned blockchain audit commitments, ABAC/PBAC, off-chain encrypted storage, and XAI artifact logging.
3. We define a reproducible synthetic multi-station workload and evaluation plan for allow, deny, and escalate decisions.
4. We identify evaluation metrics for audit completeness, tamper detection, false allows and denies, metadata leakage, latency, and explanation stability.

Use present tense if this is still a design paper. Use past tense only after implementation and experiments exist.

### Paragraph 8: Scope And Organization

Purpose:

- Close the introduction cleanly and set expectations.

Must say:

- not CCTNS/ICJS replacement;
- not raw data on-chain;
- not legal compliance proof;
- not deployment claim;
- not individual prediction from public NCRB data.

Optional:

- Paper organization sentence.

## Forbidden Phrases

Do not use:

- revolutionary;
- fully secure;
- privacy guaranteed;
- tamper-proof system;
- legally compliant system;
- state of the art;
- predicts criminals;
- replaces CCTNS;
- deployable in Indian policing;
- all police records on blockchain.

Use instead:

- tamper-evident audit;
- privacy-aware design;
- evidence-grounded;
- CCTNS/ICJS-compatible overlay;
- access-governance workflow;
- model-supported, human-reviewed decision.

## Introduction Success Criteria

- 1200-1600 words.
- 8 paragraphs.
- 12-18 strong citations.
- All factual claims mapped to `claim_source_table.csv`.
- Contributions are measurable.
- No unsupported claims.
- Reviewer can identify the novelty by paragraph 5.
