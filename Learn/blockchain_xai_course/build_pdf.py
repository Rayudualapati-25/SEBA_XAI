"""
Build PDFs from the blockchain_xai_course markdown files.

Produces:
  - blockchain_xai_course.pdf  (master, all content)
  - blockchain_track.pdf
  - xai_track.pdf
  - labs.pdf
"""
from __future__ import annotations
from pathlib import Path
from markdown_pdf import MarkdownPdf, Section

ROOT = Path(__file__).resolve().parent

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
       font-size: 11pt; line-height: 1.45; color: #1a1a1a; }
h1   { font-size: 22pt; margin-top: 0.8em; color: #0b3a66; border-bottom: 2px solid #0b3a66;
       padding-bottom: 4px; }
h2   { font-size: 16pt; margin-top: 1.4em; color: #0b3a66; }
h3   { font-size: 13pt; margin-top: 1.2em; color: #244;}
h4   { font-size: 11.5pt; margin-top: 1em; color: #244; }
p, li { font-size: 10.5pt; }
code { font-family: 'SF Mono', Menlo, Monaco, Consolas, monospace; font-size: 9.5pt;
       background: #f4f5f7; padding: 1px 4px; border-radius: 3px; }
pre  { background: #f4f5f7; padding: 10px; border-radius: 6px; overflow-x: auto;
       font-size: 9pt; line-height: 1.35; }
pre code { background: transparent; padding: 0; }
table { border-collapse: collapse; margin: 0.5em 0; font-size: 9.5pt; width: 100%; }
th, td { border: 1px solid #cdd5df; padding: 5px 8px; text-align: left; vertical-align: top; }
th   { background: #eef2f6; }
blockquote { border-left: 4px solid #0b3a66; margin-left: 0; padding-left: 12px;
             color: #444; font-style: italic; }
hr   { border: none; border-top: 1px solid #cdd5df; margin: 1.5em 0; }
a    { color: #0b3a66; text-decoration: none; }
"""


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def section(md_text: str, toc: bool = True) -> Section:
    return Section(md_text, toc=toc, paper_size="A4")


def build_pdf(output: Path, ordered_files: list[Path], title: str, subtitle: str) -> None:
    pdf = MarkdownPdf(toc_level=3)
    pdf.meta["title"] = title
    pdf.meta["author"] = "Venkat Rayudu Alapati"
    pdf.meta["subject"] = "Blockchain + Explainable AI Research Course"

    cover = f"""# {title}

## {subtitle}

A research-grade self-study course synthesizing top web courses
on Blockchain and Explainable AI.

**Author**: Venkat Rayudu Alapati
**Date**: 2026-05-23
**Pages**: see Table of Contents
"""
    pdf.add_section(section(cover, toc=False), user_css=CSS)

    for fp in ordered_files:
        rel = fp.relative_to(ROOT)
        text = read(fp)
        # add an anchor comment for orientation
        text = f"<!-- source: {rel} -->\n\n" + text
        pdf.add_section(section(text), user_css=CSS)

    pdf.save(str(output))
    print(f"wrote {output}  ({output.stat().st_size/1024:.1f} KB)")


def main() -> None:
    blockchain_files = sorted((ROOT / "blockchain").glob("*.md"))
    xai_files        = sorted((ROOT / "xai").glob("*.md"))
    intersection     = sorted((ROOT / "intersection").glob("*.md"))
    resources        = sorted((ROOT / "resources").glob("*.md"))
    labs             = sorted((ROOT / "labs").glob("*.md"))
    top_level        = [ROOT / "README.md", ROOT / "SYLLABUS.md"]

    # master
    master = top_level + blockchain_files + xai_files + intersection + resources + labs
    build_pdf(ROOT / "blockchain_xai_course.pdf", master,
              "Blockchain + Explainable AI", "A Research-Grade Self-Study Course")

    # per-track
    build_pdf(ROOT / "blockchain_track.pdf",
              [ROOT / "README.md"] + blockchain_files,
              "Blockchain Track", "12 Modules — Foundations to Research Frontier")

    build_pdf(ROOT / "xai_track.pdf",
              [ROOT / "README.md"] + xai_files,
              "Explainable AI Track", "13 Modules — Foundations to Mechanistic Interpretability")

    build_pdf(ROOT / "intersection_and_labs.pdf",
              intersection + labs + resources,
              "Intersection, Labs & Resources",
              "Verifiable + Decentralized AI · Hands-on Labs · Curated Reading")


if __name__ == "__main__":
    main()
