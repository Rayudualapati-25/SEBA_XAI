"""
Build study-notes PDFs organised by syllabus units.

Outputs:
  - FINAL_Blockchain_Notes.pdf
  - FINAL_XAI_Notes.pdf

Structure of each notes document:
  1. SRM-style cover page
  2. Table of Contents (auto, from markdown headings)
  3. Five Unit dividers, each followed by the relevant module markdown content.
"""
from __future__ import annotations
from pathlib import Path
from markdown_pdf import MarkdownPdf, Section

ROOT = Path(__file__).resolve().parent

# CSS reused for all notes pages (everything *except* the cover).
CSS_BODY = """
body { font-family: 'Times New Roman', Times, serif; font-size: 11pt;
       line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 20pt; color: #0b3a66; border-bottom: 2px solid #0b3a66;
     padding-bottom: 4px; margin-top: 0.4em; }
h2 { font-size: 14pt; color: #0b3a66; margin-top: 1.2em; }
h3 { font-size: 12pt; color: #244; margin-top: 1.0em; }
h4 { font-size: 11pt; color: #244; margin-top: 0.8em; }
p, li { font-size: 10.5pt; }
code { font-family: 'Courier New', Consolas, monospace; font-size: 9.5pt;
       background: #f4f5f7; padding: 1px 4px; border-radius: 3px; }
pre  { background: #f4f5f7; padding: 10px; border-radius: 6px;
       overflow-x: auto; font-size: 9pt; line-height: 1.35; }
pre code { background: transparent; padding: 0; }
table { border-collapse: collapse; margin: 0.5em 0; font-size: 9.5pt; width: 100%; }
th, td { border: 1px solid #cdd5df; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #eef2f6; }
blockquote { border-left: 4px solid #0b3a66; margin-left: 0; padding-left: 12px;
             color: #444; font-style: italic; }
hr { border: none; border-top: 1px solid #cdd5df; margin: 1.5em 0; }
"""

# CSS used only for the cover page.
CSS_COVER = """
body { font-family: 'Times New Roman', Times, serif; color: #1a1a1a; text-align: center; }
h1 { font-size: 16pt; margin-bottom: 0; margin-top: 60px; }
h2 { font-size: 13pt; font-weight: normal; margin-top: 4px; color: #333; }
h3 { font-size: 22pt; color: #0b3a66; margin-top: 80px; }
h4 { font-size: 14pt; font-style: italic; color: #444; margin-top: 8px; }
hr { border: none; border-top: 1.5px solid #0b3a66; width: 60%; margin: 28px auto; }
p { font-size: 12pt; margin-top: 60px; }
.meta { font-size: 11pt; margin-top: 4px; }
.code { font-size: 10.5pt; color: #555; margin-top: 80px; }
"""

# CSS for the unit divider (intermediate title page)
CSS_DIVIDER = """
body { font-family: 'Times New Roman', Times, serif; color: #1a1a1a; text-align: center; }
h1 { font-size: 14pt; color: #555; margin-top: 80px; }
h2 { font-size: 28pt; color: #0b3a66; margin-top: 18px; }
h3 { font-size: 16pt; font-weight: normal; color: #333; margin-top: 12px; }
p  { font-size: 11pt; margin-top: 40px; max-width: 500px; margin-left: auto; margin-right: auto; text-align: justify; }
.hours { font-size: 12pt; color: #777; margin-top: 6px; }
.topics { font-size: 10.5pt; color: #333; margin-top: 30px; text-align: left;
          max-width: 520px; margin-left: auto; margin-right: auto; line-height: 1.7; }
"""


def read_md(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def cover_md(course_name: str, code: str) -> str:
    return f"""# SRM University – AP, Andhra Pradesh

## Neeru Konda, Mangalagiri Mandal, Guntur District – 522240

---

### {course_name}

#### Comprehensive Study Notes

<hr/>

<p><b>Course Code:</b> {code}</p>
<p class="meta"><b>Course Category:</b> Core Elective (CW)</p>
<p class="meta"><b>L – T – P – C:</b> 3 – 0 – 0 – 3</p>
<p class="meta"><b>Department:</b> Computer Science and Engineering</p>

<p class="code"><b>Compiled for:</b> Venkat Rayudu Alapati (AP25122040029)</p>
<p class="meta"><b>Programme:</b> M.Tech (AI &amp; ML)</p>
<p class="meta"><b>Academic Year:</b> 2025 – 2026</p>
"""


def divider_md(unit_no: int, unit_title: str, hours: int, topics: list[str]) -> str:
    topic_html = "<br/>".join(f"&bull; {t}" for t in topics)
    return f"""# Unit {unit_no}

## {unit_title}

<p class="hours">Required Contact Hours: <b>{hours}</b></p>

<div class="topics">{topic_html}</div>

<p>The chapters that follow expand each topic above with theory, worked examples, reading lists, hands-on lab guidance, and end-of-chapter self-assessment questions.</p>
"""


# ----------------------------------------------------------------------------
# COURSE STRUCTURES (must match the syllabus PDFs)
# ----------------------------------------------------------------------------
BLOCKCHAIN = dict(
    name="Blockchain Technologies",
    code="AML 571",
    output="FINAL_Blockchain_Notes.pdf",
    units=[
        dict(
            no=1, title="Cryptographic Foundations and Distributed Systems", hours=9,
            topics=[
                "Introduction to Blockchain — What and Why",
                "Cryptographic hash functions (SHA-256, Keccak) and properties",
                "Merkle trees, Patricia tries, Verkle trees, KZG commitments",
                "Digital signatures: ECDSA, EdDSA, Schnorr, BLS",
                "Distributed systems: CAP/FLP, Byzantine Generals, 3f+1 bound",
            ],
            modules=["blockchain/01_foundations.md", "blockchain/02_distributed_systems.md"],
        ),
        dict(
            no=2, title="Bitcoin and Ethereum", hours=8,
            topics=[
                "Bitcoin — UTXO model, Script, Proof-of-Work",
                "Difficulty adjustment, halving, selfish mining, 51% attack",
                "Ethereum — Account model, EVM, Gas mechanics",
                "Solidity, ERC standards (ERC-20, ERC-721, ERC-4337)",
                "Lightning Network and payment channels",
            ],
            modules=["blockchain/03_bitcoin.md", "blockchain/04_ethereum.md"],
        ),
        dict(
            no=3, title="Consensus Algorithms", hours=7,
            topics=[
                "Proof-of-Work variants and tradeoffs",
                "Proof-of-Stake: Casper FFG, Tendermint, Ouroboros",
                "PBFT, HotStuff, pipelined 3-phase voting",
                "Algorand BA*, Avalanche Snowball, Solana PoH",
                "Slashing, nothing-at-stake, long-range attacks",
            ],
            modules=["blockchain/05_consensus.md"],
        ),
        dict(
            no=4, title="Scalability, Layer-2 and Zero-Knowledge Proofs", hours=9,
            topics=[
                "Scalability Trilemma, sharding, vertical vs horizontal scaling",
                "Optimistic Rollups — fraud proof bisection (Arbitrum, Optimism)",
                "ZK Rollups — zkSync, StarkNet, Polygon zkEVM",
                "Data availability — EIP-4844 blobs, Celestia, EigenDA",
                "ZKPs — SNARK vs STARK, Groth16, PLONK, Circom toolchain",
            ],
            modules=["blockchain/06_scalability_layer2.md", "blockchain/07_privacy_zk.md"],
        ),
        dict(
            no=5, title="DeFi, Security, Governance and Research Frontiers", hours=12,
            topics=[
                "DeFi — Stablecoins, AMMs, lending markets, oracles",
                "Flash loans and MEV (sandwich, arbitrage, PBS)",
                "Smart contract security — Reentrancy, access control, postmortems",
                "Governance and tokenomics — DAOs, veTokens, EigenLayer",
                "Advanced consensus — DAGs, HotStuff lineage, restaking",
                "Research frontiers — zkML, zkVMs, folding schemes, modular blockchains",
            ],
            modules=[
                "blockchain/08_defi.md",
                "blockchain/09_security_attacks.md",
                "blockchain/10_governance_tokenomics.md",
                "blockchain/11_advanced_consensus.md",
                "blockchain/12_research_frontiers.md",
            ],
        ),
    ],
    appendix_modules=["intersection/blockchain_xai_intersection.md"],
    appendix_title="Appendix A — Blockchain × XAI Research Intersection",
)


XAI = dict(
    name="Explainable Artificial Intelligence",
    code="AML 572",
    output="FINAL_XAI_Notes.pdf",
    units=[
        dict(
            no=1, title="Foundations and Taxonomy of XAI", hours=9,
            topics=[
                "What is Explainability — drivers (regulation, safety, science)",
                "Definitions — interpretability, transparency, simulatability",
                "Doshi-Velez/Kim evaluation framework",
                "Intrinsic models — Linear, GAM, EBM, decision trees",
                "Taxonomy — local/global, intrinsic/post-hoc, model-agnostic/specific",
            ],
            modules=["xai/01_foundations.md", "xai/02_taxonomy.md"],
        ),
        dict(
            no=2, title="Feature Attribution and Gradient-Based Methods", hours=8,
            topics=[
                "LIME — local linear surrogate via perturbation",
                "SHAP — Shapley values, KernelSHAP, TreeSHAP, DeepSHAP",
                "Anchors and Influence functions",
                "Gradient attribution — saliency, SmoothGrad, Integrated Gradients",
                "Grad-CAM, Grad-CAM++, Score-CAM",
            ],
            modules=["xai/03_feature_attribution.md", "xai/04_gradient_methods.md"],
        ),
        dict(
            no=3, title="Concept-Based, Counterfactual and Global Methods", hours=7,
            topics=[
                "TCAV, ACE, CRAFT, Network Dissection",
                "Concept Bottleneck Models, ProtoPNet",
                "Counterfactual explanations — Wachter, DiCE, FACE",
                "Algorithmic recourse and contrastive explanations",
                "Global methods — PDP, ICE, ALE, surrogates, ANOVA",
            ],
            modules=["xai/05_concept_based.md", "xai/06_counterfactuals.md", "xai/07_global_methods.md"],
        ),
        dict(
            no=4, title="Attention, Transformer and Mechanistic Interpretability", hours=9,
            topics=[
                "Attention Is (Not) Explanation debate",
                "Attention Rollout, Flow, Chefer et al.",
                "Probing classifiers, Logit Lens, Tuned Lens",
                "Distill Circuits, Mathematical Framework for Transformer Circuits",
                "Induction heads, IOI circuit, ROME knowledge editing",
                "Sparse Autoencoders, monosemanticity, ACDC",
            ],
            modules=["xai/08_attention_transformers.md", "xai/09_mechanistic_interpretability.md"],
        ),
        dict(
            no=5, title="Evaluation, Human-Centered XAI, Applications and Frontiers", hours=12,
            topics=[
                "Faithfulness, Plausibility, Robustness; Deletion AUC, ROAR",
                "Sanity checks (Adebayo), Quantus, ERASER",
                "Adversarial XAI, Fairwashing, Disagreement problem",
                "Human-Centered XAI — Miller, trust calibration",
                "Medical, Financial, Legal XAI; LLM citation grounding",
                "Research frontiers — SAEs at scale, ZKML, Causal XAI",
            ],
            modules=[
                "xai/10_evaluation_metrics.md",
                "xai/11_human_centered.md",
                "xai/12_applications.md",
                "xai/13_research_frontiers.md",
            ],
        ),
    ],
    appendix_modules=["intersection/blockchain_xai_intersection.md"],
    appendix_title="Appendix A — XAI × Blockchain Research Intersection",
)


# ----------------------------------------------------------------------------
# Builder
# ----------------------------------------------------------------------------
def build(course: dict) -> None:
    out = ROOT / course["output"]
    pdf = MarkdownPdf(toc_level=3)
    pdf.meta["title"] = f"{course['name']} — Study Notes"
    pdf.meta["author"] = "Venkat Rayudu Alapati"
    pdf.meta["subject"] = course["name"]

    # Cover
    pdf.add_section(
        Section(cover_md(course["name"], course["code"]), toc=False, paper_size="A4"),
        user_css=CSS_COVER,
    )

    # Units
    for unit in course["units"]:
        # Divider
        div = divider_md(unit["no"], unit["title"], unit["hours"], unit["topics"])
        pdf.add_section(Section(div, toc=False, paper_size="A4"), user_css=CSS_DIVIDER)

        # Module content
        for mod_path in unit["modules"]:
            text = read_md(ROOT / mod_path)
            # downshift main heading by prefixing unit context comment
            pdf.add_section(Section(text, paper_size="A4"), user_css=CSS_BODY)

    # Appendix (intersection module)
    if course.get("appendix_modules"):
        appx_divider = f"""# Appendix

## {course["appendix_title"]}

<p>The chapter that follows links this subject to its sister discipline, surveying the small but active research area where the two converge.</p>
"""
        pdf.add_section(Section(appx_divider, toc=False, paper_size="A4"),
                        user_css=CSS_DIVIDER)
        for mod_path in course["appendix_modules"]:
            text = read_md(ROOT / mod_path)
            pdf.add_section(Section(text, paper_size="A4"), user_css=CSS_BODY)

    pdf.save(str(out))
    print(f"wrote {out}  ({out.stat().st_size/1024:.1f} KB)")


def main() -> None:
    build(BLOCKCHAIN)
    build(XAI)


if __name__ == "__main__":
    main()
