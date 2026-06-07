# Limitations and Future Work (Draft v1)

Status: draft text for the SEBA-XAI paper. Not final camera-ready prose.
Evidence basis: `results/FINDINGS.md`, `CONTRIBUTION.md`,
`papers/final_paper/threat_model/threat_model_draft_v1.md`,
`papers/final_paper/results/results_draft_v1.md`,
`papers/final_paper/methodology/methodology_draft_v1.md`, and the cited
tables under `results/tables/`.

This section records the boundaries of the current evidence. It should be kept
in the final paper even if the wording is compressed, because these limits are
part of the honest contribution.

## 1. Synthetic Evaluation Scope

SEBA-XAI is evaluated on synthetic inter-agency access requests, not on actual
police or criminal-justice records. The workload generator is
`prototype/synthetic_access_sim/generate_synthetic_requests.py`, and the
methodology draft states that no actual records, operational signing
infrastructure, or live CCTNS/ICJS interfaces are used
(`papers/final_paper/methodology/methodology_draft_v1.md` Section 1).

This means the current paper can claim controlled reproducibility, clear
threat-model coverage, and measured behavior on the benchmark. It cannot claim
field performance, institutional acceptance, or readiness for use inside any
existing government system.

## 2. Declared Policy Oracle

The declared policy oracle in
`prototype/synthetic_access_sim/policy_oracle.py` is the benchmark labeling
function. It produces `allow`, `deny`, and `escalate` labels and explanation
artifacts for synthetic requests, as described in
`papers/final_paper/methodology/methodology_draft_v1.md` Section 3.

This oracle is useful because it gives the benchmark a deterministic reference
decision. It is not evidence that the policy exactly matches Indian police
procedure, court procedure, or department-specific access manuals. A later
paper or deployment study would need domain expert review, formal policy
mapping, and jurisdiction-specific validation.

## 3. Compromised-Signer Threat Model

The main publishable asymmetry depends on the `compromised_signer` attacker.
That attacker flips a fraction of `deny` or `escalate` decisions to `allow`
and re-signs a valid-looking log. The threat model is defined in
`papers/final_paper/threat_model/threat_model_draft_v1.md` Section 4 and
implemented in `src/seba/attacks/compromised_signer.py`.

The benchmark shows a mechanical detection asymmetry for this attacker. From
`results/tables/seed_confidence_summary.csv`, ledger/audit baselines have
detection mean 0.0/std 0.0 on `compromised_signer`, while `nspi_drift` and
`trusted_policy_oracle` have mean 1.0/std 0.0 across the five full-grid seeds
(`papers/final_paper/results/results_draft_v1.md` Section 4). This does not
measure how common signer compromise is in practice. The paper must argue why
the attacker is worth studying, not treat its operational frequency as known.

## 4. Detector Visibility and Trust Assumptions

The trusted raw-attribute policy oracle is the strongest detector in the current
benchmark. It reaches AAS mean 1.0000/std 0.0000 in
`results/tables/full_grid_aas_by_defense.csv`, as reported in
`papers/final_paper/results/results_draft_v1.md` Section 2. Its strength comes
from a separate, uncompromised view of the original request attributes
(`papers/final_paper/threat_model/threat_model_draft_v1.md` Section 2).

NS-PI should therefore be framed narrowly. It is a complementary log-only
policy-drift detector, not the strongest verifier. It is useful under weaker
auditor visibility, where only the signed decision log is available, but it is
not a substitute for independent row-level policy re-evaluation when that
independent view exists.

## 5. NS-PI Sensitivity Limits

NS-PI is a distribution-level detector, so it is weak for very small or highly
localized corruptions. From
`results/tables/nspi_compromised_signer_sensitivity_summary.csv`, NS-PI global
and per-station detection are both 0.0 at 2% and 5% global flip fractions, while
the trusted oracle remains 1.0 (`papers/final_paper/results/results_draft_v1.md`
Section 5).

Targeted corruption is also difficult. From
`results/tables/nspi_targeted_compromised_signer_summary.csv`, grouped station
and district detection are 0.0 at 10% targeted corruption, while the trusted
oracle remains 1.0 (`papers/final_paper/results/results_draft_v1.md`
Section 6). In the current synthetic workload, grouped station drift becomes
reliable at 50% of targeted station eligible rows, and grouped district drift
becomes reliable at 25% of targeted district eligible rows
(`results/FINDINGS.md` Section 5). These are benchmark observations, not
portable operating thresholds.

## 6. Workload-Size Dependence

The workload/policy-mix stress test shows that the 25% compromised-signer
result is stable across size and policy mix, but the 10% setting is not stable
for smaller workloads. From `results/tables/seed_confidence_summary.csv` and
`results/tables/workload_policy_stress_summary.csv`, at a 10% flip, global
NS-PI detection is 0.0 at N=500 and 1.0 from N=1000 onward, while per-station
detection is 0.333333 at N=500 and N=1000 and reaches 1.0 at N=2500 and N=5000
(`papers/final_paper/results/results_draft_v1.md` Section 8).

The stress matrix also has a generator limitation: the cross-jurisdiction
baseline is already about 77%, so the high-cross-jurisdiction policy-mix arm
has limited room to move (`results/FINDINGS.md` Section 6b).

## 7. XAI Quality Limits

The structured explanation trace is complete in the current benchmark, but the
rendered explanation text is not perfect. From
`results/tables/explanation_audit_quality_summary.csv`, trace completeness,
counterfactual coverage, stable decision/reason row rate, and audit
reconstruction each have mean 1.000000/std 0.000000, while decisive-attribute
full text coverage has mean 0.781000/std 0.020833
(`papers/final_paper/results/results_draft_v1.md` Section 7).

This means some decisive attributes are present in the structured trace but are
not fully surfaced in the natural-language explanation text. Counterfactual
validity is also measured against the learned NS-PI policy, not against human
review, court review, or a statutory interpretation standard.

## 8. Blockchain and Privacy Limits

The blockchain component is a file-backed permissioned-chain simulation
implemented in `prototype/synthetic_access_sim/blockchain_audit.py`, not a live
Fabric network. The Methodology draft states that all audit timing values are
local script runtimes, not infrastructure measurements
(`papers/final_paper/methodology/methodology_draft_v1.md` Section 4).

The prototype also does not establish formal privacy properties. The
off-chain/on-chain split and metadata minimization are architectural controls
(`06_proposed_architecture.md`, `prototype/synthetic_access_sim/offchain_storage.py`),
but formal metadata leakage analysis, key-management analysis, and privacy
adversary modeling remain future work.

## 9. Seed and Statistical Limits

The full-grid, sensitivity, XAI-quality, and workload/policy-mix stress
experiments use five seeds `{7, 21, 42, 99, 123}`. The seed-confidence summary
contains 139 metric/group rows and 695 per-seed values
(`results/tables/seed_confidence_summary.csv`,
`results/tables/seed_confidence_raw.csv`), but it is descriptive across-seed
evidence. It is not a formal confidence interval and does not establish
behavior beyond the evaluated synthetic workloads.

## 10. Future Work

The immediate next technical work is:

1. improve the natural-language explanation renderer so decisive attributes in
   the structured trace are consistently surfaced in text;
2. add a clearer metadata-leakage experiment for the off-chain/on-chain split;
3. evaluate a real permissioned blockchain test network separately from the
   current file-backed simulation;
4. validate the policy schema with legal and policing domain experts before any
   claim beyond synthetic benchmark behavior;
5. study additional insider and key-compromise attacker variants.

The final paper should keep the contribution conservative: SEBA-XAI combines
integrity audit, contextual policy re-evaluation, and interpretable log-only
drift monitoring, with each component useful under different visibility and
trust assumptions.
