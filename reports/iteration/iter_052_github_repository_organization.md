# Iteration 052: GitHub Repository Organization

Status: completed on 2026-06-07.

## What worked

- Moved the original numbered research notes into `research_pack/`.
- Moved downloaded literature/reference PDF folders under `sources/`.
- Updated `README.md` and `00_START_HERE.md` so the GitHub repo opens with a
  clear project map.
- Added `research_pack/README.md`, `sources/README.md`, and
  `prototype/runs/README.md`.
- Kept code, tests, scripts, result tables, figures, reports, paper source, and
  Overleaf package available for Git tracking.
- Kept large/reference-only PDFs and raw prototype run folders local-only via
  `.gitignore`.

## What is intentionally local-only

- `sources/downloaded_research_papers_2026-05-29/`
- `sources/reference_papers/`
- `prototype/runs/`

These folders are organized locally but not committed because they are either
downloaded reference PDFs or rebuildable raw run artifacts. The tracked evidence
is in `results/`, `experiments/runs/`, `reports/iteration/`, and the
reproduction scripts.

## What remains weak

- Some historical draft files still mention old paths because they document the
  state at the time they were created.
- The repository has not been validated with a local LaTeX compile because TeX
  tools are not installed in this environment.

## Next refinement

- After pushing to GitHub, check the repository page and confirm that
  `README.md`, `00_START_HERE.md`, and the paper folders render correctly.
