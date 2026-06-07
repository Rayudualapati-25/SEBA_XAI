# Related Work (Draft v1)

Status: draft text for the SEBA-XAI paper. Not final camera-ready prose.
Evidence basis: paper-level claims, citations, and URLs in this section are
drawn exclusively from `research_pack/01_literature_review.md` and `research_pack/02_literature_matrix.csv`.
Statements that are analysis or positioning rather than a sourced fact are
tagged `[INTERPRETATION]`.

We organise prior work into four clusters that correspond to the layers
SEBA-XAI overlays: (A) the Indian digital policing baseline, (B) blockchain
for evidence and chain-of-custody audit, (C) security, privacy, and access
control standards and prototypes, and (D) explainable, fair, and high-stakes
decision systems including predictive-policing feedback loops.

## A. Indian Digital Policing, CCTNS, and ICJS

### A.1 What exists
The Indian baseline is not a missing data infrastructure. The Press
Information Bureau release of 2026-03-11 reports that all 17,798 police
stations were using CCTNS as of 2026-02-01, with FIRs, chargesheets, and
related records entered in state data centres, replicated to a National Data
Centre, and searchable through standardised master codes for states,
districts, stations, acts, and sections [1]. The Ministry of
Home Affairs describes ICJS as integrating Police/CCTNS, Courts/e-Courts,
Jails/e-Prisons, Forensics/e-Forensics, and Prosecution/e-Prosecution through
a Data Sharing Matrix [2].

### A.2 What it contributes
These sources establish that an operational, inter-pillar criminal-justice
data fabric already exists in India and that record entry, replication, and
inter-pillar sharing are governed by official processes and standardised
codes. They define the institutional surface that any audit or access-control
proposal must respect.

### A.3 What is missing for SEBA-XAI / how we position
`[INTERPRETATION]` Neither source is an open research artifact: the CCTNS and
ICJS descriptions are administrative and do not include reproducible workloads,
access-decision benchmarks, or instrumented explanation logs. SEBA-XAI is
therefore positioned in `research_pack/01_literature_review.md` Section 1 as an overlay for
auditable authorization, provenance, privacy, and explainable review, not as a
replacement for CCTNS or ICJS and not as a claim of first national data-sharing
capability.

## B. Blockchain for Evidence, Chain-of-Custody, and Permissioned Audit

### B.1 What exists
A line of work uses blockchain to record evidence lifecycle events and access
provenance. The Two-Level Blockchain System for Digital Crime Evidence
Management proposes a hot/cold blockchain evidence architecture [7], and
LEChain addresses chain-of-custody and verifiability for digital forensics
[8]. A Hyperledger Fabric-based
Digital Evidence Management Model gives a practical Fabric implementation
reference [13]. The Hyperledger Fabric paper
itself describes the permissioned architecture, modular consensus, and
membership identities that motivate Fabric as a candidate audit layer for
known agencies [5]. A complementary auditable
access-control design for distributed business processes argues for blockchain
audit value across organisations [14].

### B.2 What it contributes
Collectively these works demonstrate that permissioned blockchains can host
evidence-lifecycle events, that hot/cold and on-chain/off-chain separations
are common, and that Fabric-style membership identities support known-agency
deployments. The survey on blockchain-based access-control systems [15] and
NISTIR 8403 on Blockchain for Access Control Systems [4] catalogue
patterns and constraints so that novelty claims in this space stay calibrated.

### B.3 What is missing for SEBA-XAI / how we position
`[INTERPRETATION]` These works concentrate on evidence custody or generic
data-sharing prototypes; they are not evaluated as a CCTNS/ICJS-compatible
inter-station access workflow that jointly considers attribute-based
authorization, superior approval, off-chain encryption, and explanation
logging, which is the gap noted in `research_pack/01_literature_review.md` Section 2.
SEBA-XAI takes the off-chain-data / on-chain-commitment pattern from this
cluster and adds policy-drift detection over the signed decision log, as
defined in the companion threat model and Results drafts. We do not claim a
real Fabric deployment or measure Fabric infrastructure performance.

## C. Security, Privacy, and Access Control (RBAC / ABAC / PBAC)

### C.1 What exists
NIST SP 800-162 defines ABAC as authorization based on subject, object,
action, and environmental attributes evaluated against policies, and notes
its suitability for information-sharing across organisational boundaries [3].
A Fabric+ABAC scheme for data sharing on Hyperledger Fabric shows that
chaincode can enforce fine-grained attribute policies with encrypted off-chain
storage and on-chain references [6]. More recent work on accountable and
privacy-preserving blockchain-based access control targets permission
invisibility, access anonymity, and accountability for sensitive attributes
[16]. On the privacy side, a survey of privacy-preserving machine learning
maps the trade-offs across
differential privacy, federated learning, secure multiparty computation,
homomorphic encryption, and trusted execution [17], and Deep Learning with
Differential Privacy provides the canonical differentially private training
reference [18].

### C.2 What it contributes
This cluster gives SEBA-XAI a standards-grounded vocabulary for
attribute-based and policy-based access decisions, a concrete Fabric+ABAC
implementation pattern, and a clear map of which privacy techniques carry
which utility costs. NISTIR 8403 [4] and the blockchain access-control survey
[15] further constrain what counts as a novel contribution in this area.

### C.3 What is missing for SEBA-XAI / how we position
`[INTERPRETATION]` `research_pack/01_literature_review.md` Section 3 notes that most
access-control papers in this cluster evaluate technical access logic but do
not jointly evaluate police-specific sensitive-record workflows, explanation
artifacts, superior-approval steps, and audit reconstruction under explicit
threat cases. SEBA-XAI uses Fabric+ABAC and ABAC re-execution as evaluated
baselines (as listed in the companion Results draft Section 1) and adds a
trusted raw-attribute policy oracle and an NS-PI log-only drift detector to
distinguish detector visibility, rather than proposing a new cryptographic
scheme. We do not claim formal privacy properties or production security
properties for the overlay.

## D. XAI, Fairness, and High-Stakes / Law-Enforcement Decision Systems

### D.1 What exists
Rudin argues that high-stakes decisions should prefer interpretable models
over black-box models with post-hoc explanations [9]. Dressel and Farid show that
simple baselines can rival more complex recidivism tools, warning against
overclaiming AI sophistication in criminal-justice risk scoring [19]. The
fairness literature establishes
that accuracy, calibration, and error-rate parity can conflict when base
rates differ [20], [21]. Ensign et al. analyse runaway feedback
loops in predictive policing, showing that policing more in an area can
generate more observed incidents and reinforce model attention to that area
[11]. Recent law-enforcement XAI
work emphasises stakeholder-specific explanations, AI literacy, and
automation-bias risk [10], with a dialogue-based XAI field study in a
predictive-policing setting [22] and an architecture combining blockchain
audit with XAI artifacts for legal decisions [23] and a related
blockchain-XAI-justice architecture proposal [24]. India-specific crime-XAI
work using NCRB data is exemplified by aggregate analyses [25], a state-wise
murder-motive forecasting and XAI study [26], and CriX on crime demographics
and XAI [27]. The IndianBailJudgments-1200 dataset provides an Indian
legal-NLP benchmark [28].

### D.2 What it contributes
This cluster supplies SEBA-XAI with three constraints: prefer interpretable
models for high-stakes review [9]; treat individual criminal-justice risk
prediction as inherently limited by criminal-justice AI, fairness, and
feedback-loop risks [11], [19]-[21]; and design XAI artifacts that are
stakeholder-specific and cautious about automation bias [10]. The
blockchain-XAI-justice and legal-AI audit proposals provide adjacent
architectures that combine audit trails with explanation artifacts [23], [24].

### D.3 What is missing for SEBA-XAI / how we position
`[INTERPRETATION]` `research_pack/01_literature_review.md` Section 4 notes that XAI in this
area is usually discussed for crime prediction or investigative support, not
as a first-class logged artifact inside an auditable inter-agency access-
control workflow. SEBA-XAI treats explanation traces and counterfactuals as
artifacts whose completeness, stability, and reconstruction are measured
(companion Results draft Section 7), and uses the predictive-policing
feedback-loop literature to justify scoping NS-PI as a policy-drift detector
on synthetic access decisions rather than a criminal-risk predictor. We do
not claim superiority over predictive-policing systems and do not claim that
NS-PI predicts crime or criminals.

## SEBA-XAI Positioning

`[INTERPRETATION]` Following the conservative framing in `CONTRIBUTION.md`,
SEBA-XAI is presented as an overlay that integrates and evaluates a narrow
access-governance workflow over synthetic CCTNS/ICJS-style requests. It does
not replace CCTNS or ICJS, it does not claim predictive-policing superiority,
and it does not assert real-world or operational performance. Its contribution
relative to the four clusters above is: (i) it inherits the institutional
framing from cluster A without claiming to reproduce it; (ii) it adopts the
off-chain-data / on-chain-commitment pattern from cluster B and implements
blockchain-style audit, CT-style log, signed hash-chain, and Fabric+ABAC
behaviours as evaluated baselines, not as a deployed system; (iii) it uses the
ABAC/PBAC vocabulary and patterns from cluster C, with ABAC re-execution and a
trusted raw-attribute policy oracle as baselines that bound what NS-PI can add;
and (iv) it adds, from cluster D, an interpretable rule-list NS-PI drift
detector and measured explanation/audit-quality artifacts. The evaluation is a
reproducible synthetic benchmark whose scope, defenses, attacks, and
limitations are defined in the companion Threat Model and Results drafts.
