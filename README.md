# SEBA-XAI: Explainable Access Governance for Criminal-Justice Records on Hyperledger Fabric

## The problem in one paragraph

Police records are shared between departments: police, forensic laboratories,
prosecutors, courts, and oversight bodies. When someone asks to see a sensitive
record, three questions need answering. Should they be allowed to see it? Is
there a record of that decision that nobody can quietly change afterwards? And
if someone reviews it a year later, can they find out *why* the answer was what
it was?

This project builds a working system that answers all three together.

## Why a job title is not enough

A sub-inspector and a constable might ask for the same case file and should not
get the same answer. The same officer might be allowed to see a record for one
reason and refused for another. Some records must stay closed to one department
while another reads them freely.

So the decision cannot come from the person's job title alone. It has to
consider who is asking, what they are asking for, why, and under what
circumstances.

The system is designed for the Indian CCTNS/ICJS context. It does not replace
those systems, is not compared against them, and uses no real police records —
all data is synthetic.

---

## What this is

**A running Hyperledger Fabric network, not a design and not a simulation.**

Five departments — police, forensics, prosecution, court, oversight — each run
their own server and their own ID-card issuer on Hyperledger Fabric 2.5.16.
Writing anything requires **three of the five departments to agree**, so no
single department can act alone.

It lives in `seba_fabric_workspace/crime-records-network/`.

Two design choices carry most of the weight, and both are what make this a
system rather than a layer bolted on top of one.

### The decision is made inside the blockchain

The web server cannot grant access. It passes on a request; the rules that
decide run *inside* the blockchain, on three departments' machines
independently, and all three must reach the same answer before anything is
recorded.

This is the part that is easy to miss. Most designs of this kind decide
somewhere else and then write the answer into a ledger. Then the ledger proves
the *record* wasn't altered — it proves nothing about whether the answer was
right. Here the decision and the record of it are the same event.

### An officer cannot claim authority they do not have

Each officer's role, rank, station, jurisdiction, clearance, and case
assignments are written *inside their digital ID certificate*, signed by their
own department. The blockchain reads those facts from the signed certificate,
never from the request.

So an officer can say *why* they want a file. They cannot say *who they are*.
The only things they supply are the action and the reason — and even those are
checked against a fixed list before anything looks at them.

---

## What is new here

The building blocks already exist in published research: blockchain for
tamper-proof records, attribute-based access control for permissions, and
explainable AI for justifying decisions. **We did not invent any of those.**

Five things are ours.

**1. The decision is the blockchain transaction.** Not a decision made
elsewhere and filed afterwards.

**2. Authority comes from the certificate, not the request.** An officer cannot
assert their own clearance.

**3. The reason is stored with the decision, in the same write.** Every decision
records which facts decided it, the rule that fired, and what would have changed
the outcome. Because the same code produces both, they can never disagree, and
there is no moment when one exists without the other.

**4. Looking is recorded, not just writing.** Searches and reads don't create
blockchain transactions, so who *looked* at a case would normally leave no
trace — backwards, since in police work who looked is often the more sensitive
question. Every search and read goes into a chained list where each entry
carries a fingerprint of the one before it, and the end of that chain is written
to the blockchain every 25 entries. Rewrite the list and it contradicts
something already permanent.

**5. A finding about what agreement actually proves.** This is the part worth
understanding properly.

Three of five departments must agree before a decision is committed. That sounds
like it should protect against a corrupt department. It does — against a
department that lies about the *answer*.

But all three run the same rules on the same input. So if the *input* is wrong,
all three compute the same wrong answer, agree completely, and commit it. A
department whose ID-card issuer has been compromised can issue an officer a
certificate saying `clearance: high`. Every check passes. Every signature is
valid. The ledger is perfectly consistent. And the decision was never one the
real policy would have made.

> **Agreement establishes that everyone computed the same thing. It does not
> establish that what they computed from was true.** Checking a log for
> tampering does not tell you its decisions were right.

---

## What was measured

| What we measured | Result |
|---|---|
| Time to record a decision | 72.69 ms of actual work |
| Time to verify one | 3.99 ms |
| Storage per decision | 857 B |
| Attacks blocked | 6 of 6 |

**Two things must be said with that table.**

The full time is 2072 ms, but 2000 ms of that is a waiting period we configured
ourselves — the blockchain collects transactions for two seconds before writing
a block. Across all 50 measurements the spread was under 83 ms, which is what a
fixed wait looks like. The honest figure is the remaining **73 ms**. Quoting
2072 ms as "the cost of blockchain" would be wrong.

The network also runs on one computer with a single ordering node. These are
real measurements of that setup, not predictions for a real multi-site
deployment.

Checked by: 70 smart-contract tests (~97% coverage), 48 API tests against the
running network with real certificates, an 11-step walkthrough, a 9-section
inspection of actual blocks, and a 6-attack replay. See `TESTING.md`.

## About the AI part

A language model running on the local machine turns each recorded decision into
a readable sentence.

**The AI does not decide anything.** The blockchain rules decide first and
record the decision. Only then is the AI asked to reword it — and the server
reads that decision *back from the blockchain*, not from the browser, so nobody
can get an explanation for a decision they made up. Its output is checked
against the recorded decision, and anything unsupported is replaced with fixed
template wording. Generated text is never written to the blockchain. Nothing is
sent to the internet.

---

## The earlier simulation study

`src/seba/` is a **synthetic benchmark that came before the system** and does
not describe it. It should always be labelled as a simulation.

It contributes an adversarial benchmark over a generated workload across five
seeds, and one result worth keeping: every integrity-based defence caught
ordinary tampering but caught **0%** of a re-signed log, while two methods that
check the *decisions* rather than the signatures caught **100%** — under
stronger assumptions about what the reviewer can see.

That is the same lesson as finding 5 above, reached by a different route.

We are careful about its limits. The drift detector is not the best defence
overall — it scores 0.25 against 0.79 for integrity methods and 1.00 for a
trusted oracle. It misses corruption below 10%, and its threshold moves with
workload size. `results/FINDINGS.md` records all of this, including where it
fails.

---

## Where things are

| Path | Contents |
|---|---|
| `seba_fabric_workspace/crime-records-network/` | **The system** |
| `CONTRIBUTION.md` | What we claim and what we refuse to claim |
| `TESTING.md` | How it is tested, in plain language |
| `REPRODUCE.md` | Commands to repeat the experiments |
| `src/seba/` | The earlier Python simulation study |
| `results/` | Result tables and honest findings |
| `research_pack/` | Problem framing, literature, architecture, ethics |
| `papers/` | The papers, in LaTeX |

Read `crime-records-network/README.md` first, then `docs/architecture.md`.

## How to run it

The system:

```bash
cd seba_fabric_workspace/crime-records-network
make up && make deploy && make seed
make test && make smoke
```

The earlier Python study:

```bash
pip install -e ".[dev]"
pytest
```

Typing `make` on its own lists every available command.

---

## What this work does not claim

- Real police access logs are not publicly available, so everything runs on
  synthetic data. We make no claim about behaviour on real CCTNS or ICJS data.
- The policy rules are our own, not official police policy.
- The network runs on one computer with a single ordering node, so its timings
  do not represent a real multi-site deployment.
- The certificate-authority compromise described above is analysed, not yet
  replayed against the live network. Doing so requires modelling a compromised
  department administrator.
- The privacy score counts how many columns are hidden. It is a rough
  indicator, not a mathematical privacy proof. The explanation score checks
  whether the right words appear; it does not judge whether a human would find
  the explanation useful.
- We do not claim this is ready to deploy, legally compliant, or
  production-secure.

## This is not crime prediction

This project controls **access to records**. It does not predict crimes or
suspects. Public crime statistics are summary counts, not individual access
records. Predictive policing can create feedback loops, because tomorrow's data
is shaped by today's policing. And complex prediction systems in criminal
justice often do no better than simple ones. The subject here is who may see a
file, not who might commit a crime.
