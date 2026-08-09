# Crime Records Access Network

A working blockchain system where five police-related departments share access to
crime records without any one of them being able to rewrite the shared history.

This is the real version of what the paper describes. The paper's Section V says
its blockchain was "a local permissioned audit simulation, not a live Hyperledger
Fabric deployment". This is the live deployment.

---

## What actually happens when someone requests a record

1. An officer signs in and asks to see a case file.
2. The rules **inside the blockchain** look at who they are (from their digital
   ID certificate), what the record is, and why they want it.
3. The answer is **allow**, **deny**, or **escalate** (a supervisor must decide).
4. The answer, plus the reasons for it, is written permanently to the blockchain.
5. If allowed, the actual file is fetched from the department's own storage — it
   was never on the blockchain.

---

## Words you will need

| Word | Plain meaning |
|---|---|
| **Hyperledger Fabric** | The blockchain software. Unlike Bitcoin, only known organisations can join. |
| **Chaincode** | A program that runs *inside* the blockchain. Ours is written in JavaScript. Also called a smart contract. |
| **Peer** | One department's server. It holds a full copy of the shared history and runs the chaincode. |
| **Orderer** | Decides what order transactions happen in and packages them into blocks. |
| **Certificate Authority (CA)** | Each department's ID-card issuer. Creates the digital certificates officers sign with. |
| **MSP** | The rulebook saying which certificates a department accepts. It is how the network knows "this really is Police". |
| **Channel** | The shared record the five departments write to. Ours is called `crimechannel`. |
| **Endorsement policy** | How many departments must approve a write. Ours needs **3 of 5**. |
| **On-chain / off-chain** | On-chain means stored in the blockchain. Off-chain means kept in the department's own database. Case files are off-chain. |
| **Hash** | A short fingerprint of a file. Change one letter in the file and the fingerprint changes completely. |

---

## What you need installed

| Thing | Version we used |
|---|---|
| Hyperledger Fabric | 2.5.16 |
| Node.js | 22.20.0 |
| Docker | 29.6.2, running through Colima (not Docker Desktop) |
| Ollama (for the AI wording) | 0.18.0, model `llama3.2:3b` |

The Fabric programs and Docker images must be at `../fabric-samples`. See
`../SETUP.md` for how that was installed.

---

## Running it

```bash
make up        # start the five departments (takes about 3 minutes)
make deploy    # install the rules onto all five servers
make seed      # create the 13 demo officer accounts
make ollama    # start the local AI model
make backend   # start the website at http://localhost:3001
```

Type `make` on its own to see every command.

Open `http://localhost:3001` and sign in with any of the demo usernames. The
password for all of them is `demo123`.

### Checking it works

```bash
make test          # 70 smart-contract tests, 48 API tests
make smoke         # an 11-step story from start to finish
make inspect       # look inside the blockchain itself
make verify-log    # check nobody edited the search history
```

### Producing the measurements

```bash
make measure       # speed, storage, and the attack tests
make evaluate      # explanation quality: fixed wording vs the AI
```

Results are written to `experiments/results/`.

---

## The five departments

Each department is a separate organisation with its own ID-card issuer and its
own server.

| Department | Who works there | Server port | CA port |
|---|---|---|---|
| Police | constables, sub-inspectors, inspectors, SHOs, investigating officers | 7051 | 7054 |
| Forensic Science Laboratory | lab analysts, lab director | 8051 | 8054 |
| Prosecution | public prosecutors, defence counsel | 9051 | 9054 |
| Judiciary | judges, magistrates, court clerks | 10051 | 10054 |
| Oversight | auditors, ombudsman | 11051 | 11054 |

There is also an **orderer** organisation that runs the sequencing service. It has
no officers.

Evidence details are shared through a **private data collection** visible only to
Police, Forensics and the Judiciary. The other two departments see only a
fingerprint of it.

### What is inside an officer's certificate

`role`, `rank`, `station`, `jurisdiction`, `badgeId`, `clearance`,
`credentialStatus`, and `caseAssignments`.

These facts are signed into the certificate by the department's CA. The chaincode
reads them from there, not from anything the officer typed. That is what stops
someone claiming a rank or clearance they do not have.

*(Case assignments are separated with `|` rather than commas, because Fabric's CA
tool already uses commas to separate attributes.)*

---

## What we measured

| Measurement | Simulated (paper) | This system |
|---|---|---|
| Time to record a decision | 11.10 ms | 72.69 ms |
| Time to verify one | 2.50 ms | 3.99 ms |
| Storage per decision | 353.50 B | 857 B |
| Attacks blocked | — | 6 of 6 |

The complete time to record a decision is 2072 ms. But 2000 ms of that is a
setting we chose: the orderer waits two seconds collecting transactions before
writing a block. The fair number to compare against the paper is the remaining
**73 ms**. Saying "blockchain costs 2072 ms" would be misleading.

Storage is not a like-for-like comparison either — this version stores the whole
explanation inside each entry.

Both points are written into
`experiments/results/live_fabric_measurements.md` so they travel with the numbers.

---

## Where things are

```
Makefile                  every command
docs/architecture.md      how the parts fit together
docs/evaluation.md        what we measured and its limits
docs/walkthrough.md       how to demonstrate it
network/                  blockchain configuration and startup scripts
chaincode/crimerecords/   the three programs that run inside the blockchain
backend/                  the web server that talks to the blockchain
frontend/                 the website (no build step needed)
experiments/              measurement scripts and their results
scripts/                  start, stop, check, inspect
```

---

## What this is not

- All data is synthetic. No real FIR, CCTNS or ICJS records are used.
- It runs on one computer with a single ordering node, so the speed figures do
  not represent a real multi-site setup.
- The rules are our own benchmark rules, not official police policy.
- The paper's re-signed attack is not tested here. On a real blockchain it would
  require stealing a department administrator's key, which is a much stronger
  assumption than the simulation makes.
- Every demo account shares one password and the login secret has a development
  default. This must not be deployed as it stands.
