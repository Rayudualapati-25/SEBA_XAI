# XAI Module 11 — Human-Centered XAI

> **Goal**: Understand explanations as a **human-computer interaction** problem. The best metric is "did the user understand and act correctly", not "does the heatmap look pretty".

---

## 11.1 The HCI turn

Until ~2018, XAI papers measured success by mathematical properties. Then a wave of HCI researchers (Miller, Hoffman, Mueller, Wang, Lakkaraju, Wattenberg, Viégas) shifted the question:

> *Do explanations actually help users make better decisions?*

The empirical answer is: **often, no**.

---

## 11.2 Miller (2019) — what explanation actually is

*Explanation in Artificial Intelligence: Insights from the Social Sciences* — Artificial Intelligence Journal.

Key findings from 250+ social-science papers on explanation:
1. **Explanations are contrastive** — people ask "why P rather than Q?" not "why P?"
2. **Explanations are selected** — humans don't want every cause, only the most relevant ones.
3. **Explanations are social** — they're a conversation, not a one-shot output.
4. **Probabilities don't help much** — people want causal stories.
5. **People are biased** — they prefer simple, plausible, generalizable explanations even when those are wrong.

**Implication**: faithful, complete explanations may actively confuse users. Good XAI is selection + framing, not raw attribution dumps.

---

## 11.3 Cognitive load & explanation overload

Studies (Bansal et al. 2021, Poursabzi-Sangdeh et al. 2021):
- Showing more features = more confusion.
- Numerical attributions (SHAP values) are misread by non-experts.
- Highlighting *one* feature outperforms showing all features.

**Best practice**: limit to top-3 to top-5 features for non-expert users. Use plain-language framing ("This loan was likely denied because of low income and short credit history").

---

## 11.4 Trust calibration

The goal of an explanation is not "more trust" — it is **appropriately calibrated trust**.

- **Over-reliance** — user trusts wrong answers because the explanation looked convincing.
- **Under-reliance** — user ignores correct answers because of vague unease.

Vasconcelos et al. (CSCW 2022): explanations often **increase reliance regardless of model correctness** — a problem.

Bussone, Stumpf, O'Sullivan (2015) — even nonsensical explanations can increase trust ("automation bias").

---

## 11.5 Anchoring & confirmation effects

When an explanation aligns with the user's prior, they adopt the model's prediction. When it contradicts, they often dismiss the model. This is **anchoring**, not understanding.

Mitigation: present alternative hypotheses, not single explanations.

---

## 11.6 The "AI-assisted decision-making" framing

Modern HCI–XAI research treats the unit of analysis as the **human-AI team**, not the model alone.

Key questions:
- When should AI defer to humans?
- When should AI override?
- How should AI communicate uncertainty?
- How do we design explanations that improve *team* accuracy, not just model accuracy?

Read: Bansal et al., *"Does the Whole Exceed its Parts?"* (CHI 2021).

---

## 11.7 Explanation interfaces

| Form | Example product |
|---|---|
| Local feature highlight | Loan denial reasons |
| Counterfactual ("if X were different") | Credit improvement coach |
| Conversational | LLM-grounded "Why did you say that?" |
| Visualization (PDP, heatmap) | Model debugging dashboards |
| Concept-based | Medical imaging tools |
| Prototype / example | Recommender "because you liked X" |

The *form* should match the user's mental model. A radiologist wants concepts; a borrower wants counterfactuals.

---

## 11.8 Designing a user study for XAI

A minimal protocol:

1. **Task**: real domain task (e.g., loan approval).
2. **Conditions**: no AI / AI-only / AI + explanation type 1 / type 2 / ...
3. **Metrics**: accuracy, time, calibration, trust survey, NASA-TLX (workload).
4. **Participants**: ≥30 per condition; domain experts when possible.
5. **Pre-register** hypotheses and analysis plan.
6. **Report** effect sizes, not just p-values.

Most XAI papers skip the user study. The ones that include one tend to overturn the assumption that the "better" explanation is more useful.

---

## 11.9 Fairness, accountability, transparency (FAccT)

XAI and fairness intersect but are not the same.

- An explanation may *reveal* unfairness (e.g., heavy weight on a proxy for race).
- An explanation can also *launder* unfairness (Aïvodji 2019, *fairwashing*).

For fairness, use dedicated tools (Fairlearn, AI Fairness 360, Aequitas) **alongside** XAI.

---

## 11.10 LLM explanations and "self-explanations"

LLMs can produce natural-language rationales. Beware:

- **Hallucinated rationales** — Turpin et al. (2023) showed CoT explanations can be unfaithful — the model decided early, then rationalized.
- **Sycophancy** — model gives the user the explanation they want.
- **Plausible-sounding mistakes** — the very fluency makes errors more dangerous.

Best practice: verify with non-LLM methods (probes, SAEs, citation-grounded outputs).

---

## 11.11 Reading list

- Miller — *Explanation in Artificial Intelligence: Insights from the Social Sciences*, AI Journal 2019.
- Hoffman, Mueller, Klein, Litman — *Metrics for Explainable AI: Challenges and Prospects*, 2018.
- Poursabzi-Sangdeh et al. — *Manipulating and Measuring Model Interpretability*, CHI 2021.
- Bansal et al. — *Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance*, CHI 2021.
- Vasconcelos et al. — *Explanations Can Reduce Overreliance on AI Systems During Decision-Making*, CSCW 2022.
- Bussone et al. — *The Role of Explanations on Trust and Reliance in Clinical Decision Support Systems*, ICHI 2015.
- Turpin et al. — *Language Models Don't Always Say What They Think*, NeurIPS 2023.
- ACM FAccT proceedings — annual.

## 11.12 Lab (2 hrs)

1. Pick a tabular classifier you trained earlier.
2. Design a 3-condition user study (no-explanation / SHAP / counterfactual).
3. Recruit 6 friends; have each make 20 decisions in each condition.
4. Measure accuracy, time, self-reported confidence.
5. Write a 1-page reflection on what you'd improve.

## 11.13 Quiz

1. State Miller's four key findings about how humans explain.
2. What is over-reliance and how can XAI cause it?
3. Why might counterfactual explanations be more actionable than SHAP for an end user?
4. What did Turpin et al. show about CoT explanations?
5. Why is faithfulness without plausibility insufficient for end-user XAI?
