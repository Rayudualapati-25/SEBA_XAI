# What we measured, and what the numbers mean

Every figure here was produced by a script in `experiments/` and can be
regenerated. Where a number could be misread, the caveat is written next to it.

---

## Checking the system works

Four kinds of check, because each one has something it cannot see.
`TESTING.md` at the repository root explains this in more detail.

| Check | Command | Count | What it proves |
|---|---|---|---|
| Smart contract tests | `make test-chaincode` | 70 | Each rule gives the right answer. Uses a pretend blockchain, so it cannot prove behaviour on the real one. |
| API tests | `make test-backend` | 48 | The website, server and real blockchain work together with real certificates. |
| Full walkthrough | `make smoke` | 11 | The whole story works, driven as the real officers. |
| Blockchain inspection | `make inspect` | 9 sections | Reads the actual blocks, signatures, certificates and history. |

The smart contract tests use a **mock** — a stand-in blockchain that just
remembers values in memory. That makes them run in 25 milliseconds, but it also
means they cannot catch anything specific to real Fabric. That is exactly why the
API tests exist as well.

One known difference is handled deliberately: the real Fabric returns an empty
value for a missing key, whereas a naive mock returns "undefined". Our mock copies
the real behaviour so tests cannot pass for the wrong reason.

**Coverage is about 97%** on the smart contracts. Coverage means the tests ran 97
lines out of every 100 — *not* that the code is 97% correct. You can run every
line and still have the logic wrong.

---

## Speed and storage

Produced by `experiments/measure.js`. 10 requests for each of the five seeds
{7, 21, 42, 99, 123}, so 50 timed measurements. Times are measured from the
client and include the website, the server, agreement between departments, and
writing the block.

| Measurement | Simulated (paper) | This system |
|---|---|---|
| Time to record a decision, complete | 11.10 ms | 2072.69 ms |
| — of which: the waiting period we configured | — | 2000 ms |
| — of which: the actual work | 11.10 ms | **72.69 ms** |
| Time to verify a decision | 2.50 ms | 3.99 ms |
| Storage per decision | 353.50 B | 857 B |

### Read the speed figure carefully

The complete figure looks alarming until you see where it comes from.

Our blockchain is set to collect transactions for **two seconds** before writing
them into a block. That is a setting we chose, not a cost of the design. The
evidence: across all 50 measurements the times ranged only 82 milliseconds apart,
all clustered just above 2000 ms. That flatness is the signature of a fixed wait,
not of varying computation.

The number to compare against the paper's 11.10 ms is the remaining **72.69 ms** —
the policy rules, building the explanation, three departments agreeing, and
writing the block. Lower the waiting period and the complete figure drops
immediately.

### Storage is not a like-for-like comparison

857 bytes against 353.50 is not overhead from Fabric. Our version stores the whole
explanation inside each entry; the simulated version stored a leaner record.

---

## The attack tests

Six attacks, each with a stated expectation. The script exits with an error if any
attack succeeds, so a security regression fails loudly rather than passing
silently.

| Attack | Caught by |
|---|---|
| Changing a stored explanation | recomputing its fingerprint from the blockchain |
| Editing a case file in the database | comparing with the fingerprint stored when it was filed |
| A department writing a record it may not write | the certificate check inside the blockchain |
| Backdating a request | the blockchain supplies its own timestamp |
| Reading an approval token from the blockchain | only a fingerprint of the token was ever stored |
| Deleting a line from the search log | the hash chain and its blockchain anchor |

All six are blocked.

**What this does not cover.** These are attacks on integrity, permissions and
information leakage. The paper's re-signed attack is *not* tested here. On a real
blockchain it would require stealing a department administrator's signing key,
which is a much stronger assumption than the simulation makes.

---

## Explanation quality

Produced by `experiments/evaluate-explanations.js`. Six decisions, each triggering
a different rule, written twice: once by fixed template wording and once by the
local AI.

| Measure | Template | AI |
|---|---|---|
| Mentions the deciding facts (average) | 1.00 | 0.92 |
| Mentions all of them | 1.00 | 0.83 |
| States the right decision | 1.00 | 1.00 |
| Mentions what would have changed it | 1.00 | 0.67 |
| Rejected by the checker | — | 0.50 |

The scoring rule is copied from `decisive_attribute_text_coverage()` in
`src/seba/xai_quality.py` line 117, so these numbers sit alongside the 0.781
reported in the paper.

### Four things to understand before quoting this

**1. The template scoring higher is expected, not a failure.** The measure asks
whether the deciding facts are named in the text. A template names them every
single time by construction. The original Python code calls this measure "a weak
textual proxy, not a human explanation-quality score". It rewards naming, not
readability — so it cannot show the AI's actual advantage.

**2. The AI column is what the user sees, not raw AI quality.** When the checker
rejects an AI sentence, template wording is shown instead — and that is what gets
scored. With a rejection rate of 0.50, half that column is template text.

**3. We added four word-hints the paper's list did not have** (`subject.role`,
`subject.clearance`, `object.recordType`, `subject.mspId`), because our rules use
facts the earlier simulation did not have. Without them those facts could never be
counted as mentioned.

**4. The comparison itself is not fully verified.** The scoring rule was rewritten
from Python into JavaScript. The two versions have never been run on identical
input and shown to agree. Until that check exists, "measured the same way as the
paper" is a claim, not a demonstrated fact.

---

## How much data these numbers rest on

Speed uses 50 measurements on one computer. Explanation quality uses six
decisions. That is enough to show the mechanisms work and to compare rough
magnitudes. It is **not** enough to state confidence intervals. The simulated
results in the paper used 1,000 requests across five seeds.

---

## Reproducing all of it

```bash
make up && make deploy && make seed
make ollama
ENABLE_EXPERIMENTS=1 make backend    # in a second terminal
make measure
make evaluate
```

`ENABLE_EXPERIMENTS=1` switches on the routes that deliberately damage data for
the tampering tests. It is off by default so it cannot be triggered accidentally.
