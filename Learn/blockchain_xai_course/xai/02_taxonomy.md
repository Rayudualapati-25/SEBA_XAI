# XAI Module 2 — Taxonomy of XAI Methods

> **Goal**: Build a mental map that lets you place any new XAI paper within 30 seconds.

---

## 2.1 The four-axis taxonomy

Every XAI method can be classified along four axes:

```
            Scope                Stage                Model dependency        Output form
              │                    │                         │                     │
   ┌──────────┴─────────┐  ┌───────┴───────┐  ┌──────────────┴──────┐   ┌──────────┴───────┐
   │                    │  │               │  │                     │   │                  │
 Local              Global  Intrinsic   Post-hoc  Model-specific  Model-agnostic    Visual / Textual /
                                                                                    Example-based / Rule
```

A typical paper introduces a method that is e.g. **local + post-hoc + model-agnostic + visual** (LIME for images).

---

## 2.2 Scope: Local vs Global

### Local explanations

Why did the model predict `ŷ` for *this* input `x`?

- **LIME** — locally fit a linear model around `x`.
- **SHAP (local)** — Shapley values for the single prediction.
- **Integrated Gradients** — attribution along path from baseline to `x`.
- **Counterfactuals** — minimum change to `x` that flips the prediction.

### Global explanations

How does the model behave *overall*?

- **PDP / ICE / ALE** — marginal effect of a feature.
- **Feature importance** (permutation, gain-based).
- **Surrogate models** — fit a decision tree to the black box's predictions.
- **Concept Activation Vectors (TCAV)** — sensitivity to human-defined concepts.
- **Mechanistic interpretability** — circuit-level reverse-engineering.

### Cohort explanations

Subsets between local and global — e.g., "Why does the model behave differently for women than men?" Tools: SliceFinder, Aequitas, FairLearn.

---

## 2.3 Stage: Intrinsic vs Post-hoc

| Type | Description | Example |
|---|---|---|
| **Intrinsic** | Model is interpretable by construction | Linear, GAM, EBM, small tree, prototype net |
| **Post-hoc** | Explain a trained black-box model | LIME, SHAP, Grad-CAM |

**Hybrid**: Self-explaining neural networks (Alvarez-Melis & Jaakkola, 2018), ProtoPNet, Concept Bottleneck Models — *trained* to produce explanations, sit between the two.

---

## 2.4 Model dependency

| Type | Works on |
|---|---|
| **Model-agnostic** | Any model (only needs predict()) — LIME, SHAP, PDP, permutation importance |
| **Model-specific** | Exploits internals — Grad-CAM (CNNs), Attention Rollout (Transformers), TreeSHAP (trees) |

Model-specific methods are usually **faster and more faithful** to the model's actual computation; model-agnostic ones are **more portable**.

---

## 2.5 Output form

| Form | When useful |
|---|---|
| Feature attribution (numeric per feature) | Tabular, NLP, CV |
| Saliency map (per pixel) | Vision |
| Attention heatmap | Transformer-based models |
| Concept score | High-level semantic reasoning |
| Counterfactual example | "What would change the prediction?" |
| Prototype / nearest example | Case-based reasoning |
| Natural-language rationale | LLMs, multimodal |
| Decision rule / tree | High-trust auditing |

---

## 2.6 The disagreement problem (Krishna et al., 2022)

When you run multiple explanation methods on the same model and prediction, they often disagree. Practical consequence: an analyst can pick the explanation that supports their narrative.

**Implication**: never rely on a single XAI method. Triangulate.

---

## 2.7 Evaluating an XAI method — three lenses

1. **Faithfulness** — does the explanation reflect what the model actually does?
   - Perturbation-based tests (delete top-k features → measure accuracy drop)
   - Sanity checks (Adebayo et al. 2018 — saliency maps that survive random-weight randomization are not faithful)
2. **Plausibility / human alignment** — does it make sense to humans?
   - User studies
   - Agreement with human-annotated rationales (ERASER benchmark)
3. **Robustness** — does the explanation change under small input perturbations?
   - Adversarial XAI papers (Slack et al. 2020, "Fooling LIME and SHAP")

Detailed in [Module 10](10_evaluation_metrics.md).

---

## 2.8 The XAI method tree (cheat sheet)

```
INTRINSIC
├─ Linear / Logistic / Ridge / Lasso
├─ GAM / EBM
├─ Decision trees (small)
├─ Decision rules (RIPPER, SLIM)
├─ Risk scores (integer-coef)
├─ Prototype networks (ProtoPNet, this-looks-like-that)
└─ Concept Bottleneck Models

POST-HOC
├─ Local
│  ├─ LIME
│  ├─ SHAP (KernelSHAP, TreeSHAP, DeepSHAP)
│  ├─ Anchors
│  ├─ Counterfactuals (Wachter, DiCE, FACE, MACE, GeCo)
│  ├─ Gradient methods
│  │  ├─ Vanilla saliency
│  │  ├─ Integrated Gradients
│  │  ├─ SmoothGrad
│  │  ├─ Guided Backprop
│  │  └─ Grad-CAM / Grad-CAM++
│  └─ Influence functions
└─ Global
   ├─ PDP / ICE / ALE
   ├─ Permutation importance
   ├─ Surrogate models (global tree, distillation)
   ├─ Concept-based (TCAV, ACE, CRAFT)
   ├─ Mechanistic interpretability (probing, circuits)
   └─ Functional ANOVA decomposition

EVALUATION
├─ Faithfulness (deletion / insertion, sufficiency, comprehensiveness)
├─ Sanity checks (model/data randomization)
├─ Stability / robustness
├─ Plausibility (human studies, ERASER)
└─ Run-time / computational cost
```

Print this. Stick it on your wall.

---

## 2.9 Reading list

- Adadi & Berrada — *Peeking Inside the Black-Box*, IEEE Access 2018.
- Guidotti et al. — *A Survey of Methods for Explaining Black Box Models*, CSUR 2018.
- Arrieta et al. — *Explainable AI (XAI): Concepts, Taxonomies, Opportunities and Challenges*, Information Fusion 2020.
- Krishna et al. — *The Disagreement Problem in Explainable ML*, 2022.
- Adebayo et al. — *Sanity Checks for Saliency Maps*, NeurIPS 2018.

## 2.10 Lab (1 hr)

Take last lab's XGBoost model. Run:
- Permutation importance
- TreeSHAP global
- PDP for top-3 features
- One LIME explanation

Note where they agree and disagree.

## 2.11 Quiz

1. Place SHAP for one prediction on all four axes.
2. Why is Grad-CAM model-specific?
3. Define faithfulness in one sentence.
4. Why does the disagreement problem matter for compliance?
5. Give two examples of intrinsic-interpretable models that can match black-box accuracy on tabular tasks.
