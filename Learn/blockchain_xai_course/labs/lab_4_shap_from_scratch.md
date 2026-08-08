# Lab 4 — Implement SHAP from Scratch

**Goal**: build a working KernelSHAP in ~80 lines, validate it against the `shap` library, and explore where it disagrees with LIME.

**Time**: ~4 hours.

**Prereqs**: `pip install numpy scikit-learn xgboost shap lime matplotlib`.

---

## Step 1 — Train a model

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
import xgboost as xgb

X, y = load_breast_cancer(return_X_y=True, as_frame=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

clf = xgb.XGBClassifier(n_estimators=200, max_depth=4)
clf.fit(Xtr, ytr)
print("test acc:", clf.score(Xte, yte))
```

## Step 2 — KernelSHAP from scratch

```python
import numpy as np
from itertools import combinations
from math import comb

def kernel_weight(M, s):
    if s == 0 or s == M: return 1e9
    return (M - 1) / (comb(M, s) * s * (M - s))

def kernel_shap(predict_fn, x, background, num_samples=2000, seed=0):
    """
    predict_fn:   function taking 2D array -> 1D probas
    x:            single instance (1D array of length M)
    background:   reference data (2D array)
    """
    rng = np.random.default_rng(seed)
    M = len(x)
    base = predict_fn(background).mean()

    Z = []   # coalition masks
    f = []   # model output on masked instance
    w = []   # kernel weights

    for _ in range(num_samples):
        # sample a binary mask
        z = rng.integers(0, 2, M)
        # build masked input: features in coalition = x, else = mean of background
        x_in = np.where(z, x, background.mean(0))
        Z.append(z)
        f.append(predict_fn(x_in.reshape(1, -1))[0])
        w.append(kernel_weight(M, z.sum()))

    Z = np.array(Z)
    f = np.array(f) - base   # center
    w = np.array(w)

    # Weighted linear regression: f ≈ Z @ phi  (no intercept; centered)
    W = np.diag(w)
    A = Z.T @ W @ Z
    b = Z.T @ W @ f
    phi = np.linalg.lstsq(A, b, rcond=None)[0]
    return phi, base
```

## Step 3 — Validate against the SHAP library

```python
import shap

x = Xte.iloc[0].values
background = Xtr.values[:100]
predict = lambda X: clf.predict_proba(X)[:, 1]

phi_mine, base_mine = kernel_shap(predict, x, background, num_samples=4000)

explainer = shap.KernelExplainer(predict, background)
phi_shap = explainer.shap_values(x, nsamples=4000)

# Compare
import pandas as pd
cmp = pd.DataFrame({
    "feature": Xte.columns,
    "mine": phi_mine,
    "shap": phi_shap,
    "diff": phi_mine - phi_shap
}).sort_values("shap", key=abs, ascending=False).head(10)
print(cmp)
```

The two columns should match to within ~10% on most features. Larger samples → tighter match.

## Step 4 — Compare with LIME

```python
from lime.lime_tabular import LimeTabularExplainer

lime_exp = LimeTabularExplainer(
    Xtr.values, feature_names=Xtr.columns.tolist(),
    class_names=["malignant", "benign"], mode="classification")

exp = lime_exp.explain_instance(x, clf.predict_proba, num_features=10)
for f, w in exp.as_list():
    print(f, round(w, 4))
```

Compare LIME's top features with SHAP's. They often disagree; that's the **disagreement problem**.

## Step 5 — Visualize

```python
import matplotlib.pyplot as plt

idx = np.argsort(np.abs(phi_mine))[::-1][:10]
plt.barh(range(10), phi_mine[idx][::-1])
plt.yticks(range(10), [Xte.columns[i] for i in idx][::-1])
plt.title("My SHAP values for one prediction")
plt.tight_layout()
plt.savefig("my_shap.png")
```

---

## Deliverable

- `kernel_shap.py` (~80 lines).
- A table comparing your top-10 features to the SHAP library + LIME.
- A 1-paragraph reflection on (a) why your KernelSHAP isn't exact, (b) where you observed disagreement with LIME.

## Stretch

- Implement **TreeSHAP** (much harder; consult the original paper).
- Implement **DeepSHAP** for a small neural net on the same data.
- Compute the **Shapley interaction index** for the top-2 features.
- Apply your KernelSHAP to a tiny PyTorch model and compare against `shap.GradientExplainer`.
