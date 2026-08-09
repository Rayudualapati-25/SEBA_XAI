# How this project is tested

Written for someone who has not worked with automated tests before. It explains
what testing means here, what the tests actually check, how to run them, and what
the results currently are.

---

## What a test is

A test is a small piece of code that runs part of the project and then checks the
answer. If the answer is what we expected, the test passes. If not, it fails and
prints what it expected and what it got.

The point is not to prove the software is perfect. It is to catch the moment you
break something that used to work. Without tests you find that out when your
professor is watching.

Two words you will see:

- **Assertion** — the actual check. "I expected `deny`, and I got `deny`."
- **Suite** — a collection of tests you run together.

---

## Why there are four different kinds

Different tests answer different questions, and each has a blind spot. That is
why we use several kinds rather than one.

| Kind | Question it answers | Speed | Blind spot |
|---|---|---|---|
| **Unit** | Does this one function give the right answer? | Milliseconds | Cannot see whether the pieces work *together* |
| **Integration** | Do the pieces work together against the real system? | Seconds | Slower; needs the network running |
| **End-to-end** | Does the whole story work like a real user? | About a minute | Tells you *that* something broke, not *where* |
| **Attack replay** | Does the security actually stop an attacker? | Seconds | Only tests the attacks we thought of |

A unit test is fast because it does not touch the blockchain at all. We give the
code a **mock** — a pretend blockchain that just remembers values in memory. That
makes the test run in milliseconds, but it also means a unit test can pass while
the real blockchain behaves differently. That is exactly why integration tests
exist as well.

---

## The two halves of this project

There are two separate codebases, so there are two separate test suites.

| Half | Language | What it is |
|---|---|---|
| `seba_fabric_workspace/crime-records-network/` | JavaScript | The live Hyperledger Fabric implementation |
| `src/seba/` | Python | The research package that produced the paper's simulated results |

They are tested with different tools because they are different languages:
**Mocha** for JavaScript, **pytest** for Python. The ideas are the same.

---

## Testing the Fabric implementation

Everything below runs from `seba_fabric_workspace/crime-records-network/`.

### 1. Smart contract tests — 70 tests

```bash
make test-chaincode
```

These check the rules inside the blockchain code. For example, one test files a
record as a police inspector, then has a defence counsel request it, and asserts
the answer is `deny` with the reason `RBAC_NO_PERMISSION`.

They finish in about 25 milliseconds because of the mock blockchain. There is no
Docker, no network, nothing to start.

Some things they check:

- Each of the eight access rules gives the right answer
- A forensics user cannot file a police record
- The case narrative never reaches the ledger
- An approval token is stored only as a hash, never in plain text
- A judge cannot approve their own escalation

### 2. API tests — 48 tests

```bash
make test-backend
```

These use the **real running blockchain**. They log in as real seeded officers,
file real records, and check the real answers.

This is the layer that catches what the mock cannot. Each one takes about two
seconds, because a real blockchain transaction has to be agreed by three
organisations and written into a block.

### 3. End-to-end scenario — 11 checks

```bash
make smoke
```

One continuous story, in order:

1. A police inspector files a case record
2. A forensics analyst is blocked from filing one
3. The analyst attaches evidence instead
4. A defence counsel is denied
5. A constable is escalated
6. A judge approves the escalation
7. An officer with a revoked credential is denied
8. A prosecutor is allowed
9. An auditor reconstructs the whole trail
10. Someone edits the off-chain file and the check catches it
11. Someone forges an explanation and the check catches it

If this passes, the system works the way the paper describes.

### 4. Attack replay — 6 attacks

```bash
make measure
```

Instead of checking that good things work, this checks that bad things fail. It
performs six attacks and asserts each one is caught:

| Attack | Should be caught by |
|---|---|
| Changing a stored explanation | the on-chain hash no longer matches |
| Editing a record in the database | the payload hash no longer matches |
| A department writing a record it may not write | the certificate check |
| Backdating a request | the blockchain supplies its own timestamp |
| Reading an approval token from the ledger | only the hash was ever stored |
| Deleting a line from the access log | the hash chain and its on-chain anchor |

The script exits with an error if any attack succeeds, so a security regression
fails loudly instead of passing quietly.

### Running everything

```bash
make test     # both JavaScript suites
```

---

## Testing the Python research package

From the repository root:

```bash
pip install -e ".[dev]"
pytest
```

64 tests. Each file covers one part:

| File | What it checks |
|---|---|
| `test_attacks.py` | The attack catalogue and the scoring function |
| `test_baselines.py` | The re-implemented comparison methods from the literature |
| `test_nspi_learner.py` | The rule learner produces a policy matching the oracle |
| `test_nspi_drift.py` | No false alarm on unchanged data; alarm fires on real change |
| `test_nspi_counterfactual.py` | The "what would have changed the outcome" generator |
| `test_xai_quality.py` | The explanation-quality metrics used in the paper |
| `test_schema.py` | Data records cannot be modified after creation |
| `test_grid.py` | The full every-defence-against-every-attack evaluation |
| `test_aggregate_seeds.py`, `test_seed_confidence_summary.py`, `test_workload_policy_stress.py` | The scripts that combine results across the five seeds |

---

## What the results are right now

Measured, not assumed.

| Suite | Result |
|---|---|
| Smart contract tests | **70 passed** |
| API tests | **48 passed** |
| End-to-end scenario | **11 passed, 0 failed** |
| Attack replay | **6 of 6 attacks caught** |
| Python tests | **54 passed, 2 failed, 15 skipped, 4 errors** |

### The Python suite is not fully green, and here is why

This is a real problem worth understanding rather than hiding.

Some Python tests read data files produced by earlier experiment runs. They look
for those files at `prototype/runs/`, measured from the repository root. The files
are actually stored at `seba_fabric_workspace/prototype/runs/`.

The path does not match, so those tests cannot find their input:

- **15 skipped** — the test noticed the file was missing and skipped itself politely
- **4 errors** — the test could not even start, because its setup needed the file
- **2 failed** — the test ran and its expectation did not hold

The 54 that pass are the ones testing pure logic, which need no data files.

**Nothing is lost.** The 370 run files exist; they are simply at a different path
than the tests expect. This mismatch predates the Fabric work in this repository.

Two ways to fix it, when you want to:

1. Update the path in `tests/conftest.py` to point at
   `seba_fabric_workspace/prototype/runs/`
2. Or re-run the experiments so fresh artifacts land where the tests look

Until then, be aware that `pytest` will not come back clean, and say so if asked
rather than letting someone discover it.

---

## What "coverage" means

You will see a number like 97% after the smart contract tests.

Coverage measures **how much of your code the tests actually ran**. 97% means 97
lines out of every 100 were executed at least once during testing.

It does **not** mean the code is 97% correct. You can run every line and still
have the wrong logic. High coverage means "few untested corners", not "proven
right". Treat a low number as a warning and a high number as the absence of one
particular worry.

---

## When something fails

Read the failure message. It tells you three things: which test, what it
expected, and what it got.

```
1) AccessContract
     escalates a constable with insufficient clearance:
   AssertionError: expected 'allow' to equal 'escalate'
```

That says: the rule that should escalate a low-clearance request let it through
instead. The test is doing its job — it caught a real problem.

| Symptom | Usual cause |
|---|---|
| Everything suddenly very slow | Leftover Docker containers. Run `make clean-containers` |
| API tests fail to connect | The backend is not running. Run `make backend` |
| Every blockchain test fails | The network is down. Run `make up` |
| Python tests skip a lot | The missing run artifacts described above |

---

## The honest limits of this testing

Worth stating plainly, because someone will ask.

- **The measurement scripts are not themselves tested.** A bug in the code that
  produces the latency and quality numbers would give wrong figures and nothing
  would catch it.
- **The explanation-quality scoring was rewritten from Python into JavaScript,
  and the two versions have never been run on the same input and shown to
  agree.** Until they are, "measured the same way as the paper" is a claim, not a
  demonstrated fact.
- **The attack replay only covers the six attacks we chose.** It is not proof
  that no other attack works.
- **Sample sizes are small.** Latency uses 50 measurements on one machine;
  explanation quality uses six decisions. Enough to show the mechanisms work, not
  enough to state a confidence interval.
