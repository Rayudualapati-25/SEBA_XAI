# XAI Module 10 — Evaluating Explanations

> **Goal**: A paper that introduces an explanation method is only as good as its evaluation. Master the metrics, sanity checks, and adversarial tests.

---

## 10.1 Three lenses (revisited)

| Lens | Question | Cost |
|---|---|---|
| **Faithfulness** | Does the explanation reflect what the model actually computes? | Low–Medium |
| **Plausibility** | Does it make sense to humans? | High (user studies) |
| **Robustness** | Does it change under tiny input perturbations? | Low |

A method can be plausible but unfaithful (Slack et al. attack), or faithful but not human-aligned (mech interp circuits).

---

## 10.2 Faithfulness metrics

### Deletion / Insertion (Petsiuk, Das, Saenko, 2018 — RISE paper)

```
deletion:  remove top-k most-attributed features → measure prediction drop
           area-under-curve (AUC) = lower is better (explanation captures important features)

insertion: add top-k from blank baseline → measure prediction rise
           AUC = higher is better
```

### ROAR (RemOve And Retrain) — Hooker et al., NeurIPS 2019
Remove top features, **retrain** the model, then measure accuracy. Tests whether the attributed features were actually informative — not just "the model uses them now".

### Comprehensiveness / Sufficiency — DeYoung et al. 2020 (ERASER benchmark)
- **Comprehensiveness** = drop in prediction after removing the explanation rationale.
- **Sufficiency** = prediction when *only* the rationale is kept.

A good explanation has high comprehensiveness *and* low sufficiency gap.

### Infidelity (Yeh et al., NeurIPS 2019)
```
INFD(g, f, x) = E_I [ (I^T g(x) - (f(x) - f(x - I)))² ]
```
Where `I` is a perturbation vector. Measures expected difference between attributions and actual prediction change under perturbations.

### AOPC (Area Over Perturbation Curve)
Same family as deletion / insertion AUC.

---

## 10.3 Sanity checks (Adebayo et al., NeurIPS 2018)

Two tests every saliency method should pass:

### Model parameter randomization
Re-initialize the top layers downward. A faithful saliency must change.

### Data randomization
Train the model on randomly-relabeled data. A faithful saliency must produce noticeably different attributions than the correctly-trained model.

**Methods that fail**: Guided Backprop, Guided Grad-CAM. Their outputs are too similar across these manipulations to count as model-specific explanations.

---

## 10.4 Robustness / Stability

### Local stability (Alvarez-Melis & Jaakkola, 2018)
```
Stability(x) = sup_{x' ~ x} ‖g(x) - g(x')‖ / ‖x - x'‖
```
For nearby `x'`, the explanation `g` shouldn't jump.

LIME and SHAP can fail this badly without averaging.

### Adversarial XAI
Slack et al. (AIES 2020) constructed a "biased model that hides its bias from LIME and SHAP". Showed that explanation methods themselves can be **gamed**.

Aïvodji et al. (2019) — "Fairwashing" — building a fair-looking explanation for an unfair model.

---

## 10.5 Plausibility (human-aligned) metrics

### ERASER (DeYoung et al., 2020)
NLP benchmark with human-annotated rationales. Compare explanation tokens to human-marked tokens via IoU / token-F1.

### Human studies
- **Simulatability** — can humans predict model output given the explanation? (Hase & Bansal, 2020)
- **Forward simulation** — humans use the explanation to make decisions; measure accuracy / time / trust.
- **Counterfactual simulatability** — given an explanation, can the user predict what would change if they changed feature X?

These are the gold standard. They are expensive and rare.

---

## 10.6 Specialized benchmarks

| Benchmark | Domain |
|---|---|
| **ERASER** | NLP rationales |
| **CLEVR-X** | VQA explanations |
| **GRADELLM / FActScore** | LLM hallucination grounding |
| **OpenXAI** | Tabular feature attribution standard |
| **Quantus** | Comprehensive XAI metric library (Hedström et al., 2023) |
| **Funke et al. BAM** | Benchmark for Attribution Methods (synthetic ground truth) |

Use **Quantus** for any new tabular/vision XAI work — it implements 30+ metrics.

---

## 10.7 The "disagreement problem" revisited (Krishna et al. 2022)

Empirically:
- Different methods rank features differently.
- Rank correlation across (LIME, SHAP, IG, SmoothGrad) often 0.3–0.6.
- Practitioners pick the explanation that confirms their priors.

**Practical mitigation**: report multiple methods + consistency metrics; pre-register the explanation method you'll use, before training.

---

## 10.8 What to report in a new XAI paper

A minimum checklist:
- [ ] At least one faithfulness metric (deletion/insertion AUC, ROAR, or Infidelity).
- [ ] Sanity checks (Adebayo).
- [ ] Stability metric.
- [ ] Comparison to ≥3 baselines.
- [ ] Disagreement analysis with at least 2 alternative methods.
- [ ] If applicable, plausibility metric (ERASER overlap, human study).
- [ ] Computational cost.

Without these, reviewers will ask.

---

## 10.9 Reading list

- Adebayo et al. — *Sanity Checks for Saliency Maps*, NeurIPS 2018.
- Hooker et al. — *A Benchmark for Interpretability Methods in Deep Neural Networks (ROAR)*, NeurIPS 2019.
- Yeh, Hsieh, Suggala, Inouye, Ravikumar — *On the (In)fidelity and Sensitivity of Explanations*, NeurIPS 2019.
- Petsiuk, Das, Saenko — *RISE: Randomized Input Sampling for Explanation*, BMVC 2018.
- DeYoung et al. — *ERASER: A Benchmark to Evaluate Rationalized NLP Models*, ACL 2020.
- Slack, Hilgard, Jia, Singh, Lakkaraju — *Fooling LIME and SHAP*, AIES 2020.
- Aïvodji et al. — *Fairwashing: the risk of rationalization*, ICML 2019.
- Krishna et al. — *The Disagreement Problem in Explainable Machine Learning*, 2022.
- Hedström et al. — *Quantus: An Explainable AI Toolkit for Responsible Evaluation*, JMLR 2023.

## 10.10 Lab (2 hrs)

1. Take last week's saliency methods.
2. Compute deletion AUC and insertion AUC for each.
3. Run Adebayo's model randomization sanity check.
4. Use Quantus to compute Infidelity & Stability.
5. Tabulate results across methods. Which is most faithful? Which is most stable?

## 10.11 Quiz

1. Why is deletion AUC a faithfulness metric but not a plausibility metric?
2. State the ROAR procedure and what it adds over simple deletion.
3. What did Slack et al. demonstrate, and what does it imply for compliance?
4. Define comprehensiveness and sufficiency from ERASER.
5. Why is the disagreement problem dangerous in regulated industries?
