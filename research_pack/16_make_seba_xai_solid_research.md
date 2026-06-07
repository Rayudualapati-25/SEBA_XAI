# 16 How To Make SEBA-XAI A Solid Research Project

Generated: 2026-05-29  
Updated: 2026-05-29 after XAI/audit quality experiment  
Status: supervisor-style research hardening note

## Short Answer

SEBA-XAI becomes solid research only if it is treated as a **measurable access-governance security system**, not as a broad idea about AI, blockchain, and police data.

The safe research identity is:

> SEBA-XAI is a CCTNS/ICJS-compatible research prototype for sensitive police-record access governance. It compares RBAC, ABAC/PBAC, signed logs, permissioned blockchain-style audit commitments, off-chain encrypted pointers, and explainable decision traces under reproducible synthetic inter-agency access workloads and adversarial audit attacks.

The project is already stronger than a normal M.Tech idea because it has:

- India-specific problem framing;
- literature and dataset study;
- a prototype access-request simulator;
- baselines;
- blockchain-style audit;
- off-chain record pointer verification;
- XAI/rule-trace explanations;
- multi-seed results;
- an adversarial audit benchmark direction;
- downloaded research papers and source indices.

The part that is **not yet fully solid** is the final external validity claim. The repository evidence now shows five things at the same time: cryptographic audit defenses are better for ordinary logged-field tampering, NS-PI detects the synthetic `compromised_signer` attack that ledger-only integrity checks miss, a trusted raw-attribute policy oracle also catches that attack if it has an uncompromised view of the original request data, grouped station/district NS-PI is needed for localized corruption because global drift can miss it, and the XAI/audit layer has measurable reviewability evidence. Therefore, the next step is not to make a broad "NS-PI beats blockchain" claim. The next step is to stress-test the result under workload-size and policy-mix changes.

## 1. The Hard Truth

The idea is not solid just because it combines blockchain, security, and XAI. Reviewers will reject that as an integration exercise if the paper only says:

- police data is sensitive;
- blockchain gives trust;
- XAI gives transparency;
- access control gives privacy.

Those statements are too generic.

The idea becomes research when the paper answers a testable question:

> What failure modes appear in inter-agency sensitive-record access governance, and which combination of policy enforcement, audit commitments, and explanation traces detects or reduces those failures?

That is the research problem. Everything else must support it.

## 2. Final Research Position

Use this final positioning:

> SEBA-XAI studies explainable and auditable access decisions for sensitive police/criminal-justice records. It does not predict criminals, replace CCTNS, store raw police records on-chain, or claim real deployment.

This positioning is strong because:

- CCTNS/ICJS gives the Indian infrastructure context.
- ABAC/PBAC gives the policy decision layer.
- Blockchain-style audit gives tamper-evident inter-agency logging.
- XAI gives explanation and reviewability of allow/deny/escalate decisions.
- Synthetic workloads make the work reproducible without real police data.
- Adversarial attacks make the evaluation more serious than a normal demo.

## 3. What We Can Claim Now

These claims are supported by current repository artifacts.

| Claim | Evidence | Safe wording |
|---|---|---|
| India already has digital policing/criminal-justice infrastructure | `00_problem_understanding.md`, `05_research_gap.md`, official CCTNS/ICJS sources | "The work is designed as an overlay, not a replacement." |
| Public India crime data is mostly aggregate | `03_datasets.md`, `04_dataset_matrix.csv` | "NCRB data is background context, not individual prediction data." |
| Related work exists in blockchain evidence, ABAC, XAI, and crime prediction | `01_literature_review.md`, `02_literature_matrix.csv`, downloaded papers folder | "The components exist separately; the integrated access-governance benchmark is the gap." |
| A first prototype exists | `prototype/synthetic_access_sim/` | "The prototype simulates access requests and policy decisions." |
| Baselines and results exist | `results/tables/`, `results/FINDINGS.md` | "The repository contains reproducible baseline and attack results." |
| NS-PI detects compromised-signer policy drift in the synthetic benchmark | `results/FINDINGS.md`, `results/tables/full_grid_per_attack.csv`, `results/tables/adaptive_attack_summary.csv` | "NS-PI is a complementary log-only drift detector, not a replacement for cryptographic audit or trusted raw-attribute policy re-evaluation." |
| Grouped NS-PI helps for localized compromised-signer drift | `results/tables/nspi_targeted_compromised_signer_summary.csv` | "Global drift can miss localized attacks; station/district grouped drift is required for local corruption analysis." |
| XAI/audit reviewability has been measured | `results/tables/explanation_audit_quality.csv`, `results/tables/explanation_audit_quality_summary.csv` | "The prototype produces complete structured traces and reconstructable audit commitments, while natural-language explanation coverage still needs improvement." |

## 4. What We Cannot Claim Yet

Do not claim:

- real police deployment;
- legal compliance;
- production-grade security;
- better crime prediction;
- individual suspect prediction;
- formal privacy guarantee;
- SOTA;
- that XAI creates trust by itself;
- that blockchain solves privacy.

The correct style is:

> "We evaluate a research prototype under synthetic but reproducible access-control workloads."

Not:

> "We built a secure police blockchain system for India."

## 5. The Core Novelty Must Be One Of Two Things

There are two honest publication paths.

### Path A: Narrow Method Paper

This path is now partially supported by the current evidence, but it must be written narrowly.

Working title:

> NS-PI: Neuro-Symbolic Policy Induction for Detecting Compromised Audit Signers in Explainable Police Access-Governance Logs

Core contribution:

> A learned interpretable policy model detects policy-distribution drift when an attacker controls the audit signer and re-signs a tampered log, making ordinary hash-chain verification pass.

This is stronger than a pure benchmark paper, but it is only defensible for the compromised-signer threat model currently implemented.

Required evidence:

- compromised-signer attack implemented: done;
- cryptographic detectors fail because the re-signed chain is valid: done for current baselines;
- NS-PI detects the policy shift: done across seeds 7, 21, 42, 99, and 123;
- multi-seed result is stable: done for the current synthetic workload;
- ablation shows which NS-PI component matters: partly done; needs workload stress testing.
- stronger external policy-oracle comparison: done; it catches `compromised_signer` and must be reported as the strongest baseline.
- targeted station/district sensitivity: done; grouped drift detects localized attacks better than global drift, but misses very low target-group corruption.
- explanation/audit quality evidence: done; trace completeness, counterfactual validity, duplicate-context stability, and audit reconstruction are measured.

### Path B: Benchmark Paper

Use this if Path A fails or gives weak results.

Working title:

> ADV-AUDIT: A Reproducible Adversarial Benchmark for Explainable Blockchain-Audited Police Access Governance

Core contribution:

> A benchmark, simulator, attack catalog, and evaluation protocol for comparing access-governance defenses under police-style sensitive-record sharing.

This is safer and still publishable if written honestly.

Required evidence:

- clear workload generator;
- attack catalog;
- defense catalog;
- AAS metric;
- multi-seed tables;
- failure-mode analysis;
- clear limits.

## 6. Completed Decisive Experiment

The decisive experiment has now been implemented:

> `src/seba/attacks/compromised_signer.py`

### Why This Matters

Earlier attacks modified logged fields. Hash-chain and blockchain-style defenses detected those easily because hashes broke. That did not prove NS-PI was useful.

The stronger question is:

> What if the attacker has the genuine signing key or validator authority and re-signs the corrupted log?

The implemented attack models the case where:

- row hashes can verify;
- chain signatures can verify;
- normal blockchain-style audit may pass;
- but the access-decision distribution may shift;
- NS-PI may detect that the observed policy behavior no longer matches the learned/declared policy.

This is now the clean research gap for NS-PI.

### Completed Implementation Tasks

1. Added `src/seba/attacks/compromised_signer.py`.
2. The attack flips a meaningful group of deny/escalate decisions into allow decisions.
3. The affected rows are marked as validly re-signed and policy-output compromised.
4. Signed-chain, CT-log, Fabric+ABAC, audit-only ABAC, and blockchain-style detectors are intentionally blind under this attack model.
5. NS-PI global and grouped drift detection runs on the same perturbed logs.
6. Tests verify the attack does not mutate input logs and blinds integrity detectors.
7. Results are recorded in `results/tables/`.
8. `results/FINDINGS.md` now reports the narrower honest claim.

### Result Against Success Criteria

Path A is defensible only in a narrowed form:

| Requirement | Needed result |
|---|---|
| Re-signed chain passes ledger-only checks | satisfied: ledger-only integrity/audit baselines detect 0/5 seeds |
| NS-PI detects policy drift | satisfied: NS-PI detects 5/5 seeds |
| Trusted raw oracle detects corruption | satisfied: trusted policy oracle detects 5/5 seeds |
| Result is not one-seed luck | satisfied for seeds 7, 21, 42, 99, 123 |
| Targeted station/district sensitivity tested | satisfied; grouped drift helps, global drift is weak for localized attacks |
| Explanation remains interpretable | partly satisfied; structured traces and counterfactual replay are measured, but natural-language coverage is imperfect |
| Ablation supports the mechanism | partly satisfied; needs larger workload and independent policy-oracle comparison |

So the paper can pursue Path A only as a complementary log-only policy-drift method, not as a general replacement for blockchain audit, ABAC, or an independent trusted policy oracle.

## 7. Required Experimental Matrix

The final paper should contain this matrix.

| Category | Required items |
|---|---|
| Workload | synthetic police stations, officers, cases, jurisdictions, record sensitivity, approval tokens, purpose, credential status |
| Baselines | RBAC, ABAC/PBAC, mutable log, signed hash-chain, CT-log, Fabric+ABAC-style baseline |
| Proposed method | SEBA-XAI with policy trace, explanation hash, off-chain pointer, blockchain-style audit, NS-PI if proven |
| Attacks | replay token, backdating, revocation race, explanation swap, metadata inference, collusion, compromised signer |
| Metrics | false allow, false deny, AAS, audit reconstruction, tamper detection, metadata leakage, latency, storage, explanation completeness, explanation stability |
| Ablations | no XAI hash, no off-chain pointer, no PBAC, no blockchain-style audit, no drift detector, no grouped drift |
| Seeds | at least 7, 21, 42, 99, 123 |

## 8. How To Make The Writing Solid

The paper should not start by praising blockchain or AI. It should start with the access-governance problem.

Recommended introduction flow:

1. India has CCTNS/ICJS-style digital policing infrastructure.
2. Sensitive records need inter-agency access, but access is contextual.
3. RBAC alone is too coarse for purpose, jurisdiction, approval, sensitivity, and time-window rules.
4. Audit logs must be tamper-evident across agencies.
5. Raw sensitive records and full explanations should not be placed on-chain.
6. XAI is needed to review allow/deny/escalate decisions.
7. Existing literature treats blockchain evidence, ABAC, XAI, and crime prediction separately.
8. SEBA-XAI evaluates the combined access-governance problem under reproducible attacks.

## 9. The Exact Research Questions

Use these if the paper stays close to the current prototype.

**RQ1. Access-control correctness:**  
How do RBAC and ABAC/PBAC differ in false allows and false denies under synthetic inter-agency police access requests?

**RQ2. Audit robustness:**  
How do mutable logs, signed hash-chains, CT-log baselines, Fabric+ABAC-style baselines, and blockchain-style audit commitments behave under adversarial audit attacks?

**RQ3. Compromised signer detection:**  
Can NS-PI detect policy-distribution drift when an attacker corrupts access decisions and re-signs the audit log with apparently valid authority?

**RQ4. Explainability:**  
Can rule traces, counterfactual explanations, and explanation hashes make access decisions reviewable without exposing full sensitive explanations on-chain?

**RQ5. Cost and leakage:**  
What latency, storage, and metadata-exposure overhead is introduced by audit commitments, explanation hashes, and minimized logging?

## 10. What The Final Contribution Should Look Like

Use one of these two contribution sets after the decisive experiment.

### Current Evidence-Supported Version

Contribution wording:

1. We formulate CCTNS/ICJS-compatible sensitive-record access governance as an auditable, explainable policy-decision problem.
2. We propose SEBA-XAI, an overlay combining ABAC/PBAC policy enforcement, off-chain encrypted pointers, explanation artifacts, and permissioned blockchain-style audit commitments.
3. We introduce NS-PI, a neuro-symbolic policy-induction method for detecting policy drift in audit logs, especially under validly re-signed compromised-signer attacks.
4. We evaluate the system with a reproducible synthetic multi-station workload, adversarial audit attacks, ledger-only baselines, a trusted raw-attribute policy-oracle baseline, XAI/audit-quality metrics, ablations, and multi-seed results, while reporting that NS-PI is complementary rather than globally superior.

### If NS-PI Does Not Work

Contribution wording:

1. We formulate CCTNS/ICJS-compatible sensitive-record access governance as an auditable, explainable policy-decision problem.
2. We build SEBA-XAI as a reproducible research prototype for comparing RBAC, ABAC/PBAC, signed logs, and blockchain-style audit commitments.
3. We introduce ADV-AUDIT, an adversarial benchmark for police-style access-governance audit logs.
4. We report failure modes showing where cryptographic integrity, policy re-execution, and drift-based XAI signals succeed or fail.

This second version is less flashy, but more honest if the evidence does not support the method claim.

## 11. Four-Week Hardening Plan

### Week 1: Decisive Experiment And Claim Correction

- Implement `compromised_signer`: done.
- Add tests: done.
- Re-run `make test`: done, currently `67 passed`.
- Re-run full-grid and ablation scripts: done.
- Update `results/FINDINGS.md`: done.
- Revise `CONTRIBUTION.md`: done.
- Add independent raw-attribute policy-oracle baseline: done.
- Add global workload sensitivity test: done.
- Add targeted station/district sensitivity test: done.
- Add explanation-quality and audit-reconstruction metrics: done.
- Next: add workload-size and policy-mix stress tests.

### Week 2: XAI And Audit Quality

- Add explanation completeness metric: done.
- Add decisive-attribute text coverage metric: done.
- Add counterfactual validity metric: done.
- Add explanation stability test: done.
- Add audit reconstruction script: done.
- Add one result table for explanation/audit quality: done.

### Week 3: Stress Testing

- Vary classified-record ratio.
- Vary cross-jurisdiction ratio.
- Vary revoked-credential ratio.
- Vary approval-token missing ratio.
- Report mean/std over seeds.

### Week 4: Paper Evidence Pack

- Freeze contribution sentence.
- Freeze results tables.
- Write limitations.
- Prepare figures.
- Write introduction and methodology from evidence only.
- Do not write results claims that are not in `results/`.

## 12. Professor Explanation In Simple English

Use this when explaining to a professor:

> I started with the broad idea of using blockchain, security, and XAI for police/crime data. I narrowed it into a safer research problem: explainable and auditable access governance for sensitive police records. I am not replacing CCTNS or predicting criminals. The prototype simulates inter-agency access requests, applies RBAC/ABAC/PBAC-style decisions, logs audit commitments, keeps raw records off-chain, and stores explanation hashes. I also added adversarial attacks and baselines. The important result is that normal integrity checks catch ordinary log tampering, NS-PI detects the compromised-signer case from the signed decision trace, and a trusted raw-attribute policy oracle catches it when a separate trusted request view is available. I also tested targeted station/district corruption and found that grouped drift is needed because global drift can miss localized attacks. For XAI, I measured trace completeness, counterfactual validity, explanation stability, and audit reconstruction; the structured trace is strong, but the natural-language explanation text still needs improvement.

## 13. Final Supervisor Advice

The strongest version of this research is not:

> "Blockchain + XAI for police data."

The strongest version is:

> "A reproducible adversarial evaluation of explainable, auditable access governance for sensitive police-record sharing."

That is specific, measurable, ethical, and defensible.

The next action is clear:

> Add workload-size and policy-mix stress tests. The compromised-signer, sensitivity, and XAI-quality results now define the core claim; the paper still needs evidence that the findings are not tied to one synthetic workload configuration.
