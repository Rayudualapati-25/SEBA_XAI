# SEBA-XAI Prototype Deep Syllabus

Date created: 2026-05-28

Purpose: learn the SEBA-XAI prototype in tiny technical detail, from the first synthetic access request to the final research evidence tables.

This syllabus is different from the general Blockchain + XAI syllabus. The general syllabus teaches the theory. This document teaches the actual prototype built in this repository.

---

## 0. What This Prototype Is

SEBA-XAI is a research prototype for secure, explainable, blockchain-audited access governance.

The prototype does not replace CCTNS or ICJS. It simulates an intelligent secure overlay that could sit above police-style digital records and manage access requests in a controlled, auditable, and explainable way.

In simple words:

1. A synthetic officer asks for access to a synthetic sensitive record.
2. A policy oracle decides `allow`, `deny`, or `escalate`.
3. The decision receives an explanation.
4. The request and explanation are logged.
5. Audit structures test whether tampering can be detected.
6. Off-chain storage keeps sensitive data away from the ledger.
7. Experiments measure tamper detection, latency, storage overhead, metadata leakage, and policy ablations.
8. The newer `src/seba/` package adds attacks, baselines, scoring, and NS-PI, a neuro-symbolic policy-induction method.

Important boundary:

- No real police data is used.
- No real CCTNS, ICJS, FIR, victim, witness, or juvenile data is used.
- The blockchain layer is a permissioned blockchain-style simulation, not a deployed Hyperledger Fabric network.
- The XAI layer currently uses deterministic rule-trace explanations and counterfactual explanations, not SHAP or LIME.
- The results support research evaluation only. They do not prove legal compliance, production security, or deployment readiness.

---

## 1. Learning Target

After completing this syllabus, you should be able to explain:

1. What problem the prototype solves.
2. Why the project narrowed from general crime prediction to secure access governance.
3. How synthetic access requests are generated.
4. How the policy oracle validates each request.
5. Where XAI appears in the system.
6. Why raw records stay off-chain.
7. How mutable logs, signed hash chains, and permissioned blockchain-style logs differ.
8. What the latency and storage experiments measure.
9. What policy ablation means in this project.
10. What ADV-AUDIT tests.
11. What NS-PI learns.
12. Why the current NS-PI claim is not fully proven yet.
13. What the next experiment, `compromised_signer`, must test.

---

## 2. Prototype Map

The repository contains two related implementation layers.

### Layer A: Original Synthetic Access Simulator

Location:

```text
prototype/synthetic_access_sim/
```

Main purpose:

This layer demonstrates the basic SEBA-XAI pipeline step by step.

Files:

| Step | File | What it does |
|---:|---|---|
| 1 | `generate_synthetic_requests.py` | Creates synthetic stations, officers, cases, records, and access requests. |
| 2 | `policy_oracle.py` | Applies deterministic policy rules and creates rule-trace XAI explanations. |
| 3 | `audit_baseline.py` | Compares mutable logs with signed append-only hash-chain logs. |
| 4 | `blockchain_audit.py` | Simulates permissioned blockchain-style audit blocks and validator quorum. |
| 5 | `measure_overhead.py` | Measures local decision, audit, verification, latency, and storage overhead. |
| 6 | `experiment_modes.py` | Compares baseline and proposed experiment modes. |
| 7 | `offchain_storage.py` | Simulates off-chain encrypted record envelopes and ledger pointers. |
| 8 | `policy_ablation.py` | Tests what happens when policy dimensions are removed. |
| Policy | `policies/seba_xai_policy_v1.json` | Stores configurable policy rules for the synthetic system. |

Main outputs:

```text
prototype/runs/
prototype/results/tables/
```

### Layer B: Research Package

Location:

```text
src/seba/
```

Main purpose:

This layer turns the prototype into a more research-grade evaluation package. It adds a clean schema, attack catalog, baselines, scoring, NS-PI model, drift detection, and counterfactual explanations.

Files:

| Component | Location | What it does |
|---|---|---|
| Data schema | `src/seba/schema.py` | Defines immutable records and audit events. |
| Attacks | `src/seba/attacks/` | Implements adversarial tampering scenarios. |
| Baselines | `src/seba/baselines/` | Re-implements CT-log and Fabric+ABAC-style baselines. |
| NS-PI learner | `src/seba/nspi/learner.py` | Learns interpretable policy rules from labeled access traces. |
| NS-PI drift | `src/seba/nspi/drift.py` | Detects distribution shift between declared and observed decisions. |
| NS-PI counterfactual | `src/seba/nspi/counterfactual.py` | Generates simple officer-facing counterfactual explanations. |
| Scoring | `src/seba/scoring/` | Computes attack-aware scores and detector results. |
| Experiment scripts | `scripts/` | Runs multi-seed evaluation, full grid, ablations, and evidence packaging. |
| Tests | `tests/` | Verifies schema, attacks, baselines, NS-PI, scoring, and aggregation. |

Main outputs:

```text
results/tables/
results/plots/
results/FINDINGS.md
papers/final_paper/results/
```

---

## 3. How To Study Each Unit

For every unit, follow this pattern:

1. Read the listed files.
2. Run the listed command.
3. Open the output artifacts.
4. Write a 5-10 line note in your own words.
5. Answer the viva questions.
6. Mark what is proven, what is only simulated, and what is still weak.

Do not just read code. Run it and inspect the outputs.

---

## 4. Setup Unit: Reproducibility First

### Goal

Set up the project and verify that the code runs before learning the details.

### Files to read

```text
README.md
REPRODUCE.md
Makefile
pyproject.toml
SESSION_HANDOFF.md
results/FINDINGS.md
```

### Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make test
```

Optional full reproduction:

```bash
make reproduce
```

### What to learn

- Why `pyproject.toml` exists.
- Why the package is installed in editable mode.
- Why tests are required before claiming the prototype works.
- Why deterministic seeds are used.
- Why `results/FINDINGS.md` is more important than optimistic project notes.

### Tiny details to notice

- `Makefile` defines the trusted commands.
- `make test` runs the unit test suite.
- `make reproduce` regenerates the multi-seed evidence tables.
- `REPRODUCE.md` still mentions an older expected test count in one place; always trust your fresh local test run and `SESSION_HANDOFF.md` for the latest status.

### Student output

Write a short note:

```text
I installed the package, ran tests, and confirmed the current test count. The project is reproducible because the main runs use fixed seeds and write outputs to structured results folders.
```

---

## Unit 1: Research Problem And Prototype Boundary

### Goal

Understand why this project is about access governance, not general crime prediction.

### Files to read

```text
00_problem_understanding.md
05_research_gap.md
06_proposed_architecture.md
13_implementation_kickstart.md
15_solid_research_roadmap.md
CONTRIBUTION.md
```

### Concepts

- CCTNS/ICJS-compatible overlay
- Sensitive police records
- Inter-station and inter-agency access
- Access request
- Approval workflow
- Audit trail
- Explainable decision
- Off-chain sensitive data

### What to understand

The original broad idea was "AI for police crime data." That is too broad and risky because it can easily become unsupported predictive policing. The narrowed research is stronger:

```text
Can we design and evaluate a secure, explainable, auditable access-governance overlay for sensitive police-style records?
```

### Viva questions

1. Why is this not a crime prediction paper?
2. Why does the system not replace CCTNS or ICJS?
3. What does "overlay" mean?
4. Why is secure access governance safer and more publishable?
5. What is the main research weakness still remaining?

### Student output

One paragraph explaining the project in simple language.

---

## Unit 2: Synthetic Data Generation

### Goal

Understand how synthetic police-style access requests are generated.

### File to read

```text
prototype/synthetic_access_sim/generate_synthetic_requests.py
```

### Command

```bash
python3 prototype/synthetic_access_sim/generate_synthetic_requests.py \
  --run-id learning_step1_seed42 \
  --seed 42 \
  --num-requests 1000
```

### Outputs to inspect

```text
prototype/runs/learning_step1_seed42/artifacts/stations.csv
prototype/runs/learning_step1_seed42/artifacts/officers.csv
prototype/runs/learning_step1_seed42/artifacts/cases.csv
prototype/runs/learning_step1_seed42/artifacts/records.csv
prototype/runs/learning_step1_seed42/artifacts/access_requests.csv
prototype/runs/learning_step1_seed42/artifacts/dataset_manifest.json
prototype/runs/learning_step1_seed42/metrics.json
```

### What to learn

- How stations are represented.
- How officers are represented.
- How cases are represented.
- How records are represented.
- How requests connect officer, case, record, station, action, purpose, and time.
- Why every synthetic run needs a seed.

### Tiny details to notice

- `run_id` controls where outputs are saved.
- `seed` controls reproducibility.
- `num_requests` controls workload size.
- Synthetic data is useful for testing workflow behavior, but it is not evidence about real policing outcomes.

### Viva questions

1. What is one row in `access_requests.csv`?
2. What fields are needed before a policy decision can be made?
3. Why is synthetic data acceptable for this prototype?
4. Why is synthetic data not enough for deployment claims?

### Student output

Create a small table with five fields from `access_requests.csv` and explain each in one sentence.

---

## Unit 3: Policy Oracle And Access Decision Logic

### Goal

Understand where each request is validated.

### File to read

```text
prototype/synthetic_access_sim/policy_oracle.py
```

### Command

```bash
python3 prototype/synthetic_access_sim/policy_oracle.py \
  --input-run-id learning_step1_seed42 \
  --run-id learning_step2_policy_seed42
```

### Outputs to inspect

```text
prototype/runs/learning_step2_policy_seed42/artifacts/labeled_access_requests.csv
prototype/runs/learning_step2_policy_seed42/artifacts/policy_summary.csv
prototype/runs/learning_step2_policy_seed42/artifacts/explanation_artifacts.jsonl
prototype/runs/learning_step2_policy_seed42/artifacts/policy_rules.json
prototype/runs/learning_step2_policy_seed42/metrics.json
```

### What to learn

This is where the request is validated. The policy oracle checks the request against rules and gives one of three decisions:

- `allow`
- `deny`
- `escalate`

### Tiny details to notice

For each request, the oracle adds:

- `decision`
- `primary_reason_code`
- `decisive_attributes`
- `xai_explanation`
- `decision_hash`
- `explanation_hash`
- `audit_anchor_hash`

### Simple mental model

```text
request fields
  -> policy rules
  -> decision
  -> reason code
  -> explanation
  -> hashes for audit
```

### Viva questions

1. What does the policy oracle do?
2. What is the difference between `deny` and `escalate`?
3. What is a reason code?
4. Why does the decision need a hash?
5. Why is the policy oracle not a trained AI model yet?

### Student output

Pick one row from `labeled_access_requests.csv` and explain why it was allowed, denied, or escalated.

---

## Unit 4: XAI In The Prototype

### Goal

Understand exactly where explainable AI appears.

### Files to read

```text
prototype/synthetic_access_sim/policy_oracle.py
src/seba/nspi/counterfactual.py
tests/test_nspi_counterfactual.py
```

### What to learn

There are two XAI forms in the current prototype:

1. Rule-trace explanation in the original simulator.
2. Counterfactual explanation in the `src/seba/` research package.

### Rule-trace explanation

The policy oracle explains which rule or attribute caused the decision.

Example idea:

```text
Denied because the officer's jurisdiction does not match the record jurisdiction.
```

### Counterfactual explanation

The NS-PI counterfactual module explains what minimal change could have changed the decision.

Example idea:

```text
Would have been allow if approval_token_status = PRESENT_VALID and record_sensitivity_level = MEDIUM.
```

### What XAI is not claiming

- It does not prove the decision is morally correct.
- It does not prove the decision is legally valid.
- It does not remove human review.
- It does not solve trust by itself.

### Viva questions

1. What does XAI explain in SEBA-XAI?
2. Who needs the explanation?
3. Why should explanation hashes be logged?
4. What is the difference between rule-trace and counterfactual explanation?
5. Why is XAI part of access governance and not just decoration?

### Student output

Write two explanations for one request:

1. A technical explanation for an auditor.
2. A simple explanation for an officer.

---

## Unit 5: Mutable Log Baseline

### Goal

Understand why a simple database log is weak.

### File to read

```text
prototype/synthetic_access_sim/audit_baseline.py
```

### Command

```bash
python3 prototype/synthetic_access_sim/audit_baseline.py \
  --input-run-id learning_step2_policy_seed42 \
  --run-id learning_step3_audit_seed42
```

### Outputs to inspect

```text
prototype/runs/learning_step3_audit_seed42/artifacts/mutable_access_log.csv
prototype/runs/learning_step3_audit_seed42/artifacts/tamper_test_results.csv
prototype/runs/learning_step3_audit_seed42/artifacts/audit_detection_summary.csv
```

### What to learn

A mutable log is a normal editable log. If someone changes a row and there is no external integrity check, the log itself may not prove that tampering happened.

### Tiny details to notice

- Mutable logs are useful as a baseline.
- They are easy to store and query.
- They are weak for tamper evidence.
- They help prove why stronger audit designs are needed.

### Viva questions

1. What is a mutable log?
2. Why do we include a weak baseline?
3. What tamper cases are injected?
4. Why is "baseline comparison" necessary for research?

### Student output

Explain why the mutable log exists even though it is not the proposed method.

---

## Unit 6: Signed Append-Only Hash Chain

### Goal

Understand the first tamper-evident audit mechanism.

### File to read

```text
prototype/synthetic_access_sim/audit_baseline.py
```

### Outputs to inspect

```text
prototype/runs/learning_step3_audit_seed42/artifacts/signed_hash_chain_log.csv
prototype/runs/learning_step3_audit_seed42/artifacts/tampered_logs/
prototype/runs/learning_step3_audit_seed42/artifacts/tamper_test_results.csv
```

### What to learn

Each request gets a row hash. Each row also depends on the previous row hash. This creates a chain:

```text
row 1 hash
  -> row 2 hash includes row 1 hash
  -> row 3 hash includes row 2 hash
  -> ...
```

If someone changes, deletes, or reorders a row, the chain verification fails.

### Tiny details to notice

- This is not blockchain yet.
- It is append-only log integrity.
- It detects tampering because the hash chain no longer matches.
- It is simpler than a permissioned blockchain simulation.

### Viva questions

1. What is a row hash?
2. What is a previous hash?
3. Why does reordering break the chain?
4. Why is a hash chain still not the same as a blockchain?

### Student output

Draw a 5-row hash chain and show what breaks if row 3 is edited.

---

## Unit 7: Permissioned Blockchain-Style Audit Layer

### Goal

Understand the blockchain part of SEBA-XAI.

### File to read

```text
prototype/synthetic_access_sim/blockchain_audit.py
```

### Command

```bash
python3 prototype/synthetic_access_sim/blockchain_audit.py \
  --input-run-id learning_step3_audit_seed42 \
  --run-id learning_step4_blockchain_seed42
```

### Outputs to inspect

```text
prototype/runs/learning_step4_blockchain_seed42/artifacts/permissioned_audit_blocks.jsonl
prototype/runs/learning_step4_blockchain_seed42/artifacts/block_event_index.csv
prototype/runs/learning_step4_blockchain_seed42/artifacts/validator_set.json
prototype/runs/learning_step4_blockchain_seed42/artifacts/blockchain_tamper_test_results.csv
prototype/runs/learning_step4_blockchain_seed42/artifacts/blockchain_detection_summary.csv
```

### What to learn

This prototype uses a permissioned blockchain-style audit layer.

It is closer to PoA/PBFT-style permissioned validation than PoW or PoS.

Why:

- Police and government systems need known validators.
- Unknown public miners are not suitable for sensitive police audit records.
- The prototype uses synthetic validators and a quorum rule.

### What is stored on the ledger

The ledger stores audit commitments, not raw sensitive records.

Examples:

- request ID
- decision hash
- explanation hash
- policy version
- model version
- record pointer hash
- approval event hash
- validator metadata

### What is not stored on the ledger

- Full FIR text
- witness statements
- victim records
- juvenile records
- forensic reports
- raw evidence files
- case diary content

### Tiny details to notice

- Blocks group multiple audit events.
- Validator set is known.
- A quorum rule decides whether a block is accepted.
- Tampering should be detected by block verification.

### Viva questions

1. What type of blockchain is simulated?
2. Why not PoW?
3. Why not public blockchain?
4. What is a validator?
5. What is a quorum?
6. Why should raw records stay off-chain?

### Student output

Explain the blockchain layer in three lines:

```text
The blockchain-style layer stores tamper-evident audit commitments.
It does not store raw sensitive police records.
Known validators endorse blocks using a quorum rule.
```

---

## Unit 8: Off-Chain Storage And Ledger Pointers

### Goal

Understand what "raw records stay off-chain" means.

### File to read

```text
prototype/synthetic_access_sim/offchain_storage.py
```

### Command

```bash
python3 prototype/synthetic_access_sim/offchain_storage.py \
  --input-run-id learning_step2_policy_seed42 \
  --run-id learning_step7_offchain_seed42
```

### Outputs to inspect

```text
prototype/runs/learning_step7_offchain_seed42/artifacts/
```

### Simple explanation

Raw records staying off-chain means:

```text
Sensitive content is kept in a normal protected database or encrypted storage.
The ledger stores only a pointer, hash, and audit proof.
```

So the blockchain can prove that something happened without exposing the full sensitive record.

### Why this matters

Police records can contain victim names, witness details, juvenile data, forensic reports, and investigation notes. Putting this content directly on a blockchain would create privacy and legal problems because blockchains are hard to delete or correct.

### Tiny details to notice

- The prototype simulates encrypted payload envelopes.
- It models metadata-minimized pointers.
- It measures metadata exposure.
- It does not implement production key management.

### Viva questions

1. What is an off-chain record?
2. What is an on-chain pointer?
3. Why is a hash useful?
4. What privacy risk still remains even if raw data is off-chain?
5. What is metadata leakage?

### Student output

Draw this flow:

```text
raw record -> encrypted off-chain storage -> pointer/hash -> audit ledger
```

---

## Unit 9: Latency And Storage Overhead

### Goal

Understand the cost of adding policy, XAI, and audit layers.

### File to read

```text
prototype/synthetic_access_sim/measure_overhead.py
```

### Command

```bash
python3 prototype/synthetic_access_sim/measure_overhead.py \
  --run-id learning_step5_latency_storage
```

### Outputs to inspect

```text
prototype/runs/learning_step5_latency_storage/artifacts/latency_summary.csv
prototype/runs/learning_step5_latency_storage/artifacts/latency_samples.csv
prototype/runs/learning_step5_latency_storage/artifacts/storage_overhead.csv
prototype/runs/learning_step5_latency_storage/artifacts/overhead_comparison.csv
```

### What to learn

Latency means time taken.

This step measures:

- policy oracle decision time
- XAI explanation time
- mutable log write time
- signed hash-chain write time
- signed hash-chain verification time
- blockchain-style block creation time
- blockchain-style verification time
- storage size overhead

### Tiny details to notice

- This is local benchmark timing, not real deployment latency.
- Results can change by machine.
- It is still useful because it compares relative overhead under the same environment.

### Viva questions

1. What is decision latency?
2. What is audit write latency?
3. What is verification latency?
4. Why does blockchain-style audit add overhead?
5. Why should we not call this a deployment benchmark?

### Student output

Create a short table:

| Component | What time is measured | Why it matters |
|---|---|---|

---

## Unit 10: Experiment Modes

### Goal

Understand why the prototype compares several system modes.

### File to read

```text
prototype/synthetic_access_sim/experiment_modes.py
```

### Command

```bash
python3 prototype/synthetic_access_sim/experiment_modes.py \
  --run-id learning_step6_experiment_modes
```

### Outputs to inspect

```text
prototype/results/tables/experiment_modes_step6_comparison.csv
```

### What to learn

Experiment modes compare different designs, such as:

- basic policy decision only
- policy plus explanation
- policy plus signed audit
- policy plus blockchain-style audit
- proposed SEBA-XAI-style configuration

The point is to avoid claiming the proposed method is useful without comparing it to simpler alternatives.

### Viva questions

1. Why do we need experiment modes?
2. What is a baseline?
3. Why is a simpler baseline important?
4. What does a fair comparison require?

### Student output

Explain which mode is closest to the proposed SEBA-XAI architecture.

---

## Unit 11: Policy Configuration And Ablation

### Goal

Understand how policy dimensions affect false allows, false denies, and escalations.

### Files to read

```text
prototype/synthetic_access_sim/policies/seba_xai_policy_v1.json
prototype/synthetic_access_sim/policy_ablation.py
```

### Command

```bash
python3 prototype/synthetic_access_sim/policy_ablation.py \
  --input-run-id learning_step2_policy_seed42 \
  --run-id learning_step8_policy_ablation_seed42
```

### Outputs to inspect

```text
prototype/results/tables/policy_ablation_step8_comparison.csv
prototype/runs/learning_step8_policy_ablation_seed42/metrics.json
```

### What to learn

Ablation means removing or weakening one part of the system to see what changes.

Example:

```text
Remove sensitivity rule -> check whether false allows increase.
Remove approval rule -> check whether sensitive requests are over-allowed.
Remove jurisdiction rule -> check whether cross-station access becomes unsafe.
```

### Tiny details to notice

- Ablation is required for a serious research paper.
- It shows which component actually matters.
- It prevents unsupported claims like "all parts are useful" without evidence.

### Viva questions

1. What is policy ablation?
2. Which policy dimension is most important?
3. How do false allows differ from false denies?
4. Why are false allows serious in sensitive police records?

### Student output

Write one paragraph:

```text
The most security-critical policy dimension appears to be __ because removing it changes __.
```

Fill the blanks only after reading the actual output table.

---

## Unit 12: Research Package Schema

### Goal

Understand the clean internal data model used by the new research package.

### Files to read

```text
src/seba/schema.py
tests/test_schema.py
```

### What to learn

The package uses immutable data structures. That means once an object is created, attacks should not modify it in place. Instead, attacks return a new modified log.

This is important for reproducible experiments.

### Tiny details to notice

- The schema uses frozen dataclasses.
- Audit entries have structured fields.
- Attack code should not secretly mutate original data.
- Tests enforce immutability expectations.

### Viva questions

1. What is a dataclass?
2. What does `frozen=True` mean?
3. Why is immutability useful in attack experiments?
4. Why should attacks return new logs?

### Student output

Explain one schema class in simple English.

---

## Unit 13: ADV-AUDIT Attack Catalog

### Goal

Understand the adversarial benchmark side of the research.

### Files to read

```text
src/seba/attacks/base.py
src/seba/attacks/catalog.py
src/seba/attacks/backdate.py
src/seba/attacks/replay.py
src/seba/attacks/revocation_race.py
src/seba/attacks/explanation_swap.py
src/seba/attacks/metadata_inference.py
src/seba/attacks/collusion.py
src/seba/attacks/adaptive.py
tests/test_attacks.py
```

### What to learn

The attack catalog creates ground-truth adversarial scenarios. This prevents the evaluation from becoming circular.

Current attack ideas include:

- timestamp backdating
- token replay
- revocation race
- explanation hash swap
- metadata inference
- validator collusion
- adaptive attacks

### Tiny details to notice

- Each attack should define what was changed.
- Each attack should preserve original data unless it returns a new tampered version.
- The benchmark should know the ground truth attack label.

### Viva questions

1. What is an attack catalog?
2. Why is ground truth important?
3. What is token replay?
4. What is timestamp backdating?
5. What is explanation swapping?
6. What is metadata inference?

### Student output

Choose one attack and explain:

```text
Attacker goal:
What field changes:
Which defense should detect it:
Which defense may miss it:
```

---

## Unit 14: Baseline Defenses

### Goal

Understand what the proposed system is compared against.

### Files to read

```text
src/seba/baselines/ct_log.py
src/seba/baselines/fabric_abac.py
tests/test_baselines.py
```

### What to learn

The research package includes baseline defenses so SEBA-XAI/NS-PI is not evaluated alone.

Baselines include:

- CT-log-style append-only transparency log
- Fabric+ABAC-style permissioned access-control baseline
- signed-chain style detector
- blockchain-style detector
- ABAC re-execution detector

### Tiny details to notice

- A good baseline is not weak on purpose.
- Strong baselines make the research honest.
- Current results show cryptographic baselines are very strong on the existing attack catalog.

### Viva questions

1. What is a baseline?
2. Why is Fabric+ABAC a relevant baseline?
3. Why can cryptographic baselines detect many current attacks?
4. Why is it bad research to compare only against a weak mutable log?

### Student output

Make a baseline comparison table:

| Defense | Main idea | Strength | Weakness |
|---|---|---|---|

---

## Unit 15: AAS Scoring And Evaluation Grid

### Goal

Understand how detection performance is measured.

### Files to read

```text
src/seba/scoring/aas.py
src/seba/scoring/detectors.py
src/seba/scoring/grid.py
scripts/run_full_grid.py
tests/test_grid.py
```

### Commands

```bash
python3 scripts/run_full_grid.py
```

### Outputs to inspect

```text
results/tables/full_grid_raw.csv
results/tables/full_grid_per_attack.csv
results/tables/full_grid_aas_by_defense.csv
```

### What to learn

AAS means attack-aware score. It measures how well a defense performs against attack scenarios.

The evaluation grid runs:

```text
defense x attack x seed
```

This is stronger than testing one defense on one seed.

### Tiny details to notice

- Multi-seed evaluation reduces accidental conclusions.
- Per-attack tables show where each defense works or fails.
- Aggregate scores can hide important failure cases.

### Viva questions

1. What is AAS?
2. Why do we need multiple seeds?
3. What is a defense x attack grid?
4. Why should we inspect per-attack results, not only the average?

### Student output

Read `full_grid_aas_by_defense.csv` and write three honest findings.

---

## Unit 16: NS-PI Rule-List Learner

### Goal

Understand the AI model part of the research package.

### Files to read

```text
src/seba/nspi/learner.py
tests/test_nspi_learner.py
```

### What to learn

NS-PI stands for neuro-symbolic policy induction.

In this project, NS-PI learns an interpretable rule list from policy-labeled access traces. It tries to recover the policy behavior from observed decisions.

### Why this matters

If declared policy and observed decisions differ, the system may be drifting or compromised. NS-PI gives a readable learned policy artifact that can be inspected.

### Tiny details to notice

- It is not a deep neural network.
- It is intentionally interpretable.
- It is trained on labeled synthetic traces.
- Its learned rules should be compared to declared policy.

### Viva questions

1. What does NS-PI learn?
2. Why is interpretability important here?
3. Why not use an opaque deep model first?
4. What does policy recovery mean?

### Student output

Explain NS-PI in three lines:

```text
NS-PI learns readable policy rules from access-decision traces.
It helps compare declared policy with observed decision behavior.
It is useful for audit and drift detection, not for predicting criminals.
```

---

## Unit 17: Drift Detection

### Goal

Understand why NS-PI currently does not beat cryptographic defenses on the existing attack catalog.

### Files to read

```text
src/seba/nspi/drift.py
tests/test_nspi_drift.py
results/FINDINGS.md
```

### What to learn

Drift detection looks for changes in decision distribution. It is different from hash-based tamper detection.

Hash-based detection asks:

```text
Was this logged field changed?
```

Drift detection asks:

```text
Does the observed decision behavior look different from the expected policy behavior?
```

### Current honest finding

The current attacks mostly modify logged fields. Cryptographic defenses detect these easily because row hashes break. NS-PI drift does not beat them on those attacks because a few changed rows do not always shift the distribution enough.

### Tiny details to notice

- This is not a failure to hide.
- It is an honest research finding.
- It defines the next experiment: `compromised_signer`.

### Viva questions

1. What is drift?
2. Why does a hash-chain detect row tampering better than drift detection?
3. When could drift detection be useful?
4. Why is `compromised_signer` the next important attack?

### Student output

Write the difference:

| Hash-chain detection | NS-PI drift detection |
|---|---|
| Detects changed log integrity | Detects changed decision behavior |

---

## Unit 18: Counterfactual XAI

### Goal

Understand how the prototype explains what change would alter a decision.

### Files to read

```text
src/seba/nspi/counterfactual.py
tests/test_nspi_counterfactual.py
```

### What to learn

A counterfactual explanation answers:

```text
What minimal change would have changed the decision?
```

Example:

```text
Would have been allow if approval_token_status = PRESENT_VALID.
```

### Why this matters in access governance

An officer, superior officer, auditor, or reviewer may need to know why a request was denied or escalated. A counterfactual gives a simple corrective explanation without exposing the full record.

### Tiny details to notice

- Counterfactuals must be careful in sensitive systems.
- They should not leak too much information.
- They should not teach attackers how to bypass policy.
- Explanation artifacts may themselves be sensitive.

### Viva questions

1. What is a counterfactual explanation?
2. Why can counterfactuals be useful for access requests?
3. Why can counterfactuals be risky?
4. Should explanations be logged? Why?

### Student output

Create one safe counterfactual and one unsafe counterfactual. Explain why the unsafe one should not be shown.

---

## Unit 19: Paper Evidence Pack

### Goal

Understand how code outputs become research evidence.

### Files to read

```text
scripts/prepare_paper_evidence_pack.py
papers/final_paper/results/experiment_results_narrative.md
results/tables/paper_evidence_index.csv
results/tables/paper_table_01_method_comparison.csv
results/tables/paper_table_02_tamper_detection.csv
results/tables/paper_table_03_metadata_exposure.csv
results/tables/paper_table_04_latency_storage.csv
results/tables/paper_table_05_policy_ablation.csv
```

### Command

```bash
python3 scripts/prepare_paper_evidence_pack.py
```

### What to learn

Research writing must come from generated artifacts, not imagination.

The evidence pack collects:

- method comparison
- tamper detection
- metadata exposure
- latency and storage
- policy ablation
- plots
- result narrative

### Tiny details to notice

- A paper claim should point to a table, plot, metric, log, or source.
- If an experiment does not exist, the paper must not claim it.
- If a result is weak, say it is weak.

### Viva questions

1. What is an evidence pack?
2. Why should paper writing wait for experiments?
3. What is the danger of writing claims before results?
4. Which current claim is not fully proven?

### Student output

Pick one paper table and write one safe claim that it supports.

---

## Unit 20: Next Research Experiment - Compromised Signer

### Goal

Understand the most important next step for making the research stronger.

### Files to read

```text
SESSION_HANDOFF.md
results/FINDINGS.md
src/seba/attacks/catalog.py
src/seba/scoring/detectors.py
scripts/run_ablations.py
```

### What the new attack should test

Current attacks modify fields and break hashes. Cryptographic defenses detect those easily.

The missing attack is different:

```text
The attacker changes decisions and then re-signs the audit chain with a valid signing key.
```

This means the chain may verify as valid even though the policy behavior is corrupted.

### Why this matters

This is where NS-PI may become useful:

- Hash-chain says: "The chain is valid."
- NS-PI drift may say: "The decision distribution changed suspiciously."

### Required implementation idea

Add:

```text
src/seba/attacks/compromised_signer.py
```

Then update:

```text
src/seba/attacks/catalog.py
src/seba/scoring/detectors.py
scripts/run_ablations.py
tests/
```

### What would count as a useful result

Useful result:

```text
Cryptographic detectors miss the re-signed corrupted log, while NS-PI detects a policy-distribution shift.
```

Weak result:

```text
NS-PI also misses it, or detects it only inconsistently.
```

If weak, the paper should be reframed as an ADV-AUDIT benchmark paper instead of a novel NS-PI method paper.

### Viva questions

1. What is a compromised signer?
2. Why can a valid signature still be dangerous?
3. Why might blockchain audit fail under signer compromise?
4. Why might NS-PI help?
5. What result decides whether NS-PI is a strong contribution?

### Student output

Write the proposed experiment in this format:

```text
Hypothesis:
Attack:
Expected crypto result:
Expected NS-PI result:
Failure condition:
Paper decision:
```

---

## 5. Thirty-Day Learning Plan

Use this if you want to learn the prototype properly, not just read it once.

| Day | Topic | Main output |
|---:|---|---|
| 1 | Repository setup and reproducibility | Test run note |
| 2 | Research problem and boundary | 1-page simple problem explanation |
| 3 | Synthetic stations/officers/cases/records | Data dictionary notes |
| 4 | Access request generation | Explain one request row |
| 5 | Policy oracle | Trace one request to decision |
| 6 | Rule-trace XAI | Explain allow/deny/escalate in simple language |
| 7 | Decision and explanation hashes | Hash flow diagram |
| 8 | Mutable log | Baseline weakness note |
| 9 | Signed hash-chain | 5-row hash-chain drawing |
| 10 | Tamper tests | Tamper case table |
| 11 | Permissioned blockchain-style audit | Block and validator explanation |
| 12 | Quorum validation | Explain 3-of-4 quorum |
| 13 | Off-chain storage | On-chain vs off-chain diagram |
| 14 | Metadata leakage | Metadata risk note |
| 15 | Latency metrics | Latency component table |
| 16 | Storage overhead | Storage comparison note |
| 17 | Experiment modes | Baseline vs proposed comparison |
| 18 | Policy ablation | Explain one ablation result |
| 19 | Schema package | Explain immutable dataclass |
| 20 | Attack catalog | Explain one attack deeply |
| 21 | Baseline defenses | Baseline comparison table |
| 22 | AAS scoring | Explain one score |
| 23 | Full evaluation grid | Defense x attack x seed note |
| 24 | NS-PI learner | Three-line NS-PI explanation |
| 25 | Drift detection | Hash detection vs drift detection table |
| 26 | Counterfactual XAI | Safe and unsafe explanation examples |
| 27 | Paper evidence pack | One evidence-backed claim |
| 28 | Findings review | Honest limitations note |
| 29 | Compromised signer design | Experiment proposal |
| 30 | Professor explanation rehearsal | 5-minute oral explanation |

---

## 6. Commands You Should Know By Heart

Install:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
make test
```

Run original step 1 and step 2:

```bash
make bench
```

Run full reproduction:

```bash
make reproduce
```

Run full evaluation grid:

```bash
python3 scripts/run_full_grid.py
```

Run ablations:

```bash
python3 scripts/run_ablations.py
```

Prepare paper evidence:

```bash
python3 scripts/prepare_paper_evidence_pack.py
```

---

## 7. Terms You Must Be Able To Define

| Term | Simple meaning in this project |
|---|---|
| Access request | A synthetic officer asks to access a synthetic record for a stated purpose. |
| Policy oracle | Rule-based validator that decides allow, deny, or escalate. |
| ABAC | Attribute-Based Access Control. It uses subject, object, action, and environment attributes. |
| PBAC | Policy-Based Access Control. It uses explicit policy rules and versions. |
| XAI | Explanation layer that tells why a decision happened or what would change it. |
| Rule-trace explanation | Explanation showing which rule or attribute caused the decision. |
| Counterfactual explanation | Explanation showing what minimal change could change the decision. |
| Mutable log | Editable audit log without strong tamper evidence. |
| Signed hash-chain | Append-only log where each row depends on the previous row hash. |
| Permissioned blockchain | Blockchain-style audit system with known validators. |
| Validator | Known node that endorses audit blocks. |
| Quorum | Minimum number of validators required to accept a block. |
| Off-chain storage | Sensitive records are stored outside the ledger. |
| On-chain commitment | Hash or pointer stored on ledger to prove integrity without exposing raw content. |
| Metadata leakage | Sensitive inference from non-content fields like time, role, location, or access pattern. |
| Ablation | Removing one component to measure its effect. |
| ADV-AUDIT | Adversarial benchmark for testing audit/access-governance defenses. |
| AAS | Attack-aware score used to evaluate defenses across attack scenarios. |
| NS-PI | Neuro-symbolic policy induction, used to learn interpretable policy behavior from logs. |
| Drift detection | Detecting suspicious change in decision distribution. |
| Compromised signer | Attack where a valid signer creates or re-signs a corrupted log. |

---

## 8. Professor-Ready Explanation

Use this short explanation:

```text
My prototype studies secure access governance for sensitive police-style records. It generates synthetic access requests, validates them using policy rules, explains the decision, and stores audit commitments in tamper-evident logs and a permissioned blockchain-style audit layer. Raw records stay off-chain. The newer research package adds attack scenarios, baseline defenses, scoring, and NS-PI, an interpretable policy-induction method for detecting decision-behavior drift. The current honest finding is that cryptographic defenses already detect simple log tampering well, so the next important experiment is a compromised-signer attack where the chain remains valid but the decision behavior becomes suspicious.
```

Do not say:

- "We use real police data."
- "This is deployed on CCTNS."
- "This proves legal compliance."
- "This is a production blockchain."
- "This predicts criminals."
- "NS-PI already beats all baselines."

---

## 9. Minimum Knowledge Checklist

Before saying you understand the prototype, you should be able to do all of this:

- [ ] Run `make test`.
- [ ] Run step 1 synthetic generation.
- [ ] Explain one generated request row.
- [ ] Run the policy oracle.
- [ ] Explain one allow/deny/escalate decision.
- [ ] Explain where XAI appears.
- [ ] Explain mutable log weakness.
- [ ] Explain signed hash-chain verification.
- [ ] Explain permissioned blockchain-style audit.
- [ ] Explain why raw records stay off-chain.
- [ ] Explain latency and storage metrics.
- [ ] Explain policy ablation.
- [ ] Explain one attack from the catalog.
- [ ] Explain one baseline defense.
- [ ] Explain AAS scoring.
- [ ] Explain NS-PI.
- [ ] Explain drift detection.
- [ ] Explain why current NS-PI evidence is not yet enough.
- [ ] Explain the compromised-signer next experiment.

---

## 10. Final Learning Outcome

At the end of this syllabus, you should be able to answer your professor's question:

```text
What research has been done to make a model out of this idea?
```

Answer:

```text
The research has moved from a broad idea to a working synthetic prototype and evaluation harness. The prototype generates access requests, applies policy validation, produces XAI explanations, logs audit commitments, simulates permissioned blockchain-style audit, evaluates latency/storage/privacy tradeoffs, and tests attacks and baselines. A newer NS-PI model learns interpretable policy behavior from access traces and tries to detect drift. The strongest next step is to implement and test a compromised-signer attack to prove whether NS-PI adds value beyond cryptographic tamper detection.
```

