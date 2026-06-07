# Reviewer Objection Checklist

Created: 2026-05-16

Use this on 2026-06-01 and again before the June 15 freeze.

## Core Novelty Objections

### Objection 1: Why blockchain instead of signed logs?

Answer the introduction must imply:

- Signed append-only logs are a required baseline.
- Blockchain is justified only for multi-organization audit commitments where no single agency should be the sole audit authority.
- The paper will compare blockchain with signed logs rather than assume blockchain is better.

### Objection 2: How is this different from Fabric plus ABAC?

Answer the introduction must imply:

- Fabric plus ABAC exists in generic data sharing.
- SEBA-XAI adds a police/criminal-justice access workflow, superior approval, off-chain sensitive-record commitments, XAI artifact logging, and evaluation criteria for tamper detection, metadata leakage, and explanation stability.

### Objection 3: Where is real police data?

Answer the introduction must imply:

- Restricted police data is not available for this stage.
- The core evaluation uses a documented synthetic workload because the main task is access governance, not crime prediction.
- Public NCRB/BPRD data is used only for aggregate context.

### Objection 4: Is this deployable?

Answer:

- No deployment claim.
- The paper proposes and evaluates an architecture and benchmark.
- Deployment would require legal, operational, security, and stakeholder review.

### Objection 5: Is this legally compliant?

Answer:

- No legal-compliance claim.
- The design is informed by Indian digital-policing and legal context.
- A legal expert must review compliance claims.

## Technical Scope Objections

### Objection 6: What exactly does XAI explain?

Required answer:

- allow/deny/escalate decision;
- decisive policy attributes;
- missing attributes;
- access-risk factors if a model is used;
- human override rationale;
- explanation artifact hash for audit verification.

### Objection 7: Does blockchain make the data private?

Required answer:

- No.
- Privacy comes from access control, minimization, encryption, off-chain storage, and metadata-leakage analysis.
- Blockchain records commitments and audit metadata.

### Objection 8: Is this crime prediction?

Required answer:

- No, not primarily.
- Aggregate crime analytics is secondary context only.
- Public NCRB data cannot support individual suspect prediction.

### Objection 9: Why India-specific if the workload is synthetic?

Required answer:

- India-specific context defines the workflow assumptions: CCTNS, ICJS, police stations, states/districts, standardized codes, courts, prisons, forensics, prosecution.
- Synthetic data is used because sensitive access logs and police records are not public.
- The policy variables are derived from the Indian inter-agency sharing problem.

## Language Red Flags

Remove these if found:

- "guarantees privacy"
- "tamper-proof"
- "fully secure"
- "state-of-the-art"
- "deployable"
- "legally compliant"
- "predicts criminals"
- "replaces CCTNS"
- "stores police data on blockchain"

Preferred wording:

- "tamper-evident"
- "privacy-aware"
- "CCTNS/ICJS-compatible"
- "off-chain sensitive storage"
- "access-governance overlay"
- "model-supported and human-reviewed"
- "evidence-grounded"
