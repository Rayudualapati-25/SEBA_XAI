# Demonstration procedure

A sequence for showing the implementation working, in about ten minutes. Each
part states what is being demonstrated and what output confirms it.

## Preparation

```bash
make clean-containers      # stale build containers slow Docker down
docker ps | wc -l          # expect 22 containers; if none, see below
make ollama                # local model for explanation wording
make backend               # leave running
```

If the network is not up:

```bash
make up && make deploy && make seed     # about 3 minutes
```

Open `http://localhost:3001`. All seeded accounts use the password `demo123`.

---

## Part 1 — Ledger state

```bash
make inspect
```

Nine sections, pausing between each. What each one establishes:

| Section | Establishes |
|---|---|
| 1. Containers | Five department peers, six certificate authorities, one ordering service |
| 2. Block height | All five peers report the same height and the same latest block hash |
| 3. Decoded block | Block number, previous-block hash, transaction count — the chain structure itself |
| 4. Endorsements | Three organisations signed the transaction; majority-of-five policy in effect |
| 5. Chaincode containers | Policy rules execute on the peers, not in the application |
| 6. Certificate attributes | Role, clearance, jurisdiction and case assignments are inside the officer's X.509 certificate |
| 7. Key history | Past record versions with the transaction that wrote each |
| 8. On-chain record | Metadata, `payloadHash`, `offchainUri` — no case narrative |
| 9. World state | CouchDB per department, browsable in a browser |

Sections 4 and 6 are the two properties a two-peer test network cannot show:
multi-organisation consensus, and access decided from cryptographic identity
rather than from an editable database row.

---

## Part 2 — Access governance

In the web interface, in this order:

| Sign in as | Action | Observed |
|---|---|---|
| `const.verma` | File a record | Narrative to agency storage, hash to the ledger |
| `const.verma` | Search `CASE-2026-001`, request access to a result | **Escalate** — clearance `low` against a `medium` record, with the structured explanation and the model's wording |
| `dc.nair` | Same search, request access | **Deny** for a different reason: no permission for that role on that record type |
| `judge.rana` | Escalation queue, approve | The escalation clears; the approval is itself a ledger transaction |
| `aud.qureshi` | Audit trail, then Verify payload integrity | Every decision with its explanation; integrity confirmed |
| `aud.qureshi` | Access log, then Verify log integrity | Searches and file releases, with the number of on-chain anchors compared |

The constable's escalate result is the most compact demonstration: access control,
ledger commitment and generated explanation in a single view.

Note that the same constable may *file* a record but is *escalated* when reading
one. Filing and reading are governed separately.

---

## Part 3 — Tamper detection

Confirm the log verifies:

```bash
make verify-log
```

Reports `LOG INTACT`. Now modify the database directly, bypassing the
application:

```bash
sqlite3 backend/data/offchain.sqlite "UPDATE access_log SET action='auth.whoami' WHERE seq=2;"
make verify-log
```

Reports `LOG TAMPERED` and the first divergent entry. Restoring the original
value makes it pass again, which shows the check is specific rather than simply
alarming.

The same applies to record payloads: edit a row in `payloads` and the auditor's
payload integrity check fails against the on-chain commitment.

---

## Part 4 — Verification and measurement

```bash
make test          # 70 chaincode tests, 48 backend tests
make smoke         # 11-step scenario on the live network
```

Generated results, best viewed rendered (`Cmd+Shift+V` in VS Code):

- `experiments/results/live_fabric_measurements.md`
- `experiments/results/explanation_quality.md`

Two points to state rather than leave to be discovered:

**Build latency.** The end-to-end figure is 2072 ms, of which 2000 ms is the
orderer's configured `BatchTimeout`. The comparable quantity against the paper's
simulated 11.10 ms is the marginal cost of about 73 ms. Quoting the end-to-end
figure as the cost of the audit design would be incorrect.

**Explanation quality.** The deterministic template scores higher than the model
(1.00 against 0.92 coverage), and the validator rejected half the model's
generations. The metric credits an explanation for naming the decisive
attributes, which a template does on every input; the reference implementation
describes it as a weak textual proxy. The result is expected and is reported as
such.

---

## Code worth opening

| File | Contents |
|---|---|
| `chaincode/crimerecords/lib/policy/policyEngine.js` | The eight access rules, in evaluation order |
| `chaincode/crimerecords/lib/accessContract.js` | Request assembly, policy call, explanation commitment |
| `chaincode/crimerecords/lib/util/identity.js` | Reading attributes from the signed certificate |
| `backend/src/audit/accessLog.js` | The hash chain and its verification |
| `network/configtx/configtx.yaml` | Organisations and the endorsement policy |

## Troubleshooting

| Symptom | Cause and action |
|---|---|
| No containers listed | Docker or Colima not running. Start Colima, then `make up` |
| Tests unusually slow | Stale chaincode build containers. `make clean-containers` |
| Explanations say "template wording" | Ollama not running. `make ollama`. The interface still functions |
| "Session expired" in the browser | Backend restarted. Sign in again |
