"""Validate and package the SEBA-XAI Overleaf project.

Usage:
    python3 scripts/package_overleaf.py

The script edits no manuscript content. It validates the LaTeX project and
regenerates the uploadable zip used by Overleaf.
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = REPO_ROOT / "papers" / "overleaf_ieee_journal"
DEFAULT_OUTPUT = REPO_ROOT / "papers" / "seba_xai_ieee_journal_overleaf.zip"

REQUIRED_FILES = (
    "main.tex",
    "references.bib",
    "sections/introduction.tex",
    "sections/related_work.tex",
    "sections/proposed_methodology.tex",
    "sections/limitations.tex",
    "sections/conclusion.tex",
)


def _relative_files(project_dir: Path) -> list[Path]:
    return sorted(
        path.relative_to(project_dir)
        for path in project_dir.rglob("*")
        if path.is_file()
    )


def _validate_required_files(project_dir: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        path = project_dir / rel
        if not path.exists():
            errors.append(f"missing required file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty required file: {rel}")
    return errors


def _validate_no_markdown(project_dir: Path) -> list[str]:
    markdown_files = sorted(path.relative_to(project_dir) for path in project_dir.rglob("*.md"))
    return [f"markdown file should not be in Overleaf package: {path}" for path in markdown_files]


def _validate_inputs(project_dir: Path) -> list[str]:
    main_path = project_dir / "main.tex"
    if not main_path.exists():
        return ["cannot validate inputs because main.tex is missing"]
    errors: list[str] = []
    main_text = main_path.read_text(encoding="utf-8")
    for target in re.findall(r"\\input\{([^}]+)\}", main_text):
        input_path = project_dir / f"{target}.tex"
        if not input_path.exists():
            errors.append(f"missing input target: {target}.tex")
    return errors


def _validate_citations(project_dir: Path) -> list[str]:
    bib_path = project_dir / "references.bib"
    if not bib_path.exists():
        return ["cannot validate citations because references.bib is missing"]

    bib_text = bib_path.read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib_text))
    used_keys: set[str] = set()

    for tex_path in project_dir.rglob("*.tex"):
        tex_text = tex_path.read_text(encoding="utf-8")
        for group in re.findall(r"\\cite\{([^}]+)\}", tex_text):
            used_keys.update(key.strip() for key in group.split(",") if key.strip())

    return [f"missing BibTeX key: {key}" for key in sorted(used_keys - bib_keys)]


def validate_project(project_dir: Path) -> None:
    if not project_dir.exists():
        raise SystemExit(f"Overleaf project folder not found: {project_dir}")
    if not project_dir.is_dir():
        raise SystemExit(f"Overleaf project path is not a folder: {project_dir}")

    errors: list[str] = []
    errors.extend(_validate_required_files(project_dir))
    errors.extend(_validate_no_markdown(project_dir))
    errors.extend(_validate_inputs(project_dir))
    errors.extend(_validate_citations(project_dir))

    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise SystemExit(f"Overleaf package validation failed:\n{joined}")


def write_zip(project_dir: Path, output_zip: Path) -> None:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()

    root_name = project_dir.name
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for rel_path in _relative_files(project_dir):
            source = project_dir / rel_path
            archive.write(source, Path(root_name) / rel_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package SEBA-XAI Overleaf project.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=DEFAULT_PROJECT,
        help="Overleaf project directory to package.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Zip file to create.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_dir = args.project_dir.resolve()
    output_zip = args.output.resolve()

    validate_project(project_dir)
    write_zip(project_dir, output_zip)

    files = _relative_files(project_dir)
    print(f"Packaged {len(files)} files")
    print(f"Project: {project_dir}")
    print(f"Zip: {output_zip}")


if __name__ == "__main__":
    main()
