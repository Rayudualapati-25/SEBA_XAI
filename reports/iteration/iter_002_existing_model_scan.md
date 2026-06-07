# Iteration 002: Existing Model Scan

Date: 2026-05-17  
Status: completed external model scan; no experiments run.

## Goal

Find whether a real-world model or prototype already exists that combines blockchain, security/privacy/access control, and explainable AI for police, legal, forensic, or public-safety decision workflows.

## What Worked

- Found two close blockchain+XAI audit references:
  - BAXDT: Blockchain-assisted explainable decision traces.
  - Blockchain-based auditing of legal decisions supported by explainable AI and generative AI tools.
- Found two strong police/criminal-justice blockchain references:
  - LEChain.
  - Two-Level Blockchain System for Digital Crime Evidence Management.
- Found public code for LEChain and BlendSPS.
- Clarified that the strongest testable path is not direct replication of a complete police model, but a SEBA-XAI simulator that adapts decision traces and lawful evidence access patterns.

## What Failed or Is Weak

- No exact CCTNS/ICJS-compatible blockchain-security-XAI public implementation was found.
- BAXDT appears highly relevant and claims open-source simulation, but the repository URL was not verified from accessible metadata during this scan.
- The strongest police/evidence systems do not include XAI.
- The strongest XAI+blockchain systems are not police access-governance systems.
- No experiment, benchmark, metric, or result has been generated locally yet.

## Evidence Artifacts Created

- `14_existing_models_for_testing.md`

## Interpretation

The literature gap remains valid: current work covers parts of the problem, but not a reproducible India-oriented police access-governance overlay that treats blockchain audit, security/access control, and XAI decision justification as equal pillars.

The most defensible implementation path is:

1. implement a synthetic access-control simulator;
2. use BAXDT-style decision traces for explanation artifacts;
3. use LEChain/two-level evidence-management ideas for off-chain sensitive data and on-chain commitments;
4. compare against RBAC, ABAC/PBAC, and signed-log baselines;
5. run tamper tests and ablations before writing paper claims.

## Next Experiment

Create the first runnable `synthetic_access_sim` implementation with:

- deterministic workload generation;
- policy oracle;
- baseline decisions;
- hash-chain audit log;
- explanation artifacts;
- metrics export.

Required first run:

- seed: `42`;
- request count: `1000`;
- variants: `rbac_mutable`, `abac_mutable`, `abac_hashlog`, `seba_xai_local_ledger`;
- output folder: `experiments/runs/iter_003_synthetic_access_sim_seed42/`.
