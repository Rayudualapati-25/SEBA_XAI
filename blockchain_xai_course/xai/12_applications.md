# XAI Module 12 — XAI in Domains: Medical, Finance, Law, NLP

> **Goal**: Translate generic XAI methods into domain-specific value (and risk).

---

## 12.1 Medical XAI

### Why it matters
- High-stakes decisions
- Clinicians need to validate model reasoning before acting
- Regulatory: FDA SaMD, EU MDR, India CDSCO classify ML-based devices

### Common methods by modality

| Modality | XAI methods |
|---|---|
| Radiology (CXR, CT, MRI) | Grad-CAM, LRP, ProtoPNet, BagNet |
| Pathology (WSI) | Attention-MIL highlights, concept-based |
| EHR / tabular | SHAP, EBM, GAM |
| Genomics | DeepLIFT, IG with biological priors |
| Clinical NLP | Rationale-based, Anchors, IG on tokens |

### Pitfalls
- **Shortcut learning** — model uses scanner artifacts, image markers, hospital tags (DeGrave et al. 2021 on COVID-19 CXR models).
- **Saliency ≠ diagnosis** — heatmap on lung doesn't mean "consolidation"; could be "rib".
- **Concept misalignment** — concepts defined by ML researchers may not match clinical vocabulary.

### Best practices
- Always include an **out-of-distribution test** with a different hospital / scanner.
- Combine pixel attribution with **concept-based** (TCAV, ProtoPNet) for clinical translation.
- Report calibration alongside performance.
- Engage clinicians in evaluation (DECIDE-AI, CONSORT-AI reporting standards).

### Key papers
- Caruana et al. — *Intelligible Models for HealthCare*, KDD 2015 (pneumonia EHR example, "asthma is protective" finding — classic shortcut).
- DeGrave, Janizek, Lee — *AI for radiographic COVID-19 detection selects shortcuts over signal*, Nature MI 2021.
- Rajpurkar et al. — CheXpert, CheXNet papers.
- Tonekaboni et al. — *What Clinicians Want: Contextualizing Explainable Machine Learning for Clinical End Use*, MLHC 2019.

---

## 12.2 Financial XAI

### Why it matters
- Credit decisions are regulated (US ECOA / Fair Lending; EU AI Act high-risk; India RBI guidelines).
- Adverse-action notices legally require reasons.
- Algorithmic trading needs post-mortem analysis.

### Common methods
- **SHAP** (industry standard for tabular credit models)
- **Counterfactuals / DiCE** for adverse-action / recourse
- **PDP / ALE** for model debugging
- **EBM** (Microsoft InterpretML) as a credit-modeling baseline
- **Fairness toolkits**: Aequitas, Fairlearn

### Pitfalls
- **Proxy features** for protected attributes (zipcode → race).
- **Disparate impact** invisible in SHAP rankings.
- **Adversarial robustness** — gaming the model is profitable.
- **Distribution shift** — credit models built pre-COVID failed badly during the pandemic.

### Regulatory landscape (2026)
- US: CFPB / OCC enforce model risk management (SR 11-7).
- EU: AI Act — credit scoring is "high risk", requires logging, explanation, human oversight.
- India: RBI guidelines on AI/ML in financial services.

---

## 12.3 Legal XAI

### Use cases
- Predictive policing (controversial)
- Recidivism prediction (COMPAS)
- Bail / sentencing risk scores
- Judicial decision prediction (academic, not deployed)

### Cautions
- ProPublica 2016 — *Machine Bias* — found COMPAS racially biased. Northpointe disputed. Sparked the **fair prediction debate** (Chouldechova 2017, Kleinberg et al. 2016: impossibility theorem — you can't satisfy multiple fairness criteria simultaneously).
- Rudin (2019) — explicit case for interpretable risk scores over black-box ones in criminal justice.

### Best practice
- Use **transparent risk scores** (e.g., 2HELPS2B-style integer-coefficient models).
- Document features, weights, and provenance.
- Audit subgroup performance.

---

## 12.4 NLP / LLM XAI

### Methods
- Saliency / IG over tokens
- Attention rollout, Chefer-style attribution
- Rationale extraction (ERASER benchmark)
- Influence functions, Datamodels
- Mechanistic interpretability (SAEs, circuits)
- Citation grounding (RAG attribution)

### Hot 2024–2026 topics
- **Citation-grounded LLM outputs** (Anthropic Claude Citations, Perplexity sources, OpenAI references)
- **Hallucination detection** via self-consistency, SAE features
- **Sycophancy explanations**
- **Steering vectors / activation engineering** as interpretability + control
- **Constitutional AI / RLHF interpretability**

### Open problems
- Faithfulness of natural-language self-explanations (Turpin et al. 2023).
- Cross-lingual interpretability.
- Tool-use explanation in agentic LLMs.

---

## 12.5 Computer vision in industry

| Application | XAI need |
|---|---|
| Autonomous driving | Debug failure modes; counterfactual scenes |
| Manufacturing defect detection | Validate spurious cues |
| Retail (cashierless) | Audit demographic disparity |
| Satellite imagery / agriculture | Concept-based features |

---

## 12.6 Recommender systems

- Show *why* an item was recommended ("Because you watched X").
- Inverse / counterfactual recommendations.
- Methods: PIRL (Persuasive Interpretable Recommendation), counterfactual recommender literature.

---

## 12.7 Education

- Adaptive learning systems: explain *why* a concept was recommended.
- AI tutors: rationale-based explanations of answers.
- Diagnostic models for student misconceptions.

---

## 12.8 Cybersecurity

- Anomaly detection systems should justify flagged events.
- SHAP/LIME over network features.
- Adversarial-aware explanation (the system being attacked also attacks the explanation).

---

## 12.9 Climate / scientific ML

- ML on climate models: which features drive forecast?
- Physics-informed XAI (Toms et al. 2020).
- Concept-aligned attribution for scientific reasoning.

---

## 12.10 Domain-XAI checklist (universal)

For any deployment:
- [ ] Stakeholder identified
- [ ] Explanation format matched to stakeholder
- [ ] Faithfulness validated
- [ ] Fairness audit performed independently
- [ ] Shortcut/spurious correlation test passed
- [ ] OOD performance characterized
- [ ] User-facing language tested with domain experts
- [ ] Logging + audit trail in place

---

## 12.11 Reading list

- Caruana et al. — *Intelligible Models for HealthCare*, KDD 2015.
- DeGrave, Janizek, Lee — *AI for radiographic COVID-19 detection selects shortcuts*, Nature MI 2021.
- Tonekaboni et al. — *What Clinicians Want*, MLHC 2019.
- Bhatt et al. — *Explainable Machine Learning in Deployment*, FAccT 2020.
- Chouldechova — *Fair Prediction with Disparate Impact*, FAT* 2017.
- Kleinberg, Mullainathan, Raghavan — *Inherent Trade-Offs in the Fair Determination of Risk Scores*, 2016.
- Rudin et al. — *Interpretable Machine Learning: Fundamental Principles and 10 Grand Challenges*, Stat Sci 2022.
- Turpin et al. — *Language Models Don't Always Say What They Think*, NeurIPS 2023.

## 12.12 Lab (3 hrs)

Pick *one* domain:
- Build a small model (e.g., MIMIC-III mortality / German Credit / IMDB sentiment).
- Apply 2 XAI methods.
- Critique results against domain norms.
- Write a 2-page "would you deploy?" memo.

## 12.13 Quiz

1. Why did the COMPAS debate produce an impossibility theorem?
2. What was Caruana's "asthma is protective" finding and what does it teach?
3. Why are concept-based methods better than saliency for clinician communication?
4. Name two ways shortcut learning shows up in medical imaging.
5. Why might LLM self-explanations be unfaithful?
