# SEBA-XAI: Secure Explainable Blockchain-Audited Access Governance

SEBA-XAI is a research prototype and paper workspace for secure, explainable,
auditable inter-agency police-record access governance. The project is framed
for CCTNS/ICJS-style Indian policing infrastructure, but it does **not**
replace CCTNS/ICJS and does **not** use real police records.

Current evidence status: reproducible synthetic experiments, baselines,
ablations, attack tests, sensitivity analysis, workload stress tests, and
XAI/audit-quality metrics exist under `results/`, `reports/iteration/`,
`scripts/`, `src/seba/`, and `tests/`.

## Research Direction

The strongest publishable angle is:

> A CCTNS/ICJS-compatible secure overlay for sensitive inter-agency access
> requests, combining RBAC/ABAC/PBAC-style policy decisions, off-chain
> sensitive records, permissioned blockchain-style audit commitments, and
> explainable access-decision artifacts.

This is not an "AI predicts criminals" paper. It is an access-governance,
auditability, security, and explainable-decision paper.

## Repository Map

| Path | What it contains |
|---|---|
| `00_START_HERE.md` | Quick guide to the whole repository. |
| `CONTRIBUTION.md` | Current contribution statement and novelty boundary. |
| `REPRODUCE.md` | Commands to reproduce experiments. |
| `SESSION_HANDOFF.md` | Current handoff/progress state. |
| `research_pack/` | Original research notes: problem, literature, datasets, gap, architecture, methodology, metrics, ethics, paper outline, and learning plan. |
| `src/seba/` | Main Python implementation. |
| `prototype/synthetic_access_sim/` | Prototype scripts for synthetic access workflow and audit layers. |
| `scripts/` | Reproduction, aggregation, figure, report, and Overleaf-packaging scripts. |
| `tests/` | Automated tests. |
| `experiments/` | Experiment plan and run metadata. |
| `results/` | Final result tables, plots, and honest findings. |
| `reports/iteration/` | Iteration-by-iteration research and implementation logs. |
| `papers/final_paper/` | Draft sections, claim-source material, figures, and supervisor memos. |
| `papers/overleaf_ieee_journal/` | Clean IEEE/Overleaf LaTeX project. |
| `papers/seba_xai_ieee_journal_overleaf.zip` | Uploadable Overleaf zip. |
| `papers/target_venue_shortlist.csv` | Current venue shortlist. |
| `sources/` | Source logs, literature inventory, dataset inventory, and local paper-reference folders. |
| `blockchain_xai_course/` | Learning syllabus, notes, labs, and PDFs for blockchain/XAI/prototype fundamentals. |

## Current Prototype Components

- Synthetic police-style access request generator.
- RBAC baseline.
- ABAC/PBAC-style policy oracle.
- Explainable allow/deny/escalate decision artifacts.
- Mutable audit log baseline.
- Signed append-only hash-chain baseline.
- Permissioned blockchain-style audit simulation.
- Off-chain record pointer and commitment layer.
- Metadata-exposure, latency, and storage measurements.
- Adversarial tests, including validly re-signed compromised-signer behavior.
- NS-PI log-only drift detection.
- XAI/audit-quality evaluation.

## Main Results To Use Carefully

The current results support only limited synthetic-benchmark claims:

- RBAC role/action-only access is weak in the synthetic sensitive-record
  workload.
- ABAC/PBAC-style contextual policy matches the declared synthetic oracle.
- Signed hash chains and blockchain-style audit detect controlled ordinary
  tamper cases.
- Integrity-only logs miss the validly re-signed compromised-signer case.
- NS-PI drift and a trusted raw-attribute policy oracle detect that case under
  different visibility assumptions.
- NS-PI still misses low-rate and small targeted corruption.
- Structured XAI trace quality is strong, but natural-language explanation text
  still needs improvement.

See `results/FINDINGS.md` and `papers/overleaf_ieee_journal/sections/results_discussion.tex`.

## Reproduce

Install dependencies and run:

```bash
make test
make lint
make typecheck
make reproduce
make figures
make package-overleaf
```

The full reproduction regenerates multi-seed results for seeds
`7, 21, 42, 99, 123`.

## Paper Work

Current Overleaf source:

- `papers/overleaf_ieee_journal/main.tex`
- `papers/overleaf_ieee_journal/sections/introduction.tex`
- `papers/overleaf_ieee_journal/sections/related_work.tex`
- `papers/overleaf_ieee_journal/sections/proposed_methodology.tex`
- `papers/overleaf_ieee_journal/sections/results_discussion.tex`
- `papers/overleaf_ieee_journal/sections/limitations.tex`
- `papers/overleaf_ieee_journal/sections/conclusion.tex`

Uploadable zip:

- `papers/seba_xai_ieee_journal_overleaf.zip`

## Local-Only Reference Material

Downloaded research papers and raw prototype run folders are organized locally
but ignored by Git:

- `sources/downloaded_research_papers_2026-05-29/`
- `sources/reference_papers/`
- `prototype/runs/`

The repo tracks source logs, result summaries, generated tables, and scripts so
the evidence can be reproduced without committing bulky reference PDFs or raw
run artifacts.

## Hard Boundary

Do not claim:

- real CCTNS/ICJS deployment;
- real FIR/police-record testing;
- legal compliance;
- production security;
- state-of-the-art performance;
- crime prediction or suspect prediction.

This is currently a synthetic benchmark and research prototype.
