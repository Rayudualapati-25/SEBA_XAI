# Iteration 019: Solid Research Roadmap

Date: 2026-05-28  
Status: roadmap created  
Scope: define how to turn the SEBA-XAI prototype into a defensible research paper

## What Was Done

Created:

```text
15_solid_research_roadmap.md
```

The roadmap explains:

- what is already solid in the current prototype;
- what is still weak;
- the final research scope;
- research questions and hypotheses;
- additional experiments needed;
- reviewer objections and answers;
- four-month plan;
- immediate coding tasks;
- minimum acceptance gate before calling the research solid.

## Key Decision

The research should be framed as:

> A reproducible secure-systems and responsible-AI evaluation of explainable, blockchain-audited access governance for sensitive inter-agency police records.

It should not be framed as:

> AI blockchain crime prediction for police.

## Current Strength

The project already has:

- synthetic access-control workload;
- RBAC/ABAC/PBAC comparison;
- signed hash-chain and blockchain-style audit comparison;
- off-chain pointer verification;
- XAI explanation hash logging;
- metadata exposure comparison;
- policy ablation;
- latency/storage evidence;
- paper tables, plots, and result narrative.

## Remaining Work

The roadmap identifies these required hardening tasks:

- multi-seed robustness;
- scenario stress tests;
- stronger adversary/tamper tests;
- XAI completeness and stability evaluation;
- metadata inference/leakage attack;
- audit reconstruction evaluator;
- regenerated paper evidence pack after new experiments.

## Evidence Boundary

The roadmap keeps the current research honest:

- no real police data claim;
- no CCTNS/ICJS deployment claim;
- no legal-compliance claim;
- no production cryptography claim;
- no SOTA crime-prediction claim.

## Next Step

Start the immediate coding tasks from the roadmap:

1. implement a multi-seed experiment runner;
2. implement audit reconstruction evaluator;
3. implement XAI evaluation script;
4. implement metadata leakage inference experiment.

