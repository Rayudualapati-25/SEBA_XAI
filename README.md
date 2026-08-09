# SEBA-XAI: Explainable Policy-Aware Audit for Secure Inter-Agency Police Data Access Governance

## The problem in one paragraph

Police records are shared between departments: police, forensic laboratories,
prosecutors, courts, and oversight bodies. When someone asks to see a sensitive
record, three questions need answering. Should they be allowed to see it? Is
there a record of that decision that nobody can quietly change afterwards? And if
someone reviews it a year later, can they find out *why* the answer was what it
was?

This project builds and tests a system that answers all three together.

## Why a job title is not enough

A sub-inspector and a constable might ask for the same case file and should not
get the same answer. The same officer might be allowed to see a record for one
reason and refused for another. Some records must stay closed to one department
while another reads them freely.

So the decision cannot come from the person's job title alone. It has to consider
who is asking, what they are asking for, why, and under what circumstances.

The project is designed for the Indian CCTNS/ICJS police systems. It does not
replace them, and it uses no real police records — all data is synthetic
(made-up test data).

---

## What is new here

The individual pieces already exist in published research: blockchain for
tamper-proof records, attribute-based access control for permissions, and
explainable AI for justifying decisions. **We did not invent any of those.**

Four things are new.

### 1. Studying the three together instead of separately

Most papers study access control, or audit logs, or explanations. Rarely all
three in one workflow. When you put them together, you can measure how they
interact — and find gaps that appear only in combination.

### 2. Finding an attack that tamper-proofing cannot catch

This is the core idea, and it is worth understanding properly.

A tamper-proof audit log works by signing each entry. If someone edits an entry,
the signature no longer matches, and the edit is detected.

But suppose the attacker controls the component that *does the signing*. Now they
can change a recorded decision and sign it again. The new signature is perfectly
valid. Every integrity check passes. **The log looks fine and the decision in it
is wrong.**

Think of it as a sealed envelope. Checking the seal proves nobody opened the
envelope. It proves nothing about whether the letter inside was true when it was
sealed.

### 3. Measuring how badly that gap matters

We tested this across five runs of a synthetic workload:

| Type of defence | Ordinary tampering | Re-signed attack |
|---|---|---|
| Signed hash chain | catches 100% | **catches 0%** |
| Blockchain-style audit | catches 100% | **catches 0%** |
| CT-style log | catches 100% | **catches 0%** |
| ABAC re-execution | catches 100% | **catches 0%** |
| Drift detector (NS-PI) | — | **catches 100%** |
| Trusted attribute oracle | — | **catches 100%** |

Every method that checks whether the log was *edited* scores zero. Only methods
that check whether the *decision itself makes sense* catch it.

The conclusion, which is easy to get wrong in practice:

> **Whether a log is untampered and whether its decisions are correct are two
> different things. Testing only for tampering does not tell you the decisions
> are right.**

### 4. Treating the explanation as evidence, not decoration

Every decision stores *why* it was made — which facts decided it, the rule that
fired, and what would have changed the outcome. That explanation is locked to the
decision with a hash, so it cannot be swapped later. A reviewer can check the
reasoning without opening the actual police record.

### What we are careful NOT to claim

NS-PI, our drift detector, is **not** the best defence overall. Its score across
all attacks is **0.25**, compared to **0.79** for the integrity methods and
**1.00** for the trusted oracle.

It is good at exactly one thing: raising an alarm when the reviewer can see
nothing except the signed decisions. It adds to the other methods; it does not
replace them.

We state this openly because an earlier, bigger claim was not supported by our own
evidence. `CONTRIBUTION.md` records what that claim was and why we dropped it.

---

## The four contributions, as written in the paper

1. **A layered permission system** that combines job role, attributes (rank,
   clearance, jurisdiction, case assignment) and policy rules, answering *allow*,
   *deny* or *escalate* — escalate meaning "a supervisor must decide this".
2. **A blockchain audit layer** storing, for each decision, an identifier, hashes
   of the decision and its explanation, the policy version, any approval
   reference, and a fingerprint of the record. The record itself stays with the
   agency that owns it.
3. **An explanation service** storing the deciding facts, a reason code, the
   policy version and a counterfactual, all locked to the audit entry.
4. **A repeatable attack benchmark** covering ordinary tampering plus the
   re-signed attack, comparing defences under clearly stated assumptions about
   what the reviewer can see.

---

## The working system

`seba_fabric_workspace/crime-records-network/`

The paper admits a limitation in Section V: its blockchain was **simulated**, not
a real one. We have now built the real thing.

Five departments — police, forensics, prosecution, judiciary, oversight — each
run their own server and their own ID-card issuer on Hyperledger Fabric 2.5.16.
Writing a record requires **three of the five departments to agree**, so no single
department can write to the shared record alone.

Each officer's role, rank, station, jurisdiction and clearance are written
*inside their digital ID certificate*, signed by their department. The blockchain
reads those facts from the signed certificate, not from a form the officer fills
in. That means an officer cannot claim a rank they do not have, and an
administrator cannot quietly change someone's clearance in a database.

### Measured results

| What we measured | Simulated (paper) | Real system |
|---|---|---|
| Time to record a decision | 11.10 ms | 72.69 ms |
| Time to verify one | 2.50 ms | 3.99 ms |
| Storage per decision | 353.50 B | 857 B |
| Attacks blocked | — | 6 out of 6 |

**Two things must be said with that table.**

The full time to record a decision is 2072 ms, but 2000 ms of that is a waiting
period we configured ourselves — the blockchain collects transactions for two
seconds before writing a block. The honest figure to compare is the remaining
**73 ms**. Quoting 2072 ms as "the cost of blockchain" would be wrong.

Storage is not a fair comparison either: our version stores the full explanation
inside each entry, so of course it is bigger.

Checked by: 70 smart-contract tests, 48 API tests against the running system, an
11-step full walkthrough, and a 6-attack replay. See `TESTING.md`.

### One thing we added beyond the paper

Searching and reading do not create blockchain transactions — only writing does.
So *who looked at a case* would leave no trace at all, which is backwards: in
police work, who looked is often more sensitive than who wrote.

We now record every search and read in a chained list where each entry contains a
fingerprint of the one before it. Change or delete any entry and the chain breaks.
The end of the chain is periodically written to the blockchain, so the list cannot
be rewritten afterwards without contradicting something already permanent.

### About the AI part

A language model running on the local machine turns each recorded decision into a
readable sentence.

**The AI does not decide anything.** The blockchain rules decide first and record
the decision. Only then is the AI asked to reword it. Its output is checked
against the recorded decision before being shown, and if it says anything
unsupported, fixed template wording is shown instead. Nothing is sent to the
internet.

### Where to read more

| File | Contents |
|---|---|
| `crime-records-network/README.md` | How to run it |
| `crime-records-network/docs/architecture.md` | How the parts fit together |
| `crime-records-network/docs/evaluation.md` | What we measured and its limits |
| `crime-records-network/docs/walkthrough.md` | How to demonstrate it |

---

## What is in this repository

| Path | Contents |
|---|---|
| `00_START_HERE.md` | Orientation |
| `CONTRIBUTION.md` | What we claim, and the bigger claim we dropped |
| `REPRODUCE.md` | Commands to repeat the experiments |
| `TESTING.md` | How the project is tested, in plain language |
| `seba_fabric_workspace/crime-records-network/` | The working Fabric system |
| `seba_fabric_workspace/prototype/` | The earlier Python prototype and its results |
| `src/seba/` | Python research code: NS-PI, attacks, comparison methods, metrics |
| `tests/` | Python tests |
| `experiments/` | Experiment plans and run records |
| `results/` | Result tables and findings |
| `research_pack/` | Problem framing, literature review, methodology, ethics |
| `reports/iteration/` | A log of each work session |
| `papers/` | The paper itself, in LaTeX |
| `scripts/` | Scripts that produce tables and figures |
| `sources/` | Literature and dataset lists |

---

## How to run it

The Python research code:

```bash
pip install -e ".[dev]"
pytest
```

The working blockchain system:

```bash
cd seba_fabric_workspace/crime-records-network
make up && make deploy && make seed
make test && make smoke
```

Typing `make` on its own lists every available command.

---

## What this work does not claim

- Real police access logs are not publicly available, so everything is tested on
  synthetic data. We make no claim about performance on real CCTNS or ICJS data.
- The policy rules are our own benchmark rules, not official police policy.
- The paper's blockchain results come from a simulation. The real system here runs
  on one computer with a single ordering node, so its timings do not represent a
  real multi-site deployment.
- The re-signed attack is not replayed against the real system. Doing so there
  would require stealing a department administrator's key, which is a much
  stronger assumption than the simulation makes.
- The privacy score counts how many columns are hidden. It is a rough indicator,
  not a mathematical privacy proof. The explanation score checks whether the right
  words appear in the text; it does not judge whether a human would find the
  explanation useful.
- We do not claim this is ready to deploy, legally compliant, or production-secure.

## This is not crime prediction

This project controls **access to records**. It does not predict crimes or
suspects. Public crime statistics are summary counts, not individual access
records. Predictive policing can create feedback loops, because tomorrow's data
is shaped by today's policing. And complex prediction systems in criminal justice
often do no better than simple ones. The subject here is who may see a file, not
who might commit a crime.
