# Publication Readiness Agent Plan

Date: 2026-06-05  
Agent: Zeno  
Purpose: Structure the exact next steps required to turn SEBA-XAI into a real publication.

## 1. What Is Already Complete

- Synthetic SEBA-XAI prototype exists under `src/seba/`, `prototype/synthetic_access_sim/`, and `scripts/`.
- Baselines exist: mutable log, signed hash chain, CT-style log, blockchain-style audit, Fabric/ABAC-style re-execution, trusted raw-attribute policy oracle, and NS-PI.
- Multi-seed results exist for seeds `{7, 21, 42, 99, 123}` in `results/tables/`.
- Current honest findings are documented in `results/FINDINGS.md`.
- Paper draft v1 exists at `papers/final_paper/paper_draft_v1.md`.
- Venue analysis and two-month schedule exist.
- Figures exist under `papers/final_paper/figures_tables/`.
- Reproduction workflow exists via `make reproduce`.
- The strongest supported claim is narrow: NS-PI is a complementary log-only policy-drift signal for synthetic validly re-signed compromised-signer attacks, not a replacement for ABAC, blockchain audit, or a trusted policy oracle.

## 2. What Is Not Publication-Ready

- The paper is not yet submission-ready prose; it is a combined draft.
- At the time of this agent audit, the repo had an inconsistency: `experiments/experiment_plan.md` described the work as pre-experiment planning, while later results clearly existed. This was scheduled for correction before further experiments.
- No evidence of real CCTNS/ICJS deployment exists. The paper must say synthetic benchmark only.
- No real Hyperledger Fabric network experiment exists; current blockchain layer is a local permissioned-audit simulation.
- Policy oracle is not validated by police/legal/domain experts.
- Metadata privacy is measured only as prototype leakage scoring, not formal privacy.
- NS-PI has clear missed cases: 2%, 5% global corruption and small targeted station/district corruption.
- Natural-language explanation text coverage is weak: decisive-attribute full text coverage is about `0.781` mean in current findings.
- References are mostly verified, but final IEEE formatting, access dates, and target-venue style are still unfinished.

## 3. Exact Technical Experiments Still Needed

### 3.1 Reproducibility Freeze

Run:

```bash
make test
make lint
make typecheck
make reproduce
make figures
```

Acceptance: regenerated tables match existing non-runtime metrics; any drift is documented.

### 3.2 Artifact-To-Claim Audit

Build a claim table mapping every Results, Abstract, and Contribution claim to exact CSV rows or figure sources.

Acceptance: no paper claim exists without an artifact path and metric name.

### 3.3 Experiment-Plan Reconciliation

Update the stale experiment plan to reflect completed runs, current baselines, attacks, seeds, and limitations.

Acceptance: no repo document says experiments are absent unless historically scoped.

### 3.4 Policy-Generator Stress Extension

Add or rerun stress arms for lower cross-jurisdiction baseline, higher/lower classified ratio, high revocation, and high approval-missing workloads.

Acceptance: realized workload distributions are saved and reported, not just intended knobs.

### 3.5 Low-Rate Attack Boundary

Extend compromised-signer sensitivity around 1%, 2%, 5%, 7.5%, 10%, and 12.5%.

Acceptance: paper can state detection boundary as observed synthetic behavior, not a universal threshold.

### 3.6 Grouped Drift Ablation

Compare global-only, station-only, district-only, and combined NS-PI across targeted attacks.

Acceptance: Results section clearly shows when grouped drift helps and when it fails.

### 3.7 Explanation Renderer Improvement Or Honest Retention

Either improve decisive-attribute text coverage and rerun `scripts/run_explanation_audit_quality.py`, or keep the weakness prominently.

Acceptance: final paper reports the actual measured coverage.

### 3.8 Optional High-Value Fabric Validation

If time allows, run a small Hyperledger Fabric test-network benchmark separate from the local simulation.

Acceptance: only claim “Fabric validation” if real Fabric artifacts/logs exist.

## 4. Exact Paper-Writing Sections Still Needed

- Final Abstract with synthetic-only wording.
- Final Research Questions table mapping RQ to method, metric, and artifact.
- Final Threat Model table separating ledger-only visibility, NS-PI log-only visibility, and trusted oracle visibility.
- Final Experiment Setup section with seeds, workloads, baselines, attacks, ablations, scripts, and artifacts.
- Final Results section rewritten around evidence, not architecture.
- Final Discussion section explaining why blockchain alone is insufficient.
- Final Limitations section retaining synthetic workload, no deployment, no legal compliance proof, no raw records on-chain.
- Final Reproducibility Appendix.
- Final Ethics/Security/Legal Boundary section.
- Final related-work comparison table if venue length permits.

## 5. Review Risks

- Reviewer may reject synthetic-only police workflow as insufficiently realistic.
- Reviewer may say blockchain contribution is too shallow without real Fabric.
- Reviewer may say NS-PI is weak because the trusted oracle beats it.
- Reviewer may object that “police data” framing is sensitive without domain validation.
- Reviewer may see “AI + blockchain + police” as over-broad unless the paper stays tightly on access governance.
- Reviewer may challenge compromised-signer realism.
- Reviewer may object to weak natural-language explanation coverage.
- Reviewer may penalize stale or inconsistent repo documentation.

## 6. Fourteen-Day Immediate Action Plan

### June 5-6, 2026

Freeze title, claim, research questions, and forbidden claims.

Deliverable: one-page claim-control memo.

### June 7-8, 2026

Run full reproduction and tests.

Deliverable: frozen result tables, plots, and verification note.

### June 9-10, 2026

Complete artifact-to-claim audit.

Deliverable: claim/source table for every result.

### June 11-12, 2026

Fix repo documentation inconsistency and update experiment plan.

Deliverable: current experiment matrix and limitations note.

### June 13-15, 2026

Run low-rate and grouped-drift sensitivity extensions if feasible.

Deliverable: updated sensitivity tables or documented reason for deferral.

### June 16-17, 2026

Rewrite Results, Threat Model, and Limitations.

Deliverable: paper draft v2 sections.

### June 18, 2026

Prepare supervisor-ready package.

Deliverable: draft v2, figures, result tables, reproducibility note, and review-risk memo.

## 7. Final Submission Checklist

- No real police deployment claim.
- No crime prediction framing.
- No raw records on blockchain.
- No SOTA or breakthrough claim.
- Every number appears in `results/`, `prototype/runs/`, or `experiments/runs/`.
- Every baseline and ablation is named and defined.
- Synthetic workload is labeled synthetic everywhere.
- Trusted oracle is described as stronger but requiring stronger visibility.
- NS-PI is described as complementary log-only drift detection.
- Limitations include missed low-rate and targeted attacks.
- References are verified and venue-formatted.
- `make test`, `make lint`, `make typecheck`, `make reproduce`, and figure generation are rerun before submission.

## 8. Immediate Decision

The next local action should be:

> Create a claim-control memo and update stale experiment documentation before running another experiment.

This prevents the paper from drifting into unsupported claims while the technical pipeline is being finalized.
