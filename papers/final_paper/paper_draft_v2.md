# SEBA-XAI: Explainable Policy-Aware Audit for Secure Inter-Agency Police Data Access Governance

Status: aligned manuscript draft v2 for supervisor review  
Date: 2026-06-06  
Evidence basis: `papers/final_paper/research_master_dashboard.md`,
`papers/final_paper/claim_control_memo.md`,
`papers/final_paper/artifact_to_claim_table.csv`, `results/FINDINGS.md`,
and the result tables under `results/tables/`.

This draft aligns the Introduction, Methodology, and Results with the current
claim boundary. Related Work, Threat Model, Limitations, Conclusion, and final
IEEE formatting should be merged from the existing section drafts after
supervisor review.

## Abstract

SEBA-XAI is a research prototype and synthetic benchmark for explainable,
policy-aware audit in sensitive inter-agency police and criminal-justice data
access governance. The paper studies a CCTNS/ICJS-style access workflow in
which requests are evaluated by contextual policy rules, recorded through
signed and blockchain-style audit commitments, and reviewed through structured
explanation artifacts. The evaluation compares mutable logs, signed hash
chains, blockchain-style audit, CT-style logs, ABAC/Fabric-style
re-execution, a trusted raw-attribute policy oracle, and NS-PI, an
interpretable log-only policy-drift detector. Results show that NS-PI is not
the strongest overall tamper detector and does not replace ABAC, blockchain
audit, or trusted policy re-evaluation. Its useful role is narrower: it
detects the tested validly re-signed compromised-signer attack where
ledger-only and ABAC-style baselines are blind by construction. The paper also
reports XAI reviewability, audit reconstruction, metadata exposure, local
latency/storage overhead, sensitivity limits, and known failure cases. All
results are synthetic benchmark evidence, not operational police-system
evidence.

## I. Introduction

India already has large-scale digital policing and criminal-justice
infrastructure. CCTNS provides a national police-process backbone, and official
sources report that all 17,798 police stations were using CCTNS as of
February 1, 2026. ICJS further connects police/CCTNS with courts, prisons,
forensics, and prosecution through inter-agency data sharing. This paper
therefore does not treat the Indian context as a missing-infrastructure
problem. It studies a safer and narrower question: how a secure and
explainable overlay can support governance of sensitive inter-agency access
requests without replacing CCTNS or ICJS.

The access problem is important because police and criminal-justice records
are not ordinary database rows. A request may involve FIR details, witness or
victim information, juvenile records, forensic reports, cybercrime complaints,
case-diary material, evidence references, or court/prosecution-linked records.
Whether access should be allowed depends on more than a broad organizational
role. It may depend on role, rank, station, jurisdiction, case assignment,
purpose, record sensitivity, credential status, approval state, time window,
emergency context, and relationship to court, prosecution, or forensic
workflow.

The research problem is to decide whether a sensitive inter-agency access
request should be allowed, denied, or escalated, and to preserve enough
evidence for later review. A reviewer should be able to reconstruct what was
requested, which policy version was applied, which attributes were decisive,
what explanation was produced, and which approval or review event was bound to
the request. The system must do this without storing raw sensitive records on
a shared ledger and without assuming that any one layer delivers
confidentiality, correctness, and accountability by itself.

SEBA-XAI uses three equal pillars. The first pillar is contextual access
control. RBAC is useful but too coarse for sensitive inter-agency workflows,
so the prototype uses ABAC/PBAC-style subject, object, action, and
environment attributes, including purpose, jurisdiction, approval, revocation,
and policy version. The second pillar is blockchain-style audit. Blockchain is
used only for tamper-evident commitments and audit reconstruction; raw records
remain off-chain. The third pillar is XAI. Explanations are not treated as a
decorative dashboard. They are logged artifacts containing decision labels,
reason codes, decisive attributes, policy/model versions, counterfactual
information where applicable, and hashes that bind explanations to audit
events.

The scope is deliberately not predictive policing. The paper does not predict
crime, identify suspects, or claim improved policing outcomes. Public NCRB
crime statistics are useful for domain context, but they are aggregate
reported/registered crime data and do not provide public individual access-log
records. This paper is therefore about access governance, auditability, and
explanation of access decisions.

Existing work covers parts of the problem. Blockchain and Fabric-style systems
have been studied for evidence management, provenance, access control, and
on-chain/off-chain data handling. ABAC and PBAC provide the policy vocabulary
for contextual authorization. XAI and criminal-justice fairness work explain
why high-stakes public-safety decisions require caution and reviewability.
The remaining gap is an integrated, reproducible access-governance benchmark
that jointly studies contextual authorization, off-chain commitments,
blockchain-style audit, explanation artifact logging, adversarial audit
attacks, and explicit detector visibility assumptions.

SEBA-XAI addresses this gap as a synthetic benchmark and research prototype.
It compares ledger-only integrity checks, ABAC/Fabric-style re-execution,
trusted raw-attribute policy re-evaluation, and NS-PI, a log-only
interpretable policy-drift detector. The core claim is narrow: SEBA-XAI is
evaluated as a reproducible synthetic benchmark for policy-aware audit in
sensitive inter-agency access governance. It is not a deployment paper, not a
real-police-data paper, not a legal-compliance proof, and not a
crime-prediction paper.

The paper makes five contributions:

1. It formulates a CCTNS/ICJS-compatible access-governance problem for
   sensitive inter-agency police and criminal-justice records.
2. It implements SEBA-XAI as a research prototype combining contextual policy
   evaluation, off-chain sensitive-record commitments, blockchain-style audit,
   and XAI traces.
3. It defines a reproducible synthetic benchmark with ordinary tamper cases
   and a validly re-signed compromised-signer attack.
4. It compares ledger-only audit, ABAC/Fabric-style re-execution, trusted
   policy re-evaluation, and NS-PI under explicit visibility assumptions.
5. It reports auditability, policy-drift detection, XAI reviewability,
   metadata exposure, latency, storage overhead, and failure cases.

## II. Methodology

SEBA-XAI is evaluated as a synthetic-workload research prototype. The overlay
contains a request gateway, a declared policy oracle, an explanation layer,
and a permissioned audit layer. Raw records remain off-chain. The audit layer
stores decision summaries, policy/model version identifiers, hash
commitments, anchor hashes, and minimized metadata needed for review.

The synthetic workload is generated by
`prototype/synthetic_access_sim/generate_synthetic_requests.py`. It creates
synthetic stations, officers, cases, records, and access requests. Each
request has subject, object, and environment attributes such as role, rank,
station, jurisdiction, case assignment, credential status, sensitivity level,
sealed/juvenile/witness flags, purpose, time window, emergency flag,
court/prosecutor flag, and policy version. Multi-seed experiments use seeds
`{7, 21, 42, 99, 123}`.

The declared policy oracle in
`prototype/synthetic_access_sim/policy_oracle.py` labels each request as
`allow`, `deny`, or `escalate`. It also emits a reason code, decisive
attributes, decision hash, explanation hash, and audit anchor hash. The oracle
is the benchmark labeling function. It is not an official police policy and
does not prove real-world policy correctness.

The audit designs include a mutable log, signed append-only hash chain,
CT-style log, local permissioned blockchain-style audit simulation,
ABAC/Fabric-style re-execution, trusted raw-attribute policy oracle, and
NS-PI drift detection. The blockchain-style layer is implemented in
`prototype/synthetic_access_sim/blockchain_audit.py`; it is a local
file-backed simulation, not a live Hyperledger Fabric deployment.

The attack catalog includes ordinary tamper cases such as approval-token
replay, request backdating, explanation-hash substitution, block-signature
collusion, revocation race, and metadata-inference checks. The key attack is
`compromised_signer`: it corrupts policy output and re-signs a valid-looking
log. This attack is useful because ledger-only integrity checks can pass even
when the decision itself is policy-corrupted.

NS-PI learns an interpretable policy view from the declared policy behavior
and tests whether the signed decision distribution drifts away from that
reference behavior. It has log-only visibility and does not verify individual
rows. The trusted raw-attribute policy oracle is stronger because it assumes
an independent uncompromised view of the original request attributes and
re-evaluates every event row by row. These methods are compared because they
represent different visibility assumptions, not because they solve the same
problem with the same information.

The evaluation uses five research questions:

| RQ | Focus | Evidence |
|---|---|---|
| RQ1 | Ordinary audit tampering | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv` |
| RQ2 | Validly re-signed policy corruption | `results/tables/full_grid_per_attack.csv`, `results/tables/adaptive_attack_summary.csv` |
| RQ3 | NS-PI usefulness and sensitivity limits | `results/tables/nspi_compromised_signer_sensitivity_summary.csv`, `results/tables/nspi_targeted_compromised_signer_summary.csv` |
| RQ4 | XAI and audit reviewability | `results/tables/explanation_audit_quality_summary.csv` |
| RQ5 | Metadata exposure and local overhead | `results/tables/paper_table_03_metadata_exposure.csv`, `results/tables/paper_table_04_latency_storage.csv` |

## III. Results

All results are synthetic benchmark results. They are not real CCTNS/ICJS
performance measurements, not legal-compliance evidence, and not deployment
evidence.

### A. Overall Defense Comparison

From `results/tables/full_grid_aas_by_defense.csv`, the trusted policy oracle
has the strongest overall AAS in the current benchmark:

| Defense | AAS mean | AAS std |
|---|---:|---:|
| `trusted_policy_oracle` | 1.0000 | 0.0000 |
| `abac_reexec` | 0.7917 | 0.0000 |
| `blockchain_style` | 0.7917 | 0.0000 |
| `ct_log` | 0.7917 | 0.0000 |
| `fabric_abac` | 0.7917 | 0.0000 |
| `signed_chain` | 0.7917 | 0.0000 |
| `mutable_log` | 0.5000 | 0.0000 |
| `nspi_drift` | 0.2500 | 0.0932 |

This means NS-PI is not the strongest overall detector. Its role is
complementary, not a replacement for ABAC/PBAC, blockchain-style audit, or the
trusted policy oracle.

### B. Ordinary Tamper Attacks

From `results/tables/full_grid_per_attack.csv`, signed-chain,
blockchain-style, CT-style, Fabric/ABAC-style, and ABAC re-execution defenses
detect ordinary logged-field edits better than the mutable log baseline. This
supports the expected integrity-control result: when a field edit breaks a
hash, commitment, signature, or re-execution check, cryptographic and policy
baselines can detect it.

### C. Compromised-Signer Asymmetry

The important result is the `compromised_signer` attack. From
`results/tables/full_grid_per_attack.csv` and
`results/tables/seed_confidence_summary.csv`, ledger-only and ABAC/Fabric-style
baselines have 0.0 detection for this attack, while NS-PI and the trusted
policy oracle have 1.0 detection in the five-seed full-grid setting.

| Defense Group | Detection on `compromised_signer` |
|---|---:|
| Mutable/signed/blockchain/CT/Fabric/ABAC baselines | 0.0 |
| `nspi_drift` | 1.0 |
| `trusted_policy_oracle` | 1.0 |

This should be stated carefully. Ledger-only and ABAC-style baselines are
blind here because the corrupted event is validly re-signed by construction.
The trusted oracle catches it because it has an independent raw-attribute view.
NS-PI catches it as a log-only distribution-level drift signal. NS-PI is
therefore useful in a narrower regime, not universally superior.

### D. NS-PI Sensitivity Limits

From `results/tables/nspi_compromised_signer_sensitivity_summary.csv`, NS-PI
misses 2% and 5% global compromised-signer corruption in the current
benchmark. It detects the 10% global flip condition in that sensitivity table,
but the workload stress study shows this boundary is workload-size dependent.

From `results/tables/nspi_targeted_compromised_signer_summary.csv`, global
NS-PI is weak for localized station/district attacks. Grouped drift improves
targeted detection when the target group corruption is large enough, but it
still misses 10% targeted station/district corruption in the current
benchmark. This is consistent with NS-PI being a distribution-level detector,
not a row-level verifier.

### E. XAI and Audit Reviewability

From `results/tables/explanation_audit_quality_summary.csv`, structured XAI
and audit reconstruction are strong in the current synthetic evaluation:

| Metric | Mean | Std |
|---|---:|---:|
| Trace complete rate | 1.0000 | 0.0000 |
| Counterfactual coverage rate | 1.0000 | 0.0000 |
| Counterfactual validity rate | 0.9964 | 0.0055 |
| Stable decision/reason row rate | 1.0000 | 0.0000 |
| Audit reconstruction rate | 1.0000 | 0.0000 |
| Decisive-attribute full text coverage rate | 0.7810 | 0.0208 |

The limitation is important: the structured trace is complete, but the
natural-language explanation text does not mention every decisive attribute in
all cases. This must be reported as an explanation-quality weakness unless the
renderer is improved and rerun.

### F. Metadata Exposure and Local Overhead

From `results/tables/paper_table_03_metadata_exposure.csv`, the
full-metadata ledger has a prototype metadata exposure score of 1.0000, while
the minimized-commitment ledger has a score of 0.0000 under the implemented
schema-level proxy. This is useful for comparing designs, but it is not a
formal privacy proof.

From `results/tables/paper_table_04_latency_storage.csv`, local p50
build/decision latency, verification latency, and storage per event/request
are recorded for the policy oracle/XAI stage, mutable log, signed hash chain,
and permissioned blockchain-style audit simulation. These are local prototype
measurements, not production CCTNS/ICJS or live Fabric measurements.

### G. Current Result Interpretation

The current evidence supports a conservative claim: SEBA-XAI evaluates how
integrity audit, contextual policy re-evaluation, trusted policy checking, and
log-only interpretable drift detection behave under different visibility
assumptions. Blockchain-style audit helps with ordinary tamper evidence, but
does not prove policy correctness. The trusted oracle is strongest when an
independent raw-attribute view exists. NS-PI adds a complementary log-only
signal for validly re-signed policy corruption, but it misses low-rate and
small targeted attacks.

## IV. Scope Boundaries

This draft does not claim:

- real deployment inside CCTNS or ICJS;
- access to real police records, FIR records, CCTNS logs, or ICJS logs;
- raw sensitive records stored on blockchain;
- legal compliance;
- production security;
- state-of-the-art performance;
- crime prediction or individual suspect prediction;
- live Hyperledger Fabric validation;
- formal privacy.

## V. Reproduction Freeze Status

The reproduction freeze was run for this draft on 2026-06-06. The verification
step is recorded in `papers/final_paper/reproduction_freeze_prep.md`:

```bash
make test
make lint
make typecheck
make reproduce
make figures
```

The freeze passed after fixing static typing issues in the experiment code.
The regenerated headline values matched the claims in this draft for AAS,
`compromised_signer`, NS-PI sensitivity, XAI/audit quality, metadata exposure,
and local latency/storage tables. If future regenerated tables drift from the
claims in this draft, the Results, Limitations, and
`papers/final_paper/artifact_to_claim_table.csv` must be updated before
submission.
