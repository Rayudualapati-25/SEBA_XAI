# Iteration 012: Permissioned Blockchain-Style Audit Simulation

Date: 2026-05-27  
Status: Step 4 implementation complete  
Scope: local permissioned audit-chain simulation over signed audit events

## What Was Done

Implemented the blockchain-style audit component for the SEBA-XAI prototype:

- added `prototype/synthetic_access_sim/blockchain_audit.py`;
- read Step 3 signed audit events from `prototype/runs/20260527_step3_audit_baselines_seed42/artifacts/signed_hash_chain_log.csv`;
- grouped 1000 signed audit events into 20 blocks using block size 50;
- computed event commitment hashes and Merkle roots;
- linked blocks using previous block hashes;
- added synthetic validator signatures;
- added 3-of-4 quorum endorsements from synthetic agency validators;
- injected controlled chain tampering cases;
- verified whether chain validation detected each tamper case;
- saved the run under `prototype/runs/20260527_step4_permissioned_blockchain_audit_seed42/`;
- saved summary table under `prototype/results/tables/blockchain_audit_step4_summary.csv`.

## Blockchain Type

The prototype uses a **permissioned blockchain-style simulation**.

It is closest to:

- Proof-of-Authority style known validators;
- PBFT-style quorum approval concept;
- Hyperledger Fabric-style permissioned audit thinking.

It is not:

- Proof of Work;
- Proof of Stake;
- public blockchain mining;
- a real Hyperledger Fabric deployment;
- a legal or operational deployment claim.

## Synthetic Validators

The simulated validator set contains four known agencies:

| Validator ID | Agency Type |
|---|---|
| `POLICE_AUDIT_NODE` | Police |
| `FORENSIC_AUDIT_NODE` | Forensic |
| `PROSECUTION_AUDIT_NODE` | Prosecution |
| `COURT_ICJS_AUDIT_NODE` | Court/ICJS-style |

Quorum rule:

```text
3 of 4 validators must endorse a block.
```

The signatures use deterministic demo HMAC keys only for reproducibility. This is not production-grade key management.

## Generated Artifacts

```text
prototype/runs/20260527_step4_permissioned_blockchain_audit_seed42/
  config.yaml
  logs/blockchain_audit.log
  metrics.json
  artifacts/
    README.md
    data_dictionary.md
    dataset_manifest.json
    permissioned_audit_blocks.jsonl
    block_event_index.csv
    validator_set.json
    blockchain_tamper_test_results.csv
    blockchain_detection_summary.csv
    comparison_with_step3_signed_log.csv
    tampered_chains/
```

## What The Blocks Store

The chain stores audit commitments and metadata only:

- block number;
- previous block hash;
- event commitment hashes;
- Merkle root;
- validator ID;
- validator agency type;
- block payload hash;
- validator signature;
- quorum endorsements;
- final block hash.

It does not store:

- raw police records;
- FIR text;
- witness/victim data;
- raw XAI explanation text.

## Tamper Cases

Five controlled tamper cases were generated:

| Tamper case | Meaning |
|---|---|
| `changed_event_commitment` | Event commitment hash inside a block was changed. |
| `deleted_event_commitment` | One event commitment was removed from a block. |
| `changed_merkle_root` | Merkle root was modified. |
| `changed_validator_signature` | Validator signature was modified. |
| `reordered_blocks` | Two blocks were swapped. |

## Result Summary

This is a controlled local prototype result, not proof of production blockchain security.

| Method | Tamper cases | Detected | Detection rate |
|---|---:|---:|---:|
| mutable centralized log | 4 | 0 | 0.0000 |
| signed hash-chain log | 4 | 4 | 1.0000 |
| permissioned blockchain-style simulation | 5 | 5 | 1.0000 |

Validation checks:

- original blockchain-style chain verified as valid;
- 20 blocks were created;
- 1000 event commitments were indexed;
- 4 synthetic validators were defined;
- no raw explanation text was stored in blocks;
- all five controlled chain tamper cases were detected;
- Python syntax check passed with `python3 -m py_compile`.

## What Worked

- The blockchain-style layer now anchors Step 3 signed event hashes into blocks.
- Merkle roots detect changed or deleted event commitments.
- Previous block hashes detect reordered blocks.
- Validator and quorum signatures detect signature tampering.
- The comparison table now includes mutable log, signed hash-chain log, and permissioned blockchain-style audit.

## What Is Weak Or Missing

- This is still a local simulation, not Hyperledger Fabric.
- There is no network, ordering service, MSP, channel policy, private data collection, or smart contract.
- There is no Byzantine fault simulation or validator-key compromise test.
- The demo HMAC keys are deterministic and not production key management.
- No latency, throughput, storage overhead, or metadata leakage measurement has been run yet.

## Next Step

Add measurement instrumentation:

- decision latency for Step 2;
- audit-log write and verification time for Step 3;
- block creation and verification time for Step 4;
- storage size per request/event/block;
- comparison table for overhead.

This should become the first quantitative evaluation artifact.
