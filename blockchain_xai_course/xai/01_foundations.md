# XAI Module 1 — Foundations: What Is Explainability?

> **Goal**: Get the vocabulary right. Most XAI confusion comes from conflating *interpretability*, *explainability*, *transparency*, *justification*, and *fairness*. They are not synonyms.

---

## 1.1 Why XAI exists as a field

Three forcing functions:

1. **Regulation** — GDPR Article 22 (right to explanation), EU AI Act high-risk categories, US Algorithmic Accountability Act drafts, India's DPDP Act.
2. **Safety** — deployed ML systems fail in non-obvious ways (medical misdiagnosis, biased lending, hallucination in LLMs).
3. **Science** — understanding why a model works is itself a research goal (Distill.pub, mechanistic interpretability).

DARPA's XAI Program (2017–2021) crystallized the field. Two major surveys: Adadi & Berrada (2018), Guidotti et al. (2018).

---

## 1.2 Definitions you must be able to recite

| Term | Definition (working) |
|---|---|
| **Interpretability** | The degree to which a human can *understand the cause* of a decision. (Miller 2017) |
| **Explainability** | The degree to which a system can *produce explanations* — often via post-hoc methods. |
| **Transparency** | The model's mechanism is itself inspectable (linear models, small decision trees). |
| **Simulatability** | A human can mentally simulate the model's full computation. |
| **Decomposability** | Each part of the model has an intuitive meaning. |
| **Algorithmic transparency** | Understanding of how the learning algorithm produces a model. |
| **Justification** | Reasons that *defend* a decision, not necessarily its true cause. |
| **Causality** | The actual mechanism producing the output. (Pearl) |

**Critical**: an "explanation" is not the same as the *cause*. LIME tells you what would have changed the output locally; it doesn't tell you the model's internal mechanism.

---

## 1.3 Lipton's framework (Lipton, 2016, "The Mythos of Model Interpretability")

A foundational paper. Lipton split "interpretability" into:

### Properties of models (transparency)
- **Simulatability** — a person can mentally run the model.
- **Decomposability** — each parameter / node has a meaning.
- **Algorithmic transparency** — convergence is understood.

### Properties of explanations (post-hoc)
- Text explanations
- Visualizations
- Local explanations
- Explanation by example

This split is the canonical taxonomy. Use it.

---

## 1.4 Doshi-Velez & Kim (2017) — evaluation framework

| Level | What's evaluated | Cost |
|---|---|---|
| **Application-grounded** | Real users on real task | High |
| **Human-grounded** | Real users on simpler proxy task | Medium |
| **Functionally-grounded** | Formal definition of explanation quality | Low |

Most papers operate at the *functionally-grounded* level (e.g., faithfulness scores). Papers that do application-grounded evaluation are scarce and disproportionately influential.

---

## 1.5 Who needs an explanation, and why?

| Stakeholder | Need |
|---|---|
| **End user** | Understand a single decision affecting them |
| **Domain expert** (doctor, judge) | Validate model reasoning against domain knowledge |
| **Developer / data scientist** | Debug model, audit failures |
| **Regulator / auditor** | Establish accountability, check fairness |
| **Researcher** | Understand emergent behavior, science |

Different stakeholders need *different* explanations. A SHAP plot is useless to a patient. A saliency map is useless to a regulator.

This is the **alignment-to-purpose** problem.

---

## 1.6 The accuracy–interpretability tradeoff (myth?)

The folk claim: more complex models → better accuracy but worse interpretability.

**Cynthia Rudin's counter** (2019, *Nature MI*): *"Stop explaining black-box ML models for high-stakes decisions and use interpretable models instead."* On many tabular problems, well-tuned interpretable models (sparse logistic regression, EBMs, falling-rule lists) match black-box accuracy.

The tradeoff is empirically narrower than usually assumed, but **does exist for high-dimensional perceptual tasks** (vision, speech, language).

---

## 1.7 Interpretable model families (intrinsic)

| Model | Why interpretable |
|---|---|
| **Linear / logistic regression** | Coefficients are weights |
| **Generalized Additive Models (GAMs)** | Each feature → its own learned curve |
| **Explainable Boosting Machines (EBMs)** | GAM + pairwise interactions, often as accurate as XGBoost |
| **Decision trees** (small) | Path through tree = rule |
| **Decision rules / RIPPER / SLIM** | If-then rules |
| **Falling Rule Lists** | Ordered if-then with monotone risk |
| **Risk scores (e.g., 2HELPS2B for seizures)** | Integer-coefficient scoring |
| **Generalized linear rule models** | Convex combinations of rules |
| **Prototype networks** | Predictions justified by similar training examples |

A serious XAI engineer **tries an interpretable model first**, then escalates only if needed.

---

## 1.8 Post-hoc methods (preview)

For complex models where intrinsic interpretability is unavailable, post-hoc methods explain *after the fact*.

| Method | Output |
|---|---|
| Feature attribution (LIME, SHAP, IG, gradient×input) | Importance score per feature |
| Saliency maps | Pixel importance per image |
| Concept-based (TCAV) | Importance of human concept |
| Counterfactuals | "What would change the prediction?" |
| Example-based | Nearest training examples |
| Surrogate models | A simpler model fit to the black box |
| Mechanistic | Direct circuit analysis (mech interp) |

Detailed coverage in [Module 3](03_feature_attribution.md) onwards.

---

## 1.9 The "right to explanation"

GDPR's Article 22 grants the right to "meaningful information about the logic involved" in automated decisions. Legal scholars debate whether this is a *right to explanation* or merely a *right to be informed*.

EU AI Act (2024) adds explicit transparency obligations for high-risk AI systems. India's DPDP Act, Canada's AIDA, US state laws all moving similar directions.

This pushes XAI from research curiosity to **compliance requirement**.

---

## 1.10 Common pitfalls (memorize)

1. **Confusing correlation explanations with causal ones**. SHAP tells you what the model uses, not what's true in the world.
2. **Trusting explanations of an unfit model**. If accuracy is poor, no explanation is meaningful.
3. **Aggregating local explanations into "global" claims** — disagreement is common (Krishna et al. 2022, "The Disagreement Problem").
4. **Using explanations as fairness audits**. Feature importance ≠ fairness; you need fairness metrics directly.
5. **Optimizing explanation methods for human-likeable outputs** rather than faithfulness.

---

## 1.11 Reading list

- Lipton — *The Mythos of Model Interpretability*, ICML WHI 2016.
- Doshi-Velez & Kim — *Towards a Rigorous Science of Interpretable ML*, 2017.
- Miller — *Explanation in Artificial Intelligence: Insights from the Social Sciences*, AI Journal 2019.
- Rudin — *Stop Explaining Black Box ML Models*, Nature MI 2019.
- Adadi & Berrada — *Peeking Inside the Black-Box*, IEEE Access 2018.
- Guidotti et al. — *A Survey of Methods for Explaining Black Box Models*, CSUR 2018.
- Molnar — *Interpretable Machine Learning* (free online book), Ch 1–3.

## 1.12 Lab (1 hr)

1. Fit a logistic regression and an XGBoost on the same tabular dataset (UCI Adult is fine).
2. Tabulate accuracy + a 3-sentence "explanation" you would give to (a) a regulator, (b) an end user, (c) a developer for each model.
3. Note which audience you struggled to serve.

## 1.13 Quiz

1. Distinguish *interpretability* and *explainability* in your own words.
2. State Rudin's argument against post-hoc explanations for high-stakes decisions.
3. List the three Doshi-Velez/Kim evaluation levels in order of rigor.
4. Why is "right to explanation" legally contested?
5. Give one example each of: an intrinsically interpretable model, a post-hoc local method, a post-hoc global method.
