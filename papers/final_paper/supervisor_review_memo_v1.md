# Supervisor Review Memo v1

Created: 2026-05-30
Paper: SEBA-XAI

## 1. Current Status

The paper draft now has:

- a complete combined manuscript draft: `papers/final_paper/paper_draft_v1.md`;
- six generated SVG figures;
- a figure/source manifest;
- a cleaned IEEE-style reference list;
- verified reference metadata notes;
- five-seed workload/policy-mix stress evidence;
- full reproduction, lint, and test verification.

This is ready for supervisor review as a research draft. It is not yet a final
conference/journal submission.

## 2. Main Claim To Defend

SEBA-XAI should be defended as:

> A synthetic, reproducible research prototype for blockchain-audited,
> explainable access governance over sensitive inter-agency police records,
> where blockchain-style audit, ABAC/PBAC checks, trusted policy
> re-evaluation, and NS-PI log-only drift monitoring catch different failure
> modes under different visibility assumptions.

Do not defend it as:

- a crime-prediction paper;
- a real CCTNS/ICJS deployment;
- a legal-compliance proof;
- a production blockchain system;
- a claim that NS-PI is better than blockchain overall.

## 3. Figure Placement Decision

Recommended main-paper figures:

1. Fig. 1: SEBA-XAI architecture.
2. Fig. 2: detector visibility / threat model.
3. Fig. 3: compromised-signer detection.
4. Fig. 5: XAI and audit reviewability metrics.

Recommended appendix or backup figures:

1. Fig. 4: NS-PI sensitivity curve.
2. Fig. 6: workload-size stress curve.

Reason: the main paper should first prove the system idea, the threat-model
visibility distinction, the core compromised-signer result, and the XAI
reviewability measurement. The sensitivity and stress figures are important,
but they mainly support limitations.

## 4. Strong Parts

- The research direction is narrowed and defensible.
- The three pillars are now technically connected instead of being listed
  separately.
- The blockchain role is correctly limited to audit commitments.
- Raw records remain off-chain.
- Security is evaluated through policy checks, audit attacks, baselines, and
  tamper tests.
- XAI is measured through trace completeness, counterfactual validity,
  stability, and audit reconstruction.
- The strongest result is not overclaimed: NS-PI is useful only under
  log-only compromised-signer visibility.

## 5. Weak Parts To Admit

- All experiments are synthetic.
- The policy oracle is not validated by police/legal experts.
- The permissioned blockchain is a local simulation, not a Fabric deployment.
- Metadata privacy is not formally proved.
- NS-PI misses small and targeted attacks.
- Natural-language explanation text still omits some decisive attributes.

## 6. Supervisor Questions To Ask

1. Is the narrowed SEBA-XAI contribution acceptable for an M.Tech/IEEE-level
   paper?
2. Should the paper emphasize access governance more than NS-PI?
3. Are four main figures enough, with sensitivity/stress figures moved to an
   appendix?
4. Should the paper target an applied security venue, public-safety AI venue,
   or blockchain/access-control venue?
5. Does the introduction need more India-specific legal/policy context, or is
   the current CCTNS/ICJS framing enough?

## 7. Next Work After Supervisor Feedback

- If the supervisor approves the direction: polish the manuscript into the
  target template.
- If the supervisor wants stronger implementation evidence: build a small
  real Fabric test-network experiment separately from the current local audit
  simulation.
- If the supervisor wants stronger policy realism: ask a domain expert to
  review the synthetic access-policy schema before making any stronger domain
  claim.
