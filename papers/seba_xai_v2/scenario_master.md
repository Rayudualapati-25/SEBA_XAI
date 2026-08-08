# SEBA-XAI Master Scenario — The Jewellery Shop Robbery

Working document. Source material for the introduction (compressed), methodology
(full), and figures. All names are fictional and illustrative.

---

## 1. The Case

**Crime:** Armed robbery at *Sri Lakshmi Jewellers*, Gandhi Bazaar market road.

**Jurisdiction:** Rajpur Town Police Station (**Station A**), Rajpur District,
in the state's CCTNS-connected network.

**Events:** Three masked men enter at closing time. One employee, Suresh, is
struck with an iron rod and injured. Gold ornaments (approx. 800 g) and the
owner's mobile phone are taken. Escape on a single motorcycle. One robber cuts
his forearm on a display counter and leaves blood on the glass. The shop's CCTV
and the DVR of the neighbouring textile shop record the incident.

**Registered as:** FIR No. 214/2026, Rajpur Town PS, under the robbery
provisions of the Bharatiya Nyaya Sanhita, 2023 (verify exact section from a
primary source before citing in the paper).

**The complicating fact (revealed in week 2):** one of the three accused,
identified from CCTV, is **17 years old** — a juvenile. From that moment his
identity and records fall under statutory protection, and rank no longer
determines who may see them.

---

## 2. People and Roles

### Inside Rajpur Town PS (Station A)
| Person | Role | Relation to case |
|---|---|---|
| SI Meena Kumari | Sub-Inspector, **Investigating Officer** | Assigned by SHO; owns the case diary |
| Insp. Prakash Rao | SHO, Station A | Supervises; assigns the IO |
| HC Ravi | Head Constable | Assists IO on documented tasks |
| Constable Ajay | Constable, **not assigned** | Same station, no connection to the case |

### Wider police hierarchy
| Person | Role | Relation |
|---|---|---|
| DySP Farida Begum | Sub-Division, Rajpur | **Escalation authority** for cross-boundary and sensitive requests |
| SP Rajpur | District chief | Policy authority; does NOT get automatic record access |
| SI Deepak Nair | SI, Kothapet PS (**Station B, Neighbouring District Y**) | Investigating a similar gang robbery; wants MO comparison |
| Insp. Sana Sheikh | Cyber Crime Cell, District HQ | Traces the stolen phone |

### Forensics (separate department, separate authority)
| Person | Role | Relation |
|---|---|---|
| Dr. K. Venkatesh | Scientific Officer, Regional FSL | Analyses the blood sample |
| Fingerprint Bureau examiner | NAFIS search | Matches counter lifts |

### Justice-side pillars
| Person | Role | Relation |
|---|---|---|
| APP Lakshmi Devi | Assistant Public Prosecutor | Builds the trial case after chargesheet |
| Probation Officer, JJB | Juvenile Justice Board | Sole lawful route to the juvenile's records |
| District Jail, Rajpur | Prisons | Custody of the two adult accused |
| Registrar, Sessions Court | Courts | Trial records |

### External / oversight
| Person | Role | Relation |
|---|---|---|
| Insurance surveyor | External company | Owner's theft claim: needs FIR copy only |
| RTI applicant | Public | Seeks case details mid-investigation |
| Justice (Retd.) Iyer | **Inquiry authority, 6 months later** | Reviews whether every release was proper |

---

## 3. Records the Case Generates

| # | Record | Held by | Sensitivity driver |
|---|---|---|---|
| R1 | FIR 214/2026 | Station A | Baseline; partly disclosable |
| R2 | Complainant statement (owner) | Station A | Victim identity |
| R3 | Witness statements (Suresh, passer-by) | Station A | Witness safety |
| R4 | Medico-legal certificate (Suresh) | Govt. hospital / Station A | Medical data |
| R5 | Case diary | Station A (IO only) | Investigation strategy — most restricted police record |
| R6 | Seizure memos, property list | Station A | Evidence chain |
| R7 | CCTV + DVR extraction report | Station A / Cyber cell | Third-party faces |
| R8 | Blood sample + fingerprint lifts | FSL custody | Exhibit chain integrity |
| R9 | Phone IMEI, CDR, tower dump | Cyber cell (telecom route) | Communications privacy |
| R10 | **Juvenile's identity + records** | Station A / JJB | Statutory protection — defeats rank |
| R11 | Chargesheet | Station A → Court | Disclosable at trial stage |
| R12 | Remand / custody records | Court / Jail | Liberty-related |

---

## 4. The Permissioned Blockchain — Who Runs What

This is the part the scenario must make concrete. The audit ledger is a
**consortium** ledger: known organisations, identified members, no public
mining. (In the prototype this is a Fabric-style simulated ledger; the paper
must not claim a live production network.)

**Consortium members (each operates a peer node holding the full ledger):**

1. **District Police organisation** (covers Station A, Station B's district
   via its own org, cyber cell)
2. **Regional FSL**
3. **Prosecution directorate**
4. **Courts / Juvenile Justice Board**
5. **Oversight body** (inquiry/audit authority — read-focused peer)

**Design decisions the scenario illustrates:**

- **What goes ON-chain per decision (one audit event):**
  request ID, requester attributes digest, record identifier *commitment*
  (salted hash, not the record ID in clear), decision label, decision hash,
  **explanation hash**, policy version, approval reference (if escalated),
  timestamp, block linkage.
- **What NEVER goes on-chain:** the FIR, statements, the case diary, the
  juvenile's identity, CDRs, any raw record. R1–R12 stay in the holding
  agency's own store. The ledger holds *evidence about decisions*, not data.
- **Why permissioned, not public:** members are known legal entities; the
  point is mutual non-repudiation between agencies that do not fully trust
  each other's record-keeping, not anonymity or cryptocurrency.
- **Why multiple peers matter:** Station A cannot silently rewrite history,
  because FSL, prosecution, courts, and oversight each hold the same chain.
  Any single-org rewrite diverges from four other copies.
- **Endorsement idea (Fabric-style):** an audit event is committed only when
  peers from more than one organisation endorse it — e.g. police + one
  justice-side org — so no single agency can unilaterally mint audit history.

---

## 5. The Requests — Walked Through the System

Each request is evaluated on attributes: requester identity & rank, department,
case assignment, record sensitivity class, requested action, stated purpose,
jurisdiction, case stage, emergency flag.

| # | Request | Decision | Decisive attributes | On the ledger |
|---|---|---|---|---|
| Q1 | SI Meena (IO) → full file R1–R8 | **ALLOW** | assignment=this case; jurisdiction=Station A; purpose=investigation | Event with decision+explanation hashes, policy v3.1 |
| Q2 | Constable Ajay → R5 case diary | **DENY** | assignment=none. Same station, same uniform as Q1 — different answer | Deny event recorded (denials are evidence too) |
| Q3 | SI Deepak (Station B, District Y) → R7 stills + MO summary | **ESCALATE → DySP approves R7-redacted** | cross-district; linked-case purpose; sensitivity=medium | Escalation event + **approval reference naming DySP Farida** |
| Q4 | Dr. Venkatesh (FSL) → R8 exhibit chain + R6 | **ALLOW** | department=FSL; purpose=analysis; records=exhibit class | Narrow-scope allow event |
| Q5 | Dr. Venkatesh (FSL) → R2 victim identity | **DENY** | record class=victim-identity; department entitlement=none. Same person as Q4, minutes apart | Deny event |
| Q6 | Insp. Sana (cyber) → R9 IMEI/CDR | **ALLOW** | purpose=device tracing; scope=R9 only | Allow event |
| Q7 | Insp. Sana → R4 medical report | **DENY** | outside stated purpose | Deny event |
| Q8 | APP Lakshmi → full file, pre-chargesheet | **DENY (stage)**, later **ALLOW** | case stage gate | Two events; stage attribute differs |
| Q9 | Probation Officer (JJB) → R10 | **ALLOW** | statutory role match | Allow event |
| Q10 | SP Rajpur → R10 juvenile identity | **DENY** | sensitivity class defeats rank | Deny event — the ledger now proves the SP was refused |
| Q11 | Insurance surveyor → FIR copy | **ALLOW (2 fields)** | external, purpose=claim; minimal scope | Allow event, field-limited |
| Q12 | RTI applicant → case details | **DENY** | investigation pending | Deny event |

**Teaching pairs:** Q1/Q2 (assignment beats role), Q4/Q5 (same person, two
answers), Q6/Q7 (purpose-bound), Q3 (escalation is a third outcome and the
approval itself becomes ledger evidence), Q10 (sensitivity beats rank).

---

## 6. The Audit, Six Months Later

Justice Iyer's inquiry asks:

1. Why did FSL see the exhibit chain? → ledger event Q4: decisive attributes,
   policy v3.1, explanation hash matches the stored explanation.
2. Who approved the cross-district release? → event Q3 carries the approval
   reference: DySP Farida, timestamped.
3. Was the juvenile's identity ever released? → events Q9 (JJB, lawful) and
   Q10 (SP, refused). Nothing else. The *absence* of other events is itself
   verifiable because the chain is append-only and replicated across five
   organisations.

None of this required opening a single record. The inquiry examined evidence
about decisions, verified against four independent peer copies.

---

## 7. The Attack

A compromised insider gains control of the **signing component** in the police
organisation's audit pipeline. He takes event Q5 — *DENY victim identity to
FSL* — rewrites the decision to ALLOW, recomputes the hashes, and re-signs
with the genuine key before commitment.

- Signature: **valid**
- Chain linkage: **intact**
- Peer copies: **consistent** (the corruption happened before replication)
- The inquiry's integrity check: **passes**

The ledger now faithfully preserves a decision that policy never made. This is
the failure the paper isolates: integrity mechanisms certify *that the log was
not changed after writing* — they cannot certify *that what was written was
true*. Detection requires examining the decisions rather than the signatures:
statistical drift over the decision log, or re-computation against a trusted
copy of the raw request. Both, in the benchmark: 1.00 detection where every
integrity defence scores 0.00 — each under stronger visibility assumptions.

---

## 8. Usage Map

| Paper section | What to take from this document |
|---|---|
| Introduction | Compressed: FIR, five requesters (Q1, Q2, Q3, Q4+Q5 as one contrast, inquiry), juvenile fact in one line, attack as closing beat |
| Methodology — architecture | §4 consortium, on-chain/off-chain split |
| Methodology — policy model | §5 attribute table |
| Threat model | §7 verbatim |
| Results framing | §6 + §7 (what the inquiry can and cannot answer) |
| Figure 1 candidate | §4 members + §5 flow as the architecture walkthrough |

**Honesty guards:** synthetic evaluation; simulated Fabric-style ledger, not a
live deployment; BNS section number to be verified; all names fictional.
