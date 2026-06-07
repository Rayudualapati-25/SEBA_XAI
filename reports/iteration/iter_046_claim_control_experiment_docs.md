# Iteration 046: Claim Control and Experiment Documentation Reconciliation

Date: 2026-06-05

## Scope

This iteration corrected paper-claim control and stale experiment documentation before any further experiments were run.

No new experiments were executed in this iteration. No new benchmark numbers, deployment claims, legal claims, or dataset claims were added.

## Files Updated

| File | Purpose |
|---|---|
| `papers/final_paper/claim_control_memo.md` | Created a strict claim-control memo for the SEBA-XAI paper. |
| `experiments/experiment_plan.md` | Updated the active experiment plan to reflect completed synthetic benchmark evidence and remaining publication-critical checks. |
| `08_experiment_plan.md` | Updated the root research-pack experiment plan so it no longer presents the work as only planned. |
| `papers/final_paper/publication_readiness_agent_plan.md` | Clarified that the old experiment-plan inconsistency was a historical audit finding. |

## What Worked

- The paper claim is now narrowed to a synthetic, reproducible benchmark and prototype for explainable policy-aware audit in sensitive inter-agency access governance.
- The documentation now separates completed synthetic evidence from deferred work such as real CCTNS/ICJS deployment, real FIR/police records, aggregate NCRB modeling, and live Hyperledger Fabric validation.
- The claim-control memo lists allowed claims, forbidden claims, research questions, baseline assumptions, and current evidence boundaries.

## What Is Still Weak

- The next reproduction freeze has not been run in this iteration.
- A full artifact-to-claim table for the paper still needs to be built.
- The policy oracle is still a benchmark labeling function, not an officially validated police/legal policy.
- The blockchain layer is still a local permissioned-audit simulation, not a live Fabric network.
- Metadata privacy remains a prototype leakage estimate, not a formal privacy guarantee.
- Natural-language explanation coverage remains a measured weakness unless the explanation renderer is improved and rerun.

## Next Step

Run the publication freeze in this order:

1. `make test`
2. `make lint`
3. `make typecheck`
4. `make reproduce`
5. `make figures`

After that, create an artifact-to-claim table mapping every paper claim to exact CSV, JSON, log, plot, or source-note evidence.

## Verification Notes

The current documentation should no longer describe the active experiment plans as if no experiments exist. Any remaining mention of absent experiments should be historical or explicitly scoped to a deferred part of the project.
