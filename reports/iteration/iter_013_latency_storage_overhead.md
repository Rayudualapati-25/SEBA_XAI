# Iteration 013: Latency And Storage Overhead Measurement

Date: 2026-05-27  
Status: Step 5 implementation complete  
Scope: local prototype latency and storage measurement

## What Was Done

Implemented local overhead measurement for the SEBA-XAI prototype:

- added `prototype/synthetic_access_sim/measure_overhead.py`;
- measured policy-oracle and rule-trace XAI decision latency;
- measured mutable-log creation/write and schema verification;
- measured signed hash-chain creation/write and verification;
- measured permissioned blockchain-style block creation/write and verification;
- measured storage size of key artifacts;
- saved the run under `prototype/runs/20260527_step5_latency_storage_overhead/`;
- saved summary table under `prototype/results/tables/latency_storage_step5_summary.csv`.

## Generated Artifacts

```text
prototype/runs/20260527_step5_latency_storage_overhead/
  config.yaml
  logs/measure_overhead.log
  metrics.json
  artifacts/
    README.md
    data_dictionary.md
    dataset_manifest.json
    latency_summary.csv
    latency_samples.csv
    storage_overhead.csv
    overhead_comparison.csv
    measured_outputs/
```

## Measurement Scope

The run measured 1000 synthetic requests/events and 20 simulated blockchain-style blocks.

Repeat setting:

```text
aggregate repeats = 7
```

The policy/XAI decision latency was sampled once per request. Audit and blockchain operations were repeated as aggregate local operations.

## Result Summary

These are local prototype measurements only.

| Method | Build/decision p50 total ms | Verify p50 total ms | Storage bytes | Tamper detection |
|---|---:|---:|---:|---:|
| policy oracle + rule-trace XAI | 14.384482 | n/a | 1555951 | n/a |
| mutable log | 7.471083 | 0.671125 | 459815 | 0.0000 |
| signed hash-chain log | 16.995791 | 9.101959 | 756860 | 1.0000 |
| permissioned blockchain-style layer | 11.257625 | 2.476375 | 353497 | 1.0000 |

Detailed latency:

- policy/XAI per-request p50: 0.013437 ms;
- policy/XAI per-request p95: 0.018048 ms;
- signed hash-chain per-event p50: 0.008208 ms;
- permissioned blockchain-style per-block p50: 0.350291 ms.

## Important Interpretation

The blockchain-style row measures the incremental block/validator layer over already signed audit events. It does not include the full policy decision, XAI generation, and signed-event creation pipeline.

The blockchain-style storage row uses:

- `permissioned_audit_blocks.jsonl`;
- `block_event_index.csv`;
- `validator_set.json`.

It does not include raw records or raw explanation text.

## What Worked

- The prototype now has quantitative local overhead evidence.
- The measurement script saves reproducible configs, logs, metrics, tables, and file hashes.
- The results separate latency, verification time, storage, and tamper detection.
- The report avoids claiming production performance.

## What Is Weak Or Missing

- No real network, database, CCTNS/ICJS API, Hyperledger Fabric, ordering service, or consensus latency is included.
- No concurrent load test has been run.
- No p95/p99 end-to-end workflow latency has been measured.
- No RBAC-only versus ABAC/PBAC policy baseline has been separated yet.
- The XAI layer is still deterministic rule-trace explanation, not trained-model attribution.

## Next Step

Create explicit baseline/proposed experiment modes:

- RBAC + mutable log;
- ABAC/PBAC + mutable log;
- ABAC/PBAC + signed hash-chain log;
- ABAC/PBAC + permissioned blockchain-style audit;
- ABAC/PBAC + permissioned blockchain-style audit + XAI artifact hash.

Then produce one consolidated comparison table with correctness, tamper detection, latency, and storage.
