# Iteration 007: Folder Cleanup and Guide

Date: 2026-05-27  
Status: completed light cleanup and organization guide.

## Goal

Make the research folder easier to understand and remove only unwanted disposable files.

## What Worked

- Removed macOS `.DS_Store` files from the workspace.
- Removed the Excel temporary lock file `~$SEBA_XAI_Professor_Update_Details.xlsx`.
- Added `00_START_HERE.md` as the main folder guide.
- Added `.gitignore` entries to avoid future `.DS_Store` files and Excel lock files.
- Updated `README.md` to point to `00_START_HERE.md`.

## What Was Not Removed

No research notes, PDFs, reports, spreadsheets, generated documents, scripts, or source files were deleted.

These files are not unwanted because they are part of the evidence trail or useful outputs:

- numbered research notes;
- `blockchain_xai_course/`;
- `papers/`;
- `sources/`;
- `reports/iteration/`;
- `spreadsheets/`;
- `research_documents/`;
- `professor_ready_documents/`;
- `scripts/`;
- `results/`;
- `experiments/`.

## Current Recommended Entry Point

Open `00_START_HERE.md` first. It explains which files to read and what each folder is for.

## Next Step

Keep the current structure. Future cleanup should move files only if all references and generator scripts are updated, because many generated documents and scripts currently refer to these paths.
