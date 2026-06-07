# SEBA-XAI Paper Skeleton v2

Status: aligned assembly scaffold, not final camera-ready paper.
Purpose: show how the existing evidence-bounded section drafts should be merged
into one IEEE-style paper without adding unsupported claims.

Recommended working title:

> SEBA-XAI: Explainable Policy-Aware Audit for Secure Inter-Agency Police Data Access Governance

## Evidence Rule for This Skeleton

Use the section drafts and source artifacts listed below. Do not write new
result claims unless they are backed by a table, script, iteration report, or
source note already in the repository.

Current section sources:

| Paper section | Source draft |
|---|---|
| Introduction | `papers/final_paper/introduction/introduction_final_professor.md` |
| Related Work | `papers/final_paper/related_work/related_work_draft_v1.md` |
| Methodology | `papers/final_paper/methodology/methodology_draft_v1.md` |
| Threat Model | `papers/final_paper/threat_model/threat_model_draft_v1.md` |
| Results | `papers/final_paper/results/results_draft_v1.md` |
| Limitations | `papers/final_paper/limitations/limitations_draft_v1.md` |
| Conclusion | `papers/final_paper/conclusion/conclusion_draft_v1.md` |
| Combined draft v1 | `papers/final_paper/paper_draft_v1.md` |
| Current aligned draft | `papers/final_paper/paper_draft_v2.md` |

## Abstract Placeholder

SEBA-XAI is a research prototype for explainable, blockchain-audited access
governance over sensitive police and criminal-justice records. The paper
studies a synthetic CCTNS/ICJS-style inter-agency access workflow in which
requests are evaluated by contextual policy rules, recorded through signed and
blockchain-style audit commitments, and reviewed through explanation artifacts.
The evaluation compares ledger-only integrity, ABAC-style re-execution, a
trusted raw-attribute policy oracle, and NS-PI, an interpretable policy-drift
detector. Results show that NS-PI is not the best overall tamper detector and
does not replace trusted policy re-evaluation. Its useful role is narrower: it
detects validly re-signed compromised-signer logs in the synthetic benchmark
where ledger-only baselines are blind by construction. The paper also reports
XAI/audit reviewability metrics, sensitivity boundaries, workload-size effects,
and limitations. All results are synthetic and should be presented as benchmark
evidence, not deployment evidence.

## I. Introduction

Use `papers/final_paper/introduction/introduction_final_professor.md`.

Required argument flow:

1. India already has CCTNS/ICJS-style digital policing and criminal-justice
   infrastructure.
2. The research problem is not replacement; it is auditable, explainable,
   contextual access governance over sensitive records.
3. Blockchain contributes tamper-evident audit commitments and provenance, but
   raw records must remain off-chain.
4. ABAC/PBAC contributes contextual authorization over subject, object, action,
   and environment attributes.
5. XAI contributes reviewable explanation artifacts for allow/deny/escalate
   decisions and audit reconstruction.
6. Existing work treats many of these pieces separately.
7. SEBA-XAI evaluates them together in a synthetic benchmark.
8. The paper makes no claim about actual records, operational integration, or
   crime prediction.

Contribution bullets should follow `CONTRIBUTION.md`:

- formulate the CCTNS/ICJS-compatible access-governance problem;
- propose the SEBA-XAI overlay;
- introduce an adversarial audit benchmark;
- evaluate NS-PI as a complementary log-only policy-drift detector;
- measure XAI and audit reviewability.

## II. Related Work

Use `papers/final_paper/related_work/related_work_draft_v1.md`.

Recommended compression:

- Indian digital policing baseline: CCTNS/ICJS exist and should be treated as
  the baseline, not the enemy.
- Blockchain/evidence/access audit: prior work supports evidence provenance and
  on-chain/off-chain patterns, but not this full access-governance benchmark.
- RBAC/ABAC/PBAC and privacy: standards and Fabric+ABAC patterns exist, but
  police-specific explanation/audit reconstruction under explicit threats is
  still narrow.
- XAI/fairness/high-stakes policing: XAI and feedback-loop literature justify
  caution and support the decision to avoid individual crime prediction.

## III. Methodology

Use `papers/final_paper/methodology/methodology_draft_v1.md`, now headed
"Methodology (Aligned Draft v2)".

Required subsections:

1. System overview and off-chain/on-chain boundary.
2. Synthetic workload generation.
3. Declared policy oracle and XAI artifacts.
4. Audit layers and baselines.
5. Attack catalog and compromised-signer attacker.
6. NS-PI learner and drift detector.
7. Trusted raw-attribute policy oracle.
8. Sensitivity experiments.
9. Workload/policy-mix stress.
10. XAI/audit reviewability metrics.
11. Seed-confidence aggregation and reproducibility.

Do not describe the blockchain layer as a live Fabric network. It is a
file-backed permissioned-chain simulation in the current prototype.

## IV. Threat Model

Use `papers/final_paper/threat_model/threat_model_draft_v1.md`.

Keep the central distinction:

- ledger and ABAC re-execution see the recorded canonical log;
- the trusted oracle sees an independent raw request view;
- NS-PI sees only the signed decision log.

This distinction is what makes the result interpretable. It prevents the paper
from incorrectly claiming that NS-PI is stronger than all other defenses.

## V. Results

Use `papers/final_paper/results/results_draft_v1.md`, now headed
"Results (Aligned Draft v2)".

Mandatory result points:

1. AAS ranking: trusted oracle is strongest; NS-PI is not the overall winner.
2. Ordinary tamper attacks: integrity and ABAC-style baselines work as expected.
3. Compromised-signer asymmetry: ledger/audit baselines mean 0.0/std 0.0,
   NS-PI and trusted oracle mean 1.0/std 0.0 across the five full-grid seeds.
4. Global sensitivity: NS-PI misses 2% and 5% corruption, detects 10% in the
   current global benchmark.
5. Targeted sensitivity: NS-PI misses 10% targeted station/district corruption;
   grouped drift is useful only when the target group corruption is larger.
6. XAI/audit reviewability: structured traces and reconstruction are complete;
   decisive-attribute text coverage remains imperfect.
7. Workload stress: 25% result holds across stress cells; 10% low-rate behavior
   is workload-size dependent.
8. Seed-confidence table is descriptive, not a formal interval.

## VI. Limitations

Use `papers/final_paper/limitations/limitations_draft_v1.md`.

Keep the limitations as a full section rather than burying them in Results:

- synthetic workload only;
- declared policy oracle is not validated against official operational policy;
- compromised-signer is a modeled attacker;
- trusted oracle has a strong independent-view assumption;
- NS-PI misses low-rate and very localized corruption;
- explanation text coverage is imperfect;
- blockchain layer is a file-backed simulation;
- privacy and metadata leakage are not formally established;
- low-rate stress detection remains workload-size dependent even with the
  five-seed stress matrix.

## VII. Conclusion

Use `papers/final_paper/conclusion/conclusion_draft_v1.md`.

The conclusion should repeat only the narrow claim:

SEBA-XAI evaluates integrity audit, contextual policy re-evaluation, and
interpretable log-only drift monitoring together. The prototype supports the
claim that these mechanisms catch different failure modes under different
visibility assumptions. It does not support broad claims about deployment,
crime prediction, or general superiority.

## Reference Cleanup Tasks

Before converting to final IEEE format:

1. Introduction references have a working numeric map in
   `papers/final_paper/references_ieee_map.md`; high-priority author and venue
   metadata has been checked in `papers/final_paper/references_verification_v1.md`.
2. Related Work URL and row references have been converted into the same
   numeric reference map in `papers/final_paper/references_ieee_map.md`.
3. Keep local artifact citations in Methodology/Results/Limitations until the
   final paper has reproducibility appendix references.
4. Make sure every numeric result maps to one of:
   - `results/tables/full_grid_aas_by_defense.csv`;
   - `results/tables/full_grid_per_attack.csv`;
   - `results/tables/seed_confidence_summary.csv`;
   - `results/tables/nspi_compromised_signer_sensitivity_summary.csv`;
   - `results/tables/nspi_targeted_compromised_signer_summary.csv`;
   - `results/tables/explanation_audit_quality_summary.csv`;
   - `results/tables/workload_policy_stress_summary.csv`.
5. Do not add new metrics during paper polishing. If a claim needs a new metric,
   create a new experiment first and record it under `reports/iteration/`.

## Immediate Open Items

- Review `paper_draft_v2.md` with the supervisor, then expand it with the
  accepted Related Work, Threat Model, Limitations, and Conclusion wording.
- Perform a final IEEE bibliography style pass for capitalization, venue
  abbreviations, access dates, and ordering.
- Keep the five-seed stress matrix wording aligned with
  `results/tables/workload_policy_stress_summary.csv`.
- Improve figures/tables for the Results section.
- Add a small architecture figure from `06_proposed_architecture.md` if needed.
