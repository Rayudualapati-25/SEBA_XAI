# SEBA-XAI Fabric Audit Chain

This folder is the hands-on blockchain extension for SEBA-XAI.

Purpose: move the current simulated blockchain audit step toward an actual
permissioned blockchain prototype using Hyperledger Fabric.

Important boundary:

- No real police, CCTNS, ICJS, FIR, victim, witness, or case data is used.
- Raw records are not written to blockchain.
- The blockchain stores audit commitments only.
- This folder does not replace the existing synthetic prototype.

## What This Implements

```text
SEBA-XAI synthetic request
  -> policy decision and XAI trace
  -> minimal audit event builder
  -> Hyperledger Fabric chaincode
  -> Fabric ledger stores commitment-only access-decision evidence
```

The chaincode records:

- request ID hash;
- policy version;
- decision label: `allow`, `deny`, or `escalate`;
- primary reason code;
- decision hash;
- explanation hash;
- record commitment;
- audit anchor hash;
- approval reference hash;
- decisive-attribute set hash;
- source prototype run ID;
- Fabric transaction metadata.

It deliberately does not record:

- raw FIR or police record text;
- requester name;
- officer ID;
- target record ID;
- natural-language XAI explanation;
- victim, witness, juvenile, or case details.

## Folder Layout

```text
prototype/fabric_audit_chain/
  README.md
  chaincode/javascript/          Hyperledger Fabric smart contract
  client/                        Fabric Gateway submit/query client
  config/                        environment templates
  docs/                          schema and manual demo guide
  scripts/                       end-to-end command scripts
  tools/                         local event preparation/validation tools
  runs/                          generated local run artifacts
```

## Current Machine Status

As of 2026-07-10, this Mac has run the Fabric prototype successfully using
Colima as the local Docker runtime. The working Fabric runtime is stored outside
the repository at:

```text
/Users/venkatrayudu/Workspace/Research/seba_fabric_workspace
```

This separate runtime path is intentional. The repository folder name contains a
space (`codex research`), and the Fabric sample shell scripts do not reliably
handle paths with spaces.

## Quick Start: Local Event Preparation

From the repository root:

```bash
bash prototype/fabric_audit_chain/scripts/03_prepare_events.sh
python3 prototype/fabric_audit_chain/tools/validate_audit_events.py \
  --input prototype/fabric_audit_chain/runs/20260702_fabric_audit_event_prep/artifacts/fabric_audit_events.jsonl
```

This creates commitment-only audit events from the existing SEBA-XAI synthetic
policy-oracle output.

## Full Fabric Run On This Mac

Start Colima if it is not already running, then run:

```bash
colima start --cpu 4 --memory 8 --disk 60
bash prototype/fabric_audit_chain/scripts/00_check_prereqs.sh
bash prototype/fabric_audit_chain/scripts/01_bootstrap_fabric.sh
bash prototype/fabric_audit_chain/scripts/02_start_network.sh
bash prototype/fabric_audit_chain/scripts/03_prepare_events.sh
bash prototype/fabric_audit_chain/scripts/04_submit_events.sh
```

To query one event, copy a `requestIdHash` from the generated JSONL file and run:

```bash
bash prototype/fabric_audit_chain/scripts/05_query_event.sh <requestIdHash>
```

To stop the network:

```bash
bash prototype/fabric_audit_chain/scripts/06_stop_network.sh
```

## Why Fabric Is Used

SEBA-XAI is about inter-agency police and criminal-justice access governance.
That is closer to a permissioned consortium network than a public blockchain.
Hyperledger Fabric provides identities, organizations, channels, endorsement,
and private-network deployment patterns that are more suitable for this use
case than public PoW/PoS chains.

## Honest Claim

This folder now supports the following limited claim:

> SEBA-XAI audit commitments can be submitted to a permissioned Fabric ledger
> without placing raw sensitive records on-chain.

Evidence from the completed run is stored in:

- `runs/20260710_fabric_audit_event_prep/`
- `runs/20260710_fabric_submit/artifacts/fabric_submit_results.json`
- `runs/20260710_fabric_query/artifacts/query_first_event.json`
- `/Users/venkatrayudu/Workspace/Research/codex research/experiments/runs/20260710_hyperledger_fabric_setup.json`
- `/Users/venkatrayudu/Workspace/Research/codex research/reports/iteration/iter_058_hyperledger_fabric_mac_setup.md`

This still does not prove production security, legal compliance, real
CCTNS/ICJS integration, or real police-data performance.
