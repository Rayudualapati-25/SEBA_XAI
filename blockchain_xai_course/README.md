# Blockchain + Explainable AI — Research-Grade Self-Study Course

A complete, research-oriented syllabus and notes covering Blockchain and Explainable AI (XAI), designed for a Master's / early-PhD student aiming to publish at top venues (NeurIPS, ICML, IEEE S&P, CCS, USENIX Security, FAccT, AAAI, IJCAI, IEEE Blockchain).

The course is distilled from the strongest publicly available curricula:

**Blockchain sources synthesized**
- Princeton — *Bitcoin and Cryptocurrency Technologies* (Narayanan, Bonneau, Felten, Miller, Goldfeder)
- MIT 15.S08 — *Blockchain and Money* (Gary Gensler)
- Berkeley CS294-164 — *Blockchain Technology*
- Stanford CS251 — *Cryptocurrencies and Blockchain Technologies* (Dan Boneh)
- Coursera — *Blockchain Specialization* (University at Buffalo)
- ConsenSys Academy / Ethereum Foundation EthCore curriculum
- a16z Crypto Startup School
- Zero Knowledge Proof MOOC (Boneh, Goldberg, Wahby)

**XAI sources synthesized**
- Christoph Molnar — *Interpretable Machine Learning* (the canonical reference)
- Kaggle — *Machine Learning Explainability* micro-course
- DeepLearning.AI — *AI Explainability* short courses
- DARPA XAI Program reports (2017–2021)
- Harvard CS282BR — *Topics in Interpretability*
- Stanford CS329T — *Trustworthy Machine Learning*
- CMU 10-718 — *Machine Learning in Practice* (interpretability modules)
- Anthropic / OpenAI / DeepMind mechanistic interpretability work
- Distill.pub Circuits Thread

---

## How to use this course

1. **Read the master [SYLLABUS](SYLLABUS.md)** — 18-week dual-track plan.
2. **For this repository's implementation, read [SEBA_XAI_PROTOTYPE_SYLLABUS.md](SEBA_XAI_PROTOTYPE_SYLLABUS.md)** — file-by-file learning plan for the actual prototype.
3. **For a compact 5-unit course version, read [SEBA_XAI_Prototype_5_Unit_Syllabus.md](SEBA_XAI_Prototype_5_Unit_Syllabus.md)** or the exported PDF `SEBA_XAI_Prototype_5_Unit_Syllabus.pdf`.
4. **Two parallel tracks**: 12 Blockchain modules, 13 XAI modules, plus a converged "Verifiable AI / ZKML" module.
5. **Per-module structure**: theory notes → key papers → guided lab → research questions.
6. **End every week** with a written research-style summary (1–2 pages) — this is how you build publishable intuitions.

## Directory layout

```
blockchain_xai_course/
├── README.md                # This file
├── SYLLABUS.md              # 18-week structured plan
├── SEBA_XAI_PROTOTYPE_SYLLABUS.md # Implementation-specific prototype syllabus
├── SEBA_XAI_Prototype_5_Unit_Syllabus.md # Compact 5-unit prototype syllabus
├── SEBA_XAI_Prototype_5_Unit_Syllabus.pdf # Exported 5-unit syllabus PDF
├── blockchain/              # 12 modules — foundations to research frontier
├── xai/                     # 13 modules — feature attribution to mech-interp
├── intersection/            # ZKML, on-chain ML, verifiable AI
├── resources/               # Papers, books, courses, tools
└── labs/                    # Hands-on coding labs
```

## Suggested cadence

- **15 hrs/week**: 8 hrs blockchain, 6 hrs XAI, 1 hr writing summary.
- **Full immersion**: complete in 12 weeks at 30 hrs/week (matches a focused research sprint).
- **Casual**: 6 months at 6 hrs/week.

## Research output target

By the end you should be able to:
- Implement a working consensus protocol, a smart contract system, and a basic zk circuit.
- Reproduce LIME, SHAP, Integrated Gradients, GradCAM, TCAV, and a counterfactual generator from scratch.
- Identify a tractable open problem in **Verifiable / Explainable / Decentralized ML** and write a 6-page workshop paper draft.

---

Date created: 2026-05-23. Maintained as a living document.
