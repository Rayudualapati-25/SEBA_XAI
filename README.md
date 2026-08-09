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
| `seba_fabric_workspace/crime-records-network/` | **Live Hyperledger Fabric implementation.** Five department organisations, three chaincode contracts, REST API, web interface, measurement scripts. Has its own `README.md`. |
| `seba_fabric_workspace/prototype/` | Earlier Python prototype and its run artifacts, cited for provenance by several result tables. |
| `Learn/` | Learning material only: blockchain/XAI course notes, Solidity practice, offline Fabric documentation. Not cited by the paper. |

## Live Fabric Implementation

`seba_fabric_workspace/crime-records-network/` addresses the limitation stated in
Section V of the paper, that the blockchain layer was "a local permissioned audit
simulation, not a live Hyperledger Fabric deployment."

Five department organisations (police, forensics, prosecution, court, oversight)
each run their own certificate authority and CouchDB-backed peer on Fabric
2.5.16, with MAJORITY (3 of 5) endorsement. Access decisions, their explanation
artifacts and integrity commitments are recorded on the ledger; record payloads
remain in off-chain agency storage. Officer role, clearance, jurisdiction and
case assignments are carried inside X.509 certificates and read by the chaincode
from the signed identity rather than from request parameters.

| Document | Contents |
|---|---|
| `crime-records-network/README.md` | Requirements and reproduction commands |
| `crime-records-network/docs/architecture.md` | Components, the eight-rule decision flow, code map |
| `crime-records-network/docs/evaluation.md` | Metrics, method, and limitations |
| `crime-records-network/docs/walkthrough.md` | Demonstration procedure |

Measured results, with qualifications recorded in
`crime-records-network/experiments/results/`:

| Quantity | Simulation (paper) | Live implementation |
|---|---|---|
| Audit build latency p50, marginal | 11.10 ms | 72.69 ms |
| Verification latency p50 | 2.50 ms | 3.99 ms |
| Storage per audit event | 353.50 B | 857 B |
| Replayed attacks detected | — | 6 of 6 |

Verification: 70 chaincode unit tests, 48 API integration tests against the live
network, and an 11-step end-to-end scenario.

Two qualifications that must accompany the table. The end-to-end build latency is
2072 ms, of which 2000 ms is the orderer's configured `BatchTimeout`; the marginal
figure above is the quantity comparable with the simulation. Storage is not
like-for-like, because this implementation commits the full explanation artifact
inline.

An explanation layer using a locally hosted language model rewords committed
decisions for display. The model does not make decisions: the deterministic
chaincode policy engine decides and commits, and the generated text is validated
against the committed artifact before display, with deterministic template
wording used when validation fails.

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
