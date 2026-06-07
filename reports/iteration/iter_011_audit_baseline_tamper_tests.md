# Iteration 011: Audit Baselines And Tamper Tests

Date: 2026-05-27  
Status: Step 3 implementation complete  
Scope: mutable centralized log versus signed append-only hash-chain log

## What Was Done

Implemented the first audit layer baseline for the SEBA-XAI prototype:

- added `prototype/synthetic_access_sim/audit_baseline.py`;
- read Step 2 labeled requests from `prototype/runs/20260527_step2_policy_oracle_seed42/artifacts/labeled_access_requests.csv`;
- created a mutable centralized access log;
- created a signed append-only hash-chain log;
- injected controlled tampering cases;
- verified whether each log could detect tampering by itself;
- saved the run under `prototype/runs/20260527_step3_audit_baselines_seed42/`;
- saved summary table under `prototype/results/tables/audit_baseline_step3_summary.csv`.

## Generated Artifacts

```text
prototype/runs/20260527_step3_audit_baselines_seed42/
  config.yaml
  logs/audit_baseline.log
  metrics.json
  artifacts/
    README.md
    data_dictionary.md
    dataset_manifest.json
    mutable_access_log.csv
    signed_hash_chain_log.csv
    tamper_test_results.csv
    audit_detection_summary.csv
    tampered_logs/
      mutable/
      signed_hash_chain/
```

## What The Audit Logs Contain

The audit logs store metadata and hashes only:

- event sequence;
- request ID;
- requester hash;
- requester station;
- target record hash;
- decision;
- reason code;
- policy version;
- request content hash;
- decision hash;
- explanation hash;
- audit anchor hash.

The signed hash-chain log additionally stores:

- event payload hash;
- previous event hash;
- event hash;
- demo HMAC signature;
- audit log version.

## Tamper Cases

Four controlled tamper cases were generated:

| Tamper case | Meaning |
|---|---|
| `changed_decision` | Decision value was changed after logging. |
| `deleted_event` | One audit event was removed. |
| `changed_explanation_hash` | Explanation hash was modified. |
| `reordered_events` | Two events were swapped. |

## Result Summary

This is a local audit-baseline result, not a blockchain result.

| Log type | Tamper cases | Self-detected | Self-detection rate |
|---|---:|---:|---:|
| mutable centralized log | 4 | 0 | 0.0000 |
| signed hash-chain log | 4 | 4 | 1.0000 |

Validation checks:

- 1000 audit events written to the mutable log;
- 1000 audit events written to the signed hash-chain log;
- original mutable log passed schema validation;
- original signed hash-chain passed full hash/signature validation;
- no raw explanation text was stored in the audit log;
- no empty signed-log event hashes or signatures were found;
- Python syntax check passed with `python3 -m py_compile`.

## What Worked

- The mutable log shows why a normal centralized log is a weak baseline for tamper evidence.
- The signed hash-chain detected all injected tamper cases in this controlled setting.
- The signed log uses Step 2 hashes instead of raw sensitive content.
- The output now prepares a clean comparison point for the blockchain-style audit layer.

## What Is Weak Or Missing

- This is not blockchain and does not include consensus, replication, channels, smart contracts, or Hyperledger Fabric.
- The HMAC key is deterministic and demo-only for reproducibility, not production key management.
- Tampering is synthetic and controlled.
- No latency, throughput, metadata leakage, or multi-node failure experiment has been run yet.
- No RBAC/ABAC/PBAC baseline separation has been implemented yet.

## Next Step

Implement a blockchain-style audit abstraction:

- create a simple permissioned-ledger simulation with organization IDs;
- store only audit commitments, not raw records;
- compare the ledger-style audit output with the signed hash-chain baseline;
- run the same tamper cases;
- then add latency and storage-overhead measurements.
