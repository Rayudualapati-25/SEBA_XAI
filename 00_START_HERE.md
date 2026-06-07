# Start Here: SEBA-XAI Repository Guide

This repository contains the complete SEBA-XAI research work up to the current
date: research notes, literature and dataset study, prototype code,
experiments, result tables, paper drafts, Overleaf source, and learning notes.

The project is **not** a real police deployment. All current experiments use a
synthetic access-control workload.

## Open These First

1. `README.md`  
   Main project summary, current claim boundary, and repository map.

2. `CONTRIBUTION.md`  
   Short locked contribution statement for the research paper.

3. `results/FINDINGS.md`  
   Best honest summary of the experiment results and limitations.

4. `papers/overleaf_ieee_journal/main.tex`  
   Current IEEE/Overleaf paper source.

5. `papers/seba_xai_ieee_journal_overleaf.zip`  
   Uploadable Overleaf project package.

6. `research_pack/00_problem_understanding.md`  
   Original problem framing and research questions.

7. `REPRODUCE.md`  
   How to rerun the experiments.

## Main Folders

| Folder | Purpose |
|---|---|
| `research_pack/` | Student research notes: problem, literature review, datasets, gap, architecture, methodology, ethics, paper outline, and learning plan. |
| `src/seba/` | Main Python package for schema, attacks, NS-PI drift, baselines, audit logic, and XAI quality checks. |
| `prototype/synthetic_access_sim/` | Prototype scripts for synthetic request generation, policy/XAI, audit baselines, blockchain-style audit, off-chain storage, and overhead checks. |
| `scripts/` | Reproduction, aggregation, figure generation, Overleaf packaging, and report-generation scripts. |
| `tests/` | Unit tests for the prototype and result-generation pipeline. |
| `experiments/` | Experiment plan and run metadata. |
| `results/` | Final result tables, plots, and findings used for paper claims. |
| `reports/iteration/` | Iteration-by-iteration progress notes and evidence records. |
| `papers/final_paper/` | Paper-building workspace with section drafts, claim tables, figures, and supervisor memos. |
| `papers/overleaf_ieee_journal/` | Clean Overleaf/IEEE manuscript source. |
| `sources/` | Source logs, literature/dataset inventory, and local reference-paper folders. |
| `blockchain_xai_course/` | Learning syllabus, notes, labs, and PDFs for blockchain, XAI, and prototype fundamentals. |

## Current Technical Status

Completed:

- Synthetic inter-agency access request generator.
- RBAC baseline and ABAC/PBAC-style policy oracle.
- XAI decision artifacts for allow/deny/escalate access decisions.
- Mutable log, signed hash-chain log, and permissioned blockchain-style audit.
- Off-chain record pointer and commitment workflow.
- Baseline comparisons, ablations, attacks, NS-PI drift tests, sensitivity
  analysis, workload stress tests, and XAI/audit-quality metrics.
- IEEE-style Overleaf paper draft with introduction, related work,
  methodology, results/discussion, limitations, and conclusion.

Not completed:

- Real CCTNS/ICJS/FIR/police-access-log experiments.
- Live Hyperledger Fabric deployment.
- Legal-compliance proof.
- Production security validation.
- Real-world police pilot.

## Current Core Finding

The prototype supports a limited but useful research claim:

> Blockchain/hash-chain-style integrity detects ordinary log tampering, but
> validly re-signed compromised-signer corruption can remain invisible to
> integrity-only audit methods. A trusted raw-attribute policy oracle and
> NS-PI drift detection catch different parts of that failure mode under
> different visibility assumptions. The XAI layer is strong as a structured
> audit trace, while natural-language explanation text still needs improvement.

## What Goes To GitHub

Tracked in Git:

- source code, tests, scripts, paper source, result tables, plots, reports,
  experiment plans, research notes, and Overleaf package.

Kept local but not committed:

- downloaded research-paper PDFs;
- raw prototype run folders that can be regenerated;
- cache files such as `.pytest_cache`, `.mypy_cache`, `.ruff_cache`,
  `__pycache__`, `.coverage`, and `.DS_Store`.

## Hard Boundary

Do not claim real police deployment, legal compliance, production security,
state-of-the-art performance, real police-data performance, or crime/suspect
prediction. Current results are from synthetic reproducible access-governance
experiments only.
