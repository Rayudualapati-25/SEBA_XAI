# How the system is built

Written to be readable without prior blockchain knowledge.

## The four parts

```
website  ──►  web server  ──►  rules running inside the blockchain  ──►  permanent record
                   │
                   ├──►  ordinary database: the actual case files, accounts, search log
                   └──►  local AI: rewords a decision that was already made
```

Two design choices carry most of the weight.

### The case files are not on the blockchain

The blockchain stores facts *about* a record: its type, how sensitive it is, and
a fingerprint (hash) of its contents. The file itself sits in the department's
own database.

Why: a blockchain copies everything to all five departments, permanently. Putting
case narratives on it would give every department a permanent copy of every police
file — worse for privacy, not better. It would also make deletion impossible,
which matters for juvenile records and court-ordered erasure.

### The decisions are made inside the blockchain, not in the website

The web server cannot grant access. It can only pass on a request and record what
the blockchain decided. The AI can only reword a decision after it was made.

Why: rules that live in the website can be bypassed by anyone who talks to the
server directly. Rules inside the blockchain run on all five departments' servers
and must be agreed by three of them.

---

## How a decision is made

The code is in `chaincode/crimerecords/lib/policy/policyEngine.js`.

Three sources of information are combined, and it matters which is which:

| Information | Comes from | Can the requester fake it? |
|---|---|---|
| Who they are: role, rank, station, jurisdiction, clearance, credential status, case assignments | their signed digital certificate | **No** |
| The record: type, sensitivity, juvenile/witness flags, sealed status, jurisdiction, case | the blockchain's own stored record | **No** |
| What they want to do: view, export, annotate | their request | Yes |
| The circumstances: purpose, time window, emergency flag, court link, approval token | their request | Yes |

Only the last two come from the requester. Their identity and the record's facts
cannot be tampered with by the person asking.

### The eight rules, checked in order

The first rule that matches gives the answer. Nothing after it runs.

| # | If this is true | Answer | Reason code |
|---|---|---|---|
| 1 | Their credential is suspended or revoked | deny | `CRED_NOT_ACTIVE` |
| 2 | No valid reason was given for the request | deny | `INVALID_PURPOSE` |
| 3 | Their role has no permission for this action on this record type | deny | `RBAC_NO_PERMISSION` |
| 4 | The record is sealed and they are not the court | escalate | `SEALED_RECORD` |
| 5 | A juvenile is involved and their role is not permitted | escalate | `JUVENILE_PROTECTED` |
| 6 | They are in a different jurisdiction | escalate — or allow with an emergency approval token | `CROSS_JURISDICTION` |
| 7 | They are not assigned to this case | deny | `NOT_ASSIGNED` |
| 8 | Their clearance is lower than the record's sensitivity | escalate | `INSUFFICIENT_CLEARANCE` |
| — | Everything passed | allow | `POLICY_SATISFIED` |

**The order matters.** Assignment (rule 7) is checked before clearance (rule 8),
so an unassigned officer is told "you are not on this case" rather than "your
clearance is too low". Reordering the rules would change which reasons appear in
our results.

Every rule returns four things, not one: the answer, a reason code, **which facts
decided it**, and **what would have changed the outcome**. Because the explanation
comes from the same code as the decision, the two can never disagree.

The rules are **deterministic**: no randomness, no AI, no dependence on the clock.
The same request always gives the same answer and the same reason. That is what
makes the experiments repeatable.

---

## The three programs inside the blockchain

In `chaincode/crimerecords/lib/`:

| Program | What it does |
|---|---|
| `recordContract.js` | Creates records, attaches evidence fingerprints, seals and unseals, searches |
| `accessContract.js` | Handles access requests, runs the rules, stores the explanation, handles supervisor approvals |
| `auditContract.js` | Lets reviewers verify explanations and files, rebuild a record's history, and anchor the search log |

Two helper files: `identity.js` reads the facts out of the signed certificate and
enforces which department may do what. `validate.js` checks incoming data and
computes fingerprints.

---

## Two ways we detect tampering

### 1. Checking a case file has not been altered

When a record is filed, a fingerprint of the file is stored on the blockchain.
Later, a reviewer can re-fingerprint whatever is in the department's database and
compare. If someone edited the file directly in the database, the two no longer
match.

### 2. Checking the search history has not been altered

Searching and reading do not create blockchain transactions — only writing does.
So who *looked* at a case would leave no trace.

We record every search and read in a list where each entry contains a fingerprint
of the entry before it. This is called a **hash chain**: change or delete one
entry and every entry after it stops matching.

Then, every 25 entries, the fingerprint at the end of the chain is written to the
blockchain. Now the list cannot be rewritten at all, because doing so would
contradict something already permanent.

An **epoch** marker records when the list is deliberately rebuilt — for example
when the database is recreated during development. Without it, a legitimate
rebuild would look identical to tampering. The epoch is visible in the blockchain
history, so a rebuild is allowed but never hidden.

---

## The AI wording layer

In `backend/src/llm/`.

The order of events matters:

1. The blockchain rules decide and record the decision.
2. The web server reads that decision **back from the blockchain** — not from the
   browser, so nobody can ask for an explanation of a decision they invented.
3. A prompt is built from a fixed list of safe fields.
4. The local AI writes two or three sentences.
5. The result is checked before it is shown.

The check has two levels. **Problems** mean the AI said something false — for
example claiming access was allowed when it was denied. That text is thrown away
and fixed template wording is used instead. **Warnings** mean it is true but
incomplete, such as leaving out what would have changed the outcome. That text is
still shown, with the gap recorded.

The prompt never contains the case narrative, the complainant's details, the
badge number, the approval token or the evidence description. A test enforces
this by planting marker strings and confirming they never appear.

Generated text is never written to the blockchain. If it were, the permanent
record would depend on something that can vary between runs.

---

## The website

In `frontend/`. Plain JavaScript, no build step — edit a file and refresh.

Features are listed in one file, `js/modules/index.js`. Adding a screen means
creating one file and adding one line there; the menu, the address bar and the
role-based hiding all follow automatically. See `frontend/README.md`.

The role lists in `frontend/js/core/access.js` decide what appears in the menu.
**They are not security.** They stop officers seeing buttons that would fail
anyway. The real checks are in the web server and, most importantly, in the
blockchain.
