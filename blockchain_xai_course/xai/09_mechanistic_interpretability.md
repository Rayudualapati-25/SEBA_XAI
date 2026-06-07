# XAI Module 9 — Mechanistic Interpretability

> **Goal**: Understand the program of reverse-engineering neural networks into human-understandable algorithms — the most active frontier of interpretability research.

---

## 9.1 The mech-interp thesis

> *Neural networks learn algorithms. Those algorithms can, in principle, be reverse-engineered into circuits humans can read.*

If true, this offers something stronger than post-hoc explanation: a **mechanistic understanding** that can be verified, edited, and used for safety.

The thesis is most associated with:
- **Distill.pub Circuits Thread** (2017–2020): Olah, Cammarata, Schubert, Carter, Voss, Goh, Mordvintsev.
- **Anthropic Mechanistic Interpretability team** (2021–present).
- **Neel Nanda** (Google DeepMind / Anthropic): popularized the program with TransformerLens and educational write-ups.

---

## 9.2 Why mech-interp matters for AI safety

If you can read what a model is computing, you can:
- Detect deceptive alignment.
- Find dangerous capabilities before deployment.
- Verify whether a model "knows it's lying".
- Edit knowledge / behavior surgically.

These are why Anthropic, DeepMind, OpenAI invest heavily in interpretability research.

---

## 9.3 The Distill Circuits Thread — vision

Olah et al. analyzed InceptionV1 unit by unit.

### Findings
- **Curve detectors** in early layers — clean equivariant features.
- **High-low frequency detectors** — distinguish foreground/background.
- **Multimodal neurons** (Goh et al., 2021) — single neurons that fire for both an image *and* the text of a concept (e.g., "Spider-Man" neuron).
- **Polysemantic neurons** — one neuron responding to multiple unrelated concepts → superposition.
- **Equivariance** — networks learn rotated/translated copies of similar filters.

These are direct evidence that **interpretable structure exists**.

---

## 9.4 A Mathematical Framework for Transformer Circuits (Elhage et al., 2021)

Decompose transformer behavior into:
- **Residual stream** as the communication medium.
- **Attention heads** as read/write operations.
- **MLP layers** as memory / nonlinear gates.
- **QK and OV circuits** as separable read- vs write-direction operators.

This gave the field a vocabulary and made later work (induction heads, ROME) possible.

---

## 9.5 Induction heads — Olsson et al., 2022

A specific two-layer circuit that implements in-context completion:
- **Previous-token head** at layer L: copies token T₁ to position of T₂.
- **Induction head** at layer L+1: looks back for similar pattern, copies the continuation.

Together these produce: `[T₁ T₂] ... [T₁] → predict T₂`.

These heads appear **across model scales** and explain a phase transition in in-context learning ability.

---

## 9.6 ROME / MEMIT — knowledge editing

Meng et al. (NeurIPS 2022) found that factual associations like "Eiffel Tower is in Paris" are stored in specific MLP layers. ROME edits them via rank-one updates to MLP weights.

Followups:
- **MEMIT** — mass editing (many facts at once).
- **GRACE** — robust against rollback.
- **ICE** — in-context editing without weight changes.

Used in **alignment research** to test whether edited knowledge generalizes (often it doesn't, perfectly).

---

## 9.7 Automatic circuit discovery

Manual circuit discovery is slow. Recent work automates it:
- **ACDC** (Conmy et al., NeurIPS 2023) — Automated Circuit DisCovery via edge ablation.
- **EAP / EAP-IG** — Edge Attribution Patching with Integrated Gradients.
- **Path Patching** — measures direct causal paths.

These tools take a hypothesized task (e.g., "indirect object identification") and produce the minimal circuit responsible.

---

## 9.8 Indirect Object Identification (IOI) — Wang et al. 2022

Classic case study: GPT-2 Small correctly completes "When John and Mary went to the store, John gave a drink to ___" with "Mary".

Discovered circuit:
- Duplicate-token heads
- S-inhibition heads
- Name mover heads
- Backup name mover heads (redundancy!)

The redundancy explains why simple ablation studies can mislead.

---

## 9.9 Superposition and SAEs (recap)

The superposition hypothesis: networks pack more features than they have neurons, in **interfering** directions.

SAEs (covered in [Module 8](08_attention_transformers.md)) decompose the residual stream into ~tens of thousands of sparse, near-monosemantic features. This may be the **technical breakthrough** that unblocks mech-interp at LLM scale.

Recent: **Gemma Scope** (Google DeepMind, 2024) — SAEs on every layer of Gemma 2; **SAELens, Neuronpedia, GoodFire** — tooling.

---

## 9.10 Causal analysis with abstractions

Geiger, Lu, Icard, Potts (NeurIPS 2021, ICML 2023) — **Causal Abstraction**: hypothesize a human-readable algorithm, then verify by intervention that the model implements it.

Formalizes "the model computes X" as a causal claim that can be falsified.

---

## 9.11 Limits of mech-interp

- **Scaling** — most case studies are GPT-2 Small or smaller. Big models are mostly opaque.
- **Polysemanticity / superposition** — even with SAEs, decomposition is imperfect.
- **Compositional behavior** — circuits found for one task may not compose.
- **Reproducibility** — many findings are checkpoint-specific.
- **Selection bias** — researchers report wins; we don't know how often circuits failed to be found.

Be honest about these in any paper you write.

---

## 9.12 How to start a mech-interp research project

1. Pick a small, well-defined behavior (1-token completion task).
2. Pick a small model (GPT-2 Small, Pythia 70M–410M).
3. Use TransformerLens. Run ACDC or EAP to find a candidate circuit.
4. Validate via causal interventions (ablation, patching).
5. Write up with diagrams + interactive demos.

The bar to enter is unusually low; the bar to make a *general* claim is high.

---

## 9.13 Reading list

- Olah, Mordvintsev, Schubert — *Feature Visualization*, Distill 2017.
- Olah et al. — *Zoom In: An Introduction to Circuits*, Distill 2020.
- Goh et al. — *Multimodal Neurons in Artificial Neural Networks*, Distill 2021.
- Elhage et al. — *A Mathematical Framework for Transformer Circuits*, Anthropic 2021.
- Olsson et al. — *In-Context Learning and Induction Heads*, Anthropic 2022.
- Wang et al. — *Interpretability in the Wild: A Circuit for Indirect Object Identification*, 2022.
- Meng et al. — *Locating and Editing Factual Associations in GPT (ROME)*, NeurIPS 2022.
- Conmy et al. — *Towards Automated Circuit Discovery for Mechanistic Interpretability (ACDC)*, NeurIPS 2023.
- Bricken et al. — *Towards Monosemanticity*, Anthropic 2023.
- Templeton et al. — *Scaling Monosemanticity*, Anthropic 2024.
- Geiger et al. — *Inducing Causal Structure for Interpretable Neural Networks*, ICML 2022.
- Nanda — *A Comprehensive Mechanistic Interpretability Explainer*, neelnanda.io.

## 9.14 Lab (4 hrs)

1. Install TransformerLens + GPT-2 Small.
2. Reproduce the IOI prompt: "When John and Mary went to the store, John gave a drink to ___".
3. Identify name-mover heads via attention patching. Show that ablating them drops accuracy from ~80% to ~20%.
4. Visualize one head's attention pattern.

## 9.15 Quiz

1. Why is superposition a problem for naive neuron-level interpretation?
2. State the difference between activation patching and gradient-based attribution.
3. What is an induction head and why does it matter for in-context learning?
4. Describe one finding from the IOI circuit paper that complicates naive ablation.
5. Why might SAEs be the practical breakthrough for LLM interpretability?
