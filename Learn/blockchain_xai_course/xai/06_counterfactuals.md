# XAI Module 6 — Counterfactual & Contrastive Explanations

> **Goal**: Master the "what-if" family of explanations — arguably the most actionable form of XAI.

---

## 6.1 The contrastive idea

People naturally explain by contrast: "I was denied the loan because my income was too low" implicitly says "if my income had been $X higher, I would have been approved".

Counterfactual explanations operationalize this. They are:
- **Actionable** ("change feature X to Y")
- **Aligned with how humans actually explain** (Miller, 2019)
- **Stakeholder-friendly** (no model internals required)

---

## 6.2 Wachter, Mittelstadt, Russell (2017) — the canonical formulation

> "What is the smallest change to `x` that would change the prediction to `y'`?"

```
x_cf = argmin_{x'}  d(x, x') + λ · L(f(x'), y')
```

Where:
- `d(x, x')` = distance (often weighted L1 on normalized features)
- `L(f(x'), y')` = loss pushing prediction to desired class

Optimized via gradient descent for differentiable models or genetic/discrete search for non-differentiable ones.

### Desiderata
A good counterfactual is:
1. **Valid** — actually flips the prediction.
2. **Proximate** — close to `x` in input space.
3. **Sparse** — changes few features.
4. **Actionable** — only changes mutable features (can't change race, age).
5. **Plausible** — lies on the data manifold (don't recommend "earn $1,000,000 next month").
6. **Diverse** — multiple distinct paths to flip the decision.

---

## 6.3 DiCE — Diverse Counterfactual Explanations

Mothilal, Sharma, Tan — FAT* 2020.

Generates K counterfactuals that are simultaneously:
- Valid
- Close to `x`
- Mutually **diverse** (via DPP / determinantal-point-process-like regularizer)
- Respect feature constraints (mutable / immutable, monotonic)

Library: `dice-ml`. Widely used in finance / lending.

---

## 6.4 FACE — Feasible and Actionable Counterfactual Explanations

Poyiadzi et al. — AIES 2020.

Builds a graph over training data; the counterfactual is the shortest path from `x` to a flipping region through high-density regions. Ensures **plausibility** by construction.

---

## 6.5 GeCo — Genetic Counterfactuals

Searches counterfactual space via genetic algorithm with mutation, crossover, and constraint handling. Works for arbitrary black-box models including non-differentiable trees.

---

## 6.6 MACE — Model-Agnostic Counterfactual Explanations via SAT/SMT

Karimi et al. — FAT* 2020.

Encode the model + counterfactual desiderata as a SAT/SMT problem. Provably optimal counterfactuals for piecewise-linear models (trees, ReLU nets).

---

## 6.7 Algorithmic recourse — the causal turn

Karimi, Schölkopf, Valera (FAccT 2021) point out: classical counterfactuals ignore causal structure. "Change your education from BS to PhD" isn't a single intervention — it requires years and money.

**Recourse** = the **actions** required to achieve the counterfactual, accounting for causal effects.

```
intervention I  →  features x' (downstream causal effects propagate)  →  prediction f(x')
```

Requires a causal graph (often unavailable in practice — see "recourse under uncertain causal knowledge").

---

## 6.8 Contrastive explanations (pertinent positives / negatives)

Dhurandhar et al. — NeurIPS 2018, "Explanations based on the Missing".

Two halves of any prediction:
- **Pertinent positives (PP)** — minimal subset of features that *sufficiently* causes the prediction.
- **Pertinent negatives (PN)** — features whose absence is necessary (their addition would flip).

A complete contrastive explanation: "Prediction is X because of PP, and not Y because of PN."

---

## 6.9 Counterfactuals for NLP

| Method | Approach |
|---|---|
| **Polyjuice** (Wu et al. 2021) | GPT-fine-tuned counterfactual generator |
| **CheckList** (Ribeiro et al. 2020) | Templated minimal pairs for behavioral testing |
| **MiCE** (Ross et al. 2021) | Minimal contrastive edits via Levenshtein |
| **CAT** | LLM-as-editor for counterfactual NLP |

Used to find spurious correlations (e.g., model predicts "positive" for *any* sentence with the word "amazing").

---

## 6.10 Counterfactuals for images

Hard problem — pixel space is high-dimensional and "small change" is meaningless without a manifold prior.

| Approach | Method |
|---|---|
| Latent-space (StyleGAN inversion) | Edit `w` vector → decode |
| Diffusion-based | Counterfactual via guided diffusion |
| Saliency-region edits | Inpaint salient region differently |
| Concept-aware (e.g., StylEx, Lang et al. 2021) | GAN with classifier-aligned latent directions |

---

## 6.11 Counterfactuals as compliance tools

Wachter et al. argued counterfactuals satisfy GDPR's right-to-explanation. They don't reveal model internals (good for trade secrets) but give the user actionable information.

Adopted in:
- Credit denial letters (US ECOA adverse-action notices)
- Algorithmic hiring tools
- Insurance underwriting

---

## 6.12 Failures and critiques

- **Manifold off-distribution** — gradient-descent counterfactuals often produce inputs no human would recognize.
- **Adversarial-like artifacts** — minimum-change counterfactuals can be adversarial perturbations.
- **Causal naivety** — ignoring causal relations gives unactionable advice.
- **Fairness** — counterfactual recommendations can be discriminatory if mutable features differ across groups (e.g., harder for some groups to "increase income").
- **Multiplicity** — many equally-good counterfactuals exist; which do you show?

---

## 6.13 Reading list

- Wachter, Mittelstadt, Russell — *Counterfactual Explanations Without Opening the Black Box*, Harvard JOLT 2017.
- Mothilal, Sharma, Tan — *Explaining Machine Learning Classifiers through Diverse Counterfactual Explanations (DiCE)*, FAT* 2020.
- Poyiadzi et al. — *FACE: Feasible and Actionable Counterfactual Explanations*, AIES 2020.
- Karimi et al. — *A Survey of Algorithmic Recourse*, ACM Computing Surveys 2022.
- Dhurandhar et al. — *Explanations based on the Missing*, NeurIPS 2018.
- Ross, Marasović, Peters — *Explaining NLP Models via Minimal Contrastive Editing*, ACL 2021.
- Verma, Dickerson, Hines — *Counterfactual Explanations and Algorithmic Recourse for Machine Learning: A Review*, 2024.

## 6.14 Lab (3 hrs)

1. Train a logistic regression on UCI Adult (income ≥ $50k).
2. For 10 denied applicants, generate counterfactuals using:
   - Vanilla Wachter (gradient)
   - DiCE
3. Audit: which features did each method change? Are they mutable / actionable?
4. Discuss fairness — do counterfactuals for women differ systematically from men's?

## 6.15 Quiz

1. State Wachter's objective in math.
2. Distinguish counterfactual explanation from algorithmic recourse.
3. Why is plausibility hard to enforce via gradient descent alone?
4. Define pertinent positives and pertinent negatives.
5. Why might counterfactuals discriminate even when the model itself is "fair"?
