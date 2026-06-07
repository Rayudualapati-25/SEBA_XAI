# SEBA-XAI Claim-Control Memo

Date: 2026-06-05  
Status: active claim-control document for publication drafting  
Purpose: prevent unsupported claims while converting SEBA-XAI into a journal-ready paper.

## 1. Paper Identity

Working title:

> SEBA-XAI: Explainable Policy-Aware Audit for Secure Inter-Agency Police Data Access Governance

Paper type:

> Applied information-security and XAI evaluation paper using a reproducible synthetic access-governance benchmark.

Primary target venue:

> Journal of Information Security and Applications, subscription route if publication budget is limited.

## 2. Frozen Problem Statement

In CCTNS/ICJS-style inter-agency police and criminal-justice data sharing, sensitive records require contextual access decisions and later audit review. A simple role check or ledger-only audit trail is not enough because a log may remain cryptographically valid even when the original decision was policy-corrupted or validly re-signed by a compromised signer. The research problem is to design and evaluate an access-governance framework that combines contextual policy checks, tamper-evident audit commitments, off-chain sensitive-record handling, and explainable decision traces for `allow`, `deny`, and `escalate` access decisions.

## 3. Safe One-Sentence Claim

Use this sentence consistently:

> SEBA-XAI is evaluated as a reproducible, synthetic benchmark and prototype for policy-aware audit in sensitive inter-agency access governance, comparing ledger-only integrity checks, ABAC/Fabric-style re-execution, trusted policy re-evaluation, and log-only interpretable policy-drift detection under explicit visibility assumptions.

Do not replace this with broader language such as "AI for crime prediction" or "blockchain for police data storage."

## 4. Allowed Claims

The paper may claim the following, provided the cited artifact is used in the manuscript.

| Claim | Evidence Artifact | Safe Wording |
|---|---|---|
| The evaluation uses a synthetic CCTNS/ICJS-style access-control workload, not real police records. | `prototype/runs/*/artifacts/access_requests.csv`, `results/FINDINGS.md`, `papers/final_paper/methodology/methodology_draft_v1.md` | "We evaluate on a synthetic inter-agency access-request workload." |
| The prototype compares multiple baselines and defenses. | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_raw.csv` | "We compare mutable logs, signed-chain logs, blockchain-style audit, CT-style logs, ABAC/Fabric-style re-execution, trusted policy oracle, and NS-PI." |
| Ledger-only and ABAC/Fabric-style checks detect ordinary tampering better than a mutable log in the synthetic benchmark. | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv` | "Cryptographic and ABAC-style defenses remain stronger for ordinary event edits under the tested workload." |
| Ledger-only and ABAC/Fabric-style checks are blind to the validly re-signed `compromised_signer` attack as implemented. | `results/tables/full_grid_per_attack.csv`, `results/FINDINGS.md` Section 2 | "For the synthetic compromised-signer attack, ledger-only and ABAC-style baselines have 0.0 detection because the corrupted log is validly re-signed by construction." |
| NS-PI detects the synthetic compromised-signer attack in the full-grid five-seed setting. | `results/tables/full_grid_per_attack.csv`, `results/tables/adaptive_attack_summary.csv`, `results/tables/seed_confidence_summary.csv` | "NS-PI provides a complementary log-only drift signal for the tested compromised-signer attack." |
| NS-PI is not the strongest overall defense. | `results/tables/full_grid_aas_by_defense.csv`, `results/FINDINGS.md` Section 1 | "NS-PI is not the best overall tamper detector; trusted policy re-evaluation remains stronger when an independent raw-attribute view is available." |
| Trusted policy oracle is strongest under its visibility assumption. | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/nspi_compromised_signer_sensitivity_summary.csv` | "The trusted policy oracle catches every tested compromised-signer flip fraction because it assumes an uncompromised view of original request attributes." |
| NS-PI misses low-rate and small targeted corruptions. | `results/tables/nspi_compromised_signer_sensitivity_summary.csv`, `results/tables/nspi_targeted_compromised_signer_summary.csv` | "NS-PI misses 2% and 5% global corruption and small 10% targeted station/district corruption in the current benchmark." |
| XAI artifacts are measurable and audit-linked. | `results/tables/explanation_audit_quality_summary.csv` | "The XAI layer is evaluated through trace completeness, decisive-attribute coverage, counterfactual coverage/validity, explanation stability, and audit reconstruction." |
| Natural-language explanation text still has a weakness. | `results/tables/explanation_audit_quality_summary.csv`, `results/FINDINGS.md` Section 6 | "Decisive-attribute full text coverage is incomplete and must be reported as a limitation." |
| The workload/policy-mix stress test supports stability for the 25% compromised-signer case, with weaker 10% behavior at smaller sizes. | `results/tables/workload_policy_stress_summary.csv`, `results/FINDINGS.md` Section 6b | "The 25% compromised-signer asymmetry holds across tested workload sizes and policy mixes; 10% detection remains size-dependent." |

## 5. Forbidden Claims

The paper must not claim:

- real deployment inside CCTNS or ICJS;
- access to actual police records, FIR databases, CCTNS logs, or ICJS logs;
- raw police records stored on blockchain;
- legal compliance proof;
- production security;
- improved crime prediction;
- individual suspect prediction;
- state-of-the-art performance;
- NS-PI beating blockchain or ABAC overall;
- NS-PI replacing ABAC/PBAC, blockchain audit, or trusted policy re-evaluation;
- a real Hyperledger Fabric deployment unless a separate Fabric experiment is actually run and saved;
- formal privacy unless a formal privacy model and proof are added.

## 6. Research Questions For The Paper

| RQ | Question | Primary Metrics | Evidence |
|---|---|---|---|
| RQ1 | How do audit designs compare for ordinary access-log tampering? | AAS, tamper detection rate by attack type | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv` |
| RQ2 | Where do ledger-only and policy-reexecution baselines fail under validly re-signed policy corruption? | `compromised_signer` detection rate | `results/tables/full_grid_per_attack.csv`, `results/tables/adaptive_attack_summary.csv` |
| RQ3 | Does NS-PI add a useful log-only drift signal, and where does it fail? | global/station/district detection, sensitivity by flip fraction | `results/tables/nspi_compromised_signer_sensitivity_summary.csv`, `results/tables/nspi_targeted_compromised_signer_summary.csv` |
| RQ4 | Are SEBA-XAI explanations reviewable and reconstructable from audit artifacts? | trace completeness, decisive-attribute coverage, counterfactual validity, audit reconstruction | `results/tables/explanation_audit_quality_summary.csv` |
| RQ5 | What are the privacy and overhead tradeoffs of minimized off-chain records plus audit commitments? | metadata exposure score, storage overhead, latency | `results/tables/paper_table_03_metadata_exposure.csv`, `results/tables/paper_table_04_latency_storage.csv`, `results/tables/offchain_storage_step7_summary.csv` |

## 7. Baseline Visibility Assumptions

| Method | Visibility | What It Can Detect | Main Limitation |
|---|---|---|---|
| Mutable log | Stored event rows only | Simple consistency issues if checked manually | Easy to edit without cryptographic evidence |
| Signed hash chain | Signed event sequence | Ordinary edits, deletion, ordering changes | Fails if corrupted event is validly re-signed |
| Blockchain-style audit | Block commitments and validator signatures | Ordinary event/block tampering | Local simulation, not live Fabric; fails under validly re-signed corruption by design |
| CT-style log | Inclusion/consistency proof style log | Ordinary log consistency changes | Does not know whether the signed decision was policy-correct |
| ABAC/Fabric-style re-execution | Logged attributes and declared policy | Policy inconsistencies visible from logged data | Fails if logged canonical decision and attributes are already corrupted consistently |
| Trusted policy oracle | Independent original request attributes | Row-level policy corruption | Strong assumption; requires uncompromised raw-attribute view |
| NS-PI | Signed decision log distribution | Distribution-level policy drift | Misses low-rate or very localized corruption; not a row-level verifier |

## 8. Paper Contribution Wording

Use these contribution bullets unless the supervisor changes the framing:

1. We formulate a CCTNS/ICJS-compatible access-governance problem for sensitive inter-agency police and criminal-justice records, using an `allow`/`deny`/`escalate` decision space.
2. We implement SEBA-XAI, a research prototype that combines contextual access-policy evaluation, off-chain sensitive-record commitments, blockchain-style audit logs, and XAI traces.
3. We define a reproducible synthetic benchmark for access-governance audit, including ordinary tamper cases and a validly re-signed compromised-signer attack.
4. We compare ledger-only integrity checks, ABAC/Fabric-style re-execution, trusted policy re-evaluation, and NS-PI under explicit visibility assumptions.
5. We report auditability, policy-drift, XAI reviewability, metadata-exposure, latency, and storage-overhead metrics, including negative results and sensitivity limits.

## 9. Current Evidence Boundary

The paper is currently evidence-backed as a synthetic benchmark and prototype paper. It is not yet evidence-backed as:

- a live deployment paper;
- a real-police-data paper;
- a formal cryptography paper;
- a formal privacy-proof paper;
- a crime-prediction paper;
- a production Hyperledger Fabric paper.

## 10. Next Evidence Needed Before Stronger Claims

Before making stronger claims, the project needs:

1. final reproducibility freeze with `make test`, `make lint`, `make typecheck`, `make reproduce`, and `make figures`;
2. artifact-to-claim table for every result in the final manuscript;
3. updated low-rate compromised-signer sensitivity if the paper wants a finer detection-boundary claim;
4. improved explanation renderer or explicit retention of the decisive-attribute text coverage limitation;
5. optional real Fabric test-network validation if the paper wants to claim more than local permissioned-audit simulation.

## 11. Supervisor-Ready Summary

The paper is now safest as:

> a prototype-based security and XAI evaluation of policy-aware audit for sensitive inter-agency police access governance.

The main novelty is not "using blockchain and AI in policing." The main contribution is evaluating how audit, access-policy re-execution, trusted policy checking, and explainable drift detection behave under ordinary tampering and validly re-signed policy-corruption failures.
