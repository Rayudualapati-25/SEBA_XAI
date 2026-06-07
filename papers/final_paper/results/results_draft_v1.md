# Results (Aligned Draft v2)

Status: evidence-aligned results draft for the SEBA-XAI paper. Not final
camera-ready prose.
Evidence basis: artifacts under `results/tables/`, consolidated in
`results/FINDINGS.md`, `papers/final_paper/artifact_to_claim_table.csv`,
`papers/final_paper/result_metric_dictionary.md`, and
`reports/iteration/iter_034_threat_model_results_notes.md`.

Every quantitative claim cites a local artifact path inline. Statements that
are analysis rather than a measured value are tagged `[INTERPRETATION]`. All
results are on synthetic workloads; no real records or infrastructure are used.
Detection values are rates in [0, 1] (1.0 = always detected across the seeds
used for that table). Variance is reported as across-seed sample standard
deviation from `results/tables/seed_confidence_summary.csv`.

## 0. Claim Alignment

This Results section supports the following claim-table rows:

| Result Area | Claim IDs | Main Artifacts |
|---|---|---|
| Overall defense comparison | C08-C10 | `results/tables/full_grid_aas_by_defense.csv`, `results/tables/full_grid_per_attack.csv` |
| Compromised-signer asymmetry | C11-C13 | `results/tables/full_grid_per_attack.csv`, `results/tables/adaptive_attack_summary.csv`, `results/tables/seed_confidence_summary.csv` |
| NS-PI sensitivity limits | C14-C17 | `results/tables/nspi_compromised_signer_sensitivity_summary.csv`, `results/tables/nspi_targeted_compromised_signer_summary.csv`, `results/tables/workload_policy_stress_summary.csv` |
| XAI and audit reviewability | C18-C22 | `results/tables/explanation_audit_quality_summary.csv` |
| Metadata exposure and local overhead | C23-C24 | `results/tables/paper_table_03_metadata_exposure.csv`, `results/tables/paper_table_04_latency_storage.csv` |
| Limitations and evidence boundary | C29-C30 | `results/FINDINGS.md`, `papers/final_paper/claim_control_memo.md` |

No result in this section should be read as real CCTNS/ICJS performance,
legal compliance, production security, or crime-prediction performance.

## 1. Evaluation Setup

The evaluation compares eight defenses against an attack catalog over five
random seeds {7, 21, 42, 99, 123} for the full grid, sensitivity,
explanation-quality, and workload/policy-mix stress experiments. Defenses are: `mutable_log`,
`signed_chain`, `blockchain_style`, `ct_log`, `fabric_abac`, `abac_reexec`,
`trusted_policy_oracle`, and `nspi_drift`. The per-seed records are in
`results/tables/full_grid_raw.csv`, and across-seed summaries are in
`results/tables/seed_confidence_summary.csv`.

## 2. Overall Adversarial Audit Score

The Adversarial Audit Score (AAS) aggregates detection across the catalog.
From `results/tables/full_grid_aas_by_defense.csv`:

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

`[INTERPRETATION]` On the full catalog, NS-PI has the lowest AAS among the
listed defenses and is not presented as a general tamper detector. The
integrity and re-execution defenses are stronger for ordinary tampering, and
the trusted raw-attribute oracle is the strongest baseline because it has an
independent view of the original requests. The value of NS-PI is localized to
one attack regime, examined next.

## 3. Ordinary Tamper Attacks

From `results/tables/full_grid_per_attack.csv`, the signed hash-chain,
blockchain-style audit, CT-style log, Fabric+ABAC, and ABAC re-execution
defenses detect the ordinary field-modifying attacks (`replay_approval_token`,
`backdate_request`, `swap_explanation_hash`, `collude_block_signature`,
`revocation_race`), while the mutable log does not.

`[INTERPRETATION]` This is the expected control result: defenses that verify a
hash/commitment or recompute a decision catch changes that break those checks.
It confirms the integrity baselines function correctly, which is the
precondition for interpreting the compromised-signer result in Section 4.

## 4. The Compromised-Signer Asymmetry

The decisive result concerns the compromised-signer attacker, who corrupts
policy output and re-signs a valid log. From
`results/tables/seed_confidence_summary.csv` (family
`detection_compromised_signer`):

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

An adaptive cross-check in `results/tables/adaptive_attack_summary.csv`
(compromised-signer rows) agrees: for each of seeds {7, 21, 42, 99, 123} the
integrity and ABAC baselines detect 0, while NS-PI global and per-station drift
both detect 1. As reported in `results/FINDINGS.md` Section 3, the observed
global Jensen-Shannon divergence ranged approximately 0.0244 to 0.0337 with a
permutation-test p-value of 0.004975 per seed.

`[INTERPRETATION]` Both NS-PI and the trusted raw-attribute oracle detect this
attack, but under different visibility. The oracle re-checks each event against
an independent request view; NS-PI observes only that the signed decision
distribution has shifted away from the learned policy behavior. NS-PI is
therefore a complementary log-only signal for a regime where ledger-only
integrity is blind by construction, not a replacement for the oracle.

## 5. Global Flip-Fraction Sensitivity

The strength of the NS-PI signal depends on how much of the workload is
corrupted. From `results/tables/nspi_compromised_signer_sensitivity_summary.csv`:

| Flip fraction | NS-PI global | NS-PI per-station | Trusted oracle |
|---:|---:|---:|---:|
| 0.02 | 0.0 | 0.0 | 1.0 |
| 0.05 | 0.0 | 0.0 | 1.0 |
| 0.10 | 1.0 | 0.6 | 1.0 |
| 0.15 | 1.0 | 1.0 | 1.0 |
| 0.25 | 1.0 | 1.0 | 1.0 |

At the 0.10 flip fraction, the per-station detector has across-seed std
0.547723 in `results/tables/seed_confidence_summary.csv`, indicating an
unstable boundary at that point.

`[INTERPRETATION]` NS-PI misses small global corruption at 2% and 5% in this
benchmark. In the global sensitivity table it detects the 10% flip condition,
but the workload stress study in Section 8 shows that this boundary is
workload-size dependent. The trusted oracle detects every tested flip fraction
because it operates at the row level against an independent view. These are
benchmark boundaries, not thresholds for any deployed setting.

## 6. Targeted Station/District Sensitivity

From `results/tables/nspi_targeted_compromised_signer_summary.csv`:

| Target | Flip fraction | Grouped detector mean | Trusted oracle |
|---|---:|---:|---:|
| station | 0.10 | 0.0 | 1.0 |
| station | 0.50 | 1.0 | 1.0 |
| district | 0.10 | 0.0 | 1.0 |
| district | 0.25 | 1.0 | 1.0 |

`[INTERPRETATION]` Grouped (per-station / per-district) drift becomes useful
only when the targeted corruption is a large enough share of the selected
group. It is not a row-level verifier, and at 10% targeted corruption it does
not fire, while the trusted oracle still detects. This reinforces the
complementary-not-replacement framing.

## 7. XAI and Audit Reviewability

From `results/tables/explanation_audit_quality_summary.csv`, with across-seed
variance from `results/tables/seed_confidence_summary.csv` (family
`xai_audit_quality`):

| Metric | n_seeds | Mean | Std | Min | Max |
|---|---:|---:|---:|---:|---:|
| trace complete rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| counterfactual coverage rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| counterfactual validity rate | 5 | 0.996413 | 0.005470 | 0.987627 | 1.000000 |
| stable decision/reason row rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| audit reconstruction rate | 5 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| decisive-attribute full text coverage | 5 | 0.781000 | 0.020833 | 0.755000 | 0.809000 |

`[INTERPRETATION]` Structured decision traces, counterfactual coverage,
duplicate-context stability, and audit reconstruction are complete and stable
across the five seeds. The measurable weakness is that the rendered
natural-language explanation surfaces only 0.781 of decisive attributes on
average, so the structured trace is complete but the text rendering is not. We
report this as a current limitation. Counterfactual validity is measured
against the learned NS-PI policy, not against a human or legal review standard.

## 8. Workload and Policy-Mix Stress

The headline asymmetry is tested across workload size and policy mix in
`results/tables/workload_policy_stress_summary.csv` (40 raw cells: size arm
N in {500, 1000, 2500, 5000} and four policy-mix arms at N=1000, five stress
seeds each). At a 25% compromised-signer flip, across all stress cells:
signed-chain detection is 0.0 (mean) / 0.0 (std), NS-PI global detection is
1.0 / 0.0, and trusted oracle detection is 1.0 / 0.0.

At a 10% flip, workload size still matters
(`results/tables/seed_confidence_summary.csv`, family `workload_stress`):

| N | NS-PI global mean | per-station mean | per-station std |
|---:|---:|---:|---:|
| 500 | 0.2 | 0.2 | 0.447214 |
| 1000 | 1.0 | 0.6 | 0.547723 |
| 2500 | 1.0 | 1.000000 | 0.000000 |
| 5000 | 1.0 | 1.000000 | 0.000000 |

The realized policy-mix knobs moved as intended relative to the N=1000 baseline
(classified 0.2386, cross-jurisdiction 0.7814, revoked 0.0942, approval-missing
0.4534): revoked rose to 0.2542, approval-missing to 0.5518, and classified to
0.3044, per `results/FINDINGS.md` Section 6b.

`[INTERPRETATION]` The strong 25% result is stable across size and mix; the
weak low-rate behavior is workload-size dependent. The cross-jurisdiction knob
has limited headroom because the baseline workload is already about 77%
cross-jurisdiction, which is a generator limitation rather than a result.

## 9. Seed-Level Stability

The seed-confidence consolidation in `results/tables/seed_confidence_summary.csv`
(139 metric/group rows) and `results/tables/seed_confidence_raw.csv` (695
per-seed values) provides the across-seed variance behind the headline claims.
The compromised-signer asymmetry, trace completeness, counterfactual coverage,
stable-decision rate, and audit reconstruction all show std 0.0 across their
seeds; the variable points are the low-rate / grouped sensitivity boundaries
and the explanation-text coverage metric.

`[INTERPRETATION]` This table is descriptive across-seed evidence. It is not a
formal confidence interval and does not establish robustness beyond the seeds
and synthetic workloads evaluated.

## 9b. Metadata Exposure and Local Overhead

The metadata-minimization comparison in
`results/tables/paper_table_03_metadata_exposure.csv` compares a
full-metadata ledger with a minimized-commitment ledger. The full-metadata
ledger has a prototype metadata exposure score of 1.0000, while the
minimized-commitment ledger has a score of 0.0000 under the implemented
schema-level proxy.

The local overhead table in
`results/tables/paper_table_04_latency_storage.csv` reports p50
build/decision latency, p50 verification latency where applicable, and
storage per event/request for prototype components including the policy
oracle/XAI stage, mutable log, signed hash chain, and permissioned
blockchain-style audit simulation.

`[INTERPRETATION]` These measurements support only a local prototype
tradeoff discussion. The metadata exposure score is not a formal privacy
guarantee, and the latency/storage values are not production CCTNS/ICJS or
live Fabric measurements.

## 10. Limitations

The following limitations are recorded directly from `results/FINDINGS.md`
Section 8 and the source tables:

1. The compromised-signer attacker is a synthetic threat model; the benchmark
   shows the detection asymmetry, not real-world incidence.
2. The trusted raw-attribute oracle assumes a separate, uncompromised view of
   original requests and is therefore a baseline, not a free operational
   property.
3. All workloads are synthetic; the work supports reproducible controlled
   evaluation, not real-world performance.
4. NS-PI performs poorly on single-event tampering, on low-rate 2%–5% global
   compromised-signer corruption, and on 10% targeted station/district
   corruption, consistent with its distribution-level design.
5. The rendered explanation text does not surface every decisive attribute
   (0.781 mean coverage), even though the structured trace is complete.
6. NS-PI low-rate sensitivity is workload-size dependent: global drift misses
   at N=500 and per-station drift is unreliable below N=2500 at a 10% flip.
7. The seed-confidence table is descriptive across-seed evidence and is not a
   formal statistical interval.

`[INTERPRETATION]` Taken together, the results support a narrow, conservative
claim: SEBA-XAI combines integrity audit, trusted policy re-evaluation where an
independent view exists, and an interpretable log-only drift signal, with each
mechanism catching a different failure mode under a different trust assumption.
