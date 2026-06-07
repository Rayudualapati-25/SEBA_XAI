# XAI Module 8 — Attention, Transformer & LLM Interpretability

> **Goal**: Understand the methods for interpreting transformer-based models — the dominant architecture of the LLM era.

---

## 8.1 The attention-as-explanation debate

In 2019, two papers fought:
- **Jain & Wallace** — *Attention Is Not Explanation* (NAACL 2019). Shows attention weights can be radically altered without changing predictions.
- **Wiegreffe & Pinter** — *Attention Is Not Not Explanation* (EMNLP 2019). Shows attention is often informative, even if not the unique explanation.

**Consensus** (2021–2026):
- Raw attention weights are *not* faithful explanations on their own.
- Combined with gradients (Grad×Attention, Chefer et al. 2021), they can be faithful.
- Better: use methods designed for transformers (Attention Rollout, gradient-weighted attention).

---

## 8.2 Attention Rollout (Abnar & Zuidema, 2020)

Multiply attention matrices across layers, adding the identity for residual flow:

```
A_l_rollout = (A_l + I) · A_{l-1}_rollout
normalize each row
```

Yields a single matrix showing each token's accumulated influence on the [CLS] / output token. Used heavily for ViT interpretation.

---

## 8.3 Attention Flow

Treat the network as a graph where edges = attention weights. Compute max-flow from input tokens to output. Slower than rollout but cleaner attribution.

---

## 8.4 Generic Transformer Attribution (Chefer et al., CVPR 2021)

A method-of-choice for ViTs combining:
- Gradients with respect to attention
- Layer-wise relevance propagation rules
- Aggregation across heads and layers

Produces clean, faithful heatmaps for both encoder-only (BERT/ViT) and encoder-decoder transformers.

---

## 8.5 Probing classifiers

Train a simple classifier (logistic regression) on top of intermediate layer activations to predict some property `P` (POS tag, syntactic role, sentiment).

If the probe scores high → the model encodes `P` at that layer.

### Pitfalls
- Probe accuracy ≠ model use of the property.
- Hewitt & Liang (2019) — *control task* baselines necessary to separate "info is there" from "info is usable".

---

## 8.6 Logit Lens (nostalgebraist, 2020 → formalized later)

Apply the unembedding matrix to intermediate residual stream activations to see what tokens the model "would predict" at each layer.

Shows the gradual emergence of the prediction — useful for hallucination analysis.

### Tuned Lens (Belrose et al., 2023)
Train a small learned linear probe per layer instead of using the unembedding directly. Smoother trajectories, less noise.

---

## 8.7 Activation patching / causal tracing

ROME (Meng et al., NeurIPS 2022). To find *where* in the network a fact lives:

1. Run a forward pass with the original input → cache activations.
2. Run with corrupted input (e.g., "Eiffel Tower" → "Statue of Liberty").
3. Patch in cached clean activations at one site at a time.
4. Site that recovers correct answer → "this is where the fact lives".

### Why this matters
Localized facts can then be **edited** (ROME, MEMIT, GRACE) — opening model editing as a discipline. Hot 2023–2026.

---

## 8.8 The induction-head story (Anthropic, 2022)

Olsson et al., *In-context Learning and Induction Heads*. Identified two-layer attention heads that implement [A][B] ... [A] → [B] copying — the basic mechanism of in-context learning.

This is the **canonical mechanistic-interpretability case study**. Read it.

---

## 8.9 Sparse Autoencoders (SAEs) — the 2023–2025 breakthrough

The residual stream of a transformer carries many superimposed features (superposition hypothesis, Elhage et al. 2022). SAEs decompose activations into **sparse, monosemantic features**.

Pipeline:
1. Pick a layer; collect millions of activations.
2. Train an SAE: `encoder` to k-sparse latent, `decoder` to reconstruct.
3. Each learned feature → one neuron in latent space — often human-meaningful.
4. Use **feature attribution** and **steering** to test causality.

Papers:
- Bricken et al. (Anthropic) — *Towards Monosemanticity*, 2023.
- Cunningham et al. — *Sparse Autoencoders Find Highly Interpretable Features in LMs*, ICLR 2024.
- Templeton et al. (Anthropic) — *Scaling Monosemanticity to Claude 3 Sonnet*, 2024.

This is the **best lead** the field has on understanding LLMs as of 2026.

---

## 8.10 LLM-specific interpretability tools

| Tool | Purpose |
|---|---|
| **TransformerLens** | Hooks & interventions for HF models |
| **nnsight** | Remote interventions on large models (NDIF) |
| **SAELens / Neuronpedia** | Browse SAE features |
| **Garcon / Inspect (Anthropic)** | Internal Anthropic tooling, partly OSS |
| **bertviz** | Attention head visualization |
| **OpenAI Microscope** (legacy) | Neuron visualizations for vision models |

---

## 8.11 Hallucination explanation

Open problem: *why* does a given LLM hallucinate?

Approaches:
- Self-consistency (multiple samples → disagreement = uncertainty)
- Logit Lens for divergence between layers
- SAE feature attribution at the hallucination token
- RAG attribution (which retrieved chunks influenced the output?)

Industry deployment (Anthropic Claude Citations, OpenAI Structured Outputs) now ships citation-grounded outputs as a partial answer.

---

## 8.12 Reading list

- Vaswani et al. — *Attention Is All You Need*, NeurIPS 2017 (architecture baseline).
- Jain & Wallace — *Attention Is Not Explanation*, NAACL 2019.
- Wiegreffe & Pinter — *Attention Is Not Not Explanation*, EMNLP 2019.
- Abnar & Zuidema — *Quantifying Attention Flow in Transformers*, ACL 2020.
- Chefer, Gur, Wolf — *Transformer Interpretability Beyond Attention Visualization*, CVPR 2021.
- Meng et al. — *Locating and Editing Factual Associations in GPT (ROME)*, NeurIPS 2022.
- Elhage et al. — *A Mathematical Framework for Transformer Circuits*, Anthropic 2021.
- Olsson et al. — *In-context Learning and Induction Heads*, Anthropic 2022.
- Bricken et al. — *Towards Monosemanticity*, Anthropic 2023.
- Templeton et al. — *Scaling Monosemanticity*, Anthropic 2024.
- Conmy et al. — *Towards Automated Circuit Discovery*, NeurIPS 2023.

## 8.13 Lab (4 hrs)

1. Install TransformerLens. Load GPT-2 Small.
2. Reproduce the induction-head visualization on a simple `A B A B` pattern.
3. Run Logit Lens through the layers for a factual prompt; visualize trajectory.
4. (Stretch) Use a public SAE (Neuronpedia) — find a feature that activates on "Python code" and ablate it to see effect on next-token predictions.

## 8.14 Quiz

1. Why is raw attention often not a faithful explanation?
2. Describe activation patching in one paragraph.
3. What's the difference between Logit Lens and Tuned Lens?
4. State the superposition hypothesis.
5. Why are SAEs a promising path for monosemanticity?
