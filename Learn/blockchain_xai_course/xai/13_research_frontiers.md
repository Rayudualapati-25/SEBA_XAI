# XAI Module 13 — Research Frontiers (2025–2027)

> **Goal**: Identify the active research clusters and where a Master's student can make a tractable contribution.

---

## 13.1 The XAI research map (2026)

```
                ┌────────────────────────────────────────┐
                │   MECHANISTIC INTERPRETABILITY (LLMs)   │
                │  SAEs · Circuits · Probing · Steering  │
                └────────────────────────────────────────┘
   ┌──────────────────────────┐   ┌──────────────────────────────┐
   │ CAUSAL & COUNTERFACTUAL  │   │   EVALUATION & BENCHMARKING  │
   │  Algorithmic recourse    │   │  Quantus · ERASER · OpenXAI  │
   │  Causal abstractions     │   │  Adversarial XAI · disagree. │
   └──────────────────────────┘   └──────────────────────────────┘
   ┌──────────────────────────┐   ┌──────────────────────────────┐
   │  HUMAN-AI INTERACTION    │   │  DOMAIN: MED / FIN / LAW     │
   │  Calibrated trust        │   │  Clinical translation        │
   │  Team performance        │   │  Fairwashing                 │
   └──────────────────────────┘   └──────────────────────────────┘
   ┌──────────────────────────────────────────────────────────────┐
   │  EMERGING: ZKML · VERIFIABLE EXPLANATIONS · DECENTRALIZED ML │
   └──────────────────────────────────────────────────────────────┘
```

---

## 13.2 Hot subareas

### 1. Mechanistic interpretability at scale
- SAEs on 100B+ parameter models.
- Automated circuit discovery (ACDC, EAP-IG).
- Cross-model universality of circuits.
- Practical alignment use cases (deception, jailbreak detection).

### 2. Faithful CoT and chain-of-thought interpretability
- Turpin et al. showed CoT may be unfaithful.
- Open: how to *train* models with faithful reasoning?
- Process supervision (Lightman et al. 2023 OpenAI) is a partial answer.

### 3. Multimodal & agent interpretability
- VLMs (CLIP, BLIP, Gemini): cross-modal feature attribution.
- LLM agents: explaining tool-use sequences.
- Reward model interpretability (what does the RLHF reward model actually reward?).

### 4. Causal XAI
- Counterfactuals with causal graphs.
- Algorithmic recourse under uncertain causal knowledge.
- Causal discovery from observational data + XAI integration.

### 5. Adversarial XAI
- Robust explanations that survive adversarial perturbations.
- Detecting fairwashing.
- "Honest" model architectures that can't lie to explainers.

### 6. XAI for foundation models / diffusion models
- Interpreting CLIP-like models.
- Concept activation for image generation control.
- Diffusion model interpretability via score landscapes.

### 7. Probing and feature discovery
- Sparse probing.
- Linear representation hypothesis tests.
- Geometry of representations (Park et al. 2023, *Linear Representation Hypothesis*).

### 8. Memorization vs generalization
- Influence functions at scale (Datamodels, TRAK).
- Membership inference and unlearning explanations.

### 9. Evaluation crisis
- Most explanation methods evaluated on toy benchmarks.
- Need standardized, application-grounded evals.
- Quantus, OpenXAI lead this.

### 10. XAI + Privacy
- Differentially-private explanations.
- ZK-proven explanations (ZK + XAI).

### 11. XAI + Fairness
- Explanations as fairness audits.
- Fairwashing detection.
- Subgroup-aware explanations.

### 12. Verifiable / On-Chain ML (zkML)
- Prove inference was correct + model unchanged.
- See [Intersection module](../intersection/blockchain_xai_intersection.md).

---

## 13.3 Tractable Master's-thesis-scale topics

| Topic | Why tractable |
|---|---|
| Empirical disagreement study on a new domain (legal text, audio) | Reuse existing tools |
| SAE feature analysis on a specific small model | TransformerLens makes setup fast |
| User study comparing 2 explanation forms on a real task | High novelty, modest infrastructure |
| Counterfactual quality for credit data under causal constraints | Data is available, methods extant |
| Reproducibility study of 5 saliency methods | Always publishable as a workshop paper |
| zkML proof of a tiny network's inference + interpretability | Crossroads area, sparse competition |

---

## 13.4 Venues for XAI research

| Venue | Type |
|---|---|
| **NeurIPS, ICML, ICLR** | Tier-1 ML |
| **AAAI, IJCAI** | Broader AI |
| **ACL, EMNLP, NAACL** | NLP, XAI for language |
| **CVPR, ICCV, ECCV** | Vision XAI |
| **FAccT** | Fairness, accountability, transparency |
| **CHI, CSCW, UIST** | HCI, user studies |
| **AIES** (AAAI/ACM) | AI ethics |
| **MLHC** | Healthcare ML |
| **JMLR, Nature MI, Distill (defunct but archive)** | Journals |

For first papers: **XAI4CV, Re-XAI, BlackBoxNLP** workshops are friendly entry points.

---

## 13.5 How to identify a good open problem (workflow)

1. Pick a frontier (e.g., faithful CoT).
2. Read the 10 most-cited papers in that area from the past 2 years.
3. Tabulate **claims**, **assumptions**, **limitations** of each.
4. Find:
   - A claim with weak empirical support → reproduce + extend.
   - An assumption no one tested → test it.
   - A limitation that has a small-scope fix.
5. Run a 2-week pilot. If it works, commit to a 3-month project.

---

## 13.6 Reading list — recent must-reads

- Bricken et al. — *Towards Monosemanticity*, Anthropic 2023.
- Templeton et al. — *Scaling Monosemanticity*, Anthropic 2024.
- Conmy et al. — *Automated Circuit Discovery (ACDC)*, NeurIPS 2023.
- Turpin et al. — *Language Models Don't Always Say What They Think*, NeurIPS 2023.
- Krishna et al. — *The Disagreement Problem in Explainable ML*, 2022.
- Rudin et al. — *Interpretable ML: Fundamental Principles and 10 Grand Challenges*, Statistical Science 2022.
- Park et al. — *The Linear Representation Hypothesis and the Geometry of Large Language Models*, 2023.
- Marks et al. — *Sparse Feature Circuits*, 2024.
- Karimi et al. — *A Survey of Algorithmic Recourse*, ACM CSUR 2022.

## 13.7 Lab / capstone

Pick **one**:
- Apply Sparse Autoencoders to Pythia-160M on a custom domain (e.g., medical text). Browse and document 50 interesting features.
- Empirical disagreement study: 6 methods × 4 datasets × 3 model classes. Quantify disagreement.
- User study: 30 participants, 2 explanation conditions, 1 domain task. Pre-register.
- Reproduce ACDC's IOI circuit; extend to a different prompt template.

## 13.8 Quiz

1. Name three SAE-related results from 2023–2024.
2. Why is faithful CoT an unsolved problem?
3. Define "linear representation hypothesis" in one sentence.
4. What makes algorithmic recourse harder than counterfactual explanation?
5. Pick one workshop venue you'd target with a first paper, and justify the fit.
