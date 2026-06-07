# Master Syllabus — Blockchain + Explainable AI (18 Weeks)

## Learning objectives

By the end of this course you will:
1. **Theory** — Explain consensus, cryptographic commitments, smart contracts, attribution methods, and mechanistic interpretability rigorously.
2. **Implementation** — Build small versions of each system: a toy blockchain, a smart contract dApp, a SHAP/LIME implementation, a saliency pipeline, a zk-SNARK circuit.
3. **Research literacy** — Read papers from S&P, CCS, USENIX, NeurIPS, ICML, FAccT, and write critique notes.
4. **Original contribution** — Propose a publishable workshop-paper-scale research problem at the intersection of Verifiable AI and Explainability.

---

## Week-by-week plan

| Wk | Blockchain (8 hrs) | XAI (6 hrs) | Writing (1 hr) |
|----|--------------------|-------------|----------------|
| 1  | [Module 1: Cryptographic Foundations](blockchain/01_foundations.md) | [Module 1: What is Explainability?](xai/01_foundations.md) | Define your "why" |
| 2  | [Module 2: Distributed Systems & CAP](blockchain/02_distributed_systems.md) | [Module 2: Taxonomy of XAI](xai/02_taxonomy.md) | Read Molnar Ch 1–3 summary |
| 3  | [Module 3: Bitcoin Deep Dive](blockchain/03_bitcoin.md) | [Module 3: LIME & SHAP](xai/03_feature_attribution.md) | Reproduce Molnar's penguin example |
| 4  | [Module 4: Ethereum & Smart Contracts](blockchain/04_ethereum.md) | [Module 4: Gradient-based Attribution](xai/04_gradient_methods.md) | Side-by-side LIME vs SHAP |
| 5  | [Module 5: Consensus Algorithms](blockchain/05_consensus.md) | [Module 5: Concept-based (TCAV, ACE)](xai/05_concept_based.md) | Consensus comparison table |
| 6  | [Module 6: Scalability & L2](blockchain/06_scalability_layer2.md) | [Module 6: Counterfactual Explanations](xai/06_counterfactuals.md) | Compare rollup designs |
| 7  | [Module 7: Privacy & ZKPs](blockchain/07_privacy_zk.md) | [Module 7: Global Methods (PDP/ALE/Surrogate)](xai/07_global_methods.md) | First ZK circuit + writeup |
| 8  | [Module 8: DeFi Architecture](blockchain/08_defi.md) | [Module 8: Attention & Transformer Interp](xai/08_attention_transformers.md) | DeFi attack postmortem |
| 9  | [Module 9: Security & Attack Surface](blockchain/09_security_attacks.md) | [Module 9: Mechanistic Interpretability](xai/09_mechanistic_interpretability.md) | One attack reproduced |
| 10 | [Module 10: Governance & Tokenomics](blockchain/10_governance_tokenomics.md) | [Module 10: Evaluating Explanations](xai/10_evaluation_metrics.md) | Faithfulness benchmark |
| 11 | [Module 11: Advanced Consensus (DAG/HotStuff/Sharding)](blockchain/11_advanced_consensus.md) | [Module 11: Human-Centered XAI](xai/11_human_centered.md) | User study design |
| 12 | [Module 12: Research Frontiers](blockchain/12_research_frontiers.md) | [Module 12: XAI in Domains (Med/Finance/Law)](xai/12_applications.md) | Domain critique |
| 13 | — | [Module 13: XAI Research Frontiers](xai/13_research_frontiers.md) | Literature gap doc |
| 14 | [Intersection: Verifiable & Decentralized ML / ZKML](intersection/blockchain_xai_intersection.md) | (continue) | Joint reading list |
| 15 | Lab week — implement toy ZKML inference | Lab week — implement SHAP from scratch | Lab journal |
| 16 | Research proposal draft (3 pages) | Research proposal draft (3 pages) | Merge into one |
| 17 | Polish, related work, identify venue | Polish, related work, identify venue | 6-page workshop draft |
| 18 | Get feedback, iterate, submit to arXiv | — | Submission |

---

## Assessment artifacts (you produce these)

1. **Weekly summaries** (18 × 1–2 pages)
2. **12 module quizzes** — see end of each module file
3. **6 implementation labs** — see `labs/`
4. **1 critical literature review** (~10 pages)
5. **1 research proposal** (6-page workshop format)
6. **1 reproducibility report** for an existing paper (any XAI or blockchain paper)

---

## Prerequisites

- Linear algebra, probability, basic statistics
- Python (PyTorch helpful)
- Familiarity with at least one CS theory class (algorithms / complexity)
- For ZK section: comfort with abstract algebra (groups, fields) helps but is not strictly required

## Reading shelf (highly recommended)

| Title | Why |
|---|---|
| *Bitcoin and Cryptocurrency Technologies* — Narayanan et al. (Princeton) | Best free blockchain textbook |
| *Mastering Bitcoin* — Andreas Antonopoulos | Practical reference |
| *Mastering Ethereum* — Antonopoulos & Wood | Practical Ethereum |
| *Interpretable Machine Learning* — Christoph Molnar (free) | XAI canon |
| *Explanatory Model Analysis* — Biecek & Burzykowski | Tabular XAI |
| *The Mythical Man-Month* (yes, really) | Distributed systems intuition |
| *Anthropic Transformer Circuits Thread* (online) | Modern mech-interp |
| Distill.pub — Building Blocks of Interpretability | Visual intuition |

See [resources/papers.md](resources/papers.md), [resources/books.md](resources/books.md), [resources/courses.md](resources/courses.md), [resources/tools.md](resources/tools.md) for the full curated lists.
