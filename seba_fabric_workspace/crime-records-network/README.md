# SEBA-XAI Crime Records Network

SEBA-XAI is a research prototype for explainable, blockchain-audited access
governance between five criminal-justice agencies. It uses the Hyperledger
Fabric sample binaries and containers as infrastructure, but it does **not** use
FabCar's car model, transactions, API, interface, or seed data.

It is not a CCTNS/ICJS replacement and it is not a production police system.
All demonstration data is synthetic.

## Architecture

```text
Browser
  -> Node.js API (validation and Fabric Gateway)
  -> Fabric CA X.509 identity signs the request
  -> chaincode evaluates RBAC + ABAC + contextual policy
  -> ALLOW / DENY / ESCALATE + structured explanation is committed to Fabric
  -> only an identity-bound ALLOW can release raw content from the agency vault
```

Fabric is authoritative for application-domain state:

- departments and identity-backed user profiles;
- cases, record metadata, content hashes, and off-chain references;
- access requests, decisions, explanations, approvals, and policy versions;
- evidence metadata, custody transfers, court workflow, and audit events.

Raw crime-record content and evidence bytes are deliberately **not** placed on
the shared blockchain. The prototype stores them as permission-restricted files
in each agency's local vault and commits a SHA-256 content hash and `vault://`
reference to Fabric. This avoids replicating victim data and large files to every
peer. A production system would replace this adapter with an encrypted,
agency-controlled document/object store.

There is no application PostgreSQL or SQLite database and no hidden database
fallback. CouchDB is the configured Fabric peer world-state database, not an
independent source of truth. Fabric CA maintains its own internal identity
registry as infrastructure.

## Authentication and the wallet

Each demo user has:

1. an X.509 certificate and private key issued by that department's Fabric CA;
2. a `UserProfile` ledger asset containing role, rank, department, station,
   jurisdiction, clearance, assignment, and credential status.

The local MSP folder is the Fabric "wallet": it contains the certificate and
private key used to sign transactions. It is not application data and it does
not contain a blockchain balance or a password.

No password or password hash is stored on-chain. The development login screen
selects an already-enrolled server-held identity and proves it can sign a
Fabric request. This is a custodial local-demo identity selector, not a secure
production login. A deployment would use user-controlled keys, hardware-backed
credentials, or an enterprise identity provider mapped to Fabric identities.

## Policy outcomes

Every access request returns `ALLOW`, `DENY`, or `ESCALATE` and records:

- request and decision IDs;
- reason code and decisive attributes;
- policy version and counterfactual guidance;
- explanation and decision hashes;
- signer identity hash, timestamp, and Fabric transaction evidence;
- approval reference when escalation is resolved.

The deterministic demo covers these scenarios:

1. assigned investigating officer: allowed;
2. unassigned same-station constable: denied;
3. forensic analyst: evidence use allowed, unnecessary victim data denied;
4. valid cross-district request: escalated;
5. juvenile identity data: denied without a narrow legal exception;
6. supervisor-approved escalation: allowed and linked to approval;
7. suspended/revoked identity: denied;
8. auditor: full decision reconstruction but no protected raw payload.

## Requirements

- Docker or Colima with the Docker CLI available;
- Node.js and npm;
- Hyperledger Fabric binaries, configuration, and Docker images in the sibling
  `../fabric-samples` directory;
- optional Ollama for plain-language rewording. The structured deterministic
  explanation remains authoritative.

## Start from a clean local network

```bash
make down
make all
make backend
```

Then open `http://localhost:3001`. Select a seeded Fabric identity such as
`io.krishnan`; no application password is requested.

`make all` performs, in order:

```bash
make up            # five agencies, orderer, peers, CAs, and Fabric world state
make deploy        # package/approve/commit the chaincode
make seed          # issue deterministic X.509 demo identities
make seed-users    # create UserProfile assets
make seed-domain   # create policy, departments, and cases
make seed-records  # create on-chain metadata and local synthetic vault content
```

Useful commands:

```bash
make test          # chaincode and live API suites
make smoke         # end-to-end smoke flow
make verify-log    # read direct-ledger audit events
make inspect       # inspect live ledger state
make prove         # permissioned-network checks
make down          # stop and remove the generated local network
```

## Main components

```text
chaincode/crimerecords/lib/
  governanceContract.js   departments, cases, court workflow
  userContract.js         identity-backed UserProfile and status history
  recordContract.js       record/evidence metadata, custody, protected release
  accessContract.js       requests, ALLOW/DENY/ESCALATE, approvals
  auditContract.js        direct events and reconstruction/verification
  policyContract.js       explicit policy version creation and activation
  policy/                 deterministic contextual policy and explanations

backend/src/
  fabric/                 per-user Fabric Gateway and CA registration
  routes/                 domain API routes
  storage/vault.js        replaceable agency file-vault adapter

frontend/js/modules/      cases, records, requests, approvals, evidence,
                          audit, departments, and users
```

## Known limitations

- The network runs on one computer with one orderer; it does not demonstrate
  production fault tolerance or multi-site performance.
- Demo private keys are held by the backend and login is identity selection.
- The filesystem vault has restrictive file permissions but no at-rest
  encryption, HSM/KMS integration, malware scanning, or retention policy.
- The rules are research policy fixtures, not official Indian police policy.
- There is no live CCTNS/ICJS integration and no real personal or crime data.
- The local LLM only rewords an already-made decision; it cannot authorize an
  access request or replace the deterministic evidence.
- Security, privacy, legal compliance, and production readiness have not been
  established by this prototype.
