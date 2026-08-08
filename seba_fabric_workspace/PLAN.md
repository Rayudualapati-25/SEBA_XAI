# Police Crime Records Access Network — Full System Plan

**Project:** Permissioned Hyperledger Fabric network for inter-department police
crime-records access governance. Implements the system described in the
SEBA-XAI paper (`papers/overleaf_ieee_journal`): raw records stay off-chain in
agency-controlled storage; the ledger holds access decisions, policy versions,
explanation hashes, and integrity commitments.

**Status:** PLAN — awaiting approval. Nothing below is built yet except the
base Fabric environment (verified 2026-08-03) and the existing
`seba-audit-chaincode`.

**Why this build matters for the paper** (checked against
`Explainable_Access_Governance.pdf`, 2026-08-05): the paper's Limitations
section concedes the blockchain layer "is a local permissioned audit
simulation, not a live Hyperledger Fabric deployment." This system removes
that limitation — the same access-governance workflow, running on real Fabric
with real MSP identities, endorsement policies, and Raft ordering. Its
measurements (build/verify latency p50, storage per event) are directly
comparable to the paper's Section IV-F numbers (11.10 ms / 2.50 ms / 353.50 B
for the simulated blockchain-style layer), giving a sim-vs-live table for the
extension paper.

---

## 1. Departments → Fabric Organizations

Each department is a Fabric org with its own CA, MSP, and peer. Chosen to match
the paper's actor list (officer, investigating agency, forensic user,
prosecutor/court authority, auditor):

| Org (MSP ID) | Department | Example roles (CA attributes) |
|---|---|---|
| `PoliceMSP` | Police / Investigating agencies | constable, SI, inspector, SHO, IO |
| `ForensicsMSP` | Forensic Science Laboratory | lab-analyst, lab-director |
| `ProsecutionMSP` | Prosecution / Lawyers | public-prosecutor, defense-counsel (read-limited) |
| `CourtMSP` | Courts / Judiciary | judge, court-clerk, magistrate |
| `AuditMSP` | Oversight / Internal Affairs | auditor, ombudsman |
| `OrdererMSP` | State/NCRB-style consortium operator | ordering service only, no app users |

Each user identity carries X.509 attributes: `role`, `rank`, `station`,
`jurisdiction`, `badgeId`, `clearance`. Chaincode reads them via
`ctx.clientIdentity.getAttributeValue()` — this is the ABAC layer from the paper.

**Topology (sized for this Mac / Colima 8 GiB):**
- 1 peer per org (5 peers), each with CouchDB (rich queries needed for the
  record/access indexes)
- 1 Raft orderer (single-node Raft is standard for dev; config supports 3)
- 6 Fabric CAs (5 org CAs + 1 orderer CA), TLS enabled everywhere
- ≈ 17 containers. May need `colima start --memory 10`.

## 2. Channels and privacy

- **One application channel** `crimechannel` with all 5 orgs. Simpler than
  per-pair channels and matches the paper's "one ledger among known agencies".
- **Private Data Collections** for anything sensitive-but-shared:
  - `evidenceDetails` — Police + Forensics only
  - `caseFileDetails` — Police + Prosecution + Court
  - Only hashes of private data hit the shared ledger, consistent with the
    paper's data-minimization claim.
- **Endorsement policy:** majority of orgs for record writes; the audit
  contract requires `AuditMSP` OR majority (so audit events can't be written by
  a single colluding org — relevant to the block-signature-collusion attack in
  the threat model).

## 3. Chaincode (Node.js, 3 contracts in one package `crimerecords`)

### 3.1 `RecordContract` — crime record registry (hashes only)
- `CreateCaseRecord(caseId, recordMeta)` — Police only (identity check).
  Stores: record type, sensitivity level, juvenile/witness/sealed flags,
  owning agency, off-chain URI, SHA-256 of the payload. Never the payload.
- `AttachEvidenceHash(caseId, evidenceHash)` — Forensics only; detail goes to
  the `evidenceDetails` PDC.
- `SealRecord / UnsealRecord` — Court only.
- `GetRecordMeta`, `GetRecordHistory` — read paths with visibility rules.

### 3.2 `AccessContract` — the paper's access-request flow
- `RequestAccess(recordId, action, purpose, context)` — any enrolled user.
  Builds the structured request exactly as the paper defines it:
  - **Subject** (from the X.509 certificate): role, rank, station,
    jurisdiction, credential status, case assignment
  - **Object** (from the record): record type, sensitivity level,
    juvenile/witness flags, sealed status, owning agency
  - **Action**: view / export / annotate
  - **Environment** (from args): purpose, time window, emergency flag,
    court/prosecutor link, approval token, policy version
- Deterministic **policy engine inside chaincode** (RBAC + ABAC + PBAC, ported
  from `prototype/synthetic_access_sim/policies/seba_xai_policy_v1.json`)
  returns `allow | deny | escalate`. Policy is versioned on-chain.
- `ApproveEscalation / RejectEscalation` — supervisor rank or Court/Audit.
- Every decision emits an **explanation artifact** matching the paper's
  Section III-D: decision label, reason code, decisive attributes, policy/rule
  version, counterfactual information where applicable ("what missing
  condition would have changed this denial"), and an explanation hash bound to
  the audit event so later substitution is detectable (the paper's
  explanation-hash-substitution attack).

### 3.3 `AuditContract` — hardened evolution of `seba-audit-chaincode`
Carries over the working design (composite keys, history queries, events) and
**fixes all six known findings from SETUP.md**:
1. Strict 12-field allow-list with type checks (kills the PII spread-operator bug)
2. `ctx.clientIdentity` authorization on every write; `InitLedger` admin-only
3. `VerifyAuditAnchor` recomputes the anchor from ledger state, not caller input
4. Real type validation, not `String(x).trim()`
5. `ctx.stub.getDateTimestamp().toISOString()` (Y2038 fix)
6. HMAC-SHA256 with off-chain key for request-ID hashing (anti-correlation)

**Testing:** TDD, mocha/chai/sinon with mocked stub (pattern already proven —
92 tests / 100% coverage on the current contract). Target ≥ 80% on all three
contracts, plus the mock-vs-real `getState` divergence noted in SETUP.md.

## 4. Identity, enrollment, login

Two layers, cleanly separated:

1. **Blockchain identity (Fabric CA):** an org admin registers each user with
   role attributes; the backend enrolls them and stores the X.509 keypair in a
   per-org wallet (filesystem wallet, `fabric-ca-client` + SDK).
2. **Application login (web):** username + password (bcrypt) → JWT session.
   The JWT maps to the user's wallet identity; every API call signs Fabric
   transactions **as that user**, so on-chain attribution is per-person, not
   per-server. No passwords or keys ever go on-chain.

Bootstrap seeding: `seed-identities.sh` registers ~4 demo users per department
(20 total) with realistic attributes for the demo/benchmark.

## 5. Application layer

### Backend — Node.js + Express + `@hyperledger/fabric-gateway`
- `POST /auth/login`, `POST /auth/enroll` (admin-gated)
- `POST /records`, `GET /records/:id`, `POST /records/:id/evidence`
- `POST /access/request`, `GET /access/pending`, `POST /access/:id/approve`
- `GET /audit/trail/:recordId`, `POST /audit/verify` (anchor check)
- Input validation with a schema library (joi/zod) at every boundary;
  consistent `{success, data, error}` envelope; structured error logging.
- **Off-chain record store:** PostgreSQL in docker-compose (record payloads +
  user accounts). Ledger keeps only hashes/URIs — exactly the paper's split.

### Frontend — React (Vite), one app, role-routed dashboards
- **Police:** create case records, request access, my requests
- **Forensics:** attach evidence hashes, request access to assigned cases
- **Prosecution/Court:** request case files, approve escalations, seal records
- **Auditor:** audit-trail explorer, tamper-verification button, decision
  explanations viewer (renders the XAI artifact — "why was this allowed?")
- Login page → JWT → role read from profile → dashboard routing.

## 6. Repository layout (new, inside `seba_fabric_workspace/`)

```
crime-records-network/
├── network/                 # configtx.yaml, docker-compose, CA configs,
│   ├── organizations/       #   crypto material (generated, gitignored)
│   └── scripts/             #   createChannel, joinChannel, setAnchorPeers
├── chaincode/crimerecords/  # 3 contracts + tests (lib/, test/)
├── backend/                 # Express API, wallets/, services/, routes/
├── frontend/                # React app
├── scripts/
│   ├── bootstrap.sh         # one-command: network up → deploy CC → seed users
│   ├── seed-identities.sh
│   └── smoke-test.sh        # end-to-end scenario across all 5 departments
└── docs/                    # architecture diagram, API reference, demo script
```

Existing `fabric-samples/test-network` and `seba-audit-chaincode` stay
untouched as the known-good reference.

## 7. Build phases (each ends verified)

| Phase | Deliverable | Verify |
|---|---|---|
| **P1 Network** | 5-org network + channel + PDC config, bootstrap script | all containers healthy, channel joined by 5 peers |
| **P2 Chaincode** | 3 contracts, TDD, ≥80% coverage | `npm test` green, deploy + invoke on live network |
| **P3 Identity** | CA registration/enrollment, 20 seeded users with attributes | ABAC rejection test: forensics user cannot create a case record |
| **P4 Backend** | REST API + JWT auth + Postgres off-chain store | integration tests against live network |
| **P5 Frontend** | Login + 5 role dashboards | manual walkthrough in browser preview |
| **P6 E2E + docs** | Full scenario smoke test, demo script, measurements | scripted: officer files case → forensics attaches evidence → prosecutor requests access → escalation → court approves → auditor verifies trail |

P6 also emits latency/storage numbers in the same format as the paper's RQ5
tables (build latency p50, verification latency p50, storage per event), so
the live-Fabric numbers can sit next to the paper's simulated ones
(11.10 ms / 2.50 ms / 353.50 B). P6 additionally replays a subset of the
paper's attack catalog against the live network — approval-token replay,
request backdating, explanation-hash substitution — to show which are
structurally rejected by Fabric (MSP validation, tx timestamps) versus which
need the application-layer defenses, mirroring RQ1/RQ2.

## 8. Demo scenario (what we show at the end)

1. Officer (Police) logs in, files case `FIR-2026-0042` — payload to Postgres,
   hash to ledger.
2. Forensics analyst logs in, attaches a DNA-report hash via the evidence PDC.
3. Defense counsel requests the record → policy engine → **deny** (no case
   assignment) with explanation artifact.
4. Public prosecutor requests it → **escalate** (sealed flag) → judge approves.
5. Auditor opens the trail: every event, every explanation, anchor verification
   passes; then we tamper with the off-chain payload and the verify button
   catches the hash mismatch.

## 9. Open decisions (defaults chosen, flag if you disagree)

1. **5 orgs** as listed — could add Prisons/CyberCrime later via addOrg flow.
2. **React frontend** — could be plain HTML/JS (like wallWorthy) if you prefer
   no build step.
3. **Node.js everywhere** (chaincode + backend) — matches existing chaincode
   and the fabric-nodeenv image already pulled; Go would mean new toolchain.
4. **PostgreSQL** for off-chain store — SQLite would be lighter if RAM is tight.
5. Single channel + PDCs rather than multiple channels.
