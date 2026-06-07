# Evidence-Locked Contribution Statement

Generated: 2026-05-29
Status: REVISED AFTER MULTI-SEED EVIDENCE.

## Current Defensible Contribution

> We propose **NS-PI**, a neuro-symbolic policy-induction and drift-detection component for SEBA-XAI that learns an interpretable rule-list view of access-governance decisions and flags policy-distribution drift in validly re-signed compromised-signer logs. Across five synthetic seeds, NS-PI detected the `compromised_signer` attack in 5/5 seeds while ledger-only integrity and audit-only policy baselines detected 0/5. A stronger independent raw-attribute policy oracle also detected 5/5, showing that NS-PI is best framed as a complementary log-only drift signal, not as a replacement for trusted policy re-evaluation.

This is now the first-paper claim. It is narrower than the earlier claim and better supported by the repository evidence. The XAI layer also now has measured reviewability evidence: complete decision traces, counterfactual replay validity, stability checks, and audit reconstruction from signed events to block commitments.

## What Changed From The Old Claim

The earlier locked sentence claimed that NS-PI would reduce severity-weighted false-allow rate over RBAC and ABAC/PBAC baselines across the full adversarial workload. The current evidence does **not** support that broad claim.

From `results/tables/full_grid_aas_by_defense.csv`, the overall AAS means are:

| Defense | AAS mean |
|---|---:|
| `abac_reexec` | 0.7917 |
| `blockchain_style` | 0.7917 |
| `ct_log` | 0.7917 |
| `fabric_abac` | 0.7917 |
| `signed_chain` | 0.7917 |
| `mutable_log` | 0.5000 |
| `nspi_drift` | 0.2500 |
| `trusted_policy_oracle` | 1.0000 |

So NS-PI is **not** an overall tamper-detection winner. The publishable angle is complementary detection: integrity mechanisms catch ordinary log edits, a trusted raw-attribute oracle catches policy-output corruption when the raw request view is available, and NS-PI gives a log-only drift alarm when the auditor only sees the signed decision trace.

## Evidence That Supports The Claim

Primary evidence files:

- `results/tables/full_grid_per_attack.csv`
- `results/tables/full_grid_aas_by_defense.csv`
- `results/tables/adaptive_attack_summary.csv`
- `results/tables/nspi_ablation.csv`
- `results/tables/nspi_compromised_signer_sensitivity_summary.csv`
- `results/tables/nspi_targeted_compromised_signer_summary.csv`
- `results/tables/explanation_audit_quality.csv`
- `results/tables/explanation_audit_quality_summary.csv`
- `results/tables/workload_policy_stress_summary.csv`
- `results/tables/workload_policy_stress_raw.csv`
- `results/tables/seed_confidence_summary.csv`
- `results/tables/seed_confidence_raw.csv`

Key result:

| Attack | Ledger-only integrity/audit baselines | Trusted raw oracle | NS-PI drift |
|---|---:|---:|---:|
| `compromised_signer` | 0/5 seeds detected | 5/5 seeds detected | 5/5 seeds detected |

`results/tables/adaptive_attack_summary.csv` also shows that both global drift and per-station drift detected `compromised_signer` for seeds 7, 21, 42, 99, and 123.

The sensitivity tables add the boundary condition. NS-PI misses very low-rate global corruption at 2% and 5%, and it misses 10% targeted station/district corruption. Grouped drift becomes useful for localized attacks: in the current workload, per-station drift reaches full detection at 50% of targeted station eligible rows, while per-district drift reaches full detection at 25% of targeted district eligible rows. These are not deployment thresholds; they are synthetic benchmark findings.

The explanation/audit quality tables add the XAI evidence. Across five seeds, trace completeness is 1.0, counterfactual coverage is 1.0, counterfactual validity averages 0.9964 with std 0.005470, stable decision/reason row rate is 1.0 for duplicate policy contexts, and audit reconstruction rate is 1.0. The explanation weakness is also measurable: decisive-attribute full text coverage averages 0.781 with std 0.020833, so some decisive attributes are present in the structured trace but not fully rendered in the explanation text.

The seed-confidence summary now consolidates 139 metric/group rows and 695 per-seed values from the existing raw tables. It confirms that the `compromised_signer` asymmetry is stable across the five full-grid seeds (`nspi_drift` mean 1.0/std 0.0; ledger and audit baselines mean 0.0/std 0.0), while the low-rate and targeted sensitivity boundaries remain visible.

## Novelty Boundary

This paper should **not** claim that:

- NS-PI replaces cryptographic audit logs.
- NS-PI is better than blockchain for ordinary tamper detection.
- NS-PI is stronger than an independent trusted raw-attribute policy oracle.
- SEBA-XAI proves legal compliance or deployment readiness.
- The system uses real police records.
- The system predicts criminals or individual crime risk.
- The prototype is a real Hyperledger Fabric deployment.

The honest claim is:

> SEBA-XAI needs integrity audit, trusted policy re-evaluation where possible, and interpretable policy-drift monitoring because they catch different failure modes and rely on different trust assumptions.

## First-Paper Framing

Recommended title direction:

> SEBA-XAI: Explainable Policy-Drift Detection for Blockchain-Audited Police Access Governance

Recommended contribution bullets:

1. Formulate a CCTNS/ICJS-compatible sensitive-record access-governance problem for inter-agency police data sharing.
2. Propose a SEBA-XAI overlay with off-chain records, policy-based access control, permissioned audit commitments, and logged explanation artifacts.
3. Introduce an adversarial audit benchmark covering ordinary tamper attacks, metadata leakage, and validly re-signed compromised-signer attacks.
4. Evaluate NS-PI as a complementary interpretable policy-drift detector, showing it detects the compromised-signer attack that ledger-only integrity defenses miss, while also comparing it against a stronger trusted raw-attribute policy-oracle baseline.
5. Measure XAI and audit reviewability through trace completeness, decisive-attribute text coverage, counterfactual validity, stability, and audit reconstruction metrics.

## Required Next Evidence Before Paper Submission

Before writing final IEEE-style results claims, the repo still needs:

1. ~~A seed-level confidence table for the final paper, not only mean values~~ **(DONE, iter 033)**: `results/tables/seed_confidence_summary.csv` and `results/tables/seed_confidence_raw.csv` consolidate across-seed mean/std/min/max from existing seed-level artifacts. This is descriptive stability evidence, not a deployment guarantee.
2. A threat-model paragraph that clearly defines what "compromised signer" means, what the trusted raw-attribute oracle assumes, and when NS-PI is useful as a log-only signal.
3. A limitation statement that NS-PI misses low-rate 2% and 5% global compromised-signer corruption and 10% targeted station/district corruption in the current workload.
4. A limitation statement that explanation traces are complete but rendered explanation text does not fully cover every decisive attribute.
5. ~~Stress tests over workload size and policy mix~~ **(DONE, iter 032; extended to five seeds in iter 041)**: 40-cell workload/policy-mix stress matrix (`results/tables/workload_policy_stress_summary.csv`). The compromised_signer asymmetry (integrity 0.0 / NS-PI global 1.0 / trusted oracle 1.0 at 25% flip) and counterfactual validity (1.0 in the latest regenerated stress summary) hold across N∈{500,1000,2500,5000} and across high-classified, high-cross-jurisdiction, high-revoked, and high-approval-missing mixes. Remaining limitation: at a 10% flip NS-PI global drift is inconsistent at N=500 and per-station drift needs N≥2500 for full detection in this benchmark, so the NS-PI low-rate threshold is workload-size dependent.
