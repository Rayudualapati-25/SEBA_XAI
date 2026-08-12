# Start Here: SEBA-XAI Repository Guide

Revised: 2026-08-09

This repository contains the SEBA-XAI work in full: the implemented system, the
earlier simulation study that preceded it, literature and dataset notes,
experiments, result tables, paper drafts, and learning material.

**SEBA-XAI is a working Hyperledger Fabric system**, not a design document and
not a simulation. It runs on five organisations with real certificate
authorities and a 3-of-5 endorsement policy.

It is **not** a police deployment. All records and identities are synthetic, no
real case data is used, and the network runs on a single host.

Two bodies of work live here and must never be conflated:

| | What it is | Where |
|---|---|---|
| **The system** | A running Fabric network where access decisions are executed on-chain | `seba_fabric_workspace/crime-records-network/` |
| **The earlier study** | A synthetic five-seed adversarial benchmark that came before the system | `src/seba/` |

## Open These First

1. `README.md` — what the system is, what is new, what was measured.
2. `seba_fabric_workspace/crime-records-network/README.md` — how to run it.
3. `seba_fabric_workspace/crime-records-network/docs/architecture.md` — how it works.
4. `CONTRIBUTION.md` — the contribution statement, with each claim mapped to the code that implements it, and the novelty boundary.
5. `GLOSSARY.md` — every term used in the project, defined as it is used here.
6. `TESTING.md` — how it is tested and what each kind of test cannot see.
7. `results/FINDINGS.md` — results and limitations of the earlier simulation study.
8. `research_pack/05_research_gap.md` — the gap and novelty position.
9. `REPRODUCE.md` — how to rerun the experiments.

## Main Folders

| Folder | Purpose |
|---|---|
| `seba_fabric_workspace/crime-records-network/` | **The system.** Chaincode, network config, backend, frontend, experiments. |
| `seba_fabric_workspace/prototype/` | Earlier Python prototype runs, kept as a historical record. |
| `src/seba/` | Python package for the earlier simulation study: schema, attacks, NS-PI drift, baselines, XAI quality checks. |
| `research_pack/` | Problem framing, literature review, datasets, gap, architecture, methodology, ethics. |
| `scripts/` | Reproduction, aggregation, and figure-generation scripts for the Python study. |
| `tests/` | Unit tests for the Python package. |
| `experiments/` | Experiment plans and run metadata. |
| `results/` | Result tables, plots, and findings from the Python study. |
| `reports/iteration/` | Iteration-by-iteration progress notes. |
| `papers/icdcn2027/` | Current paper build, ACM format. |
| `papers/final_paper/` | Paper workspace: section drafts, claim tables, supervisor memos. |
| `sources/` | Literature and dataset inventory. |
| `Learn/` | Learning syllabus and notes on blockchain and XAI fundamentals. |

## Current Technical Status

Built and tested:

- Five-organisation Fabric 2.5.16 network, per-org CA and CouchDB peer,
  `MAJORITY` 3-of-5 endorsement on channel `crimechannel`.
- On-chain policy evaluation: the authorisation decision is the endorsed
  transaction, not a decision made elsewhere and logged.
- Certificate-bound subject attributes, so a requester cannot assert their own
  authority.
- Decision and explanation artifact committed atomically and hash-linked.
- Escalation with separation of duties.
- Off-chain record storage under an on-chain SHA-256 commitment; private data
  collection for evidence detail.
- Read and search accountability via an off-chain hash chain anchored on-chain.
- Local explanation rendering that reads the decision back from the ledger and
  can never influence it.
- 70 chaincode tests (~97% coverage), 48 API tests against the running network,
  an 11-step walkthrough, a 9-section ledger inspection, and a 6-attack replay.
- Latency and storage measured over five seeds.
- Earlier simulation study: attack catalogue, severity-weighted scorer,
  comparison defences, NS-PI drift detection, sensitivity and stress analysis.

Not done:

- Experiments on real CCTNS, ICJS, FIR, or police access-log data.
- Multi-host deployment; the network is single-host with one ordering node.
- Replay of the certificate-authority compromise against the live network.
- Legal-compliance proof, production security validation, or a real pilot.
- Formal privacy analysis; metadata exposure uses a schema-level proxy.

## Current Core Finding

> Three of five organisations must agree before a decision is committed, and
> they do agree — but they all evaluate the same input. Endorsement therefore
> establishes agreement on a transaction, not the integrity of the premises the
> transaction was evaluated against. A compromised departmental certificate
> authority produces a decision that is unanimously endorsed, cryptographically
> valid, fully consistent, and never authorised by policy. Integrity and
> correctness are separate properties.

The earlier simulation study reached the same conclusion by a different route:
every integrity-based defence detected ordinary tampering but obtained 0.00
detection against a validly re-signed log, while methods examining the decisions
themselves obtained 1.00 under stronger visibility assumptions.

The system result is currently analytical; the simulation result is measured.
That distinction must be preserved in any write-up.

## What Goes To Git

Tracked: source code, chaincode, network configuration, tests, scripts, paper
source, result tables, plots, reports, experiment plans, research notes.

Not committed: downloaded paper PDFs, regenerable prototype run folders,
crypto material and wallets, `node_modules`, and cache files such as
`.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `__pycache__`, `.coverage`,
and `.DS_Store`.

## Hard Boundary

Do not claim real police deployment, legal compliance, production security,
state-of-the-art performance, performance on real police data, improvement over
CCTNS or ICJS, formal privacy guarantees, or crime and suspect prediction.

Do not present the system's measurements and the simulation study's results as
one evidence base. They were produced by different artifacts under different
assumptions.
