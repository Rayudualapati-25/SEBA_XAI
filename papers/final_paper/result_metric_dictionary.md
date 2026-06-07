# SEBA-XAI Result Metric Dictionary

Date: 2026-06-05  
Purpose: define the main metrics in simple language so the Results section uses consistent wording.

## 1. Access And Policy Metrics

| Metric | Simple Meaning | Used For | Main Artifact |
|---|---|---|---|
| Authorization accuracy | How often a method matches the declared synthetic policy oracle. | Comparing RBAC, ABAC/PBAC, and SEBA-XAI decision behavior. | `results/tables/paper_table_01_method_comparison.csv` |
| False allow count/rate | Cases where a method allows access but the oracle would not allow it. | Measuring high-risk access-control errors. | `results/tables/paper_table_01_method_comparison.csv`, `results/tables/paper_table_05_policy_ablation.csv` |
| False deny count/rate | Cases where a method denies access but the oracle would not deny it. | Measuring over-restrictive policy behavior. | `results/tables/paper_table_01_method_comparison.csv` |
| False escalation count/rate | Cases where a method escalates unnecessarily or misses escalation behavior compared with the oracle. | Measuring review-workflow mismatch. | `results/tables/paper_table_01_method_comparison.csv`, `results/tables/paper_table_05_policy_ablation.csv` |
| Accuracy drop from full | How much performance falls when a policy rule group is removed. | Policy ablation. | `results/tables/paper_table_05_policy_ablation.csv` |
| Extra errors vs full | Number of additional decision errors after removing a policy rule group. | Showing why contextual rules are needed. | `results/tables/paper_table_05_policy_ablation.csv` |

## 2. Audit And Tamper Metrics

| Metric | Simple Meaning | Used For | Main Artifact |
|---|---|---|---|
| Tamper detection rate | Fraction of controlled tamper cases detected by a design. | Comparing mutable logs, signed chains, blockchain-style audit, and off-chain pointer checks. | `results/tables/paper_table_02_tamper_detection.csv` |
| Detection rate by attack | Fraction of seeds where a defense detects a specific attack type. | Showing which defenses work or fail for each attack. | `results/tables/full_grid_per_attack.csv` |
| AAS | Authorization Agreement Score; summary score used in the full-grid comparison across attacks and defenses. | Overall defense comparison in the synthetic benchmark. | `results/tables/full_grid_aas_by_defense.csv` |
| Audit reconstruction rate | Whether audit records can be joined back into a complete review trail. | Testing whether request, decision, explanation, and audit artifacts can be reconstructed. | `results/tables/explanation_audit_quality_summary.csv` |
| Hash/explanation tamper detection | Whether changed explanation or audit hashes are detected. | Testing XAI artifact integrity. | `results/tables/paper_table_01_method_comparison.csv`, `results/tables/paper_table_02_tamper_detection.csv` |

## 3. NS-PI Drift Metrics

| Metric | Simple Meaning | Used For | Main Artifact |
|---|---|---|---|
| NS-PI global detection rate | Whether NS-PI detects a shift in the overall decision distribution. | Detecting broad compromised-signer corruption. | `results/tables/nspi_compromised_signer_sensitivity_summary.csv` |
| NS-PI per-station detection rate | Whether NS-PI detects drift inside station-level groups. | Detecting localized station corruption. | `results/tables/nspi_targeted_compromised_signer_summary.csv` |
| NS-PI per-district detection rate | Whether NS-PI detects drift inside district-level groups. | Detecting localized district corruption. | `results/tables/nspi_targeted_compromised_signer_summary.csv` |
| NS-PI any detection rate | Whether any NS-PI view detects the attack. | Summarizing global/grouped drift detection. | `results/tables/nspi_compromised_signer_sensitivity_summary.csv`, `results/tables/nspi_targeted_compromised_signer_summary.csv` |
| Mean global JS divergence | Average Jensen-Shannon divergence between clean and attacked decision distributions. | Measuring distribution shift size. | `results/tables/adaptive_attack_summary.csv`, `results/tables/nspi_compromised_signer_sensitivity_summary.csv` |
| Mean stations flagged | Average number of station groups flagged by NS-PI. | Understanding grouped drift behavior. | `results/tables/nspi_compromised_signer_sensitivity_summary.csv` |

## 4. XAI Metrics

| Metric | Simple Meaning | Used For | Main Artifact |
|---|---|---|---|
| Trace complete rate | Fraction of requests with a complete structured explanation trace. | Checking whether every request has reviewable explanation fields. | `results/tables/explanation_audit_quality_summary.csv` |
| Decisive attribute present rate | Whether decisive attributes are present in the structured explanation artifact. | Checking structured XAI completeness. | `results/tables/explanation_audit_quality_summary.csv` |
| Decisive attribute text coverage mean | Average share of decisive attributes mentioned in generated explanation text. | Measuring natural-language explanation quality. | `results/tables/explanation_audit_quality_summary.csv` |
| Decisive attribute full text coverage rate | Fraction of rows where all decisive attributes appear in the text. | Main explanation-text weakness. | `results/tables/explanation_audit_quality_summary.csv` |
| Counterfactual coverage rate | Fraction of target rows for which counterfactual explanations are generated. | Checking whether deny/escalate rows receive counterfactual support. | `results/tables/explanation_audit_quality_summary.csv` |
| Counterfactual validity rate | Fraction of generated counterfactuals that replay to the intended decision. | Checking whether counterfactuals are behaviorally valid in the benchmark. | `results/tables/explanation_audit_quality_summary.csv` |
| Stable decision/reason row rate | Fraction of duplicate-context rows with stable decision and reason behavior. | Checking explanation consistency. | `results/tables/explanation_audit_quality_summary.csv` |

## 5. Privacy And Overhead Metrics

| Metric | Simple Meaning | Used For | Main Artifact |
|---|---|---|---|
| Metadata exposure score | Prototype score for how much sensitive context appears in clear audit fields. | Comparing full metadata logging with minimized commitments. | `results/tables/paper_table_03_metadata_exposure.csv` |
| Clear sensitive columns | Number of audit columns that expose sensitive context directly. | Metadata minimization analysis. | `results/tables/paper_table_03_metadata_exposure.csv` |
| Hashed or commitment columns | Number of audit columns represented as hashes or commitments. | Showing off-chain/minimized audit design. | `results/tables/paper_table_03_metadata_exposure.csv` |
| Build or decision p50 latency | Median local time to build an audit artifact or generate a decision. | Local prototype overhead. | `results/tables/paper_table_04_latency_storage.csv` |
| Verify p50 latency | Median local time to verify an audit artifact. | Local verification overhead. | `results/tables/paper_table_04_latency_storage.csv` |
| Storage bytes per event/request | Approximate local storage cost per event or request. | Storage overhead comparison. | `results/tables/paper_table_04_latency_storage.csv` |

## 6. Wording Rules

- Say "measured in the synthetic benchmark," not "proved in police systems."
- Say "local permissioned-audit simulation," not "deployed Fabric network."
- Say "metadata exposure proxy," not "privacy guarantee."
- Say "trusted oracle under a stronger visibility assumption," not "real-world perfect baseline."
- Say "NS-PI is complementary," not "NS-PI replaces blockchain or ABAC."
- Say "explanation reviewability metrics," not "XAI solves trust."
