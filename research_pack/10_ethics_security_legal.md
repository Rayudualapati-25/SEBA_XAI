# 10 Ethics Security Legal Analysis

Generated: 2026-05-12  
Important: this is not legal advice. It is a research risk analysis. A qualified Indian legal expert must review any compliance claim.

## Ethical Position

This research must improve accountability and safety, not expand surveillance. The system should support reviewable access to sensitive records, not automate coercive policing decisions.

## High-Risk Data Categories

Treat these as highly sensitive:

- victim/witness identities;
- juvenile records;
- sexual-offence records;
- crimes against children;
- caste/tribe related offences;
- trafficking records;
- domestic violence and crimes against women;
- cybercrime victim reports;
- forensic reports;
- biometric and device identifiers;
- sealed, expunged, or court-restricted records;
- informant or intelligence information.

## Legal Context Sources

- Digital Personal Data Protection Act, 2023: India Code lists Act No. 22 of 2023 and states that the law concerns processing digital personal data while recognizing both individual data protection and lawful processing needs. Source: https://www.indiacode.nic.in/indiacode/handle/123456789/22037?view_type=browse
- Bharatiya Sakshya Adhiniyam, 2023: India Code lists Act No. 47 of 2023, enforced 2024-07-01, and includes sections on electronic/digital records and admissibility of electronic records. Source: https://www.indiacode.nic.in/handle/123456789/20063
- CCTNS/ICJS official context: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238241 and https://www.mha.gov.in/en/commoncontent/icjsncrb-administration

Do not claim legal compliance merely because the design uses blockchain or encryption.

## Security Risks

### Insider Misuse

Risk: a legitimate officer queries unrelated sensitive records.

Mitigation:

- case assignment checks;
- purpose limitation;
- superior approval;
- anomaly detection;
- audit review;
- rate and pattern monitoring.

### Metadata Leakage

Risk: even without raw records, audit metadata may reveal sensitive investigations.

Mitigation:

- minimize on-chain metadata;
- hash identifiers;
- avoid cleartext sensitivity/case details where not needed;
- test inference risk;
- use selective visibility/private collections only after evaluating audit trade-offs.

### False Input Problem

Risk: blockchain preserves false or abusive events if source systems submit bad data.

Mitigation:

- chain of custody for inputs;
- policy-version logging;
- human review for sensitive cases;
- dispute/correction process;
- explicit limitation in paper.

### Explanation Leakage

Risk: XAI text reveals protected attributes, confidential investigation details, or investigative logic.

Mitigation:

- role-specific explanation views;
- redact sensitive features for requesters;
- store full explanation off-chain under access control;
- hash explanation artifacts on-chain;
- define audience-specific explanation policies.

### Model Misuse

Risk: access-risk scores or aggregate crime models are treated as operational truth.

Mitigation:

- model is advisory;
- deterministic policy remains final for access control;
- human approval required for sensitive release;
- no individual suspect prediction from public aggregate data.

## Privacy Risks

- linkability across stations;
- re-identification from rare case types or timestamps;
- function creep from access governance to surveillance;
- retention conflicts if immutable logs include personal data;
- leakage through model explanations or feature importance.

Design response:

- no raw personal data on-chain;
- only hashes, policy IDs, request IDs, and minimal metadata on-chain;
- documented retention and redaction strategy for off-chain artifacts;
- privacy-risk testing as an explicit experiment.

## Fairness Risks

Public reported-crime data reflects reporting practices, police presence, FIR registration practices, and local social factors. A model trained on such data may reproduce patterns of enforcement rather than crime. Predictive-policing feedback-loop literature warns that model-driven attention can reinforce observed police activity. Source: https://proceedings.mlr.press/v81/ensign18a.html

Design response:

- do not build individual risk scores;
- report aggregate limitations;
- evaluate error by region and police-resource strata;
- include fairness caveats rather than fairness claims.

## Human Oversight

Sensitive release must require a named human decision-maker. The system should log:

- who requested;
- what was requested;
- why it was requested;
- policy decision;
- AI risk score if used;
- explanation artifact;
- who approved/denied/escalated;
- what was disclosed;
- when access expired or was revoked.

## Ethics Review

No human-subject user study should be run without ethics/IRB-style approval. The first paper can use synthetic workloads and checklist-based explanation completeness metrics to avoid human-subject risk.

## Legal Claims Allowed

Allowed:

- "The design is informed by Indian digital-policing infrastructure and electronic-record legal context."
- "The design avoids raw personal-data storage on-chain."
- "The design records audit commitments and policy/explanation hashes."

Not allowed:

- "The system is DPDP compliant."
- "The system guarantees evidence admissibility."
- "The system is deployable by Indian police."
- "The system prevents misuse."
- "The system is privacy preserving" without formal proof and threat model.

## Supervisor Warning

The paper must include limitations and misuse risks prominently. A paper that markets this as a surveillance or predictive-policing system will be weaker, more ethically risky, and harder to defend.
