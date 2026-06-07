# Threat Model (Draft v1)

Status: draft text for the SEBA-XAI paper. Not final camera-ready prose.
Evidence basis: `reports/iteration/iter_034_threat_model_results_notes.md`,
`results/FINDINGS.md`, and the artifacts under `results/tables/`.

All quantitative claims in the companion Results draft cite a local artifact
path. This section defines the actors, assets, trust assumptions, and attacker
capabilities that those results are measured against. Statements that are
analysis rather than a measured value are tagged `[INTERPRETATION]`.

## 1. System Scope and Assets

SEBA-XAI is evaluated as a synthetic-workload research prototype for
explainable, blockchain-style-audited access governance over sensitive
police and criminal-justice records. The prototype is an overlay: raw records
remain off-chain, and the audit layer holds only commitments, decision labels,
explanation hashes, and anchor hashes.

The protected assets in the evaluation are:

- the correctness of recorded access decisions (allow / deny / escalate);
- the integrity of the append-only audit record;
- the reviewability of each decision through its explanation and audit trail;
- the confidentiality of sensitive metadata in the published ledger view.

`[INTERPRETATION]` We position the prototype as compatible with CCTNS/ICJS-style
inter-agency workflows. This is a design-positioning statement carried from
`research_pack/00_problem_understanding.md` and `CONTRIBUTION.md`; it is not a measured
property of any operational system, and the prototype is not evaluated on real
records or real infrastructure.

## 2. Actors and Trust Assumptions

| Actor / component | Trust assumption used in the evaluation |
|---|---|
| Requesting officer | Intent is untrusted. A request's legitimacy depends on policy attributes: role, rank, jurisdiction, case assignment, purpose, credential status, record sensitivity, and approval state. |
| Declared policy oracle (Step 2) | Treated as the reference definition of the correct decision for each synthetic request. It is the labeling function for the benchmark, not a claim of real-world policy correctness. |
| Ledger integrity layer (signed hash-chain, blockchain-style audit, CT-style log) | Trusted to detect modification, insertion, deletion, or reordering of recorded events, conditional on the signing keys remaining uncompromised. |
| Fabric+ABAC and ABAC re-execution baselines | Re-evaluate policy over the recorded canonical output and therefore trust that recorded output. |
| Trusted raw-attribute policy oracle | Assumes a separate, uncompromised view of the original request attributes, independent of the audit log. This is a strong assumption and is presented as a baseline, not as a free operational property. |
| NS-PI drift detector | Has log-only visibility: it observes the signed decision log and does not assume any independent raw-attribute view. |
| Signing authority / enforcement node | May be compromised in the compromised-signer threat (Section 4). |

`[INTERPRETATION]` The distinction between the trusted raw-attribute oracle and
NS-PI is the central design point of the threat model: the two detectors
succeed under different visibility assumptions, so they should be read as
complementary rather than competing.

## 3. Ordinary Tamper Attacks

The benchmark first considers attackers who modify the recorded audit stream
without controlling the signing keys. These attacks are enumerated in the
catalog and recorded per seed in `results/tables/full_grid_raw.csv`:

- `replay_approval_token` — reuse of a previously valid approval token;
- `backdate_request` — alteration of a recorded timestamp;
- `swap_explanation_hash` — substitution of explanation/anchor material;
- `collude_block_signature` — manipulation of block-level signing structure;
- `revocation_race` — exploitation of revocation timing;
- `metadata_inference` — a read-only inference attack on the published ledger
  view, scored separately because it does not modify the record.

`[INTERPRETATION]` These attacks define the regime where cryptographic and
re-execution defenses are expected to be effective, because each one either
breaks a hash/commitment or changes a value that policy re-execution recomputes.
Establishing that these defenses work here is what makes the compromised-signer
blind spot (Section 4) meaningful rather than an artifact of a broken baseline.

## 4. The Compromised-Signer Attacker

The decisive attacker in this work controls the signing authority or an
enforcement node. This attacker:

1. corrupts policy output by flipping a fraction of `deny` / `escalate`
   decisions to `allow`; and
2. re-signs a valid-looking canonical log so that the chain remains internally
   consistent and correctly signed.

Because the resulting log is validly signed, ledger-only integrity checks pass
by construction: there is no broken hash, no inconsistent link, and no failed
signature for them to detect.

`[INTERPRETATION]` The realism of this attacker — an insider with signing-key
access, or a compromised enforcement node — is a modeling assumption. The
prototype demonstrates the mechanical detection asymmetry only; it does not
measure how often such compromise occurs in practice, and the paper must argue
the plausibility of the model in prose rather than treat it as established
incidence.

## 5. Detector Visibility Summary

| Detector | Visibility | Catches ordinary tamper? | Catches compromised-signer? |
|---|---|---|---|
| Ledger integrity / ABAC re-execution | Recorded canonical log | Yes (see Results) | No, by construction |
| Trusted raw-attribute oracle | Independent raw request view | Yes | Yes |
| NS-PI drift | Signed decision log only | Limited (distribution-level) | Yes, under conditions in Results |

`[INTERPRETATION]` NS-PI is a distribution-level detector with the weakest
visibility of the three, so it is expected to be the weakest detector for
single-event tampering. Its contribution is narrow: it is the only log-only
mechanism in the comparison that responds to validly re-signed
compromised-signer corruption, and it does so without an independent raw view.

## 6. Out-of-Scope Claims

The threat model deliberately excludes, and the paper does not assert:

- correctness on real police or criminal-justice records;
- readiness for operational use in CCTNS/ICJS or any production system;
- legal admissibility of the audit trail;
- formal privacy or production cryptographic properties;
- comparative claims against the broader literature beyond the implemented
  baselines.

All evaluation is on synthetic workloads, and all timing values reported in the
Results draft are local script runtimes, not infrastructure measurements.
