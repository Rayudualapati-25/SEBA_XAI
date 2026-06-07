# XAI Module 4 — Gradient-Based Attribution

> **Goal**: Master the saliency / gradient family — the workhorse of computer-vision XAI.

---

## 4.1 The core intuition

If you change pixel `x_i` by a tiny amount, how much does the output `f(x)` change?

That's the partial derivative `∂f/∂x_i`. Gradient-based methods are variations on this single idea, fixing its (many) flaws.

---

## 4.2 Vanilla saliency (Simonyan et al., 2013)

```
saliency(x_i) = | ∂f_c(x) / ∂x_i |
```

Visualize as a heatmap over the input image. Simplest possible attribution.

**Problems**
- Noisy — gradients fluctuate wildly across nearby inputs.
- Saturation — for ReLU networks, large activations zero out the gradient even when the feature matters.
- Doesn't distinguish *what* makes the prediction (positive vs negative evidence).

---

## 4.3 SmoothGrad (Smilkov et al., 2017)

Average saliency over noisy copies:
```
SmoothGrad(x) = (1/N) · Σ saliency(x + ε_i), ε_i ~ N(0, σ²)
```

Visually much cleaner. Essentially a denoising of vanilla saliency.

---

## 4.4 Integrated Gradients (Sundararajan, Taly, Yan — ICML 2017)

Solve the saturation problem by integrating along a straight path from a baseline `x'` to input `x`:

```
IG_i(x) = (x_i - x'_i) · ∫_{α=0}^{1}  ∂f(x' + α(x - x')) / ∂x_i  dα
```

Approximated by Riemann sum with ~50 steps.

### Why IG matters
Satisfies two axioms:
1. **Sensitivity** — if changing a feature changes prediction, attribution is nonzero.
2. **Implementation invariance** — two functionally-equivalent networks yield identical attributions.

Vanilla saliency violates Sensitivity (saturation). Pre-IG methods (DeConvNet, Guided Backprop) violate Implementation Invariance.

### Choice of baseline matters

| Baseline | Use case |
|---|---|
| All-zeros image | Default but problematic for "black" matters |
| Random noise | Hides biases |
| Blurred version of x | "What changed from blurry-known to detailed-classified" |
| Mean of training set | Centroidal |
| Multiple baselines, averaged | Most robust (Expected Gradients) |

**Expected Gradients** (Erion et al., 2021) averages over a distribution of baselines — combines IG with SHAP's expectation.

---

## 4.5 Guided Backprop & DeConvNet

Modify the backward pass through ReLU to suppress negative gradients. Visually nice but fails sanity checks (Adebayo et al., 2018) — they produce similar-looking saliency maps **even when the model is randomly initialized**.

Conclusion: Guided BP is essentially an edge detector, not a faithful explanation.

---

## 4.6 Grad-CAM (Selvaraju et al., ICCV 2017)

Compute the gradient of the target class score with respect to the activations of the **last conv layer**:

```
α_k = (1/Z) · Σ_{i,j} ∂y_c / ∂A^k_{i,j}
Grad-CAM = ReLU(Σ_k α_k · A^k)
```

Produces a low-resolution (e.g., 7×7) heatmap upsampled to the input. **The most-used saliency method in practice**.

### Variants
- **Grad-CAM++** — better localization when multiple instances of the class are present.
- **Score-CAM** — replaces gradients with forward-pass weights (more faithful).
- **Eigen-CAM** — uses the first principal component of activation maps.
- **HiResCAM** — corrects a small flaw in Grad-CAM's element-wise multiplication.

---

## 4.7 Layer-wise Relevance Propagation (LRP)

A backward propagation rule for redistributing the prediction relevance through the network. Different "rules" (LRP-ε, LRP-γ, LRP-αβ) work best for different layer types.

Most popular for clinical/medical imaging because it's deterministic and faithful by construction (relevance conservation across layers).

---

## 4.8 Sanity checks (Adebayo et al., NeurIPS 2018)

A paper everyone should read once.

Two tests:
1. **Model randomization test** — re-initialize weights from the top layer down. A faithful explanation should change drastically.
2. **Data randomization test** — train on permuted labels. A faithful explanation should produce different attributions than the correctly-trained model.

Result: Guided Backprop and Guided Grad-CAM **fail** both tests. Integrated Gradients and vanilla saliency pass model-randomization but only partially data-randomization.

**Takeaway**: a pretty heatmap may be edge-detection, not explanation.

---

## 4.9 Attribution for Transformers

Gradient methods generalize to transformers but care is needed:

- Saliency works token-wise.
- Integrated Gradients with token embedding baselines.
- **Attention Rollout** (Abnar & Zuidema 2020) — multiply attention matrices across layers.
- **Attention Flow** — max-flow through attention graph.
- **Chefer et al.** (2021) — generic Transformer attribution combining gradients + attention.

(More in [Module 8](08_attention_transformers.md).)

---

## 4.10 The IG family today

The 2024–2026 SOTA cluster:

- **Path-Integrated Gradients with optimal paths**
- **Bias-Free Integrated Gradients**
- **GAM (Guided Attention Maps)** for ViTs
- **CAFE / TracIn-Influence** for input + training attribution

---

## 4.11 Reading list

- Simonyan, Vedaldi, Zisserman — *Deep Inside Convolutional Networks: Visualising Image Classification Models*, 2013.
- Sundararajan, Taly, Yan — *Axiomatic Attribution for Deep Networks (Integrated Gradients)*, ICML 2017.
- Smilkov et al. — *SmoothGrad: removing noise by adding noise*, 2017.
- Selvaraju et al. — *Grad-CAM*, ICCV 2017.
- Bach et al. — *On Pixel-Wise Explanations for Non-Linear Classifier Decisions by Layer-Wise Relevance Propagation*, PLoS ONE 2015.
- Adebayo et al. — *Sanity Checks for Saliency Maps*, NeurIPS 2018.
- Erion et al. — *Improving performance of deep learning models with axiomatic attribution priors and expected gradients*, Nature MI 2021.

## 4.12 Lab (3 hrs)

1. Use a pretrained ResNet-50 on an ImageNet image.
2. Implement and visualize: vanilla saliency, SmoothGrad, Integrated Gradients (50 steps), Grad-CAM.
3. Run Adebayo's randomization test on each method. Report which survive.
4. Repeat the IG step with three different baselines. Discuss differences.

## 4.13 Quiz

1. What does the "implementation invariance" axiom rule out?
2. Why does Grad-CAM produce a low-resolution map?
3. State the SmoothGrad equation.
4. Explain in one sentence why Guided Backprop fails the sanity check.
5. Why is baseline choice central to IG's interpretation?
