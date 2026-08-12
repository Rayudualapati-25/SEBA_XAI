# Iteration 060 — Fabric-ledger-only application state

Date: 2026-08-11

## Objective

Replace the crime-records application's SQLite and PostgreSQL application-state paths with Hyperledger Fabric transactions and world state. Keep CouchDB/LevelDB only as peer-managed Fabric state databases, not as application-owned databases. Treat FabCar as a tutorial reference rather than a runtime dependency.

## Baseline

The pre-refactor mixed-storage implementation was executed with `make test` against the running local Fabric network.

- Chaincode: 98 passing tests.
- Chaincode coverage: 97.44% statements, 91.98% branches, 98.24% functions, 97.65% lines.
- Backend: 48 passing tests.
- Known mixed-storage paths: raw payloads, explanation renderings, access logs, and anchor state in SQLite; six Fabric CA registries in PostgreSQL; bcrypt password hashes in Fabric world state.

The raw command output is summarized in `experiments/runs/20260811_ledger_only_baseline.json`. This baseline is a functional result, not evidence that its storage architecture meets the new requirement.

## Proposed method

1. Store record payloads and their hashes through the record chaincode.
2. Record authenticated API access events directly as Fabric transactions.
3. Remove explanation persistence; explanations are generated views of ledger decisions.
4. Store user authorization profiles on-chain without passwords or password hashes.
5. Authenticate the local demonstration by selecting and proving access to an enrolled Fabric X.509 identity. Clearly label this as a custodial demo flow because the backend holds the development keys.
6. Return the Fabric CA servers to their default embedded registries, removing the external PostgreSQL service.
7. Remove SQLite/PostgreSQL application dependencies and runtime configuration.

## Ablations and acceptance checks

| Design choice | Baseline variant | Proposed variant | Evidence required |
|---|---|---|---|
| Record payload | SQLite payload table | Fabric world state | Chaincode and API create/read tests |
| Access audit | SQLite hash chain plus periodic anchor | Direct Fabric access-event transactions | Chaincode event query tests and API test |
| User secret | bcrypt hash in Fabric state | No application password secret | Schema/source scan and auth tests |
| CA registry | PostgreSQL service | Fabric CA embedded registry | Compose scan and network startup |
| Explanation cache | SQLite rendering table | Stateless generated explanation | Source scan and explanation API test |

## Known limitations

- Data placed in a shared Fabric channel is replicated to channel peers. Chaincode/API authorization does not prevent a peer administrator from inspecting its local state. Sensitive production deployments should use private data collections or separate channels.
- The local web login proves that the backend can sign with an enrolled Fabric identity. It does not prove possession of a browser-held private key and must not be described as production-grade end-user authentication.
- Direct ledger logging is intentionally simple for the prototype and adds a transaction per authenticated request.

## Status

In progress. The baseline passed; the proposed implementation and ablations still need to run.
