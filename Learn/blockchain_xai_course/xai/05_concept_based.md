# XAI Module 5 — Concept-Based Explanations

> **Goal**: Move from pixel-level attribution to **human-meaningful concepts** (e.g., "stripes", "wheel", "femininity in a face").

---

## 5.1 The motivation

Pixel-level saliency tells you *where*, not *what*. A doctor wants "the model flagged this because of irregular cell shape", not "pixel (243, 187) was important".

Concept-based methods answer **what concept drove the prediction**.

---

## 5.2 TCAV — Testing with Concept Activation Vectors

Kim, Wattenberg, Gilmer, Cai, Wexler, Viegas, Sayres — ICML 2018.

### Idea

1. **Define a concept** by collecting a set of positive examples (e.g., 50 striped images) and random negatives.
2. **Compute activations** at a chosen layer `l` for both sets.
3. **Train a linear classifier** to separate concept vs random in activation space → the normal to this hyperplane is the **Concept Activation Vector (CAV)**.
4. **Compute directional derivatives** of the target class prediction with respect to the CAV.
5. **TCAV score** = fraction of input samples for which the directional derivative is positive.

```
S_{C,k,l}(x) = ∂h_{l,k}(f_l(x)) / ∂C       (directional derivative)
TCAV_{C,k,l} = | {x in X_k : S_{C,k,l}(x) > 0} | / | X_k |
```

A statistical significance test (vs random concepts) rules out spurious results.

### Why TCAV matters
- Uses human-understandable concepts, not pixels.
- Works for any pretrained model.
- Established a research line that includes ACE, CRAFT, Network Dissection, Concept Bottleneck Models.

### Limits
- Requires curated concept datasets.
- Concept linear-separability assumption.
- Can suffer from concept entanglement.

---

## 5.3 ACE — Automated Concept Extraction

Ghorbani, Wexler, Zou, Kim (NeurIPS 2019).

Automates the "where do concepts come from" step:

1. Segment images into superpixels.
2. Cluster segments in activation space.
3. Treat each cluster centroid as an auto-discovered concept.
4. Run TCAV against it.

ACE finds concepts the researcher might not have thought to define.

---

## 5.4 CRAFT — Fel et al. (CVPR 2023)

Combines:
- Recursive non-negative matrix factorization (NMF) of activations
- Per-region attribution
- Per-region concept attribution

Output: a hierarchical decomposition of the prediction by concept, with localization. State of the art for concept-based CV explanations as of 2024.

---

## 5.5 Network Dissection (Bau, Zhou, Khosla, Oliva, Torralba — CVPR 2017)

For each conv filter, find the human-labeled concept (from the Broden dataset: objects, parts, materials, textures, scenes) it best aligns with. Result: assign filters to concepts.

Shows that some networks have surprisingly "monosemantic" units even without being trained for it.

Inspired modern **mechanistic interpretability** (see [Module 9](09_mechanistic_interpretability.md)).

---

## 5.6 Concept Bottleneck Models (Koh et al., ICML 2020)

Train the model in two stages:

```
x → C(x) = predicted concepts → ŷ
```

The concept layer is **explicit** — humans can inspect and even *intervene* on it ("test-time concept editing"). If the model says "this bird has white belly + curved beak" and you know that's wrong, you can correct it before the final prediction.

Trade-off: requires concept labels for training; accuracy gap if concepts are insufficient.

**Post-hoc CBMs** (Yuksekgonul, Wang, Zou — NeurIPS 2022) — convert any trained model into a CBM by fitting a concept layer on its features. Much cheaper.

---

## 5.7 Prototype networks — "this looks like that"

Chen et al. — *This Looks Like That: Deep Learning for Interpretable Image Recognition*, NeurIPS 2019.

**ProtoPNet**: the network learns a set of prototypes per class. Predictions are explained as "this part of input looks like this prototype of training class X".

Visually beautiful, used in medical imaging. Variants: ProtoTree, Deformable ProtoPNet, ProtoPool.

---

## 5.8 Concept Bottleneck for LLMs

Active 2024–2026 area:
- **Concept embeddings** for transformer features.
- **Sparse Autoencoders (SAEs)** decompose activations into thousands of monosemantic concepts (Anthropic, Bricken et al. 2023; Cunningham et al. 2024; Templeton et al. 2024 — *Scaling monosemanticity*).
- Probing classifiers find what concepts are encoded at each layer.

This is the most active research thread in XAI right now — see [Module 9](09_mechanistic_interpretability.md).

---

## 5.9 Limits & critiques

- **Concept arbitrariness** — different researchers pick different concept sets.
- **Concept leakage** — concept labels may encode unintended info (e.g., demographics).
- **Faithfulness** — concept predictors may not reflect what the underlying model actually uses (Margeloiu et al., 2021).
- **Concept entanglement** — single filters often respond to multiple concepts.

---

## 5.10 Reading list

- Kim et al. — *Interpretability Beyond Feature Attribution: Quantitative Testing with CAVs (TCAV)*, ICML 2018.
- Ghorbani et al. — *Towards Automatic Concept-based Explanations (ACE)*, NeurIPS 2019.
- Fel et al. — *CRAFT: Concept Recursive Activation FacTorization*, CVPR 2023.
- Bau et al. — *Network Dissection*, CVPR 2017.
- Koh et al. — *Concept Bottleneck Models*, ICML 2020.
- Chen et al. — *This Looks Like That*, NeurIPS 2019.
- Bricken et al. — *Towards Monosemanticity*, Anthropic 2023.
- Templeton et al. — *Scaling Monosemanticity*, Anthropic 2024.

## 5.11 Lab (3 hrs)

1. Pick a small ImageNet subset.
2. Build a "stripes" concept set (50 images of stripes) and a random negative set.
3. Compute the CAV at the last conv layer of ResNet-50.
4. Run TCAV for class "zebra" — verify that "stripes" matters; check significance vs random concepts.
5. Repeat for a class where "stripes" should *not* matter (e.g., "spaniel").

## 5.12 Quiz

1. Why is TCAV more useful than saliency for clinical communication?
2. What does the TCAV score quantify and how is significance tested?
3. State two differences between standard CBMs and post-hoc CBMs.
4. How does ProtoPNet explain a prediction?
5. What does the "monosemanticity" research line aim to demonstrate?
