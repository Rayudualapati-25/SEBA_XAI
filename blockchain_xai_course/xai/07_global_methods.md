# XAI Module 7 — Global Methods: PDP, ICE, ALE, Surrogates, Permutation Importance

> **Goal**: Master the global / cohort-level methods for tabular ML — the bread and butter of every applied XAI engagement.

---

## 7.1 Partial Dependence Plots (PDP)

Friedman, 2001.

For feature(s) `S`, marginalize out the rest:

```
PDP_S(x_S) = (1/N) Σ_i f(x_S, x_i^{(C)})
```

For each value of `x_S`, average the prediction over the dataset, holding `x_S` fixed.

### Visualization
- 1D feature → line plot.
- 2D pair → heatmap (shows interactions).

### Limits
- **Assumes feature independence** — if `x_S` is correlated with `x_C`, the marginalization creates impossible synthetic data points (a 6-foot 60-pound person).
- Only shows **average** effect — hides heterogeneity.

---

## 7.2 ICE — Individual Conditional Expectation

Goldstein et al., 2015.

Instead of averaging, plot **one line per instance**: how does *this person's* prediction change as we vary `x_S` for them?

PDP = average of all ICE curves.

When ICE curves diverge significantly, the PDP is misleading and you have heterogeneous effects.

---

## 7.3 ALE — Accumulated Local Effects

Apley & Zhu, 2020.

Solves PDP's correlation problem.

```
For interval k of feature x_j:
   compute local effect = E[ f(x_j = upper) - f(x_j = lower) | x_j in interval k ]
Accumulate and center across intervals.
```

ALE conditions on the actual data distribution, so it doesn't fabricate impossible samples. **Should be the default for correlated features.**

| Method | Handles correlation? | Computational cost |
|---|---|---|
| PDP | No | Low |
| ICE | No | Low |
| ALE | Yes | Low |
| SHAP global | Conditionally yes | Medium |

---

## 7.4 Permutation Feature Importance

Breiman, 2001 (random forests); model-agnostic since.

```
Importance(j) = error(f, X_permuted_j, y) - error(f, X, y)
```

Shuffle one feature's column, measure performance drop. Bigger drop = more important feature.

### Pitfalls
- Same correlation issue (creates impossible data points).
- Importance is **with respect to the loss**, not the prediction — interpret accordingly.
- High-cardinality features can be over-credited (use grouped permutation).

**Conditional permutation importance** fixes some of these by shuffling within strata.

---

## 7.5 Global SHAP

Aggregate local SHAP values across the dataset:
- Mean(|SHAP|) per feature → global importance
- Summary / beeswarm plot → distribution
- Dependence plots → effect across the data

This is "the SHAP plot" you see in 90% of Kaggle kernels.

---

## 7.6 Surrogate models

Train a simpler, interpretable model to mimic the black box.

### Global surrogate
```
f_black_box(x) → ŷ
g_interpretable(x) → ŷ  (regress g on f's predictions over a large sample)
```

If `g`'s R² ≈ 1, you can use `g` as the explanation. Otherwise, `g`'s explanations are unreliable.

### Knowledge distillation
A specific form of global surrogate where a *smaller neural net* mimics a larger one. Hinton et al., 2015. Not strictly XAI but related.

### Soft Decision Trees (Frosst & Hinton, 2017)
Trees with stochastic routing that can match a neural net while remaining traceable.

---

## 7.7 Functional ANOVA decomposition

Decompose `f(x) = f_∅ + Σ f_i(x_i) + Σ f_{ij}(x_i, x_j) + ...` into main effects + interactions.

EBMs do this exactly — and that's why they tend to be both accurate and interpretable on tabular data.

---

## 7.8 H-statistic for interactions

Friedman & Popescu, 2008. Measures whether feature pair `(j, k)` interacts beyond their additive effects.

```
H²_jk = Σ_i [ PDP_jk(x_i) - PDP_j(x_i) - PDP_k(x_i) ]² / Σ_i PDP_jk(x_i)²
```

Useful when you suspect interactions are driving the model.

---

## 7.9 Anchors at the global level

Aggregate Anchors across the dataset to surface high-precision rule patterns the model uses.

---

## 7.10 Functional cohorts — SliceFinder

Chung, Polyzotis, Tae, Whang (2019) — automatically find data slices where the model performs worst. Critical for fairness audits.

```
slice = {x : age > 60 AND device = "android"}
   if loss on slice >> overall loss → investigate
```

Tools: Slice Finder, Aequitas, FairLearn, Robustness Gym.

---

## 7.11 When to use which

| Task | Use |
|---|---|
| Quick global feature rank | Permutation importance or global SHAP |
| Visualize a single feature's effect | PDP + ICE (small dataset), ALE (large/correlated) |
| Inspect interaction | PDP-2D or H-statistic |
| Build an explanation for stakeholders | Surrogate tree |
| Audit subgroup performance | SliceFinder + Aequitas |
| Need axiomatic guarantees | SHAP global |

---

## 7.12 Reading list

- Friedman — *Greedy Function Approximation: A Gradient Boosting Machine*, Annals 2001 (PDP section).
- Goldstein et al. — *Peeking Inside the Black Box: Visualizing Statistical Learning with ICE*, JCGS 2015.
- Apley & Zhu — *Visualizing the Effects of Predictor Variables in Black Box Supervised Learning Models (ALE)*, JRSS B 2020.
- Breiman — *Random Forests*, ML 2001 (permutation importance).
- Friedman & Popescu — *Predictive Learning via Rule Ensembles*, AOAS 2008.
- Chung et al. — *Slice Finder: Automated Data Slicing for Model Validation*, ICDE 2019.
- Molnar — *Interpretable Machine Learning*, Ch 5–7.

## 7.13 Lab (2 hrs)

1. On the California Housing dataset, train XGBoost.
2. Generate PDP, ICE, ALE, permutation importance, global SHAP plots for the top-5 features.
3. Find at least one feature where PDP and ALE disagree → explain why (correlation).
4. Use SliceFinder to find the worst-performing data slice.

## 7.14 Quiz

1. Why can PDP be misleading for correlated features?
2. State the formal difference between PDP and ICE.
3. When would you choose ALE over SHAP?
4. Give one situation where permutation importance over-credits a feature.
5. What's the relationship between EBMs and functional ANOVA?
