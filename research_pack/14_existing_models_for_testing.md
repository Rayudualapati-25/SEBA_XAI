# 14 Existing Models For Testing

Checked: 2026-05-17  
Purpose: Identify real external systems, papers, and prototypes that can inform or test the SEBA-XAI implementation.  
Evidence boundary: This file does not claim that an exact Indian CCTNS/ICJS-compatible blockchain-security-XAI model already exists. The scan found close components, not a complete match.

## Executive Finding

No mature, public, full-stack model was found that simultaneously covers:

- Indian police or CCTNS/ICJS-style inter-agency sharing;
- fine-grained security/privacy/access control for sensitive crime records;
- blockchain-backed audit/provenance;
- explainable AI for access-request or decision justification;
- runnable public code and reproducible experiments.

The closest usable direction is to combine:

1. a BAXDT-style explainable decision trace;
2. a legal-decision blockchain audit pattern;
3. LEChain/two-level crime-evidence blockchain architecture;
4. our own synthetic multi-station access-control workload.

This supports SEBA-XAI as a legitimate research gap rather than a duplicate of an existing system.

## Shortlist Ranking

| Rank | System or paper | Fit for SEBA-XAI | Code status | Recommended use |
|---:|---|---|---|---|
| 1 | Blockchain-assisted explainable decision traces (BAXDT) | Very high for XAI artifact hashing and decision trace design | Paper claims open source, but repository URL not verified from accessible metadata | Rebuild/adapt the decision-trace idea locally |
| 2 | Blockchain-based auditing of legal decisions supported by XAI and generative AI | Very high for legal AI audit pattern | No public repo found in accessible metadata | Use as closest conceptual and evaluation precedent |
| 3 | LEChain | High for lawful evidence lifecycle, privacy, access control, blockchain | Public GitHub located | Inspect and adapt evidence/access-control workflow ideas |
| 4 | Two-Level Blockchain System for Digital Crime Evidence Management | High for police/prosecutor/court blockchain architecture | No public repo found | Borrow hot/cold blockchain split and consortium design |
| 5 | User authentication and access control to blockchain-based forensic log data | Medium for access control and forensic audit | Code only on request per paper metadata | Borrow RBAC/ABAC and formal verification ideas |
| 6 | BlendSPS | Medium for public-safety blockchain microservices | Public GitHub located | Inspect microservice/blockchain prototype patterns |
| 7 | Secure and privacy-preserving blockchain-based XAI-Justice System | Medium for justice-domain framing | Conceptual; no empirical prototype | Cite as related vision, not as implementation baseline |
| 8 | Blockchain for explainable and trustworthy AI | Medium for general XAI+blockchain theory | Conceptual | Cite for general design rationale only |

## Candidate 1: BAXDT

Full title: Blockchain-assisted explainable decision traces (BAXDT): An approach for transparency and accountability in artificial intelligence systems  
Year: 2025  
Source: https://www.sciencedirect.com/science/article/pii/S0950705125014418  
DOI: https://doi.org/10.1016/j.knosys.2025.114402

### Components Present

- Explainable AI decision traces.
- SHAP-based explanations.
- Explanation Density Metric based on cumulative SHAP contribution.
- Cryptographic hashing of explanation and decision context.
- Blockchain anchoring of trace commitments.
- Model and dataset metadata in the trace.
- Streamlit-style verification/query interface according to the abstract metadata.

### What It Proves

BAXDT is strong evidence that blockchain-backed XAI decision traces are publishable and testable. It gives SEBA-XAI a technical pattern for connecting model outputs, explanations, metadata, and immutable audit commitments.

### What It Does Not Prove

- It is not police-specific.
- It does not model CCTNS/ICJS or Indian inter-agency workflows.
- It does not appear, from accessible metadata, to include criminal-justice chain-of-custody roles.
- The paper metadata says open source, but the repository URL was not verified during this scan.

### How To Use In SEBA-XAI

Rebuild the usable idea, not the exact domain:

```text
DecisionTrace = {
  request_id,
  subject_attributes_hash,
  object_attributes_hash,
  action,
  environment_attributes_hash,
  policy_version,
  model_version,
  decision,
  confidence_or_score,
  explanation_summary,
  explanation_features,
  explanation_metric,
  timestamp,
  trace_hash
}
```

For our paper, the explanation should explain `allow`, `deny`, or `escalate` decisions for access requests, not criminal guilt or suspect risk.

## Candidate 2: Blockchain-Based Auditing Of Legal Decisions With XAI And Generative AI

Full title: Blockchain-based auditing of legal decisions supported by explainable AI and generative AI tools  
Year: 2024  
Source: https://livrepository.liverpool.ac.uk/3179806/  
DOI: https://doi.org/10.1016/j.engappai.2023.107666

### Components Present

- Blockchain audit trail for AI-assisted legal decisions.
- Explainable AI artifacts.
- Generative AI in legal decision support.
- Evaluation using Ethereum and Hyperledger Fabric according to the agent scan.
- Legal case-study framing.

### What It Proves

This is one of the closest papers to our research direction because it treats AI outputs and explanations as audit-relevant legal artifacts. It supports the argument that legal/public-sector AI decisions need verifiable reasoning history, not just model accuracy.

### What It Does Not Prove

- It is not about police records or evidence sharing.
- It does not solve classified record access control.
- It does not replace the need for ABAC/PBAC policy enforcement.
- No public implementation was found in accessible metadata.

### How To Use In SEBA-XAI

Use this as a direct related-work anchor for:

- why XAI artifacts should be auditable;
- why blockchain is useful for post-hoc review;
- why full explanations should stay off-chain while hashes or commitments go on-chain;
- why Fabric-style permissioned evaluation is relevant.

## Candidate 3: LEChain

Full title: LEChain: A blockchain-based lawful evidence management scheme for digital forensics  
Year: 2021  
Source: https://www.sciencedirect.com/science/article/pii/S0167739X1933167X  
PDF mirror located during scan: https://spritz.math.unipd.it/datasets/locard_pubs/LEChain.pdf  
DOI: https://doi.org/10.1016/j.future.2020.09.038  
Code: https://github.com/SopmmmodII/LEChain

### Components Present

- Lawful evidence lifecycle.
- Police investigation to court flow.
- Consortium blockchain.
- Fine-grained access control using CP-ABE.
- Witness privacy and juror privacy mechanisms.
- Evidence hash upload while evidence remains with the police department.

### What It Proves

LEChain is strong evidence that criminal-justice evidence workflows can be modeled with blockchain, privacy, and access-control mechanisms.

### What It Does Not Prove

- It does not include XAI.
- It is digital-forensics/evidence-management focused, not access-request justification.
- Its prototype is not evidence of operational police deployment.

### How To Use In SEBA-XAI

Use LEChain as the most relevant police/legal blockchain baseline. For implementation, inspect:

- evidence lifecycle states;
- access phases;
- attribute-based access assumptions;
- what is hashed on-chain versus stored off-chain;
- smart-contract abstractions that can be simplified for our simulator.

Do not copy its scope wholesale. SEBA-XAI should focus on access governance and explainability, not court voting or full digital-evidence lifecycle replacement.

## Candidate 4: Two-Level Blockchain System For Digital Crime Evidence Management

Full title: Two-Level Blockchain System for Digital Crime Evidence Management  
Year: 2021  
Source: https://www.mdpi.com/1424-8220/21/9/3051  
DOI: https://doi.org/10.3390/s21093051

### Components Present

- Digital crime evidence management.
- Consortium among police, prosecutors, courts, cyber analysis teams, and related agencies.
- Hyperledger Fabric implementation.
- Hot blockchain for identity/investigation information.
- Cold blockchain for large digital evidence videos.

### What It Proves

The paper supports the architectural idea that not all evidence-related data should be handled in one ledger. It also supports consortium-chain modeling for criminal-justice institutions.

### What It Does Not Prove

- No XAI layer.
- No public code found during this scan.
- Its cold-chain video storage is not directly appropriate for sensitive Indian police records.

### How To Use In SEBA-XAI

Borrow the separation principle:

- hot path: request, policy, approval, identity, audit metadata;
- cold path: encrypted record pointers, payload hashes, evidence artifacts, explanation artifacts.

For our first simulator, this becomes a two-store abstraction rather than full two-ledger Fabric deployment.

## Candidate 5: User Authentication And Access Control To Blockchain-Based Forensic Log Data

Full title: User authentication and access control to blockchain-based forensic log data  
Year: 2023  
Source: https://link.springer.com/article/10.1186/s13635-023-00142-3  
DOI: https://doi.org/10.1186/s13635-023-00142-3

### Components Present

- Blockchain-based forensic logs.
- Authentication.
- Access control.
- RBAC/ABAC-style logic.
- Edge-network setting.
- Protocol verification using AVISPA according to accessible paper metadata.

### What It Proves

This paper is useful for security rigor. It supports the idea that access-control protocols and forensic logs should be evaluated separately from AI model accuracy.

### What It Does Not Prove

- No XAI.
- No police/CCTNS/ICJS setting.
- No public repo verified.

### How To Use In SEBA-XAI

Use this for the security baseline and threat-model discussion:

- user authentication;
- attribute-based authorization;
- forensic log integrity;
- formal or semi-formal protocol checking as future work.

## Candidate 6: BlendSPS

Full title: BlendSPS: A BLockchain-ENabled Decentralized Smart Public Safety System  
Year: 2020  
Source: https://www.mdpi.com/2624-6511/3/3/47  
DOI: https://doi.org/10.3390/smartcities3030047  
Code: https://github.com/samuelxu999/Research/tree/master/Security/py_dev/BlendSPS/

### Components Present

- Public-safety system architecture.
- Blockchain-backed security service.
- Microservices.
- Ethereum and Tendermint prototype according to paper metadata.
- Edge/fog/cloud public-safety context.

### What It Proves

BlendSPS is evidence that public-safety blockchain prototypes can be implemented and evaluated as modular services.

### What It Does Not Prove

- It is surveillance/IoT-centered, not classified police records.
- It does not include XAI.
- It does not solve India-specific inter-agency access governance.

### How To Use In SEBA-XAI

Use only for implementation architecture inspiration:

- modular services;
- blockchain service boundary;
- edge/public-safety threat assumptions.

It should not be a central related-work claim for XAI or police record governance.

## Candidate 7: Secure And Privacy-Preserving Blockchain-Based XAI-Justice

Full title: A Secure and Privacy-Preserving Blockchain-Based XAI-Justice System  
Year: 2023  
Source: https://www.mdpi.com/2078-2489/14/9/477  
DOI: https://doi.org/10.3390/info14090477

### Components Present

- Blockchain.
- Privacy techniques such as differential privacy and homomorphic encryption.
- Explainable AI.
- NLP and legal decision support.
- Justice-system framing.

### What It Proves

This paper is useful as a broad justice-domain precedent for combining blockchain, privacy, and XAI.

### What It Does Not Prove

- It is mostly conceptual.
- It does not provide a reusable police access-control implementation.
- It does not provide empirical results strong enough to use as a baseline.

### How To Use In SEBA-XAI

Cite it in related work as a broad XAI-justice framework, then clearly distinguish SEBA-XAI:

- SEBA-XAI targets access governance, not general judicial decision-making.
- SEBA-XAI will use reproducible synthetic access workloads.
- SEBA-XAI will compare baselines and ablations.

## Candidate 8: Blockchain For Explainable And Trustworthy AI

Full title: Blockchain for explainable and trustworthy artificial intelligence  
Year: 2019/2020  
Source: https://scholarworks.aub.edu.lb/handle/10938/25595?show=full  
DOI: https://doi.org/10.1002/widm.1340

### Components Present

- General blockchain and XAI framework.
- Smart contracts.
- Trusted oracles.
- Decentralized storage.
- Consensus among AI and XAI predictors.

### What It Proves

This is a useful theoretical foundation for why blockchain can support trust and accountability around AI decision processes.

### What It Does Not Prove

- It is not police, law-enforcement, or India specific.
- It is not a direct implementation baseline for access control.
- It does not handle classified crime records or CCTNS/ICJS-compatible workflows.

### How To Use In SEBA-XAI

Use as background only. The core SEBA-XAI novelty must come from the police access-governance formulation and experimental simulator, not from generic claims that blockchain improves AI trust.

## What To Test First

The first practical model should be our own SEBA-XAI simulator, using external models as design references.

### First Testable System

```text
synthetic_access_sim
```

Minimum components:

- synthetic multi-station access-request generator;
- deterministic policy oracle;
- RBAC baseline;
- ABAC/PBAC baseline;
- signed append-only log baseline;
- blockchain-style audit ledger;
- off-chain explanation artifact store;
- XAI explanation generator;
- tamper-injection tests;
- metric exporter.

### Why Not Replicate BAXDT Directly First

BAXDT is highly relevant, but it appears to be domain-generic and the public repository URL was not verified. Replicating its entire setup would not answer the police access-governance research question. A local BAXDT-style trace inside SEBA-XAI is more useful.

### Why Not Start With LEChain Directly

LEChain has code and police/legal relevance, but it does not include XAI and focuses on lawful evidence management. It is better used as a blockchain/access-control reference than as the main implementation.

## Proposed Experimental Bridge

### Baselines

| Baseline | Purpose | Source inspiration |
|---|---|---|
| RBAC + mutable log | Weak conventional baseline | Standard access-control baseline |
| ABAC/PBAC + mutable log | Contextual authorization baseline | NIST ABAC and Fabric ABAC literature |
| ABAC/PBAC + signed hash-chain log | Strong non-blockchain audit baseline | Forensic logging and append-only audit practice |
| LEChain-style evidence/access workflow | Police/legal blockchain reference | LEChain |

### Proposed SEBA-XAI

| Component | Function | External precedent |
|---|---|---|
| Policy oracle | Ground-truth allow/deny/escalate labels | ABAC/PBAC literature |
| Access-risk model | Learns or scores suspicious requests | Own simulator workload |
| XAI trace | Explains decision drivers and failed policy rules | BAXDT |
| Ledger commitment | Hashes request, policy, model, approval, and explanation artifacts | BAXDT and legal-decision audit paper |
| Off-chain store | Keeps raw record and full explanation outside ledger | LEChain and two-level blockchain paper |
| Tamper tests | Mutates logs, policies, approvals, explanation artifacts, or pointers | Forensic log and blockchain audit literature |

## Minimum Decision Trace For Our Code

Every access decision should produce two artifacts.

### Off-Chain Explanation Artifact

```json
{
  "trace_id": "trace-000001",
  "request_id": "req-000001",
  "decision": "escalate",
  "policy_version": "policy-v1",
  "model_version": "access-risk-v0",
  "reason_codes": [
    "CROSS_JURISDICTION",
    "WITNESS_SENSITIVE"
  ],
  "decisive_attributes": {
    "subject.station": "PS_A",
    "object.originating_station": "PS_B",
    "object.witness_flag": true,
    "environment.purpose": "investigation"
  },
  "failed_rules": [],
  "required_approval": "district_superior",
  "xai_method": "policy_trace_v1",
  "created_at": "2026-05-17T00:00:00+05:30"
}
```

### On-Chain Or Ledger Event

```json
{
  "event_id": "evt-000001",
  "trace_id": "trace-000001",
  "request_hash": "sha256:...",
  "policy_hash": "sha256:...",
  "model_hash": "sha256:...",
  "explanation_hash": "sha256:...",
  "approval_hash": "sha256:...",
  "previous_event_hash": "sha256:...",
  "event_hash": "sha256:..."
}
```

This is the cleanest way to connect blockchain and XAI without putting sensitive police records or full explanations on-chain.

## Strong Claims We Can Make Now

- Existing work supports blockchain-backed evidence provenance, legal-decision auditing, access-control enforcement, and XAI traceability as separate or partially integrated ideas.
- A direct, reproducible, India-oriented police access-governance overlay combining all three pillars remains underexplored based on this scan.
- SEBA-XAI should be evaluated first through synthetic access-control workloads because real CCTNS/ICJS request logs are not public.

## Claims We Cannot Make Yet

- SEBA-XAI is more secure than existing systems.
- SEBA-XAI improves police operations.
- SEBA-XAI is legally compliant in India.
- SEBA-XAI has deployment readiness.
- SEBA-XAI outperforms Hyperledger Fabric, LEChain, or BAXDT.
- SEBA-XAI predicts crime or criminals.

These require code, baselines, ablations, metrics, and expert review.

## Immediate Kickstart Tasks

1. Inspect LEChain code and record which smart-contract/access-control ideas are reusable.
2. Try to locate the BAXDT repository again through author pages, DOI landing pages, GitHub search, and supplementary material.
3. Implement a minimal BAXDT-style `DecisionTrace` object in `synthetic_access_sim`.
4. Implement a local hash-chain ledger before attempting full Hyperledger Fabric.
5. Generate 1,000 synthetic access requests with deterministic seed `42`.
6. Run RBAC, ABAC/PBAC, signed-log, and SEBA-XAI ledger variants on the same workload.
7. Save metrics under `experiments/runs/` and comparison tables under `results/tables/`.
8. Write paper claims only after those artifacts exist.

## Final Recommendation

Use **BAXDT + LEChain** as the main external comparison pair:

- BAXDT gives the explainable decision-trace and blockchain audit idea.
- LEChain gives the police/legal evidence lifecycle, privacy, and access-control precedent.

The research contribution should be framed as:

> SEBA-XAI adapts explainable decision-trace auditing to a police inter-agency access-governance workflow, using off-chain sensitive artifacts, permissioned ledger commitments, ABAC/PBAC enforcement, and reproducible synthetic workload evaluation.

This is narrower, testable, and stronger than claiming a general AI policing system.
