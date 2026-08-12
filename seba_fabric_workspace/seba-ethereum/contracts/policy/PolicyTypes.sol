// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * PolicyTypes — shared enums and structs for the SEBA-XAI access-governance
 * system, ported from the Hyperledger Fabric chaincode's policyV1.js.
 *
 * Fabric carried these as free-text certificate attributes and JSON strings.
 * On a public EVM chain we make them typed enums so the compiler enforces the
 * domain and callers cannot smuggle unknown values past the policy engine.
 *
 * The leading `None`/`Unset` members are deliberate sentinels: an
 * unregistered address decodes to member 0, which every rule treats as
 * "not granted", mirroring the chaincode's `null`-means-denied behaviour.
 */

// Membership Service Providers → the five organisations of the consortium.
enum Msp {
    None,
    Police,
    Forensics,
    Prosecution,
    Court,
    Audit
}

// Roles, grouped by owning MSP (see roleBelongsToMsp in PolicyV1).
enum Role {
    None,
    // Police
    Constable,
    SubInspector,
    Inspector,
    Sho,
    InvestigatingOfficer,
    // Forensics
    LabAnalyst,
    LabDirector,
    // Prosecution
    PublicProsecutor,
    DefenseCounsel,
    // Court
    Judge,
    Magistrate,
    CourtClerk,
    // Audit
    Auditor,
    Ombudsman
}

// Record types. Index order matters: PolicyV1 encodes RBAC as bitmasks over it.
enum RecordType {
    None,
    Fir,
    CaseDiary,
    Evidence,
    ForensicReport,
    WitnessStatement,
    Chargesheet,
    CourtOrder
}

// Sensitivity ranks 0/1/2 (low/medium/high).
enum Sensitivity {
    Low,
    Medium,
    High
}

enum Action {
    View,
    Export,
    Annotate
}

// Purpose. `Unset` (member 0) preserves the chaincode's INVALID_PURPOSE deny
// path — a request that fails to declare a purpose is rejected, not defaulted.
enum Purpose {
    Unset,
    Investigation,
    ForensicAnalysis,
    Prosecution,
    JudicialProceeding,
    AuditReview,
    DefensePreparation
}

// Clearance. `Unset` maps to rank -1 in the engine, so a caller with no
// clearance attribute never satisfies a sensitivity gate.
enum Clearance {
    Unset,
    Low,
    Medium,
    High
}

enum Decision {
    Allow,
    Deny,
    Escalate
}

// ── Structs consumed by the pure policy engine ─────────────────────────────

// Caller attribute snapshot, assembled from the on-chain IdentityRegistry
// instead of an X.509 certificate. `assignedToCase` is resolved by the caller
// (AccessManager) against the record under request, replacing the chaincode's
// comma/pipe split of the `caseAssignments` attribute.
struct Subject {
    Msp msp;
    Role role;
    string jurisdiction;
    Clearance clearance;
    bool active; // credentialStatus == "active"
    bool assignedToCase;
}

// Object attributes read from RecordRegistry state.
struct RecordCtx {
    RecordType recordType;
    Sensitivity sensitivity;
    bool juvenile;
    bool sealed_;
    string jurisdiction;
    string caseId;
}

// Environment attributes from the request arguments.
struct EnvCtx {
    Purpose purpose;
    bool emergencyFlag;
    bool hasApprovalToken;
}

// The decision + its explanation artifact. Mirrors the object the chaincode
// stored on the ledger and hashed for later verification. `decisiveAttributes`
// is a comma-joined string (the chaincode used an array) so it hashes and
// returns cleanly across the ABI.
struct Outcome {
    Decision decision;
    string reasonCode;
    string decisiveAttributes;
    string counterfactual;
    string policyVersion;
}
