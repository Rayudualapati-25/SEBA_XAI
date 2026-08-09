# SEBA-XAI: Explainable Policy-Aware Audit for Secure Inter-Agency Police Data Access Governance

Research artifact for the SEBA-XAI paper. The work addresses a governance
problem rather than a prediction problem: when a sensitive criminal-justice
record is requested across agencies, how should the request be decided, recorded,
and later explained to a reviewer.

Job role alone is not sufficient to decide access. A sub-inspector and a
constable may request the same case file and should not receive the same answer;
the same officer may be permitted for one purpose and denied for another; and
some records must remain closed to one department while another may read them.

The project is framed for CCTNS/ICJS-compatible Indian policing infrastructure.
It does not replace CCTNS or ICJS, and it uses no real police records.

---

## What is novel

The literature already provides the individual building blocks: permissioned
ledgers and blockchain audit, ABAC and XACML-style policy, off-chain storage, and
explainable AI for high-stakes decisions. The contribution of this work is not
any one of those mechanisms.

**1. Joint evaluation in one inter-agency access-governance workflow.** Access
control, tamper-evident audit, and explanation are normally studied separately.
This work evaluates them together on a single CCTNS/ICJS-compatible request
workflow, so that the interaction between them can be measured rather than
assumed.

**2. Isolating an attack that integrity checking cannot reach.** The specific gap
the paper identifies is what happens when an audit log is *validly re-signed
after the policy output has been corrupted*. An attacker who controls the signing
component can alter a recorded decision and sign it again: the entry verifies
correctly even though the decision it records was never made. Ordinary integrity
checking passes, and the log is wrong.

**3. The measured consequence.** Across five seeds of a synthetic workload, every
integrity-based defence tested (signed hash chain, blockchain-style audit,
CT-style log, ABAC re-execution) detects ordinary tampering at 1.00 but obtains
**0.00** detection for the re-signed attack. Two methods that examine the
decisions themselves rather than the log's integrity — a statistical drift
detector over the decision log, and a trusted raw-attribute policy oracle —
obtain **1.00** under stronger visibility assumptions.

The conclusion this supports is a separation that is easy to conflate in
practice: **integrity of the log and correctness of the decision are different
properties, and an evaluation that measures only tamper detection has not
measured whether decisions are right.**

**4. Explanation treated as audit evidence, not presentation.** Each decision
stores its decisive attributes, reason code, policy version, and counterfactual
as a structured artifact hash-linked to the audit event. A reviewer can check the
grounds of a decision without opening the underlying record.

### What is deliberately not claimed

NS-PI, the drift detector, is **not** an overall tamper-detection winner. Its
severity-weighted adversarial audit score is 0.2500, against 0.7917 for the
integrity-based defences and 1.0000 for the trusted policy oracle. Its value is
narrower and specific: it is the only method that raises an alarm when the
auditor can see nothing but the signed decision trace. It is a complementary
log-only signal, not a replacement for trusted policy re-evaluation. See
`CONTRIBUTION.md` for the evidence-locked statement and the broader claim that
the evidence did not support.

---

## Contributions, as stated in the paper

1. **Layered access-control service.** Combines role-based, attribute-based and
   policy-based rules, returning *allow*, *deny* or *escalate* for inter-agency
   record requests, so decisions follow context rather than role.
2. **Permissioned blockchain audit layer.** Each decision event records the
   request identifier, decision hash, explanation hash, policy version, approval
   reference where one exists, and record commitment. Raw records remain
   off-chain with the holding agency.
3. **Explainable decision service.** Decisive attributes, reason code, policy
   version and counterfactual information stored as a structured artifact
   hash-linked to the audit event.
4. **Reproducible adversarial benchmark.** Ordinary tampering attacks plus the
   validly re-signed compromised-signer attack, with defences compared under
   explicitly stated visibility assumptions.

---

## Live Hyperledger Fabric implementation

`seba_fabric_workspace/crime-records-network/`

The paper states in Section V that its blockchain layer is "a local permissioned
audit simulation, not a live Hyperledger Fabric deployment." This implementation
removes that limitation.

Five department organisations — police, forensic science, prosecution,
judiciary, and oversight — each run their own certificate authority and
CouchDB-backed peer on Fabric 2.5.16, with MAJORITY (3 of 5) endorsement and a
private data collection for evidence detail. Three chaincode contracts provide
the record registry, the eight-rule access policy, and audit verification.

Officer role, rank, station, jurisdiction, clearance, credential status and case
assignments are carried inside X.509 certificates issued by each department's
certificate authority, and the chaincode reads them from the signed identity
rather than from request parameters. Access therefore depends on cryptographic
identity rather than on a database row that an administrator could edit.

| Quantity | Simulation (paper) | Live implementation |
|---|---|---|
| Audit build latency p50, marginal | 11.10 ms | 72.69 ms |
| Verification latency p50 | 2.50 ms | 3.99 ms |
| Storage per audit event | 353.50 B | 857 B |
| Replayed attacks detected | — | 6 of 6 |

Two qualifications belong with that table. End-to-end build latency is 2072 ms,
of which 2000 ms is the orderer's configured `BatchTimeout`; the marginal figure
is the quantity comparable with the simulation, and quoting the end-to-end figure
as the cost of the audit design would be incorrect. Storage is not like-for-like,
because this implementation commits the full explanation artifact inline.

Verification: 70 chaincode unit tests, 48 API integration tests against the live
network, an 11-step end-to-end scenario, and a six-attack replay.

Beyond the paper's design, the implementation adds a tamper-evident record of
**reads and searches**. These are ledger queries and produce no transaction, so
who searched for a case would otherwise leave no trace. They are recorded in a
hash chain whose head is periodically anchored on-chain, which makes editing or
deleting an entry detectable.

An explanation layer uses a locally hosted language model to reword committed
decisions into plain language. The model does not participate in the decision:
the deterministic chaincode policy engine decides and commits first, and
generated text is validated against the committed artifact before display, with
deterministic template wording used when validation fails.

Documentation: `crime-records-network/README.md` for reproduction,
`docs/architecture.md` for the decision flow and code map, `docs/evaluation.md`
for metrics and limitations, `docs/walkthrough.md` for a demonstration sequence.

---

## Repository map

| Path | Contents |
|---|---|
| `00_START_HERE.md` | Orientation for the repository |
| `CONTRIBUTION.md` | Evidence-locked contribution statement and novelty boundary |
| `REPRODUCE.md` | Commands to reproduce the experiments |
| `SESSION_HANDOFF.md` | Current progress state |
| `seba_fabric_workspace/crime-records-network/` | Live Fabric implementation |
| `seba_fabric_workspace/prototype/` | Earlier Python prototype, code and run summaries |
| `src/seba/` | Python research package: NS-PI, attacks, baselines, scoring, XAI quality metrics |
| `tests/` | Python test suite |
| `experiments/` | Experiment plan and run metadata |
| `results/` | Result tables, plots and findings |
| `research_pack/` | Problem framing, literature review, datasets, methodology, metrics, ethics |
| `reports/iteration/` | Iteration-by-iteration research log |
| `papers/` | IEEE paper: LaTeX sources, figures, supervisor memos |
| `scripts/` | Reproduction, aggregation, figure and packaging scripts |
| `sources/` | Literature and dataset inventories |

---

## Reproduce

Python experiments:

```bash
pip install -e ".[dev]"
pytest
```

See `REPRODUCE.md` for the full experiment sequence.

Live Fabric implementation:

```bash
cd seba_fabric_workspace/crime-records-network
make up && make deploy && make seed
make test && make smoke
```

`make` with no target lists every command.

---

## Scope and limitations

- Real police access logs and records are not publicly available, so the
  evaluation uses a reproducible synthetic workload. No claim is made about
  performance on operational CCTNS or ICJS data.
- The policy is a declared benchmark policy, not validated operational police
  policy.
- The paper's blockchain results are from a simulated permissioned ledger; the
  live implementation in this repository is a single-host deployment with a
  single-node ordering service, so its latency figures do not represent a
  distributed deployment.
- The compromised-signer attack is not replayed against the live network. There
  it would require a compromised MSP administrator key, a strictly stronger
  assumption than the simulation makes.
- The metadata-exposure score is a schema-level proxy, not a formal privacy
  proof. The explanation text-coverage metric is a weak textual proxy, not a
  human explanation-quality score.
- No claim is made of deployment inside an operational system, legal compliance,
  validation on real records, or production security.

## Position on predictive policing

This work governs access to records; it does not predict crime or suspects.
Aggregate public crime statistics are not individual-level access-control data,
predictive policing can create feedback loops when observed crime data is shaped
by earlier policing decisions, and complex criminal-justice prediction systems do
not reliably outperform simple baselines. The subject is the governance of
access, not the prediction of crime.
