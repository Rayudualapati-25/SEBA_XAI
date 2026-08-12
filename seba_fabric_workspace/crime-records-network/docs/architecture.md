# Architecture

## Trust and storage boundaries

```text
Browser -> Node API -> per-user Fabric Gateway -> five-organisation Fabric channel
                    -> agency-controlled raw-content vault
                    -> optional local LLM wording
```

Fabric is authoritative for departments, UserProfiles, cases, record/evidence
metadata, access requests, decisions, approvals, custody, court workflow, policy
versions, and audit events. The chaincode derives identity and attributes from
the transaction's Fabric CA certificate and enforces authorization.

Raw case narratives, personal documents, and evidence bytes are never written
to the shared channel. They remain in the owning agency's vault. Fabric stores
only `offChainReference`, `contentHash`, classification, lifecycle, and access
evidence. The backend rehashes content before release and chaincode first proves
that the exact signing identity has a grant.

The prototype uses no application PostgreSQL/SQLite database. CouchDB is
Fabric's peer world-state projection; the ordered blockchain remains the source
of history. Fabric CA's identity registry is infrastructure, not domain state.

## Contracts

| Contract | Authoritative assets/actions |
|---|---|
| `GovernanceContract` | Department, Case, assignment, prosecution/court workflow |
| `UserContract` | identity-backed UserProfile, status, history |
| `RecordContract` | RecordMetadata, EvidenceMetadata, custody, seal, authorized release |
| `AccessContract` | AccessRequest, AccessDecision, pending escalation, Approval |
| `AuditContract` | direct application events, explanation/payload verification, reconstruction |
| `PolicyContract` | immutable versions and explicit activation/supersession |

## Contextual decision

The policy combines:

- subject: MSP, enrollment identity, role, rank, station, jurisdiction, and
  clearance from X.509, verified against the UserProfile; current credential
  state from UserProfile and assignment from the Case asset;
- resource: record type, case, sensitivity, jurisdiction, owner, seal, and
  juvenile/witness/victim protection flags from Fabric state;
- action and context: view/export/annotate, purpose, emergency state, court
  link, and approval-token commitment.

It returns `ALLOW`, `DENY`, or `ESCALATE` with a reason code, decisive
attributes, counterfactual guidance, policy version, explanation hash, decision
hash, and transaction evidence. A role by itself is never sufficient for
sensitive raw content.

Current rule order is deterministic:

1. inactive credential -> deny;
2. invalid purpose -> deny;
3. role/action/record mismatch -> deny;
4. sealed record outside court -> escalate;
5. juvenile data outside the narrow exception -> deny;
6. unnecessary victim-protected data -> deny;
7. cross-jurisdiction request -> escalate unless narrowly approved emergency;
8. missing case assignment -> deny;
9. insufficient clearance -> escalate;
10. auditor raw-content request -> deny metadata-only;
11. otherwise -> allow.

The browser's role-aware navigation is only a convenience. The backend validates
requests, while the chaincode is the authorization boundary.

## Identity and login limitation

Fabric CA issues each X.509 identity. `UserContract` maps its enrollment ID to
the public authorization profile and status; no password/hash is accepted.

For local development, the backend holds all seeded MSP private keys and the
login screen selects one. It then proves that key can call
`AuthenticateCurrentUser`. This demonstrates Fabric identity mapping, but is
not production end-user authentication. Production requires user-controlled or
hardware-backed keys and secure identity federation.

## XAI boundary

The deterministic structured explanation is created with the decision and is
the auditable evidence. The optional local LLM may only reword this artifact.
It receives no case narrative or personal details, cannot change authorization,
and is rejected when grounding checks detect contradictions or invented facts.
