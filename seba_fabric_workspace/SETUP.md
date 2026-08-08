# Hyperledger Fabric Test Network — Setup

Environment for running the Fabric v2.5 test network and the `seba-audit-chaincode`
on this Mac (Apple Silicon, macOS 25.3).

Verified working: **2026-08-03**.

---

## Quick start

```bash
./bootstrap-network.sh
```

Tears down anything running, brings up the network, creates `mychannel`, deploys
the chaincode, and runs the smoke test. Takes about 90 seconds.

Tear down when done:

```bash
cd fabric-samples/test-network && ./network.sh down
```

---

## What is installed

| Component | Version | Notes |
|---|---|---|
| Homebrew | 6.0.9 | already present |
| Git | 2.50.1 | already present |
| cURL | 8.12.1 | already present |
| Xcode CLT | installed | `/Library/Developer/CommandLineTools` |
| jq | 1.7.1 | already present |
| **Go** | **1.26.5** | installed via `brew install go` |
| Node.js | 22.20.0 | already present; chaincode needs >= 18 |
| Docker CLI | 29.6.1 | via Colima, **not** Docker Desktop |
| Docker Compose | 2.40.2 | already present |
| Colima | running | 4 CPUs, 8 GiB RAM, 60 GiB disk, virtiofs |
| Fabric binaries | 2.5.16 | `fabric-samples/bin/` |
| Fabric docs | release-2.5 | `../Learn/fabric-docs/docs/source/` (120 pages, offline) |

### Docker images pulled

`fabric-peer:latest` · `fabric-orderer:latest` · `fabric-ca:latest` ·
`fabric-nodeenv:2.5` · `fabric-ccenv:2.5` · `fabric-baseos:2.5` ·
`fabric-javaenv:2.5` · `fabric-tools:latest` · `couchdb:3.4.2`

Total ~4.8 GB. All present locally, so the network works offline.

`fabric-nodeenv:2.5` is the one that matters for this project — the peer uses it
to build the JavaScript chaincode. Without it `deployCC` fails.

---

## Runtime layout

Started by `network.sh up createChannel -ca`:

| Container | Port |
|---|---|
| `orderer.example.com` | 7050 |
| `peer0.org1.example.com` | 7051 |
| `peer0.org2.example.com` | 9051 |
| `ca_org1` | 7054 |
| `ca_org2` | 8054 |
| `ca_orderer` | 9054 |
| `dev-peer0.org1...sebaaudit` | chaincode container |
| `dev-peer0.org2...sebaaudit` | chaincode container |

State database is **goleveldb** (the default). The chaincode uses only composite
keys and history queries — no `getQueryResult` rich queries — so CouchDB is not
required. The `couchdb:3.4.2` image is pulled anyway if you ever want
`./network.sh up createChannel -s couchdb`.

---

## Scripts

### `bootstrap-network.sh [channel] [chaincode-name]`

Full clean bring-up with preflight checks (docker reachable, `peer` on PATH,
`fabric-nodeenv` present) and a smoke test at the end. Defaults: `mychannel`,
`sebaaudit`.

### `smoke-test-seba-chaincode.sh [channel] [chaincode-name]`

Exercises every contract method against a running network:

1. `InitLedger`
2. `RecordAccessDecision`
3. `ReadAccessDecision`
4. `VerifyAuditAnchor` — matching anchor returns `match:true`
5. `VerifyAuditAnchor` — tampered anchor returns `match:false`
6. `QueryByDecision("allow")` — composite-key index
7. `GetHistoryForRequest`
8. Duplicate write is rejected

Each run uses a unique `requestIdHash` (derived from a timestamp), so it is safe
to run repeatedly against the same ledger. Override with `RUN_ID=... ./smoke-test-...`.

Last result: **8 passed, 0 failed**.

---

## Chaincode unit tests

Offline unit tests with a mocked `ChaincodeStub` — no network or containers needed.

```bash
cd seba-audit-chaincode && npm test
```

```bash
cd seba-audit-chaincode && npm run test:coverage
```

92 tests, 100% statement/branch/function/line coverage on `lib/sebaAuditContract.js`.
Stack: mocha + chai + sinon + nyc, following the `asset-transfer-basic` sample pattern.

Caveat: the mock's `getState` resolves `undefined` for a missing key, whereas the
real `fabric-shim` returns an **empty Buffer**. Verified against the live network —
`AuditEventExists` returns `false` there, not `undefined`. Keep that divergence in
mind before treating a mock-only result as a production finding.

## Known security findings (NOT yet fixed)

Reviewed 2026-08-03. The contract is functional but its central privacy claim does
not hold as written. See the review notes for detail; summary:

| Severity | Finding |
|---|---|
| CRITICAL | PII can reach the ledger. `RecordAccessDecision` spreads the whole parsed payload (`...event`, line 94); unvalidated fields (`policyVersion`, `primaryReasonCode`, `sourcePrototypeRun`, `createdAtUtc`) and **arbitrary extra keys** are persisted verbatim to state and broadcast via `setEvent`. Demonstrated with a live transaction. |
| CRITICAL | No authorization. No `ctx.clientIdentity` check anywhere — any channel member can commit forged audit records or re-run `InitLedger`. Endorsement policy governs signing peers, not submitters. |
| HIGH | `VerifyAuditAnchor` compares a caller-supplied value against a caller-supplied value. Not an integrity proof. |
| HIGH | Required-field validation is presence-only (`String(x).trim()`), so non-string types pass. Confirmed independently by the test suite. |
| MEDIUM | Y2038: only `txTimestamp.seconds.low` is read (lines 85-88). Fix: `ctx.stub.getDateTimestamp().toISOString()`. |
| MEDIUM | Unsalted SHA-256 over possibly low-entropy IDs — brute-forceable correlation. Consider HMAC with an off-chain key. |

Primary fix: replace the `FORBIDDEN_FIELDS` denylist with a strict allow-list that
picks only the 12 known fields and type-checks each one.

## Fix applied during setup

`~/.docker/config.json` contained `"credsStore": "desktop"` — left behind by a
Docker Desktop install that is no longer on the machine. Every `docker pull`
failed with:

```
error getting credentials - err: exec: "docker-credential-desktop": executable file not found
```

The key was removed. `auths` was empty, so no stored credentials were lost.
Backup at `~/.docker/config.json.bak-predesktop-removal`.

---

## Notes on Docker Desktop

Docker here is provided by **Colima**, not Docker Desktop. `/Applications/Docker.app`
does not exist. Everything above was built and verified on Colima.

If Colima is not running:

```bash
colima start
```

A stale `desktop-linux` Docker context still exists from the old install. The
active context is `colima`; leave it that way unless you install Docker Desktop.

The gRPC FUSE file-sharing warning in the Fabric docs is Docker Desktop-specific
and does not apply — Colima uses virtiofs.

---

## Common commands

```bash
cd fabric-samples/test-network && ./network.sh up createChannel -ca
```

```bash
cd fabric-samples/test-network && ./network.sh deployCC -ccn sebaaudit -ccp ../../seba-audit-chaincode -ccl javascript
```

```bash
docker ps --format '{{.Names}}\t{{.Status}}'
```

```bash
docker logs -f peer0.org1.example.com
```

Offline docs are greppable, e.g.:

```bash
grep -rn "peer lifecycle chaincode" ../Learn/fabric-docs/docs/source/commands/
```
