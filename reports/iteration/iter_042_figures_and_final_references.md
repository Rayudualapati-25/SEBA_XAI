# Iteration 042 — Generated Paper Figures and IEEE Reference List

Date: 2026-05-30
Status: completed

## 1. Goal

Complete the next reviewer-facing paper-preparation step after the figure/table
plan and reference-verification pass:

1. generate actual paper SVG figures from the current result tables;
2. add a manifest so each figure has a source path and caption guardrail;
3. create a cleaned IEEE-style reference list for supervisor review;
4. make figure generation reproducible from a command;
5. insert the generated figures and cleaned references into the combined draft.

## 2. What Changed

Created:

- `scripts/generate_paper_figures.py`
- `papers/final_paper/figures_tables/fig_01_seba_xai_architecture.svg`
- `papers/final_paper/figures_tables/fig_02_detector_visibility.svg`
- `papers/final_paper/figures_tables/fig_03_compromised_signer_detection.svg`
- `papers/final_paper/figures_tables/fig_04_nspi_sensitivity.svg`
- `papers/final_paper/figures_tables/fig_05_xai_audit_quality.svg`
- `papers/final_paper/figures_tables/fig_06_workload_stress_detection.svg`
- `papers/final_paper/figures_tables/paper_figures_manifest.md`
- `papers/final_paper/references_ieee_final_v1.md`
- `papers/final_paper/paper_draft_v1.md`

Updated:

- `Makefile`
- `REPRODUCE.md`
- `papers/final_paper/README.md`
- `papers/final_paper/references_ieee_map.md`

## 3. Figure Evidence Sources

| Figure | Evidence source |
|---|---|
| Architecture | `06_proposed_architecture.md`, methodology draft |
| Detector visibility | threat-model draft |
| Compromised-signer detection | `results/tables/seed_confidence_summary.csv` |
| NS-PI sensitivity | `results/tables/nspi_compromised_signer_sensitivity_summary.csv` |
| XAI/audit quality | `results/tables/explanation_audit_quality_summary.csv` |
| Workload stress | `results/tables/workload_policy_stress_summary.csv` |

The generated figures do not introduce new measurements. They visualize
existing CSV-backed evidence and architecture boundaries.

## 4. Reference Work

`papers/final_paper/references_ieee_final_v1.md` is now the cleaned
IEEE-style reference list for supervisor review. It is based on the verified
metadata in `papers/final_paper/references_ieee_map.md` and
`papers/final_paper/references_verification_v1.md`.

The same reference list has also been inserted into
`papers/final_paper/paper_draft_v1.md`, replacing the earlier reference-map
placeholder.

The final venue template may still require small changes to punctuation,
abbreviated venue names, or access-date placement.

## 5. What Worked

- The figure-generation script reads directly from result CSVs.
- The script writes all figures to `papers/final_paper/figures_tables/`.
- `make figures` now regenerates the figures.
- Ruff passes on the new figure-generation script.

## 6. What Is Still Weak

- The figures are embedded as Markdown image links in `paper_draft_v1.md`, but
  they are not yet placed inside a formatted IEEE template.
- The architecture and visibility figures are schematic; they must not be
  presented as deployment diagrams.
- The final reference list is cleaned for supervisor review, but not locked to
  a specific journal or conference template.

## 7. Verification

Commands run:

```bash
python3 scripts/generate_paper_figures.py
python3 -m ruff check scripts/generate_paper_figures.py
make figures
```

Observed status:

- figure generation completed successfully;
- six SVG files were written;
- Ruff passed on `scripts/generate_paper_figures.py`;
- `make figures` completed successfully.

## 8. Next Step

Perform a supervisor-review language pass over `paper_draft_v1.md` and decide
which generated figures should remain in the main paper versus appendix. No new
result claims are needed for that step.
