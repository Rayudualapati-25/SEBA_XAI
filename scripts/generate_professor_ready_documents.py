from __future__ import annotations

import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "professor_ready_documents"
SEPARATE = OUT / "separate_files"
COMBINED = OUT / "ALL_PROFESSOR_READY_DOCUMENTS.md"


SOURCE_ORDER = [
    "README.md",
    "research_brief.md",
    "00_problem_understanding.md",
    "01_literature_review.md",
    "03_datasets.md",
    "05_research_gap.md",
    "06_proposed_architecture.md",
    "07_methodology.md",
    "08_experiment_plan.md",
    "09_evaluation_metrics.md",
    "10_ethics_security_legal.md",
    "11_paper_outline.md",
    "12_five_day_learning_plan.md",
    "13_implementation_kickstart.md",
    "14_existing_models_for_testing.md",
    "sources/source_log.md",
    "sources/literature_matrix.md",
    "sources/dataset_inventory.md",
    "experiments/experiment_plan.md",
    "experiments/runs/README.md",
    "reports/iteration/iter_001_research_scoping.md",
    "reports/iteration/iter_002_existing_model_scan.md",
    "reports/iteration/iter_003_professor_ready_documents.md",
    "results/plots/README.md",
    "papers/final_paper/README.md",
    "papers/final_paper/introduction/README.md",
    "papers/final_paper/introduction/introduction_control_document.md",
    "papers/final_paper/introduction/introduction_skeleton.md",
    "papers/final_paper/introduction/introduction_draft_v0.md",
    "papers/final_paper/introduction/20_day_introduction_plan.md",
    "papers/final_paper/introduction/reviewer_objection_checklist.md",
]


PURPOSES = {
    "README.md": "This document introduces the overall research pack and states the safest research direction: a secure, explainable, blockchain-audited overlay for Indian police data sharing.",
    "research_brief.md": "This document records the early research framing for AI, blockchain, security, and explainability in Indian police and crime-data systems.",
    "00_problem_understanding.md": "This document defines the research problem and explains why the work should complement CCTNS and ICJS rather than replace them.",
    "01_literature_review.md": "This document organizes the main academic and official sources that support the three equal pillars of the proposed research.",
    "03_datasets.md": "This document reviews possible datasets for crime analysis, access-control simulation, and evaluation of the proposed system.",
    "05_research_gap.md": "This document identifies the gap between existing work and the proposed SEBA-XAI research direction.",
    "06_proposed_architecture.md": "This document presents the proposed system architecture, including the data layer, security layer, blockchain audit layer, and XAI layer.",
    "07_methodology.md": "This document explains the research methodology and the planned experimental workflow for the proposed system.",
    "08_experiment_plan.md": "This document gives the experiment plan, baselines, ablations, and expected evidence needed before making research claims.",
    "09_evaluation_metrics.md": "This document defines the metrics that should be used to evaluate authorization, auditability, security, XAI quality, and system cost.",
    "10_ethics_security_legal.md": "This document records the ethical, legal, security, and privacy risks that must be considered before claiming practical deployment value.",
    "11_paper_outline.md": "This document gives a structured outline for an IEEE-style research paper based on the SEBA-XAI direction.",
    "12_five_day_learning_plan.md": "This document gives a short learning plan to help the student prepare the technical background for writing and implementation.",
    "13_implementation_kickstart.md": "This document converts the research plan into a first practical implementation path using a deterministic synthetic access-control simulator.",
    "14_existing_models_for_testing.md": "This document records the scan of existing models and papers that are closest to the proposed blockchain-security-XAI system.",
    "sources/source_log.md": "This document keeps a traceable source log for official India references, academic papers, datasets, and technical standards.",
    "sources/literature_matrix.md": "This document summarizes the important literature and standards in a matrix-style note for later citation and comparison.",
    "sources/dataset_inventory.md": "This document lists the main datasets considered for the research and records their expected usefulness and limitations.",
    "experiments/experiment_plan.md": "This document records the planned experiments, baselines, and implementation evidence required for the research.",
    "experiments/runs/README.md": "This document defines how experiment runs should be stored so that future results are reproducible.",
    "reports/iteration/iter_001_research_scoping.md": "This document reports the first research-scoping iteration, including what worked, what failed, and what should happen next.",
    "reports/iteration/iter_002_existing_model_scan.md": "This document reports the scan of external models and explains why a custom SEBA-XAI simulator is still needed.",
    "reports/iteration/iter_003_professor_ready_documents.md": "This document reports the conversion of Markdown research notes into professor-ready academic documents.",
    "results/plots/README.md": "This document explains how plots should be stored once experiments have been completed.",
    "papers/final_paper/README.md": "This document sets the writing guardrails for the final paper and prevents unsupported results from being written.",
    "papers/final_paper/introduction/README.md": "This document defines the workspace for the paper introduction and the supporting evidence files.",
    "papers/final_paper/introduction/introduction_control_document.md": "This document controls the structure, scope, and evidence requirements for the paper introduction.",
    "papers/final_paper/introduction/introduction_skeleton.md": "This document provides a paragraph-level skeleton for the introduction section.",
    "papers/final_paper/introduction/introduction_draft_v0.md": "This document contains the first rough introduction draft and should be improved only with evidence-safe claims.",
    "papers/final_paper/introduction/20_day_introduction_plan.md": "This document gives a detailed 20-day plan for researching, drafting, reviewing, and freezing the introduction.",
    "papers/final_paper/introduction/reviewer_objection_checklist.md": "This document lists likely reviewer objections and helps strengthen the introduction before supervisor review.",
}


ACADEMIC_USE = {
    "README.md": "This document can be used as the opening note when submitting the research folder to a guide or supervisor.",
    "research_brief.md": "This document can be used to explain the starting point of the research and the reason for choosing this topic.",
    "00_problem_understanding.md": "This document can be used as the base for the problem statement section of the paper.",
    "01_literature_review.md": "This document can be used to prepare the related work section and to identify which papers need full-text verification.",
    "03_datasets.md": "This document can be used to justify dataset selection and to avoid unsupported claims about private police records.",
    "05_research_gap.md": "This document can be used to write the research gap and novelty boundaries.",
    "06_proposed_architecture.md": "This document can be used to draw the system architecture diagram and explain the main components.",
    "07_methodology.md": "This document can be used to write the methodology section after the first implementation exists.",
    "08_experiment_plan.md": "This document can be used as the checklist for baseline experiments, proposed-method experiments, and ablations.",
    "09_evaluation_metrics.md": "This document can be used to build the results table and evaluation section after experiments are run.",
    "10_ethics_security_legal.md": "This document can be used to write the limitations, ethics, legal, and security-risk discussion.",
    "11_paper_outline.md": "This document can be used as the structure for the first full paper draft.",
    "12_five_day_learning_plan.md": "This document can be used as a short self-study plan before implementation and writing.",
    "13_implementation_kickstart.md": "This document can be used as the immediate coding plan for the first reproducible prototype.",
    "14_existing_models_for_testing.md": "This document can be used to justify why SEBA-XAI should be implemented instead of simply copying an existing system.",
    "sources/source_log.md": "This document can be used as the master evidence register for citations.",
    "sources/literature_matrix.md": "This document can be used to build a formal literature matrix in the paper appendix.",
    "sources/dataset_inventory.md": "This document can be used to support the dataset discovery and limitation discussion.",
    "experiments/experiment_plan.md": "This document can be used to create experiment scripts, run records, and comparison tables.",
    "experiments/runs/README.md": "This document can be used as the required format for future experiment evidence.",
    "reports/iteration/iter_001_research_scoping.md": "This document can be used to show research progress and honest limitations after the first scoping stage.",
    "reports/iteration/iter_002_existing_model_scan.md": "This document can be used to show why existing work does not remove the need for a custom implementation.",
    "reports/iteration/iter_003_professor_ready_documents.md": "This document can be used to show how the research notes were converted into academic review documents.",
    "results/plots/README.md": "This document can be used to organize future graphs and figures.",
    "papers/final_paper/README.md": "This document can be used to keep the paper-writing process evidence-based.",
    "papers/final_paper/introduction/README.md": "This document can be used to manage the introduction-writing workspace.",
    "papers/final_paper/introduction/introduction_control_document.md": "This document can be used as the supervisor-facing control note for the introduction.",
    "papers/final_paper/introduction/introduction_skeleton.md": "This document can be used to write a complete introduction paragraph by paragraph.",
    "papers/final_paper/introduction/introduction_draft_v0.md": "This document can be used as the starting draft for the introduction after citation cleanup.",
    "papers/final_paper/introduction/20_day_introduction_plan.md": "This document can be used as the daily writing schedule until the introduction deadline.",
    "papers/final_paper/introduction/reviewer_objection_checklist.md": "This document can be used before submission to test whether the introduction is defensible.",
}


def slugify(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", path).strip("_").lower()


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback.replace("_", " ").replace("/", " - ").replace(".md", "").title()


def strip_first_h1(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip()
    return text.strip()


def demote_headings(text: str, levels: int = 1) -> str:
    result = []
    for line in text.splitlines():
        if line.startswith("#"):
            match = re.match(r"^(#{1,6})(\s+.*)$", line)
            if match:
                hashes, rest = match.groups()
                new_level = min(6, len(hashes) + levels)
                result.append("#" * new_level + rest)
                continue
        result.append(line)
    return "\n".join(result)


def move_long_code_blocks(text: str, title: str) -> tuple[str, list[str]]:
    appendices: list[str] = []
    pattern = re.compile(r"```([^\n`]*)\n(.*?)\n```", re.DOTALL)

    def replace(match: re.Match[str]) -> str:
        lang = match.group(1).strip()
        code = match.group(2)
        line_count = len(code.splitlines())
        if line_count < 28:
            return match.group(0)
        label = f"Appendix Code Block {len(appendices) + 1}"
        appendices.append(
            f"### {label}: Long Code From {title}\n\n"
            f"```{lang}\n{code}\n```\n"
        )
        return f"[Long code block moved to {label}.]"

    return pattern.sub(replace, text), appendices


def extract_references(text: str) -> list[str]:
    url_pattern = re.compile(r"https?://[^\s)\]>]+")
    urls = []
    seen = set()
    for url in url_pattern.findall(text):
        cleaned = url.rstrip(".,;")
        if cleaned not in seen:
            urls.append(cleaned)
            seen.add(cleaned)
    return urls


def wrap(paragraph: str) -> str:
    return textwrap.fill(paragraph.strip(), width=100)


def build_document(index: int, source_path: str, text: str) -> tuple[str, str]:
    title = extract_title(text, source_path)
    body = strip_first_h1(text)
    body = demote_headings(body, levels=1)
    body, appendices = move_long_code_blocks(body, title)
    refs = extract_references(text)

    purpose = PURPOSES.get(
        source_path,
        f"This document organizes research notes from `{source_path}` for academic review.",
    )
    academic_use = ACADEMIC_USE.get(
        source_path,
        "This document can be used as a supporting note in the research folder.",
    )

    abstract = (
        f"{purpose} The polished version keeps the original technical meaning, but presents it in a "
        "cleaner academic format so that a faculty member can understand the purpose, evidence, "
        "limitations, and next use of the note."
    )
    introduction = (
        f"The original file `{source_path}` is part of the SEBA-XAI research pack. "
        "It supports the larger research direction of designing a secure, explainable, "
        "blockchain-audited access-governance overlay for sensitive police and criminal-justice "
        "data sharing in India. This version keeps the intent of the original note while improving "
        "the structure for academic reading."
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
        wrap(introduction),
        "",
        "## 2. Purpose of This Document",
        "",
        wrap(purpose),
        "",
        "## 3. Main Academic Notes",
        "",
        (
            "The following notes preserve the substance of the original file. Claims that require "
            "experimental evidence should still be treated as planned work unless the repository "
            "contains matching results, logs, or tables."
        ),
        "",
        body if body else "[Add detailed content here.]",
        "",
        "## 4. Academic Use",
        "",
        wrap(academic_use),
        "",
        "## Conclusion",
        "",
        wrap(
            "This document is useful as a structured academic note for the SEBA-XAI research work. "
            "It should be read as a planning or evidence document, not as proof of completed "
            "experimental results. Any final paper section derived from this note must cite the "
            "supporting sources and must avoid claims that are not yet backed by local artifacts."
        ),
        "",
        "## References",
        "",
    ]

    doc.append(f"- Original source file: `{source_path}`")
    if refs:
        for ref in refs:
            doc.append(f"- {ref}")
    else:
        doc.append("- No external URL was present in the original Markdown file.")

    doc.extend(["", "## Appendix", ""])
    if appendices:
        doc.extend(appendices)
    else:
        doc.append("No additional appendix material is required for this document.")

    return title, "\n".join(doc).rstrip() + "\n"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    SEPARATE.mkdir(parents=True, exist_ok=True)
    for old_file in SEPARATE.glob("*.md"):
        old_file.unlink()

    source_paths = []
    for rel in SOURCE_ORDER:
        path = ROOT / rel
        if path.exists():
            source_paths.append(rel)

    # Include any future Markdown files that are not generated artifacts.
    ordered_set = set(source_paths)
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("professor_ready_documents/"):
            continue
        if rel.startswith("scripts/"):
            continue
        if rel not in ordered_set:
            source_paths.append(rel)
            ordered_set.add(rel)

    combined_parts = []
    for index, rel in enumerate(source_paths, start=1):
        text = (ROOT / rel).read_text(encoding="utf-8")
        title, rendered = build_document(index, rel, text)
        out_file = SEPARATE / f"{index:02d}_{slugify(rel)}_professor_ready.md"
        out_file.write_text(rendered, encoding="utf-8")
        combined_parts.append(rendered)

    COMBINED.write_text("\n\n---\n\n".join(combined_parts), encoding="utf-8")
    print(f"Generated {len(source_paths)} professor-ready documents in {SEPARATE}")
    print(f"Generated combined document at {COMBINED}")


if __name__ == "__main__":
    main()
