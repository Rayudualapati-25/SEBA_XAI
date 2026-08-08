# Crime Records Access Network

A permissioned Hyperledger Fabric implementation of the SEBA-XAI access
governance design for inter-agency police crime-record access. Five departments
participate as separate organisations. Access decisions, their explanations, and
integrity commitments are recorded on the ledger; raw records remain in
agency-controlled off-chain storage.

The implementation addresses the limitation stated in Section V of the paper,
that the blockchain layer was "a local permissioned audit simulation, not a live
Hyperledger Fabric deployment."

---

## Requirements

| Component | Version used |
|---|---|
| Hyperledger Fabric | 2.5.16 |
| Node.js | 22.20.0 |
| Docker | 29.6.2 via Colima (not Docker Desktop) |
| Ollama | 0.18.0, model `llama3.2:3b` |

Fabric binaries and Docker images are expected at `../fabric-samples`. See
`../SETUP.md` for how that environment was installed.

## Reproduction

```bash
make up        # 5 organisations, channel, 22 containers (~3 min)
make deploy    # install and commit the chaincode on all five peers
make seed      # register 13 department users with certificate attributes
make ollama    # start the local model used for explanation wording
make backend   # API and web interface on http://localhost:3001
```

`make` with no target lists every available command. Sign in at
`http://localhost:3001` with any seeded username and password `demo123`.

Verification:

```bash
make test          # 70 chaincode tests, 48 backend tests
make smoke         # 11-step end-to-end scenario on the live network
make inspect       # read ledger state directly
make verify-log    # access-log integrity against on-chain anchors
```

Measurement:

```bash
make measure       # latency, storage, attack replay
make evaluate      # explanation quality, template versus local model
```

Results are written to `experiments/results/`.

---

## Repository layout

```
Makefile                  operational entry points
docs/
  architecture.md         components, decision flow, code map
  evaluation.md           metrics, method, and limitations
  walkthrough.md          demonstration procedure
network/                  configtx, compose files, channel and CA scripts
chaincode/crimerecords/   three smart contracts and their unit tests
backend/                  REST API, Fabric gateway, off-chain store
frontend/                 web interface (no build step; see frontend/README.md)
experiments/              measurement scripts and generated results
scripts/                  network lifecycle, verification, inspection
```

## Organisations

Each department is a Fabric organisation with its own certificate authority,
MSP, and CouchDB-backed peer. Users are enrolled with role attributes embedded
in their X.509 certificates, which the chaincode reads from the signed identity
rather than from request parameters.

| MSP | Department | Peer | CA |
|---|---|---|---|
| `PoliceMSP` | Police and investigating agencies | 7051 | 7054 |
| `ForensicsMSP` | Forensic Science Laboratory | 8051 | 8054 |
| `ProsecutionMSP` | Prosecution | 9051 | 9054 |
| `CourtMSP` | Judiciary | 10051 | 10054 |
| `AuditMSP` | Oversight and internal affairs | 11051 | 11054 |
| `OrdererMSP` | Consortium operator | 7050 | 12054 |

Channel `crimechannel`, endorsement policy MAJORITY (3 of 5). The
`evidenceDetails` private data collection is distributed to Police, Forensics and
Court, so that a majority endorsement can be satisfied entirely by collection
members.

Certificate attributes: `role`, `rank`, `station`, `jurisdiction`, `badgeId`,
`clearance`, `credentialStatus`, `caseAssignments`. Case assignments are
pipe-separated because Fabric CA uses the comma as its attribute separator.

## Results summary

| Quantity | Simulation (paper) | This implementation |
|---|---|---|
| Audit build latency p50, marginal | 11.10 ms | 72.69 ms |
| Verification latency p50 | 2.50 ms | 3.99 ms |
| Storage per audit event | 353.50 B | 857 B |
| Attacks detected | — | 6 of 6 |

The end-to-end build latency is 2072 ms, of which 2000 ms is the orderer's
configured `BatchTimeout`. The marginal figure above is the comparable quantity.
Storage is not like-for-like: this implementation commits the full explanation
artifact inline. Both caveats are recorded in
`experiments/results/live_fabric_measurements.md`.

## Scope and limitations

- Synthetic data only. No FIR, CCTNS or ICJS records are used.
- Single-host Docker with a single-node Raft ordering service. Latency figures do
  not represent a distributed deployment.
- The policy is a declared benchmark policy, not validated operational police
  policy.
- The compromised-signer attack from the paper's catalogue is not replayed here.
  On a live Fabric network it requires a compromised MSP administrator key, a
  strictly stronger assumption than in the simulation.
- Demo accounts share a fixed password and the JWT secret defaults to a
  development value. Not deployable as-is.
