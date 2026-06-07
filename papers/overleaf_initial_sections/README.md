# Overleaf Initial Sections

Created: 2026-06-01

This folder contains an IEEE/Overleaf-ready initial draft for the professor's requested sections:

- `main.tex`
- `sections/introduction.tex`
- `sections/related_work.tex`
- `sections/proposed_methodology.tex`
- `references.bib`

## Purpose

The professor asked to first put the idea into writing before fine-tuning the problem statement and contribution. This version therefore focuses on:

1. Introduction
2. Related Work
3. Proposed Methodology

## Writing Position

The draft frames the research as:

> A secure, explainable, blockchain-audited overlay for inter-agency police record access governance in a CCTNS/ICJS-style environment.

It does not claim:

- replacement of CCTNS or ICJS;
- live deployment;
- actual police-record testing;
- raw police records on-chain;
- legal compliance proof;
- state-of-the-art crime prediction.

## How to Use in Overleaf

Upload the full `papers/overleaf_initial_sections/` folder to Overleaf. Compile `main.tex` with the standard LaTeX/BibTeX flow.

If the target venue provides a different Overleaf template, keep the content from the three files under `sections/` and paste them into that venue's `main.tex`.

## Immediate Supervisor Discussion Points

- Is the problem statement narrow enough?
- Should the paper emphasize access governance more than policy-drift detection?
- Are the contribution bullets acceptable for an initial M.Tech/IEEE-style paper?
- Should the methodology section include prototype implementation details now, or only architecture and experiment design?
