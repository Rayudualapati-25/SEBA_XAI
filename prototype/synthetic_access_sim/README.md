# Synthetic Access Simulator

Status: Step 8 implementation complete.

This folder contains the first runnable implementation artifact for SEBA-XAI. It generates a deterministic synthetic workload of police-style access requests, applies a deterministic policy oracle with rule-trace explanations, tests local audit-log baselines, simulates a permissioned blockchain-style audit chain, models off-chain encrypted record pointers with metadata minimization, and runs configured policy ablations.

Important boundary:

- The generated data is fully synthetic.
- It does not contain real CCTNS, ICJS, FIR, police, victim, witness, or case data.
- Step 2 makes deterministic policy-oracle decisions for synthetic requests.
- Step 3 tests local audit-log tamper detection, but it does not claim deployment-grade security or blockchain consensus.
- Step 4 simulates permissioned blockchain-style audit blocks. It is not Hyperledger Fabric and not a deployed blockchain.
- Step 5 measures local latency and storage overhead. It is not a deployment benchmark.
- Step 6 compares explicit baseline/proposed experiment modes.
- Step 7 simulates off-chain encrypted payload envelopes and metadata-minimized ledger pointers. It is not production encryption or key management.
- Step 8 moves policy dimensions into a JSON config and runs PBAC/ABAC ablations.

## Step 1 Output

The generator creates:

- synthetic police stations;
- synthetic officers;
- synthetic cases;
- synthetic records;
- synthetic access requests;
- a dataset manifest;
- a dataset profile;
- a reproducible run folder.

## Run

```bash
python3 prototype/synthetic_access_sim/generate_synthetic_requests.py \
  --run-id 20260527_step1_synthetic_requests_seed42 \
  --seed 42 \
  --num-requests 1000
```

The output is written to:

```text
prototype/runs/<run_id>/
  config.yaml
  logs/generation.log
  metrics.json
  artifacts/
    stations.csv
    officers.csv
    cases.csv
    records.csv
    access_requests.csv
    dataset_manifest.json
    data_dictionary.md
    dataset_profile.csv
    README.md
```

## Next Step

Step 2 added the deterministic policy oracle that labels each request as:

- `allow`
- `deny`
- `escalate`

The oracle should also output reason codes and decisive attributes.

## Step 2: Policy Oracle And Basic XAI

```bash
python3 prototype/synthetic_access_sim/policy_oracle.py \
  --input-run-id 20260527_step1_synthetic_requests_seed42 \
  --run-id 20260527_step2_policy_oracle_seed42
```

The output is written to:

```text
prototype/runs/<run_id>/
  config.yaml
  logs/policy_oracle.log
  metrics.json
  artifacts/
    labeled_access_requests.csv
    policy_summary.csv
    explanation_artifacts.jsonl
    policy_rules.json
    dataset_manifest.json
    data_dictionary.md
    README.md
```

Step 2 adds:

- `decision`: `allow`, `deny`, or `escalate`;
- `primary_reason_code`;
- `decisive_attributes`;
- `xai_explanation`;
- `decision_hash`;
- `explanation_hash`;
- `audit_anchor_hash`.

Important boundary: the XAI output is a deterministic rule-trace explanation, not a trained ML explanation such as SHAP or LIME.

## Step 3: Audit Baselines And Tamper Tests

```bash
python3 prototype/synthetic_access_sim/audit_baseline.py \
  --input-run-id 20260527_step2_policy_oracle_seed42 \
  --run-id 20260527_step3_audit_baselines_seed42
```

The output is written to:

```text
prototype/runs/<run_id>/
  config.yaml
  logs/audit_baseline.log
  metrics.json
  artifacts/
    mutable_access_log.csv
    signed_hash_chain_log.csv
    tampered_logs/
    tamper_test_results.csv
    audit_detection_summary.csv
    dataset_manifest.json
    data_dictionary.md
    README.md
```

Step 3 built the first audit baseline:

- mutable centralized access log;
- signed append-only hash-chain log;
- verification script that detects changed, removed, or reordered records.

Important boundary: Step 3 is not blockchain. It is the required audit baseline before implementing a blockchain-style audit layer.

## Step 3 Result

For the four injected tamper cases:

| Log type | Tamper cases | Self-detected |
|---|---:|---:|
| Mutable centralized log | 4 | 0 |
| Signed hash-chain log | 4 | 4 |

## Step 4: Permissioned Blockchain-Style Audit

Step 4 builds the permissioned blockchain-style audit abstraction and compares it with the signed hash-chain baseline.

```bash
python3 prototype/synthetic_access_sim/blockchain_audit.py \
  --input-run-id 20260527_step3_audit_baselines_seed42 \
  --run-id 20260527_step4_permissioned_blockchain_audit_seed42
```

The output is written to:

```text
prototype/runs/<run_id>/
  config.yaml
  logs/blockchain_audit.log
  metrics.json
  artifacts/
    permissioned_audit_blocks.jsonl
    block_event_index.csv
    validator_set.json
    tampered_chains/
    blockchain_tamper_test_results.csv
    blockchain_detection_summary.csv
    comparison_with_step3_signed_log.csv
    dataset_manifest.json
    data_dictionary.md
    README.md
```

Important boundary: this is a permissioned PoA/PBFT-style simulation with known synthetic validators. It is not PoW, not PoS, and not a real deployed blockchain.

## Step 4 Result

| Method | Tamper cases | Detected |
|---|---:|---:|
| Mutable centralized log | 4 | 0 |
| Signed hash-chain log | 4 | 4 |
| Permissioned blockchain-style simulation | 5 | 5 |

Step 4 created:

- 20 blocks;
- 1000 event commitments;
- 4 synthetic validator nodes;
- 3-of-4 quorum endorsement rule.

## Next Step

Step 5 measures local latency and storage-overhead across the decision engine, signed audit log, and blockchain-style audit simulation.

## Step 5: Latency And Storage Overhead

```bash
python3 prototype/synthetic_access_sim/measure_overhead.py \
  --run-id 20260527_step5_latency_storage_overhead
```

The output is written to:

```text
prototype/runs/<run_id>/
  config.yaml
  logs/measure_overhead.log
  metrics.json
  artifacts/
    latency_summary.csv
    latency_samples.csv
    storage_overhead.csv
    overhead_comparison.csv
    dataset_manifest.json
    data_dictionary.md
    README.md
```

Important boundary: Step 5 measures local Python prototype overhead only. It is not a real CCTNS/ICJS, Hyperledger Fabric, or production blockchain benchmark.

## Step 5 Result

Local prototype summary for 1000 synthetic requests/events:

| Method | Build/decision p50 total ms | Verify p50 total ms | Storage bytes | Tamper detection |
|---|---:|---:|---:|---:|
| Policy oracle + rule-trace XAI | 14.384482 | n/a | 1555951 | n/a |
| Mutable log | 7.471083 | 0.671125 | 459815 | 0.0000 |
| Signed hash-chain log | 16.995791 | 9.101959 | 756860 | 1.0000 |
| Permissioned blockchain-style layer | 11.257625 | 2.476375 | 353497 | 1.0000 |

Important interpretation: the blockchain-style row measures the block/validator layer over already signed audit events. It is not the complete end-to-end system latency and not a network consensus benchmark.

## Next Step

Step 6 separates RBAC, ABAC/PBAC, signed-log, and blockchain-style methods into explicit baseline/proposed experiment modes.

## Step 6: Explicit Experiment Modes

```bash
python3 prototype/synthetic_access_sim/experiment_modes.py \
  --run-id 20260527_step6_experiment_modes_seed42
```

The output is written to:

```text
prototype/runs/<run_id>/
  config.yaml
  logs/experiment_modes.log
  metrics.json
  artifacts/
    experiment_mode_predictions.csv
    experiment_mode_comparison.csv
    decision_confusion_by_method.csv
    method_definitions.json
    dataset_manifest.json
    data_dictionary.md
    README.md
```

Methods compared:

1. RBAC + mutable log
2. ABAC/PBAC + mutable log
3. ABAC/PBAC + signed hash-chain log
4. ABAC/PBAC + permissioned blockchain-style audit
5. SEBA-XAI full: ABAC/PBAC + permissioned blockchain-style audit + XAI hash

Important boundary: Step 6 uses the Step 2 policy oracle as the deterministic expected label for synthetic requests. It is not real police access-control ground truth.

## Step 6 Result

| Method | Accuracy vs policy oracle | Audit tamper detection | XAI hash logged | Estimated build p50 ms |
|---|---:|---:|---:|---:|
| RBAC + mutable log | 0.2900 | 0.0000 | false | 8.298958 |
| ABAC/PBAC + mutable log | 1.0000 | 0.0000 | false | 21.745625 |
| ABAC/PBAC + signed hash-chain log | 1.0000 | 1.0000 | false | 31.270333 |
| ABAC/PBAC + blockchain-style audit | 1.0000 | 1.0000 | false | 42.527958 |
| SEBA-XAI full | 1.0000 | 1.0000 | true | 42.527958 |

Important interpretation: ABAC/PBAC modes match the oracle because the oracle defines the expected synthetic policy labels. This is not real-world police access-control accuracy.

## Step 7 Addition

Step 7 adds off-chain encrypted storage/pointer simulation and metadata-leakage analysis.

## Step 7: Off-Chain Storage And Metadata Leakage

```bash
python3 prototype/synthetic_access_sim/offchain_storage.py \
  --run-id 20260527_step7_offchain_encrypted_pointers_seed42
```

The output is written to:

```text
prototype/runs/<run_id>/
  config.yaml
  logs/offchain_storage.log
  metrics.json
  artifacts/
    offchain_record_store.jsonl
    offchain_pointer_table.csv
    full_metadata_ledger.csv
    minimized_commitment_ledger.csv
    metadata_leakage_comparison.csv
    offchain_tamper_test_results.csv
    storage_overhead_offchain.csv
    offchain_storage_summary.csv
    dataset_manifest.json
    data_dictionary.md
    README.md
```

Important boundary: Step 7 uses deterministic demo encryption for reproducibility. It demonstrates the storage/pointer design and metadata-exposure measurement, not production cryptography.

## Step 7 Result

| Metric | Value |
|---|---:|
| Synthetic off-chain record payloads | 900 |
| Request pointer commitments | 1000 |
| Full metadata clear sensitive columns | 19 |
| Minimized metadata clear sensitive columns | 0 |
| Full metadata exposure score | 1.0000 |
| Minimized metadata exposure score | 0.0000 |
| Controlled tamper cases detected | 7/7 |

Important interpretation: the metadata score is a schema-level exposure measure. It is not differential privacy, anonymity, or legal-compliance proof.

## Step 8: Policy Configuration And Ablation

```bash
python3 prototype/synthetic_access_sim/policy_ablation.py \
  --run-id 20260528_step8_policy_config_ablation_seed42
```

The output is written to:

```text
prototype/runs/<run_id>/
  config.yaml
  logs/policy_ablation.log
  metrics.json
  artifacts/
    policy_config_snapshot.json
    policy_rule_group_summary.csv
    policy_ablation_predictions.csv
    policy_ablation_comparison.csv
    policy_ablation_by_scenario.csv
    policy_ablation_effects.csv
    dataset_manifest.json
    data_dictionary.md
    README.md
```

The policy config is:

```text
prototype/synthetic_access_sim/policies/seba_xai_policy_v1.json
```

Important boundary: Step 8 compares methods against the deterministic Step 2 policy oracle. This is policy-oracle consistency, not real police access-control accuracy.

## Step 8 Result

| Method | Accuracy vs policy oracle | False allows | False denies | False escalations |
|---|---:|---:|---:|---:|
| RBAC role/action only | 0.2900 | 656 | 54 | 0 |
| Full configured PBAC/ABAC | 1.0000 | 0 | 0 | 0 |
| No approval rules | 0.9470 | 0 | 0 | 53 |
| No assignment rules | 0.9350 | 0 | 0 | 65 |
| No sealed-record rules | 0.8680 | 32 | 0 | 100 |
| No privacy rules | 0.9540 | 46 | 0 | 0 |
| No jurisdiction rules | 0.9920 | 8 | 0 | 0 |
| No sensitivity rules | 0.9560 | 19 | 0 | 25 |
| No emergency/network rules | 0.9990 | 1 | 0 | 0 |
| No context-review fallback | 0.9850 | 15 | 0 | 0 |

Important interpretation: false allows are the highest-risk error because the method grants access where the reference policy would deny or escalate.

## Next Step

Add paper-ready plots/tables and a short experiment narrative for the prototype results.
