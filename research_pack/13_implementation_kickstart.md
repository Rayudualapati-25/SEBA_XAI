# 13 Implementation Kickstart

Generated: 2026-05-16  
Purpose: Convert the research pack into the first runnable implementation plan.  
Reviewer note: This file combines local repository inspection with an independent sub-agent review.

## Executive Decision

Start implementation with a **deterministic synthetic access-control and audit simulator**, not full Hyperledger Fabric and not crime prediction.

Prototype name:

```text
synthetic_access_sim
```

Why this is the smartest first move:

- The paper's strongest contribution is access governance, auditability, and XAI for sensitive inter-agency record requests.
- Real CCTNS/ICJS request logs and FIR-level records are not public.
- NCRB/BPRD data is useful for aggregate context, not the core access-governance experiment.
- A local simulator can produce baseline, proposed-method, ablation, tamper-test, and XAI-artifact evidence quickly.
- Full Fabric can be added after the experiment logic is stable.

Safe claim today:

> The repository contains a well-scoped, evidence-conscious research plan for SEBA-XAI, but implementation and experimental evidence are still missing. The immediate next build should be a deterministic synthetic access-control and audit simulator with baselines, tamper tests, XAI artifact logging, and reproducible run records.

## Repository Check: What Each File Is Doing

| File or folder | What it contains | Implementation status |
|---|---|---|
| `README.md` | Top-level SEBA-XAI framing and hard boundary. | Good guardrail; no implementation. |
| `research_brief.md` | Early scoping memo. | Useful background; superseded by the numbered files in this folder. |
| `00_problem_understanding.md` | Defines access-governance problem and research questions. | Strong implementation scope. |
| `01_literature_review.md` | Evidence-grounded literature review. | Good source base; some full-text verification remains. |
| `02_literature_matrix.csv` | Source matrix with contributions and limitations. | Good for related-work table. |
| `03_datasets.md` | Dataset discovery and suitability review. | Correctly selects synthetic workload as core. |
| `04_dataset_matrix.csv` | Dataset matrix. | Useful for paper and dataset decisions. |
| `05_research_gap.md` | Rejected weak angles and publishable gap. | Strong; should govern implementation scope. |
| `06_proposed_architecture.md` | SEBA-XAI architecture. | Best system blueprint. |
| `07_methodology.md` | Workload, oracle, baselines, proposed methods, ablations. | Ready to translate into code. |
| `08_experiment_plan.md` | Experiments and metrics. | Ready to become test/benchmark harness. |
| `09_evaluation_metrics.md` | Metric definitions. | Should become metrics code. |
| `10_ethics_security_legal.md` | Risk/legal/privacy boundaries. | Guardrails for claims. |
| `11_paper_outline.md` | IEEE-style paper outline. | Useful after results exist. |
| `12_five_day_learning_plan.md` | Learning plan. | Supportive, not implementation. |
| `sources/` | Source log, dataset inventory, literature matrix. | Traceability artifacts. |
| `experiments/experiment_plan.md` | Older experiment plan. | Consistent with current plan; keep as traceability. |
| `experiments/runs/README.md` | Required run-record format. | Placeholder; no runs yet. |
| `reports/iteration/iter_001_research_scoping.md` | Honest iteration report. | Says no datasets/prototypes/results. |
| `results/tables/` | Literature/dataset tables only. | No experiment tables yet. |
| `results/plots/README.md` | Plot rules. | No plots yet. |
| `papers/final_paper/README.md` | Paper drafting guardrail. | Correctly blocks results writing before experiments. |
| `papers/final_paper/introduction/` | Introduction plan, skeleton, draft, evidence register. | Good writing workspace; still pre-results. |
| `papers/*.pdf` | Local blockchain/digital-evidence papers. | Useful background for blockchain audit design. |

Ignored as implementation artifacts:

- `.DS_Store`
- `.git/` internals

## What Is Missing

There is currently no runnable research implementation.

Missing implementation pieces:

- no synthetic workload generator;
- no policy oracle;
- no RBAC baseline;
- no ABAC/PBAC baseline;
- no signed append-only log baseline;
- no Fabric-style audit abstraction;
- no full Hyperledger Fabric prototype;
- no off-chain encrypted payload pointer simulation;
- no XAI explanation artifact generator;
- no explanation hash verification;
- no tamper-injection tests;
- no latency/throughput benchmark harness;
- no metrics scripts;
- no experiment run folders;
- no plots;
- no ablation results;
- no downloaded/profiled NCRB/BPRD datasets.

This is not a weakness if handled honestly. It simply means the next phase must move from research planning to a small reproducible prototype.

## First Prototype: `synthetic_access_sim`

Build a local simulator that models sensitive inter-station/inter-agency access requests.

### Core Question

For each request:

> Should Officer A from Station X access Record R from Station Y, should the request be denied, or should it be escalated to a superior officer?

The simulator must also answer:

> Can the system reconstruct why the decision was made after logs, approvals, explanations, or payload pointers are tampered with?

### Entities To Generate

- states;
- districts;
- police stations;
- officers;
- superior officers;
- cases;
- records;
- approvals;
- credentials;
- access requests;
- audit events;
- explanation artifacts.

### Subject Attributes

- officer ID;
- role;
- rank;
- station;
- district/state jurisdiction;
- active or revoked credential;
- assigned case IDs;
- clearance/training flag;
- prior request count;
- recent denied/escalated request count.

### Object Attributes

- record ID;
- record type;
- case ID;
- originating station;
- jurisdiction;
- sensitivity level;
- victim flag;
- witness flag;
- juvenile flag;
- evidence-media flag;
- sealed/restricted flag;
- retention status.

### Environment Attributes

- timestamp;
- purpose;
- time window;
- emergency flag;
- court/prosecutor request flag;
- network/node status;
- policy version;
- approval token status.

## Minimum Policy Oracle

Build this before any ML or blockchain code. Without the oracle, metrics are meaningless.

Oracle outputs:

- `allow`
- `deny`
- `escalate`

Minimum deterministic rules:

- revoked credential -> `deny`;
- expired approval token -> `deny`;
- stale case assignment -> `deny`;
- sealed record without court/prosecutor authorization -> `deny`;
- juvenile/witness/victim-sensitive record -> `escalate`;
- cross-jurisdiction classified request -> `escalate`;
- emergency override -> `escalate` unless policy explicitly permits temporary access;
- valid case assignment + valid role/rank + correct jurisdiction + allowed purpose + valid time window + non-classified record -> `allow`.

Every oracle decision must include:

- decision;
- reason code;
- decisive attributes;
- failed rules;
- required approval if escalated;
- policy version.

## Baselines To Implement First

### Baseline A: RBAC + Mutable Log

Purpose:

- simplest baseline;
- role/rank-only access;
- mutable JSON/CSV/SQLite log.

Expected weakness:

- poor context handling;
- easy tamper case.

### Baseline B: ABAC/PBAC + Mutable Log

Purpose:

- contextual policy baseline;
- evaluates subject, object, action, and environment attributes.

Expected strength:

- stronger authorization correctness than RBAC.

Expected weakness:

- audit trail still mutable.

### Baseline C: ABAC/PBAC + Signed Append-Only Log

Purpose:

- strong non-blockchain audit baseline.

Implementation:

- each event includes `prev_hash`;
- event hash covers canonical event JSON;
- verification walks the hash chain.

Expected strength:

- detects many tampering cases with less complexity than blockchain.

Important:

- This baseline is not a weak strawman. If it performs well, report honestly.

## Proposed Methods To Implement After Baselines

### Proposed P1: Fabric-Style Audit + ABAC/PBAC

Do not start with full Fabric. First build a local ledger abstraction:

- append-only event store;
- organization ID;
- channel/collection label if needed;
- event hash;
- policy hash;
- request hash;
- actor credential hash.

This gives the paper a stable experiment harness before Fabric deployment complexity.

### Proposed P2: P1 + Off-Chain Encrypted Pointer Simulation

Store raw payload simulation off-chain:

- payload ID;
- encrypted payload placeholder;
- payload hash;
- access token;
- expiration;
- pointer hash on ledger.

Do not store raw FIRs, witness records, or personal data on-chain.

### Proposed P3: P2 + Superior Approval Commitments

Add:

- approval token ID;
- approving officer role/rank;
- approval timestamp;
- approval expiry;
- approval hash;
- revocation status.

### Proposed P4: P3 + XAI Artifact Logging

Add structured explanation JSON:

```json
{
  "request_id": "...",
  "decision": "allow|deny|escalate",
  "policy_version": "...",
  "reason_codes": ["..."],
  "decisive_attributes": ["..."],
  "failed_rules": ["..."],
  "missing_attributes": ["..."],
  "risk_score": 0.0,
  "role_view": "officer|superior|auditor",
  "human_override": false
}
```

Write only the explanation hash to the audit ledger.

## Suggested Implementation Layout

Create this later when implementation begins:

```text
src/
  synthetic_access_sim/
    __init__.py
    config.py
    models.py
    generator.py
    policy_oracle.py
    baselines.py
    audit_logs.py
    xai_artifacts.py
    tamper.py
    metrics.py
    runner.py
configs/
  synthetic_access_sim.yaml
scripts/
  run_synthetic_access_sim.py
  summarize_run.py
tests/
  test_policy_oracle.py
  test_audit_logs.py
  test_tamper_detection.py
```

Run outputs must go here:

```text
experiments/runs/<run_id>/
  config.yaml
  logs/
  metrics.json
  artifacts/
  README.md
```

Tables and plots:

```text
results/tables/
results/plots/
```

## First Configuration

Use a small configuration first:

```yaml
seed: 42
states: 3
districts_per_state: 3
stations_per_district: 5
officers_per_station: 20
cases_per_station: 30
records_per_case: 5
requests: 10000
sensitive_record_ratio: 0.25
classified_record_ratio: 0.10
cross_jurisdiction_ratio: 0.15
revoked_credential_ratio: 0.03
stale_assignment_ratio: 0.05
emergency_request_ratio: 0.02
court_prosecutor_request_ratio: 0.04
policy_version: v1
```

Scale later:

- 10 stations;
- 50 stations;
- 100 stations;
- 500 stations.

## Metrics To Produce In First Run

Access-control metrics:

- authorization accuracy;
- false allow rate;
- false deny rate;
- false escalation rate;
- escalation precision;
- policy coverage;
- reason-code completeness.

Audit metrics:

- audit completeness;
- audit reconstruction success;
- tamper detection rate;
- hash verification failure rate;
- false tamper alert rate.

Performance metrics:

- decision latency p50/p95/p99;
- audit write latency p50/p95/p99;
- throughput;
- storage overhead per request.

XAI metrics:

- explanation completeness;
- explanation hash verification;
- role-specific explanation coverage.

Metadata/privacy metrics:

- visible identifier count;
- metadata leakage score;
- sensitive-attribute inference proxy if implemented.

## Tamper Tests To Implement

Minimum tamper scenarios:

- delete mutable log row;
- alter decision from `deny` to `allow`;
- alter explanation artifact;
- alter payload pointer;
- replay approval token;
- backdate request timestamp;
- remove superior approval event;
- revoke credential after request and test reconstruction;
- simulate compromised station log;
- remove policy version record.

Expected pattern:

- mutable logs should fail many tamper checks;
- signed logs should catch event deletion/alteration;
- Fabric-style audit should catch ledger-commitment mismatch;
- none of the methods can fix false input at the source.

## Tests To Write Before Large Experiments

Policy edge cases:

- revoked credential denies;
- expired approval denies;
- stale assignment denies;
- juvenile record escalates;
- witness/victim sensitive record escalates;
- cross-jurisdiction classified request escalates;
- normal assigned non-sensitive request allows;
- emergency request escalates;
- sealed record denies without court/prosecutor approval;
- sealed record escalates or allows only under explicit authorized path.

Audit tests:

- hash chain validates for untouched signed log;
- hash chain fails after row deletion;
- hash chain fails after event mutation;
- explanation hash verifies before tamper;
- explanation hash fails after tamper;
- audit reconstruction fails when required event is missing.

Metrics tests:

- false allow calculation is correct;
- false deny calculation is correct;
- p95 latency calculation is correct;
- audit completeness calculation handles missing events.

## First 7-Day Build Sprint

### Day 1: Set Up Implementation Skeleton

- Create `src/`, `configs/`, `scripts/`, `tests/`.
- Add `synthetic_access_sim.yaml`.
- Define dataclasses or typed dictionaries for officers, stations, cases, records, requests, decisions, and audit events.

### Day 2: Workload Generator

- Implement deterministic generator using seed.
- Export generated workload to JSONL or CSV under run artifacts.
- Validate request distribution.

### Day 3: Policy Oracle

- Implement `allow`, `deny`, `escalate` rules.
- Add reason codes.
- Add unit tests for all edge cases.

### Day 4: RBAC And ABAC/PBAC Baselines

- Implement RBAC baseline.
- Implement ABAC/PBAC baseline.
- Compare against oracle.
- Save first metrics JSON.

### Day 5: Signed Log And Fabric-Style Audit Abstraction

- Implement hash-chained signed log.
- Implement local ledger abstraction.
- Add verification and reconstruction functions.

### Day 6: XAI Artifacts And Tamper Tests

- Generate structured explanation JSON.
- Hash explanations.
- Inject tamper scenarios.
- Compute tamper detection metrics.

### Day 7: First Run Record

- Run one baseline and one proposed method.
- Save config, logs, metrics, and artifacts.
- Create `results/tables/initial_comparison.csv`.
- Update an iteration report: `reports/iteration/iter_002_synthetic_access_sim.md`.

## What To Put In The Paper After First Run

Only after the first run exists:

- one table comparing RBAC, ABAC/PBAC, signed log, and Fabric-style audit;
- one tamper detection table;
- one explanation artifact example;
- one run configuration table;
- one honest limitations paragraph.

Do not write a results section before run artifacts exist.

## Do Not Start With These

Do not start with full Hyperledger Fabric:

- too much setup risk before the experiment logic is stable;
- can be added after local ledger abstraction works.

Do not start with NCRB crime prediction:

- useful secondary context;
- not the core research contribution.

Do not start with FIR NLP:

- no verified official open FIR text dataset exists in this repo;
- licensing/provenance risk is high.

Do not start with a UI dashboard:

- visually appealing but not publishable evidence.

Do not start with broad PAX-ICJS++:

- too broad for the first implementation;
- keep it as future vision.

## Claims To Avoid Until Evidence Exists

Do not claim:

- deployed or deployable in Indian policing;
- replacement for CCTNS or ICJS;
- legal compliance with DPDP or Bharatiya Sakshya Adhiniyam;
- evidence admissibility;
- formal privacy preservation;
- fairness;
- operational benefit to police;
- state-of-the-art crime prediction;
- individual suspect prediction from NCRB;
- blockchain is better than signed logs.

## Smart Researcher Move

The winning path is not to build the biggest system. It is to build the smallest experiment that can survive reviewer attack.

That means:

- deterministic generator;
- explicit oracle;
- strong signed-log baseline;
- measurable Fabric-style audit abstraction;
- XAI artifact hashes;
- tamper tests;
- ablations;
- honest negative results.

If this works, then the next paper phase can add full Hyperledger Fabric, NCRB/BPRD aggregate context, and optional cybersecurity/access-control benchmarks.
