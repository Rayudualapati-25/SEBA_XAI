# Iteration 024: Research Paper Download Folder

Date: 2026-05-29

## Goal

Create a separate folder containing the research papers and technical references needed for the SEBA-XAI literature base.

## What Worked

- Created `downloaded_research_papers_2026-05-29/`.
- Copied existing local PDFs from `papers/` into the new folder.
- Downloaded directly accessible PDFs from arXiv, NIST, Springer Open, Frontiers, MDPI resource URLs, SCITEPRESS, PMLR, AUB ScholarWorks, and Liverpool Repository.
- Added `download_index.csv` to keep source URLs and paper status traceable.
- Added `not_downloaded_or_manual_access.csv` for important papers that could not be directly downloaded.

## What Failed Or Is Weak

- Several ScienceDirect, IEEE, Wiley, PMC, and ORCA direct PDF attempts either returned HTML pages or were blocked.
- These blocked items were not treated as downloaded papers.
- Failed HTML attempts were moved into `downloaded_research_papers_2026-05-29/failed_direct_downloads_html/`.

## Evidence Produced

- Downloaded PDF folder: `downloaded_research_papers_2026-05-29/`
- Index: `downloaded_research_papers_2026-05-29/download_index.csv`
- Manual-access list: `downloaded_research_papers_2026-05-29/not_downloaded_or_manual_access.csv`

## Next Step

Manually obtain the blocked ScienceDirect/IEEE/Wiley papers through institutional access or Google Scholar, then update the index without making unsupported claims from papers that have not been fully reviewed.
