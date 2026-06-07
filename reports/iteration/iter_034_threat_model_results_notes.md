# Iteration 034 - Threat Model And Results Notes (Paper-Facing)

Date: 2026-05-30
Status: notes only - not the IEEE Results section

## Purpose

Consolidate a paper-facing threat model and a results-notes scaffold built
**only** from evidence already generated in `results/tables/` and recorded in
`results/FINDINGS.md`, `CONTRIBUTION.md`, and iterations 027-033.

Strict rules followed here:

- No new metric is produced in this iteration. Every number is copied from an
  existing table artifact and the source file is named.
- Any statement that is not a direct table value is explicitly tagged
  `[INTERPRETATION]`.
- Any claim that lacks a table artifact is omitted, not estimated.
- No deployment, legal-compliance, real-police-data, or SOTA claim is made.

This is a writing-safety scaffold so the eventual Results and Threat Model
sections cannot drift away from the evidence.

---

## 1. System Under Evaluation (scope)

SEBA-XAI is a synthetic-workload research prototype for explainable,
blockchain-style-audited access governance over sensitive police/criminal-
justice records. Raw records stay off-chain; the audit layer holds
commitments, decisions, and explanation/anchor hashes.

`[INTERPRETATION]` The system is positioned as a CCTNS/ICJS-compatible overlay,
not a replacement and not a deployment. This framing is carried from
`CONTRIBUTION.md` and `00_problem_understanding.md`; it is a positioning claim,
not a measured result.

---

## 2. Threat Model

### 2.1 Actors and trust assumptions

| Actor / component | Trust assumption in the evaluation |
|---|---|
| Requesting officer | Untrusted intent; legitimacy depends on policy attributes (role, jurisdiction, case assignment, purpose, credential, approval). |
| Declared policy oracle (Step 2) | The reference definition of correct allow/deny/escalate for synthetic requests. It is the labeling function, not ground-truth real policy. |
| Ledger integrity layer (signed hash-chain, blockchain-style, CT-log) | Trusted to detect any change to a recorded field, insertion, deletion, or reorder **provided the signing keys are not compromised**. |
| Fabric+ABAC / ABAC re-execution baseline | Re-evaluates policy over the *recorded canonical output*; trusts that recorded output. |
| Trusted raw-attribute policy oracle | Assumes a **separate, uncompromised view** of the original request attributes, independent of the audit log. This is a strong assumption and is treated as a baseline, not a free guarantee. |
| NS-PI drift detector | Sees only the signed decision log (log-only visibility). Does not assume an independent raw view. |
| Signing authority / enforcement node | **May be compromised** in the `compromised_signer` threat (see 2.2). |

### 2.2 Attacks evaluated (all in the catalog, all in `results/tables/full_grid_raw.csv`)

Ordinary integrity attacks (modify a recorded field / structure):
`replay_approval_token`, `backdate_request`, `swap_explanation_hash`,
`collude_block_signature`, `revocation_race`, plus `metadata_inference`
(read-only inference, scored separately).

Key adversarial attack:

- `compromised_signer` - the attacker corrupts policy output (flips
  deny/escalate to allow for a fraction of events) and **re-signs a
  valid-looking canonical log**. By construction, ledger integrity checks
  pass, because the chain is internally consistent and validly signed.

`[INTERPRETATION]` The realism argument for `compromised_signer` (insider with
signing-key access, or compromised enforcement node) is a modeling assumption.
The paper must justify it in prose; the repository only demonstrates the
mechanical detection asymmetry, not real-world incidence.

---

## 3. What Each Layer Catches (table-backed)

### 3.1 Overall adversarial audit score

Source: `results/tables/full_grid_aas_by_defense.csv`
(also reproduced in `results/FINDINGS.md` section 1).

| Defense | AAS mean | AAS std |
|---|---:|---:|
| `trusted_policy_oracle` | 1.0000 | 0.0000 |
| `abac_reexec` | 0.7917 | 0.0000 |
| `blockchain_style` | 0.7917 | 0.0000 |
| `ct_log` | 0.7917 | 0.0000 |
| `fabric_abac` | 0.7917 | 0.0000 |
| `signed_chain` | 0.7917 | 0.0000 |
| `mutable_log` | 0.5000 | 0.0000 |
| `nspi_drift` | 0.2500 | 0.0932 |

`[INTERPRETATION]` NS-PI is the weakest overall detector and must not be sold
as a general tamper detector. Its value is narrow and conditional (section 3.3).

### 3.2 Ordinary integrity attacks

Source: `results/tables/full_grid_per_attack.csv`.
Signed-chain, blockchain-style, CT-log, Fabric+ABAC, and ABAC re-execution
detect the ordinary field-modifying attacks; the mutable log does not.

`[INTERPRETATION]` This is the expected control result: hash/commitment and
re-execution checks catch changes that break a hash or change a recomputed
decision. It establishes that the integrity baselines work, so the
`compromised_signer` blind spot is meaningful rather than a broken baseline.

### 3.3 The compromised-signer asymmetry (decisive result)

Source: `results/tables/full_grid_per_attack.csv` and
`results/tables/seed_confidence_summary.csv` (family
`detection_compromised_signer`).

| Defense | n_seeds | Detection mean | Std |
|---|---:|---:|---:|
| `signed_chain` | 5 | 0.0 | 0.0 |
| `blockchain_style` | 5 | 0.0 | 0.0 |
| `ct_log` | 5 | 0.0 | 0.0 |
| `fabric_abac` | 5 | 0.0 | 0.0 |
| `abac_reexec` | 5 | 0.0 | 0.0 |
| `mutable_log` | 5 | 0.0 | 0.0 |
| `nspi_drift` | 5 | 1.0 | 0.0 |
| `trusted_policy_oracle` | 5 | 1.0 | 0.0 |

Adaptive cross-check, source `results/tables/adaptive_attack_summary.csv`
(`compromised_signer` rows): for seeds 7, 21, 42, 99, 123 the integrity/ABAC
baselines detect 0, while NS-PI global and per-station both detect 1. Observed
global JS divergence ranged approximately 0.0244-0.0337 with permutation-test
p-value 0.004975 per seed (values from `results/FINDINGS.md` section 3, which
cites the adaptive table).

`[INTERPRETATION]` Both NS-PI (log-only) and the trusted raw-attribute oracle
catch this attack, but for different reasons and under different trust
assumptions. NS-PI sees a distribution shift in the signed log; the oracle
re-checks against an independent request view. NS-PI is therefore a
complementary log-only signal, not the strongest verifier.

---

## 4. XAI And Audit Reviewability (table-backed)

Source: `results/tables/explanation_audit_quality_summary.csv` and the
seed-confidence rows (family `xai_audit_quality`).

| Metric | n_seeds | Mean | Std | Min | Max |
|---|---:|---:|---:|---:|---:|
| trace complete rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| counterfactual coverage rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| counterfactual validity rate | 5 | 0.996413 | 0.005470 | 0.987627 | 1.000000 |
| stable decision/reason row rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| audit reconstruction rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| decisive-attribute full text coverage | 5 | 0.781000 | 0.020833 | 0.755000 | 0.809000 |

`[INTERPRETATION]` Structured explanation traces and audit reconstruction are
complete and stable across five seeds. The measurable weakness is that the
rendered natural-language explanation does not surface every decisive attribute
(0.781 mean). This must be reported as a current limitation, not hidden.
Counterfactual validity is measured against the *learned NS-PI policy*, not a
human legal standard.

---

## 5. Workload And Seed-Confidence Stability (table-backed)

### 5.1 Global flip-fraction sensitivity

Source: `results/tables/nspi_compromised_signer_sensitivity_summary.csv` and
seed-confidence family `global_sensitivity`.

| Flip fraction | NS-PI global | NS-PI per-station | Trusted oracle |
|---:|---:|---:|---:|
| 0.02 | 0.0 | 0.0 | 1.0 |
| 0.05 | 0.0 | 0.0 | 1.0 |
| 0.10 | 1.0 | 0.6 | 1.0 |
| 0.15 | 1.0 | 1.0 | 1.0 |
| 0.25 | 1.0 | 1.0 | 1.0 |

Note: at the 0.10 point, NS-PI per-station has std 0.547723 across seeds
(from `results/tables/seed_confidence_summary.csv`), i.e. unstable.

### 5.2 Targeted station/district sensitivity

Source: `results/tables/nspi_targeted_compromised_signer_summary.csv` and
seed-confidence family `targeted_sensitivity`.

| Target | Flip fraction | Grouped detector mean | Trusted oracle |
|---|---:|---:|---:|
| station | 0.10 | 0.0 | 1.0 |
| station | 0.50 | 1.0 | 1.0 |
| district | 0.10 | 0.0 | 1.0 |
| district | 0.25 | 1.0 | 1.0 |

### 5.3 Workload-size stability of the headline result

Source: `results/tables/workload_policy_stress_summary.csv` and
seed-confidence family `workload_stress`.

At a 25% `compromised_signer` flip, across size arms N in {500,1000,2500,5000}
and the four policy-mix arms (3 stress seeds each): signed-chain detection
0.0 mean/0.0 std; NS-PI global detection 1.0 mean/0.0 std; trusted oracle
1.0 mean/0.0 std.

At a 10% flip, workload size still matters:

| N | NS-PI global mean | per-station mean | per-station std |
|---:|---:|---:|---:|
| 500 | 0.0 | 0.333333 | 0.577350 |
| 1000 | 1.0 | 0.333333 | 0.577350 |
| 2500 | 1.0 | 1.000000 | 0.000000 |
| 5000 | 1.0 | 1.000000 | 0.000000 |

`[INTERPRETATION]` The strong 25% result is stable; the weak low-rate/grouped
behaviour is workload-size dependent. Stress arms use 3 seeds while the
full-grid/sensitivity/XAI tables use 5 seeds - this seed-count mismatch is a
reporting caveat the paper must state.

---

## 6. Strong / Weak / Not-Proven (the honest split)

### Strong (stable, table-backed, multi-seed)

- `compromised_signer` asymmetry: integrity/ABAC baselines 0/5, NS-PI 5/5,
  trusted oracle 5/5 (std 0.0). Holds across the 24-cell workload/policy-mix
  stress matrix at 25% flip.
- XAI trace completeness, counterfactual coverage, stable-decision rate, and
  audit reconstruction: 1.0 mean, 0.0 std across 5 seeds.
- Ordinary integrity attacks are caught by the integrity/ABAC baselines
  (control result holds).

### Weak (real but limited / unstable)

- NS-PI overall AAS is the lowest of all defenses (0.2500, std 0.0932).
- NS-PI misses low-rate global corruption at 2% and 5%.
- Per-station drift at 10% flip is unstable (std ~0.55) and needs N>=2500.
- Rendered explanation text covers only 0.781 of decisive attributes.
- Cross-jurisdiction stress knob has limited headroom (baseline already ~77%).

### Not proven (must not be claimed)

- Any real-world police detection performance (synthetic workload only).
- That `compromised_signer` reflects real attacker incidence (modeling
  assumption, no field data).
- That the trusted raw-attribute oracle's independent view is operationally
  free (it is an assumption, scored as a baseline).
- Legal admissibility, deployment readiness, or production Fabric/CCTNS latency
  (timing values are local Python runtimes only).
- Differential-privacy or formal-privacy guarantees from metadata minimization.

---

## 7. Source-to-Claim Map (for the future Results section)

| Claim to write | Backing table |
|---|---|
| Overall AAS ranking | `full_grid_aas_by_defense.csv` |
| Per-attack detection | `full_grid_per_attack.csv`, `full_grid_raw.csv` |
| Compromised-signer asymmetry + stability | `seed_confidence_summary.csv` (detection_compromised_signer), `adaptive_attack_summary.csv` |
| Global sensitivity boundary | `nspi_compromised_signer_sensitivity_summary.csv` |
| Targeted sensitivity boundary | `nspi_targeted_compromised_signer_summary.csv` |
| XAI / audit reviewability | `explanation_audit_quality_summary.csv` |
| Workload / policy-mix robustness | `workload_policy_stress_summary.csv` |
| Across-seed stability for all of the above | `seed_confidence_summary.csv`, `seed_confidence_raw.csv` |

Any Results sentence that cannot point to a row in one of these tables must be
cut or tagged `[INTERPRETATION]`.

---

## 8. Verification

This iteration adds documentation only; it generates no tables and changes no
code. Repository state inherited from iter 033 (per `SESSION_HANDOFF.md` and
local check):

- `make test`: 75 passed.
- `make lint`: passed.
- `make reproduce`: passed.

No experiment or reproduction commands were required for this notes-only step.
Local table-inspection checks were used only to verify cited values. No commit
made.

## 9. Next Step

Draft the IEEE Threat Model and Results sections using section 7 as the
source-to-claim map and section 6 as the mandatory honesty split. Do not
introduce any metric that is not already in `results/tables/`.
