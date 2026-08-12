# 05 Research Gap and Novelty Position

Revised: 2026-08-09
Status: aligned to the implemented system. Supersedes the 2026-05-12 version,
which framed the project as a proposed overlay before the system existed.

---

## 1. What a reviewer will treat as already known

Nothing in this list may be claimed as a contribution.

1. India operates national digital policing and justice infrastructure through
   CCTNS and ICJS.
2. Blockchain has been applied to digital evidence management and chain of
   custody.
3. Hyperledger Fabric is an established permissioned platform with a documented
   endorsement and ordering architecture.
4. Attribute-based access control is a mature model with a NIST specification.
5. Combinations of Fabric with attribute-based access control already exist in
   the literature.
6. The limitations of predictive policing, and the argument for interpretable
   models in high-stakes settings, are both well documented.
7. Aggregate crime analytics on public Indian data is an existing research area.

---

## 2. Framings that must be rejected

**"Police records on a blockchain."** A permissioned ledger replicates every
write to every organisation permanently. Placing case narratives, witness or
victim identities, juvenile records, or forensic media on-chain worsens
confidentiality and makes legally required deletion impossible.

**"Crime prediction from public data."** Public aggregate statistics cannot
support individual-level inference, and predictive policing is subject to
documented feedback effects.

**"A CCTNS replacement."** CCTNS and ICJS operate at national scale. A
replacement claim is neither credible nor evaluable here.

**"Explainability establishes trust."** Explanations can be incomplete or
misleading, and stakeholder needs differ. Explanation is useful here only
because it is committed as verifiable evidence, not because it is displayed.

---

## 3. The gap

Existing work has established that a permissioned ledger can hold access-control
state and that attribute-based policy can govern record access. What the
literature has treated as an implementation detail is **where the authorisation
decision is computed, and what the requester is permitted to assert about
themselves.**

Two consequences follow, and both are structural rather than incidental.

When a decision is computed off-chain and the ledger stores the outcome, the
ledger's guarantee covers the *record of* the decision, not the decision. An
integrity check confirms that the entry was not altered after writing. It
cannot establish that the entry was correct when written.

When subject attributes travel in the transaction payload, the requester is
asserting their own authority, and the policy engine is trusting the party the
policy exists to constrain.

The gap this project addresses is therefore:

> There is limited work in which the authorisation decision for sensitive
> inter-agency record access is itself the endorsed on-chain computation, with
> subject attributes bound to the requester's issued certificate rather than
> supplied in the request, and with the justification for the decision committed
> atomically alongside it — together with an analysis of what endorsement
> consensus does and does not establish about the resulting record.

**Verification task before submission.** This positioning is stated against the
literature surveyed in `01_literature_review.md` and `02_literature_matrix.csv`.
Before any venue submission, each of the Fabric-plus-ABAC works cited must be
checked individually on two specific points — whether policy evaluation occurs
in chaincode or in an off-chain service, and whether subject attributes derive
from certificate attributes or from request parameters. The claim must be
narrowed to whatever that check supports. It is a positioning claim, not yet a
verified survey result.

---

## 4. Problem statement

How can access to sensitive criminal-justice records shared between departments
be authorised such that the decision is jointly computed and endorsed by
multiple organisations, the requester cannot assert their own authority, the
grounds of every decision are preserved as verifiable evidence, raw records
never enter the shared ledger, and a reviewer months later can reconstruct and
independently check what was decided and why?

---

## 5. Research questions

**RQ1.** Can authorisation be executed as an endorsed on-chain computation for
a realistic multi-agency criminal-justice policy, and what does that cost in
latency and storage?

**RQ2.** What is gained by binding subject attributes to issued certificates
rather than accepting them from the request?

**RQ3.** Does committing decision and justification atomically produce audit
evidence that a reviewer can independently verify without access to the
underlying records?

**RQ4.** What classes of failure remain undetectable to a correctly functioning
endorsement policy, and what does that imply about the guarantees a permissioned
audit trail actually provides?

**RQ5.** Can read and search activity — which generates no ledger transactions
— be made accountable without placing that activity on-chain?

---

## 6. Novelty position

The contribution is the system and the security result it makes visible, not
any of its constituent techniques.

- **Locus of decision.** Authorisation is the endorsed transaction. Three of
  five organisations independently execute the same deterministic policy and
  must agree before any decision exists.
- **Locus of authority.** Identity attributes are read from the certificate
  issued by the requester's own department. The requester supplies intent —
  action and purpose — never authority.
- **Binding of justification.** Reason code, decisive attributes, counterfactual,
  and policy version are produced by the same evaluation as the outcome and
  committed in the same state write, so decision and explanation cannot diverge.
- **Accountability for reads.** An anchored off-chain hash chain gives searches
  and reads tamper-evidence without putting them on-chain.
- **A negative result about consensus.** Endorsement establishes agreement on a
  transaction, not the integrity of the premises it was evaluated against. A
  compromised departmental certificate authority yields a decision that is
  unanimously and correctly endorsed, fully consistent, and wrong.

The last item is the sharpest finding and the one most likely to generalise
beyond this application, because it concerns what a permissioned audit trail
can be relied upon to prove.

---

## 7. What must not be claimed

- Invention of attribute-based access control, permissioned ledgers, or
  explainable AI.
- Any comparison with, or improvement over, CCTNS, ICJS, or a deployed system.
- Deployment readiness, legal compliance, or evidentiary admissibility.
- Validation on real records, real access logs, or real officer identities.
- Formal privacy guarantees.
- Performance representative of a distributed deployment; the current network
  is single-host with one ordering node.
- Any crime, suspect, or risk prediction.

---

## 8. Title direction

**SEBA-XAI: On-Chain Policy Evaluation with Certificate-Bound Attributes for
Inter-Agency Criminal-Justice Record Access**

Alternatives:

1. When Consensus Is Not Enough: Endorsed Access Decisions and Their Limits in
   Permissioned Criminal-Justice Record Sharing
2. Deciding On-Chain: Certificate-Bound Attribute Authorisation with Committed
   Justification on Hyperledger Fabric
3. SEBA-XAI: A Permissioned-Blockchain System for Explainable Inter-Agency
   Access Governance
