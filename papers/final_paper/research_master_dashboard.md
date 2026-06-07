# SEBA-XAI Research Master Dashboard

Date: 2026-06-05  
Status: working control dashboard for paper writing  
Use: start here before editing the paper, running experiments, or discussing progress with the supervisor.

## 1. Current Paper Identity

Working title:

> SEBA-XAI: Explainable Policy-Aware Audit for Secure Inter-Agency Police Data Access Governance

Short description:

> SEBA-XAI is a synthetic benchmark and research prototype for studying explainable, policy-aware audit in sensitive inter-agency police and criminal-justice access governance.

The paper is **not** a crime-prediction paper. It is **not** a real CCTNS/ICJS deployment paper. It is **not** a legal-compliance proof.

## 2. One-Sentence Problem Statement

In CCTNS/ICJS-style inter-agency data sharing, sensitive police and criminal-justice records need contextual access decisions and later audit review; simple role checks and ledger-only audit logs are not enough when a decision can be policy-corrupted but still validly re-signed.

## 3. Final Safe Claim

Use this wording as the main claim:

> SEBA-XAI is evaluated as a reproducible, synthetic benchmark and prototype for policy-aware audit in sensitive inter-agency access governance, comparing ledger-only integrity checks, ABAC/Fabric-style re-execution, trusted policy re-evaluation, and log-only interpretable policy-drift detection under explicit visibility assumptions.

## 4. What Has Been Completed

| Area | Current Status | Main Evidence |
|---|---|---|
| Problem framing | Completed and narrowed | `papers/final_paper/claim_control_memo.md`, `research_pack/05_research_gap.md` |
| Synthetic workload | Completed for current benchmark | `prototype/runs/*`, `results/FINDINGS.md` |
| Policy oracle and XAI traces | Completed for synthetic requests | `prototype/synthetic_access_sim/policy_oracle.py`, `results/tables/explanation_audit_quality_summary.csv` |
| Mutable log baseline | Completed | `results/tables/paper_table_02_tamper_detection.csv` |
| Signed hash-chain baseline | Completed | `results/tables/paper_table_02_tamper_detection.csv` |
| Blockchain-style audit simulation | Completed as local simulation | `prototype/synthetic_access_sim/blockchain_audit.py`, `results/tables/full_grid_per_attack.csv` |
| ABAC/Fabric-style re-execution baseline | Completed as simulation | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv` |
| Trusted policy oracle baseline | Completed as strong visibility baseline | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv` |
| NS-PI drift detector | Completed for current benchmark | `results/tables/adaptive_attack_summary.csv`, `results/tables/nspi_*summary.csv` |
| Metadata exposure study | Initial completed synthetic study | `results/tables/paper_table_03_metadata_exposure.csv` |
| Latency/storage study | Initial local prototype study | `results/tables/paper_table_04_latency_storage.csv` |
| Workload/policy stress | Completed for current five-seed matrix | `results/tables/workload_policy_stress_summary.csv` |
| Paper draft | Draft v1 exists, not final | `papers/final_paper/paper_draft_v1.md` |

## 5. What The Current Evidence Supports

| Supported Finding | Evidence | How To Say It |
|---|---|---|
| Trusted policy oracle is strongest in the current synthetic benchmark. | `results/tables/full_grid_aas_by_defense.csv` | "The trusted policy oracle is strongest under its independent raw-attribute visibility assumption." |
| Ledger-only and ABAC-style baselines detect ordinary tampering better than mutable logs. | `results/tables/full_grid_per_attack.csv` | "Cryptographic and ABAC-style baselines are strong for ordinary logged-field edits in the tested workload." |
| Ledger-only and ABAC-style baselines miss validly re-signed compromised-signer corruption. | `results/tables/full_grid_per_attack.csv` | "They are blind to this attack by construction when the corrupted event is validly re-signed." |
| NS-PI detects the tested compromised-signer attack in the full-grid setting. | `results/tables/adaptive_attack_summary.csv` | "NS-PI provides a complementary log-only drift signal for the tested compromised-signer attack." |
| NS-PI is not the best overall defense. | `results/tables/full_grid_aas_by_defense.csv` | "NS-PI is complementary, not a replacement for ABAC, blockchain audit, or trusted policy re-evaluation." |
| NS-PI misses low-rate and small targeted corruptions. | `results/tables/nspi_compromised_signer_sensitivity_summary.csv`, `results/tables/nspi_targeted_compromised_signer_summary.csv` | "The detector has clear sensitivity limits." |
| XAI traces are structurally measurable and audit-linked. | `results/tables/explanation_audit_quality_summary.csv` | "The prototype measures trace completeness, counterfactual validity, explanation stability, and audit reconstruction." |
| Natural-language explanation text still has a weakness. | `results/tables/explanation_audit_quality_summary.csv` | "Decisive-attribute full text coverage is incomplete and must be reported as a limitation." |

## 6. What We Must Not Claim

- Do not claim real CCTNS/ICJS deployment.
- Do not claim access to real police records, FIR records, CCTNS logs, or ICJS logs.
- Do not claim raw records are stored on blockchain.
- Do not claim legal compliance.
- Do not claim production security.
- Do not claim state-of-the-art performance.
- Do not claim crime prediction or individual suspect prediction.
- Do not claim NS-PI beats blockchain, ABAC, or the trusted oracle overall.
- Do not claim a real Hyperledger Fabric deployment unless a real Fabric experiment is added.
- Do not claim formal privacy unless a formal model and proof are added.

## 7. Research Questions To Use

| RQ | Question | Main Evidence |
|---|---|---|
| RQ1 | How do audit designs compare for ordinary access-log tampering? | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv` |
| RQ2 | Where do ledger-only and ABAC/Fabric-style baselines fail under validly re-signed policy corruption? | `results/tables/full_grid_per_attack.csv`, `results/tables/adaptive_attack_summary.csv` |
| RQ3 | Does NS-PI add a useful log-only drift signal, and where does it fail? | `results/tables/nspi_compromised_signer_sensitivity_summary.csv`, `results/tables/nspi_targeted_compromised_signer_summary.csv` |
| RQ4 | Are SEBA-XAI explanations reviewable and reconstructable from audit artifacts? | `results/tables/explanation_audit_quality_summary.csv` |
| RQ5 | What are the privacy and overhead tradeoffs of minimized off-chain records plus audit commitments? | `results/tables/paper_table_03_metadata_exposure.csv`, `results/tables/paper_table_04_latency_storage.csv` |

## 8. Contribution Wording

Use these contribution claims only with evidence references:

1. Formulate a CCTNS/ICJS-compatible access-governance problem for sensitive inter-agency records.
2. Implement SEBA-XAI as a research prototype combining contextual policy evaluation, off-chain record commitments, blockchain-style audit, and XAI traces.
3. Define a reproducible synthetic benchmark with ordinary tamper cases and validly re-signed compromised-signer attacks.
4. Compare ledger-only audit, ABAC/Fabric-style re-execution, trusted policy re-evaluation, and NS-PI under explicit visibility assumptions.
5. Report auditability, drift detection, XAI reviewability, metadata exposure, latency, storage overhead, and failure cases.

## 9. Main Weaknesses To Keep Honest

| Weakness | Why It Matters |
|---|---|
| Synthetic workload only | It supports controlled evaluation, not real police performance. |
| Policy oracle is not official policy | It is a benchmark labeling function, not legal or police validation. |
| Blockchain layer is local simulation | It supports permissioned-audit reasoning, not real Fabric deployment claims. |
| NS-PI misses low-rate attacks | The detector is distribution-level, not row-level. |
| Trusted oracle is stronger | NS-PI should be positioned as complementary log-only monitoring. |
| XAI natural-language coverage is incomplete | The paper must report the explanation-text limitation. |
| Metadata exposure is not formal privacy | It is a synthetic leakage proxy, not a proof. |

## 10. Next Research Steps

1. Use `papers/final_paper/artifact_to_claim_table.csv` while editing the paper.
2. Run the reproduction freeze only after the paper claims are aligned:
   - `make test`
   - `make lint`
   - `make typecheck`
   - `make reproduce`
   - `make figures`
3. Build the final Results section from `results/FINDINGS.md` and the artifact-to-claim table.
4. Keep every strong claim tied to a table, plot, log, or source note.
5. Send the supervisor the title, problem statement, contribution bullets, and one-page limitation summary before expanding scope.

## 11. Best Paper Framing

The strongest feasible paper framing is:

> SEBA-XAI as a benchmarked architecture for explainable policy-drift detection and trusted policy re-evaluation in blockchain-audited police access governance.

This is stronger than a broad "AI + blockchain for police data" idea because it is narrower, measurable, and supported by current artifacts.
