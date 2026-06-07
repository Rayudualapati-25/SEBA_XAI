from __future__ import annotations

import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_documents"
SEPARATE = OUT / "separate_documents"
COMBINED = OUT / "ALL_RESEARCH_DOCUMENTS.md"
INDEX = OUT / "README.md"


DOCUMENTS = [
    {
        "title": "Research Overview and Problem Understanding",
        "files": ["README.md", "research_brief.md", "00_problem_understanding.md"],
        "about": "This document explains the research problem, the Indian CCTNS/ICJS context, and the reason for choosing a secure explainable blockchain-audited overlay instead of a CCTNS replacement.",
        "intro": "I started this research by first understanding the actual public-safety problem. The important point is that India already has CCTNS and ICJS-style infrastructure, so the research should not be framed as replacing existing systems. The useful research direction is to design an intelligent secure overlay for auditable access governance.",
        "conclusion": "The problem is strongest when it is framed as access governance for sensitive police and criminal-justice records. This keeps the research practical and avoids weak claims about replacing national systems or predicting individual crime.",
    },
    {
        "title": "Literature Review and Evidence Base",
        "files": ["01_literature_review.md", "sources/literature_matrix.md", "sources/source_log.md"],
        "about": "This document reviews the major research themes: Indian digital policing infrastructure, blockchain evidence systems, access control, privacy, XAI, and high-stakes criminal-justice AI.",
        "intro": "This review was prepared to understand what is already published and where my research can still contribute. The review is intentionally strict because a good research paper cannot be built only from attractive keywords like blockchain, security, and XAI.",
        "conclusion": "The literature shows that many components already exist separately. The research gap is in combining them into a reproducible police access-governance workflow with blockchain audit, ABAC/PBAC security, and XAI explanation artifacts.",
    },
    {
        "title": "Dataset Discovery and Suitability Study",
        "files": ["03_datasets.md", "sources/dataset_inventory.md"],
        "about": "This document studies India-specific and global datasets that may support crime analytics, access-control simulation, security testing, and XAI experimentation.",
        "intro": "The dataset study is important because the paper must not make claims that the data cannot support. Public Indian crime datasets are useful, but they are mostly aggregate and reported-case based. They cannot support individual suspect prediction.",
        "conclusion": "The most suitable core dataset approach is a reproducible synthetic multi-station access-control workload, supported by NCRB/BPRD data only for aggregate context and optional trend analysis.",
    },
    {
        "title": "Research Gap and Novelty Formulation",
        "files": ["05_research_gap.md"],
        "about": "This document identifies weak research angles to reject and defines the narrow publishable gap for SEBA-XAI.",
        "intro": "This document was written like a supervisor check. I used it to separate attractive but weak ideas from a research problem that can actually be implemented and evaluated.",
        "conclusion": "The strongest novelty is not blockchain alone or crime prediction alone. The novelty is a measurable access-governance overlay that combines permissioned audit, ABAC/PBAC, off-chain sensitive data, superior approval, and XAI artifact logging.",
    },
    {
        "title": "Proposed System Architecture",
        "files": ["06_proposed_architecture.md"],
        "about": "This document presents the SEBA-XAI architecture and explains how the blockchain, security, privacy, access-control, and XAI layers work together.",
        "intro": "The architecture is designed as an overlay. It assumes existing agency systems remain the source of raw records, while SEBA-XAI provides auditable authorization, explanation, and review support around access requests.",
        "conclusion": "The architecture is defensible because it does not put raw sensitive police data on-chain. It uses blockchain only for audit commitments, while access control and XAI handle decision governance and justification.",
    },
    {
        "title": "Research Methodology",
        "files": ["07_methodology.md"],
        "about": "This document explains the staged methodology for synthetic workload generation, policy-oracle design, baseline comparison, proposed-method evaluation, XAI logging, and ablation testing.",
        "intro": "The methodology is built as a systems evaluation rather than a deployment study. This keeps the work realistic for an M.Tech-level paper and makes it possible to produce reproducible evidence before writing final claims.",
        "conclusion": "The minimum publishable method is to implement the simulator, compare baselines, run ablations, record metrics, and report limitations honestly.",
    },
    {
        "title": "Experiment Plan",
        "files": ["08_experiment_plan.md", "experiments/experiment_plan.md", "experiments/runs/README.md"],
        "about": "This document defines the experiments needed to test access-control correctness, audit completeness, tamper detection, latency, metadata leakage, XAI reviewability, and aggregate crime-trend context.",
        "intro": "This experiment plan is the bridge between the research idea and evidence. It prevents the paper from becoming only an architecture proposal by requiring baselines, ablations, tamper tests, and run records.",
        "conclusion": "The paper should not include a results section until these experiments have produced saved metrics, logs, tables, plots, and failure-case notes.",
    },
    {
        "title": "Evaluation Metrics",
        "files": ["09_evaluation_metrics.md"],
        "about": "This document defines the metrics for authorization, auditability, blockchain overhead, privacy leakage, XAI quality, aggregate crime modeling, and fairness diagnostics.",
        "intro": "Metrics are important because the paper must evaluate what it actually claims. For this research, accuracy alone is not enough. Audit reconstruction, false allows, tamper detection, latency, and explanation quality also matter.",
        "conclusion": "The evaluation should report trade-offs clearly. A signed log may be faster than blockchain, XAI may add overhead, and synthetic data cannot prove real-world fairness.",
    },
    {
        "title": "Ethics, Security, and Legal Risk Analysis",
        "files": ["10_ethics_security_legal.md"],
        "about": "This document records the ethical, legal, privacy, and security risks connected with police data, XAI, blockchain audit records, and sensitive access workflows.",
        "intro": "Because this research deals with police and criminal-justice data, ethics and legal boundaries are not optional. The system must be treated as a research prototype unless official access, expert review, and formal validation are obtained.",
        "conclusion": "The research must avoid deployment, legal-compliance, fairness, and privacy-guarantee claims until they are supported by evidence and expert review.",
    },
    {
        "title": "Final Paper Outline and Writing Direction",
        "files": ["11_paper_outline.md", "papers/final_paper/README.md"],
        "about": "This document organizes the proposed IEEE-style paper structure and states the writing boundaries for a truthful research paper.",
        "intro": "This paper outline was prepared to help move from research notes to a proper academic paper. It keeps the paper focused on the SEBA-XAI system and prevents unsupported result writing.",
        "conclusion": "The outline should be used after implementation evidence exists. Until then, the paper can present motivation, related work, design, methodology, and planned evaluation, but not fabricated results.",
    },
    {
        "title": "Learning Plan for the Student",
        "files": ["12_five_day_learning_plan.md"],
        "about": "This document gives a short learning plan for understanding CCTNS/ICJS context, blockchain audit, access control, XAI, datasets, and paper writing.",
        "intro": "The learning plan is included because the topic crosses several technical areas. A student writing this paper needs enough understanding of each pillar to defend the work before a guide or reviewer.",
        "conclusion": "The learning plan should be followed alongside implementation, not after it. The student should learn enough to explain why each design choice is present.",
    },
    {
        "title": "Implementation Kickstart",
        "files": ["13_implementation_kickstart.md"],
        "about": "This document converts the research idea into the first practical implementation path using a deterministic synthetic access-control and audit simulator.",
        "intro": "The implementation should begin with the smallest working system. A synthetic access simulator is better than starting with full Hyperledger Fabric or crime prediction because it directly tests the strongest contribution of the paper.",
        "conclusion": "The first implementation target should be `synthetic_access_sim`, with a policy oracle, baselines, hash-chain logging, XAI explanation artifacts, and saved metrics.",
    },
    {
        "title": "Existing Models and Replication Candidates",
        "files": ["14_existing_models_for_testing.md", "reports/iteration/iter_002_existing_model_scan.md"],
        "about": "This document records existing models and papers that are closest to SEBA-XAI and explains what can be tested, adapted, or cited.",
        "intro": "This model scan was done to check whether the proposed work already exists in the world. The result is that related parts exist, but a complete Indian police access-governance system with blockchain, security, and XAI was not found.",
        "conclusion": "The best external references are BAXDT for explainable decision traces and LEChain for police/legal evidence blockchain design. SEBA-XAI should adapt these ideas into its own reproducible simulator.",
    },
    {
        "title": "Introduction Writing Package",
        "files": [
            "papers/final_paper/introduction/README.md",
            "papers/final_paper/introduction/introduction_control_document.md",
            "papers/final_paper/introduction/introduction_skeleton.md",
            "papers/final_paper/introduction/introduction_draft_v0.md",
            "papers/final_paper/introduction/20_day_introduction_plan.md",
            "papers/final_paper/introduction/reviewer_objection_checklist.md",
        ],
        "about": "This document combines the planning material for writing the paper introduction by June 15, including paragraph structure, evidence checks, and reviewer objections.",
        "intro": "The introduction must make the research problem clear without overstating the work. It should explain the India context, the CCTNS/ICJS baseline, the access-governance gap, and why blockchain, security, and XAI are all needed.",
        "conclusion": "The introduction should be frozen only after evidence checks, citation cleanup, supervisor-style critique, and consistency checks with the architecture and methodology.",
    },
    {
        "title": "Research Progress and Artifact Management",
        "files": [
            "reports/iteration/iter_001_research_scoping.md",
            "reports/iteration/iter_003_professor_ready_documents.md",
            "results/plots/README.md",
        ],
        "about": "This document records research progress and explains how artifacts, plots, and iteration reports should be maintained.",
        "intro": "A good research project needs an evidence trail. These notes record what has been done, what is still weak, and how future results should be stored for reproducibility.",
        "conclusion": "The project is now organized, but the next meaningful progress must come from implementation and experiments. Future paper writing should be based on artifacts saved in the repository.",
    },
]


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def wrap(text: str) -> str:
    return textwrap.fill(text.strip(), width=98)


def demote_headings(text: str) -> str:
    lines = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})(\s+.*)$", line)
        if match:
            hashes, rest = match.groups()
            lines.append("#" * min(6, len(hashes) + 2) + rest)
        else:
            lines.append(line)
    return "\n".join(lines).strip()


def extract_refs(text: str) -> list[str]:
    refs = []
    seen = set()
    for url in re.findall(r"https?://[^\s)\]>]+", text):
        clean = url.rstrip(".,;")
        if clean not in seen:
            refs.append(clean)
            seen.add(clean)
    return refs


def read_source(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        return f"[Missing source file: `{rel}`]"
    return path.read_text(encoding="utf-8")


def strip_title(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip()
    return text.strip()


def render_doc(index: int, item: dict[str, object]) -> str:
    title = str(item["title"])
    files = list(item["files"])
    source_blocks = []
    all_refs: list[str] = []
    seen_refs = set()

    for rel in files:
        raw = read_source(str(rel))
        for ref in extract_refs(raw):
            if ref not in seen_refs:
                all_refs.append(ref)
                seen_refs.add(ref)
        body = demote_headings(strip_title(raw))
        source_blocks.append(f"### Source Note: `{rel}`\n\n{body}")

    abstract = (
        f"{item['about']} It is written as a professor-ready academic note and keeps the "
        "research claims limited to what the current repository evidence supports."
    )

    doc = [
        f"DOCUMENT {index}: {title}",
        "",
        f"# {title}",
        "",
        "## Student Details",
        "Name: [Add your name]  ",
        "Roll Number: [Add roll number]  ",
        "Course: [Add course]  ",
        "Subject: [Add subject]  ",
        "Faculty: [Add faculty name]  ",
        "Date: 17 May 2026",
        "",
        "## Abstract",
        "",
        wrap(abstract),
        "",
        "## 1. Introduction",
        "",
        wrap(str(item["intro"])),
        "",
        "## 2. Document Scope",
        "",
        wrap(str(item["about"])),
        "",
        "## 3. Main Academic Content",
        "",
        (
            "The following material is organized from the research notes already prepared in the repository. "
            "The wording has been kept simple and evidence-conscious so that it can be reviewed by a faculty member."
        ),
        "",
        "\n\n".join(source_blocks),
        "",
        "## Conclusion",
        "",
        wrap(str(item["conclusion"])),
        "",
        "## References",
        "",
    ]

    for rel in files:
        doc.append(f"- Source file: `{rel}`")
    if all_refs:
        for ref in all_refs:
            doc.append(f"- {ref}")
    else:
        doc.append("- No external URL was present in the selected source notes.")

    doc.extend(
        [
            "",
            "## Appendix",
            "",
            "### Appendix A: Evidence Boundary",
            "",
            (
                "This document should not be treated as proof of experimental results. Any claim about "
                "accuracy, performance, security improvement, legal compliance, deployment readiness, or "
                "operational benefit requires matching artifacts in `experiments/runs/`, `results/`, and "
                "`reports/iteration/`."
            ),
        ]
    )
    return "\n".join(doc).rstrip() + "\n"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    SEPARATE.mkdir(parents=True, exist_ok=True)
    for old in SEPARATE.glob("*.md"):
        old.unlink()

    combined = []
    index_lines = [
        "# Curated Research Documents",
        "",
        "This folder contains one professor-ready document for each major research activity completed in the SEBA-XAI project.",
        "",
        "## Documents",
        "",
    ]

    for idx, item in enumerate(DOCUMENTS, start=1):
        rendered = render_doc(idx, item)
        filename = f"{idx:02d}_{slug(str(item['title']))}.md"
        path = SEPARATE / filename
        path.write_text(rendered, encoding="utf-8")
        combined.append(rendered)
        index_lines.append(f"{idx}. [{item['title']}](separate_documents/{filename})")

    COMBINED.write_text("\n\n---\n\n".join(combined), encoding="utf-8")
    INDEX.write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    print(f"Generated {len(DOCUMENTS)} curated research documents.")
    print(f"Folder: {SEPARATE}")
    print(f"Combined: {COMBINED}")


if __name__ == "__main__":
    main()
