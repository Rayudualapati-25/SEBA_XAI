# Glossary

Every term used in the SEBA-XAI project, defined as it is used *here* rather
than in general. Where a term corresponds to code, the file is named.

Created: 2026-08-10

---

## 1. The system

**SEBA-XAI** — Secure, Explainable, Blockchain-Audited access governance. A
permissioned-blockchain system that decides whether a request to read a
sensitive criminal-justice record should be allowed, denied, or escalated, and
commits the decision together with the reasoning behind it. Implemented on
Hyperledger Fabric in `seba_fabric_workspace/crime-records-network/`.

**Access governance** — Deciding and recording *who may see which record, why,
and on whose authority*. Distinct from access control, which only decides.
Governance adds the requirement that the decision remain reviewable afterwards.

**System, not overlay** — SEBA-XAI executes the authorisation decision inside
the ledger rather than computing it elsewhere and writing the result down. An
overlay would log decisions; this makes them.

---

## 2. Hyperledger Fabric — the network

**Hyperledger Fabric** — An open-source permissioned blockchain platform. Unlike
public blockchains, every participant is a known, identified organisation. Version
2.5.16 here.

**Permissioned blockchain** — A blockchain where participants must be admitted
and hold issued identities. There is no mining, no anonymous participation, and
no cryptocurrency.

**Organisation (org)** — One independent participant in the network. This project
has five: Police, Forensics, Prosecution, Court, Audit. Each runs its own peer
and its own certificate authority.

**Peer** — A process belonging to one organisation that stores that org's copy of
the ledger, executes chaincode, and endorses transactions. Five here, one per
department.

**Orderer (ordering service)** — The process that receives endorsed transactions,
puts them in a total order, and packages them into blocks. Uses the `etcdraft`
consensus protocol. One node here, which is a deliberate scope limit.

**Channel** — A private communication and ledger scope shared by a set of
organisations. This project uses one channel, `crimechannel`, shared by all five.

**Ledger** — The append-only record. Two parts: the **blockchain** (the ordered,
immutable chain of blocks) and the **world state** (the current value of every
key, for fast lookup).

**World state** — The current value of every key in the ledger, held in CouchDB.
Derived from the blockchain; the blockchain is the authority.

**CouchDB** — The document database backing each peer's world state. Chosen over
the simpler LevelDB because it supports *rich queries* — querying by field
contents, which `QueryPendingEscalations` relies on.

**Block** — A batch of transactions plus a hash of the previous block. That
backward hash link is what makes the chain tamper-evident.

**Genesis block** — The first block, containing the channel's configuration. Some
settings, such as `BatchTimeout`, are sealed into it and cannot be changed
without rebuilding the channel.

**BatchTimeout** — How long the orderer waits, collecting transactions, before
cutting a block. Set to `2s` here, which accounts for 2000 ms of the 2072 ms
end-to-end commit latency. The system's own work is the remaining ~73 ms.

**Block height** — The number of blocks on a peer's chain. All five peers should
report the same height; a divergence means a peer is behind or the network is
inconsistent.

**etcdraft** — The Raft-based consensus protocol used by the ordering service to
agree on transaction order.

---

## 3. Fabric — chaincode and its lifecycle

**Chaincode** — The program that runs *on* the blockchain; Fabric's term for a
smart contract. Here it is `crimerecords`, written in JavaScript, comprising
three contracts.

**Smart contract** — Code that executes as part of a transaction and whose result
is agreed by multiple parties. In this project, the access-policy engine is a
smart contract, which is what makes the decision itself the consensus object.

**Transaction** — One invocation of chaincode: proposed, endorsed, ordered,
validated, committed.

**Endorsement** — A peer executing a proposed transaction and signing the result.
Endorsement happens *before* ordering; the network commits only what enough
organisations independently computed and signed.

**Endorsement policy** — The rule stating how many, and which, organisations must
endorse. Here `MAJORITY Endorsement` — three of the five orgs.

**Chaincode definition** — The agreed parameters of a deployed chaincode: name,
version, sequence, endorsement policy, private data collections. Committed to
the channel and approved by each org.

**Sequence** — An integer that must increase by exactly one with each committed
chaincode definition. A fresh channel starts at 1. Hardcoding it breaks after a
rebuild, which is why `deployCC.sh` now resolves it automatically.

**Version** — A human-readable label for the chaincode (`1.6` here). Unlike
sequence, it carries no protocol meaning.

**Package ID** — A hash of the packaged chaincode plus its label, e.g.
`crimerecords_1.6:56b29714…`. Uniquely identifies exactly one build. Two packages
built from identical source can have different package IDs if the packaging
differs, which is why installation must be checked by package ID and never by
label.

**Label** — A human-chosen name attached to a chaincode package
(`crimerecords_1.6`). Not unique, and therefore not safe to identify a package by.

**Install / approve / commit** — The three deployment stages. *Install* places the
package on a peer; *approve* records one organisation's agreement to a
definition; *commit* makes the definition active once enough orgs have approved.

**Private data collection (PDC)** — Data shared with only a subset of
organisations, where the full channel stores just a hash. Here `evidenceDetails`,
restricted to Police, Forensics, and Court.

**Transient data** — Data passed to a transaction without being written to the
blockchain. Used to send private evidence detail into a PDC.

**Composite key** — A ledger key assembled from multiple parts, e.g.
`access~recordId~decisionId`, allowing range queries over a prefix.

**Key history** — Fabric's record of every past value of a key. Used by
`GetAuditTrail` to reconstruct how a record changed, and by
`GetAccessLogAnchors` to retrieve every anchor ever written.

**Gateway** — The client-side API for submitting transactions. The backend opens
one gateway connection *per logged-in user*, so every transaction is signed by
that individual's key rather than a shared service account.

---

## 4. Fabric — identity and permissions

**MSP (Membership Service Provider)** — The component that decides which
certificates belong to which organisation, and what they are permitted to do.
Each org has one: `PoliceMSP`, `ForensicsMSP`, `ProsecutionMSP`, `CourtMSP`,
`AuditMSP`.

**Certificate Authority (CA)** — The service that issues X.509 certificates for
an organisation's members. Six run here — one per org plus the orderer's. **A
compromised CA is the central threat in this project**, because it can issue an
identity carrying any attributes it likes.

**X.509 certificate** — The signed digital identity document a user presents.
Contains their public key, their organisation, and — critically in this system —
their attributes.

**Certificate attribute** — A named value embedded in the certificate and signed
by the issuing CA: `role`, `rank`, `station`, `jurisdiction`, `badgeId`,
`clearance`, `credentialStatus`, `caseAssignments`. Because these are signed by
the department, **the requester cannot forge them**. Read in
`lib/util/identity.js`.

**Enrolment** — Obtaining a certificate and private key from a CA. `make seed`
enrols the 13 demo officers.

**TLS** — Encryption of the connections between peers, orderer, and clients.
Separate from the identity certificates used to sign transactions.

**Client identity (`ctx.clientIdentity`)** — The chaincode-side handle to the
caller's certificate, through which attributes and MSP are read.

---

## 5. Docker

**Docker image** — A frozen, read-only package containing a program plus its
runtime and libraries. The template a container is created from.

**Container** — A running instance of an image, with its own filesystem, memory,
and network address. One image, many containers: a single `fabric-peer` image
produces all five peers.

**Docker context** — Which Docker daemon the CLI talks to. This machine has
three: `colima` (where the network runs), `default`, and `desktop-linux` (the
shell default). A plain `docker ps` reads `desktop-linux` and shows nothing —
use `docker --context colima ps`.

**Colima** — A lightweight Linux VM providing Docker on macOS, used instead of
Docker Desktop.

**Tag** — A label pointing at an image, e.g. `:2.5.16`, `:2.5`, `:latest`.
Several tags can name the same image.

**Volume** — Docker-managed persistent storage. Removing volumes destroys ledger
data, which is what makes a teardown a genuine reset.

**Fabric images used here** — `fabric-peer`, `fabric-orderer`, `fabric-ca`,
`couchdb` run the network; `fabric-nodeenv` supplies the Node runtime in which
your chaincode is built and executed; `fabric-ccenv` and `fabric-javaenv` serve
Go and Java chaincode and are unused here.

**Chaincode container** — A container the peer builds from *your* source at
install time, named `dev-peer0.<org>.example.com-crimerecords_1.6-<packageID>`.
Five exist, one per organisation. These are the processes that actually run the
policy engine.

---

## 6. The access-control model

**RBAC (Role-Based Access Control)** — Permissions attached to job titles. Rule 3
of the engine: the base matrix of which role may perform which action on which
record type. Insufficient alone, because two officers of the same rank can
warrant opposite answers.

**ABAC (Attribute-Based Access Control)** — Decisions from attributes of the
subject, object, action, and environment. Rules 4–8: jurisdiction, assignment,
clearance, juvenile and sealed flags.

**PBAC (Policy-Based Access Control)** — Adds versioned policy, revocation
handling, and approval requirements. Rules 1 and 6's emergency exception, plus
the `policyVersion` recorded on every decision.

**Subject** — Who is asking. Attributes come from the certificate.

**Object** — What is being asked for. Attributes come from ledger state.

**Action** — What they want to do: `view`, `export`, `annotate`. Supplied by the
requester.

**Environment** — The circumstances: `purpose`, `timeWindow`, `emergencyFlag`,
`courtLink`, `approvalToken`. Supplied by the requester, and allow-listed before
use.

**Allow / deny / escalate** — The three possible outcomes. **Escalate** is a
first-class result meaning *a human authority must decide*, and the resulting
approval becomes part of the evidence.

**Clearance** — The sensitivity level a requester is cleared for: `low`,
`medium`, `high`. Compared against the record's sensitivity in rule 8.

**Jurisdiction** — The district a requester operates in. A mismatch escalates
unless an emergency approval token is present.

**Case assignment** — The list of case IDs an officer is assigned to, carried in
their certificate. Officers not assigned are denied, except roles whose duty is
cross-case review.

**Credential status** — Whether an identity is `active`. Rule 1 denies anything
else, which is how revocation takes effect.

**Purpose** — The declared reason for a request, which must be one of six
recognised values. A request with no valid purpose is denied.

**Assignment-exempt roles** — Roles whose work spans cases and are therefore not
subject to the assignment check: judge, magistrate, auditor, ombudsman, public
prosecutor, SHO.

**Escalation approver** — A role permitted to resolve an escalation: SHO, judge,
magistrate, ombudsman.

**Separation of duties** — The rule that an approver may not share both MSP and
role with the requester, so a request cannot be approved by its own originator's
position.

**Rule order** — The engine evaluates eight rules in fixed order and the first
match is final. Assignment is checked before clearance, so an unassigned officer
is told they are not on the case rather than that their clearance is too low.
Reordering would change the reason codes throughout the results.

**Deterministic policy** — No randomness, no clock dependence, no model
inference. The same request always yields the same decision, which is what
allows independent peers to agree.

---

## 7. Decision and explanation artifacts

**Decision event** — The record committed for each request: identifiers, a
minimised subject snapshot, the environment, the decision, the explanation, the
explanation hash, and the policy version.

**Explanation artifact** — The structured justification: decision, reason code,
decisive attributes, counterfactual, policy version. Produced by the same
evaluation as the decision and committed in the same write.

**Reason code** — A stable machine-readable label for *why*, e.g.
`RBAC_NO_PERMISSION`, `CROSS_JURISDICTION`, `INSUFFICIENT_CLEARANCE`,
`CRED_NOT_ACTIVE`, `NOT_ASSIGNED`, `SEALED_RECORD`, `JUVENILE_PROTECTED`,
`POLICY_SATISFIED`.

**Decisive attributes** — The specific fields that determined the outcome, named
by the rule that fired.

**Counterfactual** — What would have had to differ for the outcome to change, e.g.
*"decision would change if requester clearance were 'high'"*. Directly useful to
someone who has been refused.

**Explanation hash** — A SHA-256 digest of the explanation artifact, committed
alongside it, so a later substitution can be detected.

**Policy version** — Which version of the rules produced this decision
(`crime-policy-v1`), so old decisions remain interpretable after the rules change.

**Hash-linked / commitment** — Storing a hash rather than the data, so the data
can be verified later without being stored on the ledger.

**Atomic commitment** — Decision and explanation are written in one state update,
so neither can exist without the other and they cannot be made to disagree.

---

## 8. Off-chain storage and read accountability

**Off-chain storage** — Where the actual case files live: the agency's own
database, never the ledger. The ledger holds only a hash and a location
reference.

**Payload hash** — A SHA-256 commitment to a record's contents, stored on-chain.
Re-hashing the off-chain file and comparing detects direct database edits.

**Access log** — An off-chain record of reads and searches. Necessary because
reads do not create transactions, so *who looked* would otherwise leave no trace.

**Hash chain** — A list in which each entry contains a hash of the previous one:
`entryHash(n) = sha256(entryHash(n-1) ‖ canonical(entry n))`. Altering one entry
invalidates every entry after it.

**Anchor** — Writing the head hash of the off-chain access log to the ledger, by
default every 25 entries. After anchoring, the log cannot be rewritten without
contradicting something already permanent.

**Epoch** — An identifier for one continuous run of the access log. If the log is
legitimately rebuilt the epoch changes and the sequence may restart — permitted,
but visible in ledger history, so a rebuild can never be disguised as normal
operation.

**Monotonic sequence** — The anchor sequence number must strictly increase within
an epoch, preventing an attacker from re-anchoring an older head to conceal
later reads.

**Audit reconstruction** — Rebuilding what happened from committed evidence:
record metadata, key history, and every access decision with its explanation.

---

## 9. Explainable AI

**XAI (Explainable AI)** — Making an automated decision inspectable. Here the
explanation is *evidence committed with the decision*, not text displayed to a
user and discarded.

**Ollama** — A tool for running language models locally. Nothing is sent to the
internet.

**llama3.2:3b** — The local model used to reword committed decisions into plain
language.

**The model never decides** — The chaincode decides and commits first; the
backend then reads that decision *back from the ledger* and asks the model only
to phrase it. Generated text is never written on-chain.

**Validator** — The check applied to generated text. **Problems** mean the text
contradicts the committed decision, and it is discarded in favour of template
wording. **Warnings** mean the text is accurate but incomplete, and it is shown
with the gap recorded.

**Template wording** — Deterministic phrasing generated from the decision fields,
used as the fallback and as a baseline.

**Decisive-attribute text coverage** — The fraction of decisive attributes
actually named in the rendered text. Measures the *rendering*, not the artifact.
A known weakness: 0.781 in the simulation study, meaning traces are structurally
complete while the prose is not.

---

## 10. The simulation study (`src/seba/`)

Terms below belong to the **earlier synthetic study**, not the implemented
system. The two evidence bases must not be merged.

**Synthetic workload** — Generated officers, records, cases, and requests. Used
because real police access logs are not public.

**Seed** — A fixed random-number seed making a run reproducible. Five are used:
7, 21, 42, 99, 123.

**NS-PI (Neuro-Symbolic Policy Induction)** — The component that learns an
interpretable rule-list view of decisions and raises an alarm when the decision
distribution drifts.

**Drift detection** — Comparing two decision distributions and deciding whether
they differ by more than sampling noise.

**Jensen-Shannon divergence** — The symmetric measure of difference between two
probability distributions used by the drift detector.

**Permutation test** — Significance testing by shuffling labels many times (500
by default) and counting how often the shuffled divergence matches or exceeds the
observed one. The alarm fires when `p ≤ 0.05` *and* the divergence clears an
absolute floor.

**Attack catalogue** — The seven attacks scored: `replay_approval_token`,
`backdate_request`, `swap_explanation_hash`, `collude_block_signature`,
`revocation_race`, `compromised_signer`, `metadata_inference`.

**Compromised signer** — The decisive attack. The attacker corrupts a decision
and then re-signs the log with a genuine key, so every integrity check passes
while the stored decision was never authorised.

**AAS (Adversarial Audit Score)** — A severity-weighted detection rate across the
attack catalogue, normalised to [0, 1]. A defence catching only low-severity
attacks scores below one catching high-severity ones.

**Defences compared** — `mutable_log` (no integrity), `signed_chain`,
`blockchain_style`, `ct_log` (Certificate-Transparency-style Merkle log),
`abac_reexec` (re-running policy), `fabric_abac`, `nspi_drift`, and
`trusted_policy_oracle`.

**Trusted policy oracle** — A baseline that re-evaluates each request against an
uncompromised view of the original attributes. The strongest defence tested, and
also the strongest assumption: it presumes a trustworthy independent record of
the request.

**Visibility assumption** — What a defence is assumed to see. The oracle needs the
raw request; NS-PI needs only the signed decision log. This is why NS-PI matters
despite scoring lower overall — the two answer different questions under
different access.

**Trace completeness / counterfactual coverage / counterfactual validity /
audit reconstruction rate** — Measures of whether every decision has a full
structured trace, whether counterfactuals were produced, whether they actually
flip the decision when applied, and whether the trail can be rebuilt end to end.

**Metadata exposure score** — A schema-level count of how many fields remain
visible. A rough indicator, explicitly not a privacy proof.

---

## 11. Criminal-justice domain

**CCTNS** — Crime and Criminal Tracking Network and Systems. India's national
police record network. **Context for this project, never a baseline** — nothing
here is compared against or claims to improve it.

**ICJS** — Inter-Operable Criminal Justice System. Links the police pillar with
courts, prisons, forensics, and prosecution.

**FIR (First Information Report)** — The document recording a reported offence;
the starting point of a case file.

**Case diary** — The investigating officer's running record of an investigation.

**Chargesheet** — The document filed with the court on completion of
investigation.

**Juvenile protection** — Statutory restriction on the identity and records of a
minor. In this system it overrides rank: a superintendent is still escalated.

**Sealed record** — A record placed under court restriction. Escalates for
everyone except the Court itself.

**SHO (Station House Officer)** — The officer in charge of a police station; one
of the escalation approvers.

**Cross-jurisdiction request** — A request for a record outside the requester's
district. Escalates rather than being silently granted or refused.

---

## 12. Paper and venue

**ICDCN** — International Conference on Distributed Computing and Networking.
The 28th edition, January 2027, NITK Surathkal.

**acmart / sigconf** — The ACM LaTeX document class and the conference format
mandated by the call for papers.

**Double-blind review** — Author names and affiliations must not appear in the
submitted PDF.

**CCS concepts** — The ACM Computing Classification System categories a paper
declares.

**Camera-ready** — The final formatted version submitted after acceptance.
