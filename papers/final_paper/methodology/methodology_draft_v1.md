# Methodology (Aligned Draft v2)

Status: evidence-aligned methodology draft for the SEBA-XAI paper. Not final
camera-ready prose.
Evidence basis: `CONTRIBUTION.md`, `results/FINDINGS.md`,
`papers/final_paper/research_master_dashboard.md`,
`papers/final_paper/claim_control_memo.md`,
`papers/final_paper/artifact_to_claim_table.csv`,
`papers/final_paper/threat_model/threat_model_draft_v1.md`,
`papers/final_paper/results/results_draft_v1.md`, `06_proposed_architecture.md`,
`07_methodology.md`, `08_experiment_plan.md`, `09_evaluation_metrics.md`,
`scripts/run_full_grid.py`, `scripts/run_ablations.py`,
`scripts/run_nspi_sensitivity.py`, `scripts/run_nspi_targeted_sensitivity.py`,
`scripts/run_explanation_audit_quality.py`,
`scripts/run_workload_policy_stress.py`,
`scripts/run_seed_confidence_summary.py`, and the prototype generator and
oracle scripts under `prototype/synthetic_access_sim/`.

Every quantitative claim in this draft cites a local artifact path inline.
Statements that are analysis rather than a measured value are tagged
`[INTERPRETATION]`. All evaluation is on synthetic workloads.

## 0. Claim Alignment

This methodology supports the following claim-table rows:

| Claim ID | Methodology Role |
|---|---|
| C01 | Defines the evaluation as a synthetic CCTNS/ICJS-style access-governance workload. |
| C03 | Defines the compared baselines and defenses. |
| C04 | States that the blockchain layer is a local permissioned-audit simulation, not a live Fabric deployment. |
| C11 | Defines the validly re-signed compromised-signer attack. |
| C18-C22 | Defines the XAI and audit reviewability metrics. |
| C23-C24 | Defines metadata exposure and local overhead measurements. |
| C29 | Preserves the evidence boundary: no real deployment, no real police data, no formal privacy proof, and no production Fabric claim. |

The methodology should therefore be read as a reproducible benchmark design,
not as an operational integration design.

## 1. System Overview

SEBA-XAI is evaluated as a synthetic-workload research prototype for
explainable, blockchain-style-audited access governance over sensitive
police and criminal-justice records. The overlay positions a request gateway,
a declared policy oracle, an explanation layer, and a permissioned audit
layer above existing agency record systems, as described in
`06_proposed_architecture.md`. Raw records remain off-chain; the audit layer
stores decision summaries, policy and model/version identifiers, hash
commitments, anchor hashes, and minimized metadata required for review.

`[INTERPRETATION]` This work studies the overlay as a benchmark instrument,
not as an operational system. No actual records, operational signing
infrastructure, live CCTNS/ICJS interfaces, or live Hyperledger Fabric network
are used. The architecture text in
`06_proposed_architecture.md` is taken as the reference for component
naming; the implemented prototype reduces that architecture to a set of
scripted, file-backed stages so that every defense, attack, and metric is a
pure function over the recorded artifacts.

## 2. Synthetic Workload Generation

The workload is produced by the deterministic generator
`prototype/synthetic_access_sim/generate_synthetic_requests.py`, invoked
through the multi-seed driver used by
`scripts/run_full_grid.py` and the stress harness in
`scripts/run_workload_policy_stress.py`. The generator emits synthetic
stations, officers, cases, records, and access requests, together with a
`config.yaml`, a `dataset_manifest.json`, and a `dataset_profile.csv`, into
`prototype/runs/<run_id>/artifacts/`, consistent with the Stage 1 entity and
attribute lists in `07_methodology.md`.

Each request is parameterized by subject, object, and environment
attributes (role, rank, station, jurisdiction, case assignment, credential
status, sensitivity level, sealed/juvenile/witness flags, time window,
purpose, emergency flag, court/prosecutor flag, and policy version), as
listed in `07_methodology.md`. Scenario types are drawn from a fixed weight
vector (`normal`, `cross_jurisdiction_sensitive`, `revoked_credential`,
`stale_assignment`, `juvenile_witness`, `emergency`, `court_request`,
`sealed_record`, `expired_approval_token`, `random`) using the baseline
weights documented at the top of `scripts/run_workload_policy_stress.py`
(`BASELINE_WEIGHTS = [20, 14, 8, 10, 9, 8, 8, 8, 7, 8]`). The integer seed
controls all randomness; multi-seed evaluations use the seed sets defined
in Section 13.

`[INTERPRETATION]` The generator does not claim distributional realism
relative to actual CCTNS/ICJS traffic and does not use real FIR, CCTNS, ICJS,
or police access-log records. It defines a controlled,
reproducible reference workload over which detector behavior can be
measured and compared.

## 3. Declared Policy Oracle and XAI Artifacts

Stage 2 in `07_methodology.md` is implemented by
`prototype/synthetic_access_sim/policy_oracle.py`, which labels each
synthetic request with one of {`allow`, `deny`, `escalate`}. For each
request, the oracle also emits a reason code, a decisive-attribute list,
and the artifact hashes used by the audit layer: a decision hash, an
explanation hash, and an audit anchor hash. The deterministic rules used by
the oracle (revoked-credential deny, sealed-record deny unless court/
prosecutor flag with valid approval, juvenile/witness escalation,
cross-jurisdiction classified escalation, valid case assignment plus
role/rank plus purpose plus time window allow, stale assignment or expired
approval deny) follow the minimum rule list in `07_methodology.md`.

The oracle is treated as the labeling function for the benchmark, as
recorded in `papers/final_paper/threat_model/threat_model_draft_v1.md`
Section 2. `[INTERPRETATION]` It is not a claim of real-world policy
correctness; it is the reference decision against which detector behavior
is scored on the synthetic workload.

The XAI artifacts produced per request, together with their hash
commitments, are the substrate for the reviewability metrics in Section 11
and for the audit-reconstruction join performed by
`scripts/run_explanation_audit_quality.py`.

## 4. Audit Layers

The prototype implements four layered audit views over the labelled
requests, each cited by file path so the implementation surface is
explicit:

- A mutable database-style log baseline
  (`prototype/synthetic_access_sim/audit_baseline.py`), used by the
  `mutable_log` defense in `scripts/run_full_grid.py`.
- A signed append-only hash-chain on the canonical event records, exercised
  by the `signed_chain_detector` in `scripts/run_ablations.py` and by the
  `signed_chain` defense column of `results/tables/full_grid_raw.csv`.
- A permissioned blockchain-style audit layer
  (`prototype/synthetic_access_sim/blockchain_audit.py`) that emits a
  `block_event_index.csv` and a `permissioned_audit_blocks.jsonl` under
  `prototype/runs/<run_id>/artifacts/`, located by the helper
  `_step4_artifacts_for` in `scripts/run_explanation_audit_quality.py`. The
  corresponding defense column in `results/tables/full_grid_raw.csv` is
  `blockchain_style`.
- Off-chain encrypted pointer commitments with metadata minimization
  (`prototype/synthetic_access_sim/offchain_storage.py`), consistent with
  the on-chain / off-chain split in `06_proposed_architecture.md`.

`[INTERPRETATION]` The blockchain-style audit layer is a file-backed
simulation of permissioned chain commitments, not a Hyperledger Fabric
deployment, as also stated in `prototype/synthetic_access_sim/README.md` and
claim row C04 in `papers/final_paper/artifact_to_claim_table.csv`.
All audit timings reported elsewhere are local script runtimes, not
infrastructure measurements.

## 5. Baselines

The eight defenses scored per seed and per attack in
`results/tables/full_grid_aas_by_defense.csv` and
`results/tables/full_grid_raw.csv` are:

- `mutable_log` — a baseline database-style append log with no integrity
  mechanism, used as the lower bound for tamper detection.
- `signed_chain` — an append-only log with per-event hash chaining and
  signature verification, invoked through `signed_chain_detector` in
  `scripts/run_ablations.py`.
- `blockchain_style` — the permissioned audit-block view from
  `prototype/synthetic_access_sim/blockchain_audit.py`, checked via the
  quorum-style detector wired into `scripts/run_ablations.py`.
- `ct_log` — a Certificate-Transparency-style log baseline implemented in
  `seba.baselines.ct_log_detector` and invoked from
  `scripts/run_ablations.py`.
- `fabric_abac` — a Fabric-style ABAC re-evaluation baseline implemented in
  `seba.baselines.fabric_abac_detector` and invoked from
  `scripts/run_ablations.py`.
- `abac_reexec` — a plain ABAC re-execution of the recorded canonical
  output via `abac_reexecution_detector` in `scripts/run_ablations.py`.
- `trusted_policy_oracle` — the stronger independent-view baseline
  implemented by `seba.baselines.TrustedRawPolicyOracle`, instantiated for
  example in `scripts/run_nspi_sensitivity.py`. It re-evaluates policy over
  an uncompromised raw request view rather than the recorded canonical
  output.
- `nspi_drift` — the NS-PI drift detector described in Section 7.

Cross-references in `CONTRIBUTION.md` and
`papers/final_paper/results/results_draft_v1.md` confirm that the integrity
and ABAC baselines reach AAS mean 0.7917 in
`results/tables/full_grid_aas_by_defense.csv`, the mutable log reaches
0.5000, NS-PI reaches 0.2500, and the trusted raw-attribute oracle reaches
1.0000.

`[INTERPRETATION]` The baseline list is chosen to span ledger-only
integrity (mutable, signed chain, blockchain-style, CT-style), policy
re-execution over the recorded output (Fabric+ABAC, ABAC re-execution), and
policy re-evaluation over an independent raw view (trusted oracle), so that
NS-PI can be compared against detectors with strictly different
visibilities, consistent with the visibility table in
`papers/final_paper/threat_model/threat_model_draft_v1.md` Section 5 and
claim rows C03, C09, and C10.

## 6. Attack Catalog

The catalog attacks recorded per seed in `results/tables/full_grid_raw.csv`
are:

- `replay_approval_token` — reuse of a previously valid approval token;
- `backdate_request` — alteration of a recorded timestamp;
- `swap_explanation_hash` — substitution of explanation/anchor material;
- `collude_block_signature` — manipulation of block-level signing
  structure;
- `revocation_race` — exploitation of revocation timing;
- `metadata_inference` — a read-only inference attack on the published
  ledger view, scored separately because it does not modify the record.

A `compromised_signer` attack, implemented in
`seba.attacks.compromised_signer.compromised_signer` and invoked by
`scripts/run_nspi_sensitivity.py`, flips a configurable fraction of `deny`
or `escalate` decisions to `allow` and re-signs the resulting log so that
ledger-only integrity checks pass by construction
(`papers/final_paper/threat_model/threat_model_draft_v1.md` Section 4).

In addition, two adaptive attacks are exercised by
`scripts/run_ablations.py` through `seba.attacks.adaptive.ADAPTIVE_ATTACKS`:
`policy_skew_corruption` and `coordinated_laundering`. Their per-seed
detection outcomes appear in `results/tables/adaptive_attack_summary.csv`.

Each attack is implemented as a pure function over the recorded log and
runs once per seed; the resulting perturbed log is the only input visible
to the corresponding detector, mirroring the threat-model assumption that
the defender sees what the audit layer recorded.

## 7. NS-PI Drift Detector

NS-PI learns an interpretable rule-list view of the declared-policy
behavior with `seba.nspi.learn_policy` (max depth 8, minimum leaf size 10
for the full grid in `scripts/run_full_grid.py`; 20 for the train/test
ablation in `scripts/run_ablations.py`), and then compares the recorded
decision distribution against the policy's reference distribution. The
comparison uses a Jensen-Shannon divergence statistic with a
permutation-test alarm in `seba.nspi.drift.drift_test`, configured in
`scripts/run_nspi_sensitivity.py` with 200 permutations and `alpha=0.05`.
A grouped variant (`per_group_drift`) runs the same test per station or per
district. Both the global and grouped variants are exercised by
`scripts/run_full_grid.py`, `scripts/run_ablations.py`,
`scripts/run_nspi_sensitivity.py`, and
`scripts/run_nspi_targeted_sensitivity.py`.

The observed global divergence and p-value ranges for the
compromised-signer attack are reported in
`results/tables/adaptive_attack_summary.csv` and summarized in
`results/FINDINGS.md` Section 3 (approximately 0.0244 to 0.0337 with
permutation p-value 0.004975 per seed).

`[INTERPRETATION]` NS-PI is a distribution-level detector: it has log-only
visibility and does not verify individual events. Its contribution is
narrow, complementary detection in the compromised-signer regime
(`results/FINDINGS.md` Section 2 and
`papers/final_paper/threat_model/threat_model_draft_v1.md` Section 5). It is
not claimed to replace ABAC/PBAC, blockchain-style audit, or the trusted
raw-attribute policy oracle.

## 8. Trusted Raw-Attribute Policy Oracle

The trusted raw-attribute policy oracle baseline
(`seba.baselines.TrustedRawPolicyOracle`, used in
`scripts/run_nspi_sensitivity.py` and
`scripts/run_nspi_targeted_sensitivity.py`) assumes a separate,
uncompromised view of the original request attributes. It re-evaluates
policy on each event against that view and flags any mismatch with the
recorded decision. In the full grid it reaches AAS 1.0000
(`results/tables/full_grid_aas_by_defense.csv`).

`[INTERPRETATION]` This is reported as a strong baseline rather than as a
free operational property, as recorded in
`papers/final_paper/threat_model/threat_model_draft_v1.md` Section 2 and
`results/FINDINGS.md` Section 8. The oracle's strength depends on an
independent-view assumption that may not hold in every deployment, so
NS-PI's log-only signal remains relevant where the assumption fails.

## 9. Sensitivity Experiments

Two sensitivity studies vary the compromised-signer attack so that the
NS-PI boundary can be located in the synthetic workload:

- Global flip-fraction sweep, implemented in
  `scripts/run_nspi_sensitivity.py` over
  `FLIP_FRACTIONS = (0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.35, 0.50)`.
  Outputs are `results/tables/nspi_compromised_signer_sensitivity_raw.csv`
  and `results/tables/nspi_compromised_signer_sensitivity_summary.csv`.
- Targeted station/district sweep, implemented in
  `scripts/run_nspi_targeted_sensitivity.py` over
  `FLIP_FRACTIONS = (0.10, 0.25, 0.50, 0.75, 1.00)` and
  `SCOPES = ("station", "district")`. Outputs are
  `results/tables/nspi_targeted_compromised_signer_raw.csv` and
  `results/tables/nspi_targeted_compromised_signer_summary.csv`.

`[INTERPRETATION]` The sweeps are designed to locate the regime where the
NS-PI alarm becomes reliable in this benchmark and to make the limitations
visible alongside the headline detection, consistent with
`results/FINDINGS.md` Sections 4 and 5.

## 10. Workload and Policy-Mix Stress

`scripts/run_workload_policy_stress.py` runs a 40-cell matrix combining
workload size and policy mix. The size arm uses N in {500, 1000, 2500,
5000} at the baseline policy mix; the policy-mix arm uses N=1000 at four
overrides (`high_cross_jurisdiction`, `high_revoked_credential`,
`high_approval_missing`, `high_classified_proxy`), with weight vectors
defined in the `MIX_ARMS` dictionary inside the same script. Each cell is
run over five seeds {7, 21, 42, 99, 123}, and metrics are written to
`results/tables/workload_policy_stress_raw.csv` and aggregated in
`results/tables/workload_policy_stress_summary.csv`.

Per cell, the script records realized policy-mix ratios, signed-chain
detection (expected zero for the compromised-signer attack by
construction), NS-PI global and per-station drift detection at 25% and 10%
flip, trusted-oracle detection, counterfactual coverage and validity, the
NS-PI rule-list training accuracy, and a wall-clock runtime.

`[INTERPRETATION]` The classified-record ratio knob is explicitly labelled
as an indirect proxy via sensitive-scenario weights inside
`scripts/run_workload_policy_stress.py`; the realized classified ratio is
recorded so the reader can audit the effect. The stress matrix tests
robustness of the headline compromised-signer asymmetry across size and
mix, while exposing the size-dependent behavior of the low-rate (10%)
detector as reported in `results/FINDINGS.md` Section 6b.

## 11. XAI and Audit Reviewability Evaluation

`scripts/run_explanation_audit_quality.py` consumes the labelled requests,
the signed log, the permissioned block index, and the block JSONL emitted
by the prototype audit layer, and computes the metrics that appear in
`results/tables/explanation_audit_quality.csv` and
`results/tables/explanation_audit_quality_summary.csv`:

- trace completeness — fraction of requests with all required structured
  trace fields (decision, reason, rules, decisive attributes, policy
  version, decision hash, explanation hash, audit anchor hash);
- decisive-attribute text coverage — fraction of decisive attributes that
  appear in the rendered natural-language explanation, reported as both a
  per-request mean and a full-coverage indicator;
- counterfactual coverage — fraction of deny/escalate rows that receive a
  counterfactual explanation, computed in conjunction with
  `seba.nspi.counterfactual.explain_request`;
- counterfactual validity — fraction of generated counterfactuals that
  replay to the proposed `allow` decision under the learned NS-PI policy;
- duplicate-context stability — fraction of duplicate policy-context rows
  that retain a stable decision and reason;
- audit reconstruction — fraction of events that can be reconstructed by
  joining the request record, the signed event, the block-event index, and
  the block commitments.

`[INTERPRETATION]` The decision/reason rendering and reconstruction
metrics describe the structured trace, while the decisive-attribute text
coverage describes how completely those decisive attributes appear in the
generated explanation text; the latter is the explicit weakness reported
in `results/FINDINGS.md` Section 6 (mean 0.781, std 0.020833).

## 12. Seed-Level Confidence Aggregation

`scripts/run_seed_confidence_summary.py` consolidates the across-seed
mean, sample standard deviation (ddof=1, only when n_seeds is at least 2),
min, and max for the metrics already produced by the other scripts. The
inputs are the seed-level raw tables `results/tables/full_grid_raw.csv`,
`results/tables/adaptive_attack_summary.csv`,
`results/tables/explanation_audit_quality.csv`,
`results/tables/nspi_compromised_signer_sensitivity_raw.csv`,
`results/tables/nspi_targeted_compromised_signer_raw.csv`, and
`results/tables/workload_policy_stress_raw.csv`. The outputs are
`results/tables/seed_confidence_summary.csv` (one row per metric/group) and
`results/tables/seed_confidence_raw.csv` (per-seed values used in the
summary).

`[INTERPRETATION]` This aggregator runs no new experiments; it produces a
descriptive across-seed stability table over existing per-seed artifacts,
as also stated in `results/FINDINGS.md` Section 6c. A `std_defined` flag is
recorded so single-seed metrics are not presented as if they had measured
variance.

## 13. Reproducibility

The five-seed set `{7, 21, 42, 99, 123}` is used by the full grid
(`scripts/run_full_grid.py`), the ablations and adaptive attacks
(`scripts/run_ablations.py`), the global and targeted NS-PI sensitivity
sweeps (`scripts/run_nspi_sensitivity.py` and
`scripts/run_nspi_targeted_sensitivity.py`), the explanation/audit
quality evaluation (`scripts/run_explanation_audit_quality.py`), and the
workload and policy-mix stress matrix
(`scripts/run_workload_policy_stress.py`). The seed-level confidence aggregator
(`scripts/run_seed_confidence_summary.py`) operates over whatever seed
columns are present in those raw tables.

Reproduction entry points are the `Makefile` targets (`make lint`,
`make test`, `make reproduce`) and the step-by-step instructions in
`REPRODUCE.md`, both verified in `results/FINDINGS.md` Section 10.

`[INTERPRETATION]` The seeds and scripts above define the boundary of what
the results in `papers/final_paper/results/results_draft_v1.md` can claim:
descriptive across-seed stability on synthetic workloads, not a formal
statistical interval and not a statement about any deployed system.
