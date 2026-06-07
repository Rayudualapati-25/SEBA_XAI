# Iteration 017: Prototype Hardening After Code Review

Date: 2026-05-28  
Status: targeted hardening complete  
Scope: anchored pointer verification, artifact-derived detection rates, and clearer latency metrics

## What Was Done

This iteration fixed the main prototype weaknesses found during project review:

- strengthened Step 7 off-chain pointer verification;
- anchored pointer fields to Step 2 policy/XAI artifacts and Step 4 block-index artifacts;
- added recomputed pointer-commitment tamper cases;
- changed Step 6 experiment comparison to read tamper detection rates from generated artifacts;
- changed Step 5 latency output to use a clearer `ms_per_unit_p50` field;
- changed Step 5 policy/XAI timing from a single summed pass to repeated aggregate p50 timing;
- regenerated Step 5, Step 6, and Step 7 artifacts.

## Files Changed

```text
prototype/synthetic_access_sim/offchain_storage.py
prototype/synthetic_access_sim/experiment_modes.py
prototype/synthetic_access_sim/measure_overhead.py
```

## Regenerated Evidence

```text
prototype/runs/20260527_step5_latency_storage_overhead/
prototype/runs/20260527_step6_experiment_modes_seed42/
prototype/runs/20260527_step7_offchain_encrypted_pointers_seed42/
prototype/results/tables/latency_storage_step5_summary.csv
prototype/results/tables/experiment_modes_step6_comparison.csv
prototype/results/tables/offchain_storage_step7_summary.csv
```

## Result Summary

The off-chain pointer tamper suite now has 10 controlled tamper cases. All 10 were detected by local verification.

Important examples:

| Tamper case | Why it matters | Detection reason |
|---|---|---|
| `changed_explanation_hash_recomputed_commitment` | Tests whether a forged pointer can hide by recomputing its own commitment. | Fails because `explanation_hash` no longer matches the Step 2 labeled request artifact. |
| `changed_event_commitment_recomputed_pointer` | Tests whether a pointer can be redirected to a different audit event. | Fails because `event_commitment_hash` no longer matches the Step 4 block-event index. |
| `changed_storage_node_recomputed_commitment` | Tests whether an off-chain location can be changed with a recomputed pointer hash. | Fails because `storage_node_id` no longer matches deterministic storage-node assignment. |

Step 6 now records detection evidence from files instead of hard-coding the rates:

```text
Step 3 source: prototype/runs/20260527_step3_audit_baselines_seed42/artifacts/audit_detection_summary.csv
Step 4 source: prototype/runs/20260527_step4_permissioned_blockchain_audit_seed42/artifacts/blockchain_detection_summary.csv
Step 7 source: prototype/runs/20260527_step7_offchain_encrypted_pointers_seed42/artifacts/offchain_tamper_test_results.csv
```

## Verification

Commands run:

```bash
python3 -m py_compile prototype/synthetic_access_sim/generate_synthetic_requests.py prototype/synthetic_access_sim/policy_oracle.py prototype/synthetic_access_sim/audit_baseline.py prototype/synthetic_access_sim/blockchain_audit.py prototype/synthetic_access_sim/measure_overhead.py prototype/synthetic_access_sim/experiment_modes.py prototype/synthetic_access_sim/offchain_storage.py prototype/synthetic_access_sim/policy_ablation.py
python3 prototype/synthetic_access_sim/measure_overhead.py --run-id 20260527_step5_latency_storage_overhead --repeats 7
python3 prototype/synthetic_access_sim/offchain_storage.py --run-id 20260527_step7_offchain_encrypted_pointers_seed42
python3 prototype/synthetic_access_sim/experiment_modes.py --run-id 20260527_step6_experiment_modes_seed42 --repeats 7
```

Additional consistency check:

```text
files_exist=True
offchain_detected=10/10
unmeasured_rates=[]
latency_header_has_ms_per_unit_p50=True
```

## What Worked

- Pointer verification is now stronger because it checks against generated source artifacts, not only against the pointer row itself.
- Step 6 comparison is more reproducible because detection rates are read from CSV artifacts.
- Latency output is clearer because per-unit p50 is separated from aggregate total p50.

## What Is Still Weak Or Missing

- The prototype still uses deterministic demo HMAC keys and demo encryption, not production cryptography.
- The blockchain layer is still a local permissioned PoA/PBFT-style simulation, not Hyperledger Fabric.
- Stronger attacker cases such as compromised quorum keys are not implemented.
- No real CCTNS/ICJS/FIR/police data is used.
- The policy oracle is synthetic and should not be claimed as official Indian police access policy.

## Next Step

Prepare paper-ready experiment tables and plots from the current evidence:

- false allows/denies/escalations by method;
- tamper detection by audit design;
- metadata exposure comparison;
- local latency/storage overhead;
- policy ablation effects.

