# Iteration 058: Hyperledger Fabric Mac Setup And Live Audit Event Submission

Date: 2026-07-10

## Purpose

Set up Hyperledger Fabric locally on the Mac and connect the SEBA-XAI prototype to an actual permissioned blockchain-style ledger. This iteration moves the prototype beyond an in-memory or file-only audit simulation by committing commitment-only access-decision audit events to a live Fabric test network.

## What Was Set Up

- Installed and verified Docker CLI, Docker Compose, and Colima.
- Started Colima as the local container runtime.
- Installed Hyperledger Fabric samples, binaries, and Docker images in `/Users/venkatrayudu/Workspace/Research/seba_fabric_workspace`.
- Started the Fabric `test-network`.
- Created channel `seba`.
- Deployed chaincode `seba-audit` version `1.0`.
- Confirmed chaincode definition on both `Org1MSP` and `Org2MSP`.

The Fabric runtime was moved outside the repo because the repository path contains a space (`codex research`), and Fabric sample shell scripts do not handle that path reliably.

## Scripts Updated

- `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/scripts/_project_docker_config.sh`
- `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/scripts/00_check_prereqs.sh`
- `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/scripts/01_bootstrap_fabric.sh`
- `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/scripts/02_start_network.sh`
- `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/scripts/03_prepare_events.sh`
- `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/scripts/04_submit_events.sh`
- `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/scripts/06_stop_network.sh`
- `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/tools/build_audit_events.py`
- `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/config/fabric_paths.env`

## Evidence Produced

- Event preparation:
  `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/runs/20260710_fabric_audit_event_prep/`
- Fabric submission result:
  `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/runs/20260710_fabric_submit/artifacts/fabric_submit_results.json`
- Queried ledger event:
  `/Users/venkatrayudu/Workspace/Research/codex research/prototype/fabric_audit_chain/runs/20260710_fabric_query/artifacts/query_first_event.json`
- Experiment run record:
  `/Users/venkatrayudu/Workspace/Research/codex research/experiments/runs/20260710_hyperledger_fabric_setup.json`
- Summary table:
  `/Users/venkatrayudu/Workspace/Research/codex research/results/tables/fabric_actual_setup_summary.csv`

## Result Summary

| Metric | Value |
|---|---:|
| Events prepared | 25 |
| Events validated | 25 |
| Events submitted to Fabric | 25 |
| Allow / deny / escalate | 3 / 8 / 14 |
| Raw records on-chain | false |
| Total submit elapsed time | 50,650.77 ms |
| p50 submit latency | 2,023.05 ms |
| p95 submit latency | 2,027.81 ms |

First queried request hash:
`f02dea6f047664266cb38f7289c300a3e2c4bb5d36154341096002448c918bd3`

First Fabric transaction ID:
`594199f53df43cf8b5c1f43250a9ee3232fcf182e36f530c914beafc7a33d336`

## What Worked

- The Mac can now run a local Hyperledger Fabric test network through Colima.
- The SEBA-XAI audit chaincode was deployed successfully.
- Synthetic access-decision audit events were transformed into commitment-only Fabric events.
- The prototype submitted 25 events to Fabric and queried one event back from the ledger.
- The on-chain event contains hashes, policy version, decision code, explanation hash, record commitment, and Fabric transaction metadata.

## What Is Still Weak

- This is a local Fabric test-network result, not a real multi-agency deployment.
- The workload is synthetic and derived from the earlier SEBA-XAI policy-oracle prototype.
- The measured latency is useful for prototype evidence only; it should not be presented as production performance.
- No real police, FIR, CCTNS, or ICJS data was used.

## Research Claim Now Supported

The project can now honestly claim that the proposed audit layer has been tested on a real local Hyperledger Fabric permissioned test network, where commitment-only SEBA-XAI access-decision events are submitted and read back without placing raw sensitive records on-chain.

## Research Claim Still Not Supported

The project still cannot claim production readiness, legal compliance, deployment in CCTNS/ICJS, real police-data validation, or superior performance over operational blockchain systems.

## Next Step

Run the same event workload against the file-based signed hash-chain audit layer and compare:

- write latency,
- verification latency,
- tamper detection,
- audit reconstruction completeness,
- storage overhead,
- metadata exposure.

This comparison will make the paper stronger because Fabric will no longer stand alone; it will be evaluated against simpler audit baselines.
