# Experiment Results Narrative

Generated: 2026-05-27T19:08:35.731293Z

## 1. Experiment Scope

The current SEBA-XAI prototype was evaluated on a deterministic synthetic workload of 1,000 access requests. The workload is not real police data and is not CCTNS/ICJS data. The Step 2 policy oracle is used as the reference label for access decisions. Therefore, the reported accuracy values mean agreement with the synthetic policy oracle, not agreement with real police decisions.

The experiment evidence covers five areas:

- decision behavior of RBAC, ABAC/PBAC, and SEBA-XAI modes;
- tamper detection for mutable logs, signed hash-chain logs, blockchain-style audit blocks, and off-chain pointers;
- metadata exposure in full versus minimized ledger designs;
- local latency and storage overhead;
- policy ablation effects.

## 2. Main Method Comparison

The RBAC mutable-log baseline reached `0.2900` accuracy against the synthetic policy oracle, with `656` false allows and `54` false denies. This is expected because the RBAC baseline uses mainly role, action, credential, and purpose. It does not evaluate jurisdiction, sensitivity, privacy flags, approval state, sealed-record status, or fallback review.

The proposed SEBA-XAI mode reached `1.0000` agreement with the same oracle and had `0` false allows in this synthetic run. This should be interpreted carefully: it shows that the configured ABAC/PBAC policy and the SEBA-XAI mode are aligned with the synthetic reference policy. It does not prove real-world correctness.

The full SEBA-XAI row also includes blockchain-style audit and XAI explanation-hash logging. Its local estimated p50 build path is `42.088542` ms for the 1,000-request workload, with `1110.357` bytes per event in the saved audit artifacts. These are local prototype measurements, not deployment performance.

## 3. Audit And Tamper Detection

The mutable log detected `0/4` controlled tamper cases by internal self-verification. The signed hash-chain detected `4/4` controlled cases, because changed rows break payload hashes, event links, or demo signatures. The permissioned blockchain-style audit layer detected `5/5` controlled block or commitment tamper cases.

The off-chain storage and pointer layer detected `10/10` controlled tamper cases. This includes stronger pointer tests where the pointer commitment was recomputed after changing the explanation hash, event commitment, or storage node. Those cases were detected because pointer verification now anchors fields back to Step 2 policy/XAI artifacts and Step 4 block-index artifacts.

These results support a limited claim: the prototype can detect the controlled tamper cases represented in the repository. They do not prove security against compromised keys, malicious quorum validators, production cryptographic attacks, or operational insider misuse.

## 4. Metadata Exposure

The full-metadata ledger view exposes `19` clear sensitive/context columns and has a schema-level exposure score of `1.0000`. The minimized commitment ledger exposes `0` clear sensitive/context columns and has a schema-level exposure score of `0.0000`.

This supports the design choice that raw records and clear operational context should not be placed directly on the audit ledger. The result is only a schema-level exposure comparison. It is not differential privacy, anonymity, or a legal-compliance proof.

## 5. Policy Ablation

The full configured PBAC/ABAC policy is the reference configured method and has `0` extra errors versus itself. Removing sealed-record rules created `32` additional false allows and `100` additional false escalations. Removing privacy rules created `46` additional false allows. Removing sensitivity rules created `19` additional false allows and `25` additional false escalations.

This supports the argument that the access-control layer should not be reduced to simple RBAC. Sensitive police access decisions require contextual rules for record sensitivity, privacy flags, sealed status, approval, jurisdiction, and assignment.

## 6. What This Proves

- The prototype can generate a reproducible synthetic access-control workload.
- The RBAC baseline is weak against the synthetic policy oracle.
- The ABAC/PBAC policy layer aligns with the synthetic policy oracle in the current run.
- The signed hash-chain and blockchain-style audit layers detect the controlled tamper cases represented in the artifacts.
- The off-chain pointer design can be verified against policy/XAI and blockchain artifacts.
- The minimized ledger design reduces direct metadata exposure at schema level.
- The policy ablation shows which rule groups matter in the synthetic workload.

## 7. What This Does Not Prove

- It does not prove real police decision accuracy.
- It does not prove CCTNS/ICJS deployment readiness.
- It does not prove legal compliance.
- It does not prove production security or privacy.
- It does not prove Hyperledger Fabric performance.
- It does not prove SOTA crime prediction.
- It does not use real FIR, victim, witness, juvenile, or investigation records.

## 8. Paper Use

The safest paper claim is:

> We design and evaluate a synthetic SEBA-XAI prototype for secure, explainable, and auditable inter-agency police-record access governance. The evaluation compares RBAC, ABAC/PBAC, signed hash-chain audit, permissioned blockchain-style audit, off-chain pointer verification, metadata exposure, and policy ablations under a reproducible synthetic workload.

The paper should avoid saying that the system is ready for real policing. It should say that this is a reproducible research prototype and a conservative architecture direction.

## 9. Generated Paper Tables

- `results/tables/paper_table_01_method_comparison.csv`
- `results/tables/paper_table_02_tamper_detection.csv`
- `results/tables/paper_table_03_metadata_exposure.csv`
- `results/tables/paper_table_04_latency_storage.csv`
- `results/tables/paper_table_05_policy_ablation.csv`

## 10. Generated Plots

- `results/plots/paper_false_allows_by_method.svg`
- `results/plots/paper_tamper_detection_by_design.svg`
- `results/plots/paper_metadata_exposure_score.svg`
- `results/plots/paper_latency_build_verify.svg`
- `results/plots/paper_policy_ablation_false_allows.svg`

## Appendix: Compact Tables

### Method Comparison

| method_name | accuracy_vs_policy_oracle | false_allow_count | false_deny_count | audit_tamper_detection_rate | xai_hash_logged |
| --- | --- | --- | --- | --- | --- |
| RBAC + mutable log | 0.2900 | 656 | 54 | 0.0000 | false |
| ABAC/PBAC + mutable log | 1.0000 | 0 | 0 | 0.0000 | false |
| ABAC/PBAC + signed hash-chain log | 1.0000 | 0 | 0 | 1.0000 | false |
| ABAC/PBAC + blockchain-style audit | 1.0000 | 0 | 0 | 1.0000 | false |
| SEBA-XAI full: ABAC/PBAC + blockchain-style audit + XAI hash | 1.0000 | 0 | 0 | 1.0000 | true |

### Tamper Detection

| artifact_layer | design_or_artifact | tamper_cases | detected | detection_rate |
| --- | --- | --- | --- | --- |
| audit_log | mutable_log | 4 | 0 | 0.0000 |
| audit_log | signed_hash_chain | 4 | 4 | 1.0000 |
| blockchain_audit | permissioned_blockchain_style | 5 | 5 | 1.0000 |
| offchain_storage_pointer | offchain_store | 3 | 3 | 1.0000 |
| offchain_storage_pointer | pointer_table | 7 | 7 | 1.0000 |

### Metadata Exposure

| ledger_design | clear_sensitive_columns | metadata_exposure_score | decision_visible | purpose_visible |
| --- | --- | --- | --- | --- |
| full_metadata_ledger | 19 | 1.0000 | true | true |
| minimized_commitment_ledger | 0 | 0.0000 | false | false |

### Policy Ablation

| method_name | disabled_rule_groups | accuracy_drop_from_full | false_allow_delta_from_full | false_escalate_delta_from_full |
| --- | --- | --- | --- | --- |
| RBAC role/action only | none | 0.7100 | 656 | 0 |
| Full configured PBAC/ABAC | none | 0.0000 | 0 | 0 |
| Ablation: approval rules removed | approval | 0.0530 | 0 | 53 |
| Ablation: assignment rules removed | assignment | 0.0650 | 0 | 65 |
| Ablation: sealed-record rules removed | sealed_record | 0.1320 | 32 | 100 |
| Ablation: privacy rules removed | privacy | 0.0460 | 46 | 0 |
| Ablation: jurisdiction rules removed | jurisdiction | 0.0080 | 8 | 0 |
| Ablation: sensitivity rules removed | sensitivity | 0.0440 | 19 | 25 |
| Ablation: emergency/network rules removed | emergency\|network | 0.0010 | 1 | 0 |
| Ablation: fallback review removed | fallback_review | 0.0150 | 15 | 0 |
