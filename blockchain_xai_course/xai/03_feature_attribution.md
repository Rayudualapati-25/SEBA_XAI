# XAI Module 3 — LIME, SHAP, and the Feature Attribution Family

> **Goal**: Master the two most-cited XAI methods. Be able to implement both from scratch in ~100 lines of Python each.

---

## 3.1 LIME — Local Interpretable Model-agnostic Explanations

Ribeiro, Singh, Guestrin — KDD 2016. **The first widely-adopted post-hoc method.**

### Idea
For a single instance `x`, fit a simple, interpretable surrogate model `g` (e.g., sparse linear) in the local neighborhood of `x` such that `g` approximates `f` there. The surrogate's coefficients become the explanation.

### Algorithm

```
Input: model f, instance x, num_samples N
1. Sample N perturbations x'_i in the neighborhood of x.
   - Tabular: perturb features around x.
   - Text: randomly delete words.
   - Image: superpixels (SLIC) toggled on/off.
2. Compute model predictions y'_i = f(x'_i).
3. Weight each sample by a kernel π(x, x'_i) — closer to x → higher weight.
4. Fit a linear model g on (x'_i, y'_i) weighted by π and with sparsity (L1).
5. Return g's coefficients as the explanation.
```

### Strengths
- Truly model-agnostic.
- Intuitive output (sparse linear).

### Weaknesses
- **Instability** — different random seeds give different explanations (Alvarez-Melis & Jaakkola, 2018).
- **Choice of neighborhood** is arbitrary and influences results.
- **Adversarial vulnerability** — Slack et al. (2020) showed a model can be made to lie to LIME while still being biased.

---

## 3.2 SHAP — SHapley Additive exPlanations

Lundberg & Lee — NeurIPS 2017. **The single most-cited XAI method**.

### Idea
Borrow Shapley values from cooperative game theory. For each feature, ask: "What is its marginal contribution to the prediction, averaged over all possible coalitions of other features?"

### Shapley value formula

For player i in game v with N players:

```
φ_i(v) = Σ_{S ⊆ N \ {i}}  [ |S|! · (|N|-|S|-1)! / |N|! ] · [ v(S ∪ {i}) - v(S) ]
```

In ML: `v(S) = E[f(X) | X_S = x_S]` — expected prediction conditioned on the features in S being fixed at x's values.

### Why Shapley values matter
They are the **unique** allocation satisfying:
1. **Efficiency** — Σ φ_i = f(x) - E[f(X)] (attributions sum to the gap from baseline)
2. **Symmetry** — symmetric features get equal credit
3. **Dummy** — irrelevant features get 0
4. **Linearity** — for two games combined, attributions add

This axiomatic uniqueness is what gives SHAP its theoretical edge over LIME.

### Variants

| Variant | Speed | Faithfulness |
|---|---|---|
| **KernelSHAP** | Slow (model-agnostic via weighted regression) | Good |
| **TreeSHAP** | Fast (exact, exploits tree structure) | Exact for tree ensembles |
| **DeepSHAP / Deep LIFT** | Medium (chain rule with reference) | Good for NNs |
| **PartitionSHAP** | Medium (hierarchical Owen values) | Useful for high-dim features |
| **FastSHAP** | Very fast (amortized via a learned predictor) | Good after training |

### Conditional vs marginal expectation
- **Marginal** (`E[f | do(X_S = x_S)]`) — break dependence, like in interventional causal inference.
- **Conditional** (`E[f | X_S = x_S]`) — preserve dependence.

Aas et al. (2021) showed marginal SHAP can credit features that aren't in the model. Use conditional when features are correlated. Most libraries default to marginal — beware.

---

## 3.3 SHAP visualizations to know

- **Force plot** — per-prediction, additive.
- **Waterfall plot** — per-prediction, sequential.
- **Summary / beeswarm plot** — global, distribution of attributions across data.
- **Dependence plot** — feature value vs SHAP value with color = interacting feature.
- **Decision plot** — multi-prediction comparison.

---

## 3.4 LIME vs SHAP — when to use which

| Use case | Pick |
|---|---|
| Tree ensemble (XGBoost, LightGBM, RF) | **TreeSHAP** (fast, exact) |
| Black box, prototype phase | LIME (faster setup) |
| Need theoretical guarantees | SHAP |
| Need to explain text or images | Either, but consider gradient methods too |
| Tight compute budget | LIME |
| Compliance documentation | SHAP (axiomatic story is easier to defend) |

---

## 3.5 Anchors — Ribeiro et al. 2018

A rule-based local explanation: "Anchor" = a set of feature predicates such that, whenever those predicates hold, the model's prediction is the same with high probability (e.g., precision ≥ 0.95).

```
IF age > 50 AND education = "Bachelor"  THEN predict = "income > 50K"  (precision 0.97, coverage 0.12)
```

Pros: high-precision, easy to read.
Cons: anchors may not exist for all instances; coverage trade-off.

---

## 3.6 DeepLIFT / Layer-wise Relevance Propagation (LRP)

Both methods backpropagate attributions through a neural network using a reference / baseline input, distributing credit to inputs.

- **DeepLIFT** (Shrikumar et al., 2017) — chain rule with multipliers relative to reference.
- **LRP** (Bach et al., 2015) — propagate relevance backward via custom rules per layer.

Both are precursors to Integrated Gradients and underlie DeepSHAP.

---

## 3.7 Influence functions — Koh & Liang (2017)

A different kind of explanation: *which training points most influenced this prediction?*

Approximates leave-one-out retraining without retraining, via implicit Hessian-vector products.

Useful for debugging mislabeled data, finding adversarial training examples, and credit attribution. Computationally expensive for large models; scalable variants (TracIn, Datamodels) are active research.

---

## 3.8 Implementing KernelSHAP in 60 lines (sketch)

```python
import numpy as np
from itertools import combinations
from math import comb

def kernel_weight(M, s):
    if s == 0 or s == M: return 1e6   # large weight, edge case
    return (M - 1) / (comb(M, s) * s * (M - s))

def kernel_shap(f, x, background, num_samples=2000):
    M = len(x)
    masks, weights, ys = [], [], []
    for _ in range(num_samples):
        z = np.random.randint(0, 2, M)
        x_masked = np.where(z, x, background.mean(0))
        masks.append(z)
        weights.append(kernel_weight(M, z.sum()))
        ys.append(f(x_masked))
    Z = np.array(masks); w = np.array(weights); y = np.array(ys)
    # Weighted linear regression with intercept = E[f]
    base = f(background).mean()
    y_centered = y - base
    W = np.diag(w)
    phi = np.linalg.lstsq(Z.T @ W @ Z, Z.T @ W @ y_centered, rcond=None)[0]
    return phi  # one Shapley value per feature
```

This is enough to convince yourself the math works. Production SHAP is much more optimized.

---

## 3.9 Reading list

- Ribeiro, Singh, Guestrin — *"Why Should I Trust You?": Explaining the Predictions of Any Classifier*, KDD 2016.
- Lundberg & Lee — *A Unified Approach to Interpreting Model Predictions*, NeurIPS 2017.
- Lundberg et al. — *From local explanations to global understanding with explainable AI for trees*, Nature MI 2020.
- Ribeiro, Singh, Guestrin — *Anchors: High-Precision Model-Agnostic Explanations*, AAAI 2018.
- Shrikumar, Greenside, Kundaje — *Learning Important Features Through Propagating Activation Differences (DeepLIFT)*, ICML 2017.
- Aas, Jullum, Løland — *Explaining individual predictions when features are dependent*, 2021.
- Slack et al. — *Fooling LIME and SHAP*, AIES 2020.
- Koh & Liang — *Understanding Black-box Predictions via Influence Functions*, ICML 2017.

## 3.10 Lab (3 hrs)

1. Implement KernelSHAP from scratch (use the sketch above as starter).
2. Verify it matches `shap` library output on 5 examples from a small XGBoost model.
3. Run TreeSHAP on the same model; compare runtime.
4. Implement an "adversarial" model that detects when it's being explained and returns a different (benign) function (per Slack et al.).

## 3.11 Quiz

1. State the four Shapley axioms.
2. Why is TreeSHAP exact and KernelSHAP only approximate?
3. Explain marginal vs conditional SHAP and when each is appropriate.
4. How does LIME's neighborhood choice affect explanations?
5. What is an "anchor" and when does it not exist?
