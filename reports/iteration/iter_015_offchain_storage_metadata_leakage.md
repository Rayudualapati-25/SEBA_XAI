# Iteration 015: Off-Chain Storage And Metadata Leakage

Date: 2026-05-27  
Status: Step 7 implementation complete  
Scope: off-chain encrypted payload simulation, pointer commitments, and metadata-exposure comparison

## What Was Done

Implemented the next SEBA-XAI prototype step:

- added `prototype/synthetic_access_sim/offchain_storage.py`;
- created encrypted synthetic payload envelopes for records kept off-chain;
- created per-request pointer commitments that bind request, payload, decision, explanation, and audit-block references;
- generated a full metadata ledger view for comparison;
- generated a minimized commitment ledger view;
- measured schema-level metadata exposure;
- ran controlled tamper tests for payload and pointer integrity;
- saved the run under `prototype/runs/20260527_step7_offchain_encrypted_pointers_seed42/`;
- saved summary tables under `prototype/results/tables/`, `results/tables/`, and `experiments/runs/`.

## Generated Artifacts

```text
prototype/runs/20260527_step7_offchain_encrypted_pointers_seed42/
  config.yaml
  logs/offchain_storage.log
  metrics.json
  artifacts/
    README.md
    data_dictionary.md
    dataset_manifest.json
    offchain_record_store.jsonl
    offchain_pointer_table.csv
    full_metadata_ledger.csv
    minimized_commitment_ledger.csv
    metadata_leakage_comparison.csv
    offchain_tamper_test_results.csv
    storage_overhead_offchain.csv
    offchain_storage_summary.csv
```

Additional result records:

```text
prototype/results/tables/offchain_storage_step7_summary.csv
results/tables/offchain_storage_step7_summary.csv
experiments/runs/20260527_step7_offchain_encrypted_pointers_seed42.json
```

## Result Summary

| Metric | Value |
|---|---:|
| Synthetic off-chain record payloads | 900 |
| Request pointer commitments | 1000 |
| Full metadata clear sensitive columns | 19 |
| Minimized metadata clear sensitive columns | 0 |
| Full metadata exposure score | 1.0000 |
| Minimized metadata exposure score | 0.0000 |
| Controlled tamper cases detected | 7/7 |

## Metadata Leakage Result

| Ledger design | Events | Columns | Clear sensitive columns | Hashed/commitment columns | Exposure score |
|---|---:|---:|---:|---:|---:|
| Full metadata ledger | 1000 | 27 | 19 | 4 | 1.0000 |
| Minimized commitment ledger | 1000 | 15 | 0 | 12 | 0.0000 |

The full metadata ledger exposes clear fields such as role, station, record type, case type, sensitivity level, privacy flags, purpose, action, decision, reason code, and approval requirement. The minimized ledger replaces these with hashes and commitments.

## Tamper Test Result

Controlled tamper cases detected:

- changed ciphertext;
- changed payload hash;
- deleted off-chain store record;
- changed pointer commitment;
- changed payload hash in pointer;
- changed explanation hash in pointer;
- changed storage node.

All seven controlled tamper cases were detected by local verification.

## Interpretation

This step fills the missing off-chain storage part of the SEBA-XAI architecture. It supports the design claim that raw records should not be stored on the audit chain. The blockchain-style audit layer can point to hashes and commitments, while the encrypted synthetic payload remains off-chain.

The metadata result is useful because it shows a measurable reason for minimization. A naive audit ledger can expose sensitive context even if raw records are not stored on-chain. The minimized design reduces direct schema-level exposure while still preserving verifiable payload, decision, explanation, and block references.

## What Worked

- The prototype now has a storage/pointer layer linked to Step 2 decision/XAI hashes and Step 4 audit block references.
- The minimized ledger has zero clear sensitive columns under the current schema-level metric.
- Payload and pointer tampering is detectable through recomputed hashes and commitments.
- The run creates reproducible artifacts and a root experiment record.

## What Is Weak Or Missing

- The encryption is deterministic demo encryption for reproducibility, not production-grade cryptography.
- The metadata exposure score is schema-level only; it is not differential privacy, anonymity, or a legal-compliance proof.
- Stable hashes can still allow linkage if an attacker has auxiliary knowledge.
- No key rotation, HSM, access-token exchange, storage service, or Fabric private data collection exists yet.
- No concurrency/load test has been run.

## Next Step

Implement formal PBAC policy configuration files and a policy ablation:

- move policy dimensions into structured YAML/JSON;
- test RBAC-only, RBAC+jurisdiction, RBAC+sensitivity, RBAC+approval, and full ABAC/PBAC;
- measure false allows, false denies, escalations, and latency for each ablation;
- update the experiment-mode comparison so the security/access-control contribution is clearer.
