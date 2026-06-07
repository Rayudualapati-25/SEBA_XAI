# Multi-Seed Evaluation Findings

Generated: 2026-06-06
Status: regenerated from `scripts/run_full_grid.py`, `scripts/run_ablations.py`, `scripts/run_nspi_sensitivity.py`, `scripts/run_nspi_targeted_sensitivity.py`, `scripts/run_explanation_audit_quality.py`, `scripts/run_workload_policy_stress.py`, and `scripts/run_seed_confidence_summary.py` over seeds `{7, 21, 42, 99, 123}`. The workload/policy-mix stress arm now also uses the same five-seed set.

These findings define what the SEBA-XAI paper can honestly claim.

## 1. Overall AAS By Defense

From `results/tables/full_grid_aas_by_defense.csv`:

| Defense | AAS mean | AAS std |
|---|---:|---:|
| `abac_reexec` | 0.7917 | 0.0000 |
| `blockchain_style` | 0.7917 | 0.0000 |
| `ct_log` | 0.7917 | 0.0000 |
| `fabric_abac` | 0.7917 | 0.0000 |
| `signed_chain` | 0.7917 | 0.0000 |
| `mutable_log` | 0.5000 | 0.0000 |
| `nspi_drift` | 0.2500 | 0.0932 |
| `trusted_policy_oracle` | 1.0000 | 0.0000 |

Interpretation: NS-PI is **not** the best overall tamper detector. Cryptographic and ABAC-style defenses remain stronger for ordinary event edits because hashes, commitments, endorsement checks, and policy re-execution directly catch changed fields. The strongest baseline is now `trusted_policy_oracle`, which uses an independent raw-attribute view and reaches AAS 1.0 in this synthetic benchmark.

## 2. The New Useful Result

The decisive result is the `compromised_signer` attack.

From `results/tables/full_grid_per_attack.csv`:

| Defense | Detection rate on `compromised_signer` |
|---|---:|
| `mutable_log` | 0.0 |
| `signed_chain` | 0.0 |
| `blockchain_style` | 0.0 |
| `ct_log` | 0.0 |
| `fabric_abac` | 0.0 |
| `abac_reexec` | 0.0 |
| `nspi_drift` | 1.0 |
| `trusted_policy_oracle` | 1.0 |

This is the publishable asymmetry, but it must be stated carefully: if an attacker can corrupt policy output and re-sign a valid-looking canonical log, ledger-only integrity checks pass by construction. NS-PI can still notice that the learned decision distribution has shifted away from the declared policy behavior. However, a trusted raw-attribute oracle with a separate view of the original requests also catches the attack, so NS-PI is not the strongest possible defense; it is a complementary log-only signal.

## 3. Adaptive Attack Details

From `results/tables/adaptive_attack_summary.csv`, for `compromised_signer`:

| Seed | Integrity/ABAC baselines detected | NS-PI global detected | NS-PI per-station detected |
|---:|---:|---:|---:|
| 7 | 0 | 1 | 1 |
| 21 | 0 | 1 | 1 |
| 42 | 0 | 1 | 1 |
| 99 | 0 | 1 | 1 |
| 123 | 0 | 1 | 1 |

Observed global JS divergence ranged from approximately `0.0244` to `0.0337`, with permutation-test p-value `0.004975` in each seed.

From `results/tables/nspi_ablation.csv`, the full NS-PI drift detector and both global-only and per-station-only variants detected `compromised_signer` on the two ablation seeds tested (`99` and `123`).

## 4. Global Sensitivity Result

From `results/tables/nspi_compromised_signer_sensitivity_summary.csv`:

| Flip fraction | NS-PI global detection | NS-PI per-station detection | NS-PI any detection | Trusted oracle detection |
|---:|---:|---:|---:|---:|
| 0.02 | 0.0 | 0.0 | 0.0 | 1.0 |
| 0.05 | 0.0 | 0.0 | 0.0 | 1.0 |
| 0.10 | 1.0 | 0.6 | 1.0 | 1.0 |
| 0.15 | 1.0 | 1.0 | 1.0 | 1.0 |
| 0.20 | 1.0 | 1.0 | 1.0 | 1.0 |
| 0.25 | 1.0 | 1.0 | 1.0 | 1.0 |
| 0.35 | 1.0 | 1.0 | 1.0 | 1.0 |
| 0.50 | 1.0 | 1.0 | 1.0 | 1.0 |

This is an important limitation and should be included in the paper: NS-PI reliably detects the global compromised-signer attack once the flip fraction reaches about 10% in the current workload, but it misses smaller 2% and 5% corruptions. The trusted raw-attribute oracle catches every tested flip fraction because it compares each event against the original trusted request view.

## 5. Targeted Station/District Sensitivity Result

From `results/tables/nspi_targeted_compromised_signer_summary.csv`:

| Target scope | Target flip fraction | Mean global flip fraction | NS-PI global detection | NS-PI per-station detection | NS-PI per-district detection | NS-PI any detection | Trusted oracle detection |
|---|---:|---:|---:|---:|---:|---:|---:|
| station | 0.10 | 0.0042 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| station | 0.25 | 0.0114 | 0.0 | 0.6 | 0.2 | 0.6 | 1.0 |
| station | 0.50 | 0.0234 | 0.0 | 1.0 | 0.8 | 1.0 | 1.0 |
| station | 0.75 | 0.0348 | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| station | 1.00 | 0.0468 | 0.2 | 1.0 | 1.0 | 1.0 | 1.0 |
| district | 0.10 | 0.0102 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| district | 0.25 | 0.0264 | 0.0 | 0.8 | 1.0 | 1.0 | 1.0 |
| district | 0.50 | 0.0532 | 0.2 | 1.0 | 1.0 | 1.0 | 1.0 |
| district | 0.75 | 0.0798 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| district | 1.00 | 0.1066 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |

Interpretation: global NS-PI is weak for localized attacks because the total changed share of the full workload can remain small. Grouped drift is the useful version for this threat model. In the current synthetic workload, station-level grouped NS-PI detects targeted station corruption reliably from 50% of the targeted eligible rows, and district-level grouped NS-PI detects targeted district corruption reliably from 25% of the targeted eligible rows. NS-PI still misses very small targeted corruption at 10% of the target group. The trusted raw-attribute oracle detects every case because it performs row-level policy re-evaluation against an uncompromised request view.

## 6. XAI And Audit Quality Result

From `results/tables/explanation_audit_quality_summary.csv`:

| Metric | Mean | Std | Min | Max |
|---|---:|---:|---:|---:|
| Trace complete rate | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| Decisive attribute text coverage mean | 0.9310 | 0.0054 | 0.9231 | 0.9369 |
| Decisive attribute full text coverage rate | 0.7810 | 0.0208 | 0.7550 | 0.8090 |
| Counterfactual coverage rate | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| Counterfactual validity rate | 0.9964 | 0.0055 | 0.9876 | 1.0000 |
| Stable decision/reason row rate | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| Audit reconstruction rate | 1.0000 | 0.0000 | 1.0000 | 1.0000 |

Interpretation: the XAI layer now has measurable evidence, not just architecture text. Every synthetic request has a complete decision trace with decision, reason, rules, decisive attributes, policy version, decision hash, explanation hash, and audit anchor hash. Counterfactual explanations are generated for all deny/escalate rows in the current workload, and 99.64% replay to the proposed `allow` decision under the learned NS-PI policy. Audit reconstruction succeeds across all tested events by joining request records, signed hash-chain events, block index rows, and block commitments.

Important limitation: the decisive-attribute full text coverage rate is 0.781. This means the explanation artifacts are structurally complete, but not every decisive attribute is explicitly surfaced in the natural-language explanation text. The paper should report this as a current explanation-quality weakness, not hide it.

## 6b. Workload And Policy-Mix Stress Result

From `results/tables/workload_policy_stress_summary.csv` (40 raw cells: size arm
N∈{500,1000,2500,5000} and four policy-mix arms at N=1000, each over seeds
{7,21,42,99,123}; `cs25`/`cs10` = compromised_signer at 25%/10% flip).

What survives every workload size and policy mix:

| Property | Result |
|---|---|
| compromised_signer @25% — integrity (signed_chain) | 0.0 (blind by construction) at every size and mix |
| compromised_signer @25% — NS-PI global drift | 1.0 at every size and mix |
| compromised_signer @25% — trusted oracle | 1.0 at every size and mix |
| counterfactual validity | 1.0 at every size and mix in the latest regenerated stress summary |
| NS-PI rule-list train accuracy | improves with size: 0.9148 (N=500) → 0.9738 (N=5000) |

Realized policy-mix knobs moved as intended (vs N=1000 baseline classified
0.2386 / cross-juris 0.7814 / revoked 0.0942 / approval-missing 0.4534):
revoked 0.0942 → 0.2542, approval-missing 0.4534 → 0.5518, classified 0.2386 → 0.3044.

What is weak (size-dependent, reported honestly):

| Metric | N=500 | N=1000 | N=2500 | N=5000 |
|---|---:|---:|---:|---:|
| cs10 NS-PI global detection | 0.2 | 1.0 | 1.0 | 1.0 |
| cs10 NS-PI per-station detection | 0.2 | 0.6 | 1.0 | 1.0 |

So the earlier "≈10% global detection threshold" remains workload-size
dependent: global drift is inconsistent at N=500 and stable from N=1000 onward
in this benchmark, while per-station grouped drift reaches full detection only
from N=2500. The cross-jurisdiction knob also has limited headroom because the
baseline workload is already about 78% cross-jurisdiction (the high-cross arm
reaches about 0.82) — a generator limitation, not a result.

Boundary: the classified-ratio knob is an indirect proxy (sensitive-scenario
weights); realized ratios are reported so the effect is auditable. Synthetic
workload only.

## 6c. Seed-Level Confidence / Stability Summary

From `results/tables/seed_confidence_summary.csv` and
`results/tables/seed_confidence_raw.csv`:

| Evidence area | Rows/seeds | Main result |
|---|---:|---|
| Full-grid `compromised_signer` | 5 seeds | NS-PI drift and trusted oracle detection mean 1.0/std 0.0; ledger/audit baselines mean 0.0/std 0.0 |
| XAI/audit quality | 5 seeds | trace completeness, counterfactual coverage, stable decision/reason rows, and audit reconstruction all mean 1.0/std 0.0 |
| Counterfactual validity | 5 seeds | mean 0.996413/std 0.005470/min 0.987627 |
| Decisive-attribute full text coverage | 5 seeds | mean 0.781000/std 0.020833/min 0.755000/max 0.809000 |
| Workload stress | 5 seeds per cell | 25% compromised-signer asymmetry holds across all stress cells; 10% per-station detection remains size-dependent |

Interpretation: the seed-confidence table is now the safer source for paper
wording because it reports the measured variance behind headline claims. It
does not add new experiments and should not be described as a statistical proof.
It is a descriptive stability table over the raw seed-level artifacts already
in the repository.

## 7. What This Means For The Paper

The paper should now be framed as:

> A secure explainable access-governance overlay where blockchain-style audit and ABAC/PBAC enforce ordinary integrity and policy checks, trusted raw-attribute policy re-evaluation provides the strongest audit baseline when available, and NS-PI adds explainable log-only policy-drift monitoring for validly re-signed compromised-signer failures.

The paper should **not** say:

- NS-PI beats blockchain overall.
- NS-PI replaces ABAC/PBAC.
- NS-PI beats a trusted independent policy oracle.
- The system is deployment-ready.
- The result proves legal compliance.
- The model predicts crime or criminals.

## 8. Remaining Weaknesses

1. The `compromised_signer` attack is a synthetic threat model. It is useful, but the paper must explain why this attacker model is realistic enough to study.
2. The trusted raw-attribute oracle assumes a separate uncompromised view of original request attributes. This is a strong assumption and must be described as a baseline, not a free operational guarantee.
3. The current workload is synthetic. The paper can claim reproducibility and controlled evaluation, not real-world police performance.
4. NS-PI still performs poorly on single-row tamper events, low-rate 2% to 5% global compromised-signer corruption, and 10% targeted station/district corruption, which is expected because it is a distribution-level detector.
5. The natural-language explanation text does not fully mention every decisive attribute in all cases. The trace is complete, but the rendered explanation can be improved.
6. NS-PI drift sensitivity is workload-size dependent: at a 10% compromised-signer flip, global drift misses at N=500 and per-station drift is unreliable below N=2500 (see section 6b). The cross-jurisdiction stress knob also has limited headroom because the baseline workload is already ~77% cross-jurisdiction.
7. The seed-confidence table is descriptive across-seed evidence. It is not a formal confidence interval and does not prove operational robustness.

## 9. Research Decision

The solid first-paper direction is no longer "AI + blockchain + police data" in a broad way.

The solid direction is:

> **SEBA-XAI as a benchmarked architecture for explainable policy-drift detection and trusted policy re-evaluation in blockchain-audited police access governance.**

This is narrower, measurable, and supported by current repository evidence.

## 10. Verification Commands

Latest verification:

- `make lint` passed.
- `make typecheck` passed after fixing typing issues in the attack registry,
  NS-PI helper signatures, counterfactual edit typing, and scoring grid types.
- `make reproduce` passed and regenerated the multi-seed pipeline artifacts.
- `make figures` passed and regenerated the paper SVG figures under
  `papers/final_paper/figures_tables/`.
- `python3 scripts/run_full_grid.py` regenerated the full-grid result tables.
- `python3 scripts/run_ablations.py` regenerated adaptive attack and NS-PI ablation tables.
- `python3 scripts/run_nspi_sensitivity.py` generated compromised-signer sensitivity tables.
- `python3 scripts/run_nspi_targeted_sensitivity.py` generated targeted station/district compromised-signer sensitivity tables.
- `python3 scripts/run_explanation_audit_quality.py` generated XAI and audit reconstruction quality tables.
- `python3 scripts/run_workload_policy_stress.py` generated the workload/policy-mix stress tables (40 raw cells, 40/40 ok).
- `python3 scripts/run_seed_confidence_summary.py` generated 139 metric/group rows and 695 per-seed values.
- `make test` passed with `75 passed` after adding `tests/test_workload_policy_stress.py` and `tests/test_seed_confidence_summary.py`.
