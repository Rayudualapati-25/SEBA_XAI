"""Build the SEBA-XAI prototype syllabus PDF."""

from __future__ import annotations

from pathlib import Path

from markdown_pdf import MarkdownPdf, Section


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "SEBA_XAI_Prototype_5_Unit_Syllabus.md"
OUTPUT = ROOT / "SEBA_XAI_Prototype_5_Unit_Syllabus.pdf"

CSS = """
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.45;
  color: #1a1a1a;
}
h1 {
  font-size: 22pt;
  color: #0b3a66;
  border-bottom: 2px solid #0b3a66;
  padding-bottom: 4px;
}
h2 {
  font-size: 16pt;
  color: #0b3a66;
  margin-top: 1.2em;
}
h3 {
  font-size: 13pt;
  color: #24384a;
  margin-top: 1em;
}
p, li {
  font-size: 10.5pt;
}
code {
  font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
  font-size: 9pt;
  background: #f4f5f7;
  padding: 1px 4px;
  border-radius: 3px;
}
pre {
  background: #f4f5f7;
  padding: 9px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 8.7pt;
  line-height: 1.3;
}
pre code {
  background: transparent;
  padding: 0;
}
table {
  border-collapse: collapse;
  width: 100%;
  font-size: 8.7pt;
  margin: 0.6em 0;
}
th, td {
  border: 1px solid #cdd5df;
  padding: 5px 7px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #eef2f6;
}
blockquote {
  border-left: 4px solid #0b3a66;
  margin-left: 0;
  padding-left: 12px;
  color: #444;
}
hr {
  border: none;
  border-top: 1px solid #cdd5df;
  margin: 1.4em 0;
}
"""


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")

    cover = """# SEBA-XAI Prototype

## Five-Unit Full Syllabus

**Project:** Secure Explainable Blockchain-Audited Access Governance Prototype

**Level:** M.Tech / early research project

**Date:** 2026-05-28

This PDF is generated from `SEBA_XAI_Prototype_5_Unit_Syllabus.md`.
"""

    pdf = MarkdownPdf(toc_level=3)
    pdf.meta["title"] = "SEBA-XAI Prototype: Five-Unit Full Syllabus"
    pdf.meta["author"] = "Venkata Rayudu Alapati"
    pdf.meta["subject"] = "SEBA-XAI prototype learning syllabus"
    pdf.add_section(Section(cover, toc=False, paper_size="A4"), user_css=CSS)
    pdf.add_section(Section(text, toc=True, paper_size="A4"), user_css=CSS)
    pdf.save(str(OUTPUT))
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

