// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "./policy/PolicyTypes.sol";
import "./policy/PolicyV1.sol";
import "./policy/PolicyEngine.sol";
import "./lib/ExplanationLib.sol";
import "./identity/IdentityRegistry.sol";
import "./RecordRegistry.sol";

/**
 * AccessManager — the paper's access-request flow, ported from
 * lib/accessContract.js.
 *
 * RequestAccess assembles the structured request (subject attributes from the
 * IdentityRegistry, object attributes from the RecordRegistry, environment from
 * the call arguments), runs the deterministic PolicyEngine, and stores the
 * decision together with its explanation artifact and explanation hash as one
 * immutable audit event. Escalated decisions are later resolved by a
 * supervisory/judicial role.
 */
contract AccessManager {
    using ExplanationLib for Outcome;

    enum Status {
        Granted,
        Denied,
        Pending,
        Approved,
        Rejected
    }

    struct AccessDecision {
        bool exists;
        uint256 decisionId;
        string recordId;
        string caseId;
        Action action;
        Decision decision;
        Status status;
        // Subject snapshot — role/context only, no personal fields.
        address subjectAddr;
        Msp subjectMsp;
        Role subjectRole;
        string subjectStation;
        string subjectJurisdiction;
        Clearance subjectClearance;
        // Environment.
        Purpose purpose;
        bool emergencyFlag;
        string courtLink;
        bytes32 approvalTokenHash; // sha256(token), or 0 — never the raw token.
        // Explanation artifact + its commitment.
        string reasonCode;
        string decisiveAttributes;
        string counterfactual;
        string policyVersion;
        bytes32 explanationHash;
        uint256 createdAt;
        // Resolution (only for escalated decisions).
        bool resolved;
        bool approved;
        address resolvedBy;
        Role resolvedByRole;
        uint256 resolvedAt;
        string note;
    }

    IdentityRegistry public immutable identity;
    RecordRegistry public immutable records;

    uint256 private _seq;
    mapping(bytes32 => AccessDecision) private _decisions; // keccak(recordId,id)
    mapping(bytes32 => uint256[]) private _byRecord; // keccak(recordId) -> ids
    bytes32[] private _allDecisionKeys;

    event AccessDecisionMade(
        uint256 indexed decisionId,
        string recordId,
        Decision decision,
        string reasonCode
    );
    event EscalationResolved(
        uint256 indexed decisionId,
        string recordId,
        bool approved
    );

    constructor(IdentityRegistry _identity, RecordRegistry _records) {
        identity = _identity;
        records = _records;
    }

    function _key(
        string memory recordId,
        uint256 decisionId
    ) private pure returns (bytes32) {
        return keccak256(abi.encode(recordId, decisionId));
    }

    // ── Request flow ──────────────────────────────────────────────────────────

    /**
     * Request access to a record. Runs the policy engine and stores the
     * decision + explanation. Returns the new decisionId.
     *
     * `approvalToken` is the raw token supplied for an emergency
     * cross-jurisdiction request; only its SHA-256 commitment is stored.
     */
    function requestAccess(
        string calldata recordId,
        Action action,
        Purpose purpose,
        bool emergencyFlag,
        string calldata courtLink,
        bytes calldata approvalToken
    ) external returns (uint256) {
        IdentityRegistry.Identity memory caller = identity.getIdentity(
            msg.sender
        );
        require(caller.registered && caller.role != Role.None, "unauthorized: caller has no role");

        (bool exists, RecordCtx memory rctx) = records.getRecordCtx(recordId);
        require(exists, "record does not exist");

        bool hasToken = approvalToken.length > 0;
        Subject memory subject = Subject({
            msp: caller.msp,
            role: caller.role,
            jurisdiction: caller.jurisdiction,
            clearance: caller.clearance,
            active: caller.active,
            assignedToCase: identity.isAssignedToCase(msg.sender, rctx.caseId)
        });
        EnvCtx memory env = EnvCtx({
            purpose: purpose,
            emergencyFlag: emergencyFlag,
            hasApprovalToken: hasToken
        });

        Outcome memory outcome = PolicyEngine.evaluate(
            subject,
            rctx,
            action,
            env
        );

        uint256 decisionId = ++_seq;
        bytes32 k = _key(recordId, decisionId);
        _writeDecision(
            k,
            decisionId,
            recordId,
            rctx.caseId,
            action,
            caller,
            purpose,
            emergencyFlag,
            courtLink,
            hasToken ? sha256(approvalToken) : bytes32(0),
            outcome
        );

        _byRecord[keccak256(bytes(recordId))].push(decisionId);
        _allDecisionKeys.push(k);

        emit AccessDecisionMade(
            decisionId,
            recordId,
            outcome.decision,
            outcome.reasonCode
        );
        return decisionId;
    }

    // Field-by-field storage write to keep the request path within stack limits.
    function _writeDecision(
        bytes32 k,
        uint256 decisionId,
        string calldata recordId,
        string memory caseId,
        Action action,
        IdentityRegistry.Identity memory caller,
        Purpose purpose,
        bool emergencyFlag,
        string calldata courtLink,
        bytes32 approvalTokenHash,
        Outcome memory outcome
    ) private {
        AccessDecision storage d = _decisions[k];
        d.exists = true;
        d.decisionId = decisionId;
        d.recordId = recordId;
        d.caseId = caseId;
        d.action = action;
        d.decision = outcome.decision;
        d.status = _statusFor(outcome.decision);

        d.subjectAddr = msg.sender;
        d.subjectMsp = caller.msp;
        d.subjectRole = caller.role;
        d.subjectStation = caller.station;
        d.subjectJurisdiction = caller.jurisdiction;
        d.subjectClearance = caller.clearance;

        d.purpose = purpose;
        d.emergencyFlag = emergencyFlag;
        d.courtLink = courtLink;
        d.approvalTokenHash = approvalTokenHash;

        d.reasonCode = outcome.reasonCode;
        d.decisiveAttributes = outcome.decisiveAttributes;
        d.counterfactual = outcome.counterfactual;
        d.policyVersion = outcome.policyVersion;
        d.explanationHash = outcome.hashOutcome();
        d.createdAt = block.timestamp;
    }

    function _statusFor(Decision decision) private pure returns (Status) {
        if (decision == Decision.Allow) return Status.Granted;
        if (decision == Decision.Deny) return Status.Denied;
        return Status.Pending;
    }

    // ── Escalation resolution ──────────────────────────────────────────────────

    function approveEscalation(
        string calldata recordId,
        uint256 decisionId,
        string calldata note
    ) external {
        _resolve(recordId, decisionId, note, true);
    }

    function rejectEscalation(
        string calldata recordId,
        uint256 decisionId,
        string calldata note
    ) external {
        _resolve(recordId, decisionId, note, false);
    }

    function _resolve(
        string calldata recordId,
        uint256 decisionId,
        string calldata note,
        bool approve
    ) private {
        Role callerRole = identity.roleOf(msg.sender);
        require(
            PolicyV1.isEscalationApprover(callerRole),
            "unauthorized: role may not resolve escalations"
        );

        AccessDecision storage d = _decisions[_key(recordId, decisionId)];
        require(d.exists, "access decision does not exist");
        require(d.status == Status.Pending, "decision is not pending escalation");

        // The requester may not approve their own escalation. Mirrors the
        // chaincode's msp+role check, and also blocks the same address.
        Msp callerMsp = identity.mspOf(msg.sender);
        require(
            msg.sender != d.subjectAddr &&
                !(callerMsp == d.subjectMsp && callerRole == d.subjectRole),
            "unauthorized: requester cannot approve its own escalation"
        );

        d.status = approve ? Status.Approved : Status.Rejected;
        d.resolved = true;
        d.approved = approve;
        d.resolvedBy = msg.sender;
        d.resolvedByRole = callerRole;
        d.resolvedAt = block.timestamp;
        d.note = bytes(note).length > 500 ? _truncate(note) : note;

        emit EscalationResolved(decisionId, recordId, approve);
    }

    function _truncate(
        string calldata s
    ) private pure returns (string memory) {
        bytes calldata b = bytes(s);
        bytes memory out = new bytes(500);
        for (uint256 i = 0; i < 500; i++) {
            out[i] = b[i];
        }
        return string(out);
    }

    // ── Views ────────────────────────────────────────────────────────────────

    function getDecision(
        string calldata recordId,
        uint256 decisionId
    ) external view returns (AccessDecision memory) {
        AccessDecision memory d = _decisions[_key(recordId, decisionId)];
        require(d.exists, "access decision does not exist");
        return d;
    }

    /** (exists, explanationHash) for a decision — used by AuditRegistry. */
    function getExplanationHash(
        string calldata recordId,
        uint256 decisionId
    ) external view returns (bool exists, bytes32 explanationHash) {
        AccessDecision storage d = _decisions[_key(recordId, decisionId)];
        return (d.exists, d.explanationHash);
    }

    function decisionIdsByRecord(
        string calldata recordId
    ) external view returns (uint256[] memory) {
        return _byRecord[keccak256(bytes(recordId))];
    }

    function queryDecisionsByRecord(
        string calldata recordId
    ) external view returns (AccessDecision[] memory) {
        uint256[] storage ids = _byRecord[keccak256(bytes(recordId))];
        AccessDecision[] memory out = new AccessDecision[](ids.length);
        for (uint256 i = 0; i < ids.length; i++) {
            out[i] = _decisions[_key(recordId, ids[i])];
        }
        return out;
    }

    function decisionCount() external view returns (uint256) {
        return _allDecisionKeys.length;
    }

    /** Every pending escalation across all records (view iteration). */
    function queryPendingEscalations()
        external
        view
        returns (AccessDecision[] memory)
    {
        uint256 n = _allDecisionKeys.length;
        AccessDecision[] memory tmp = new AccessDecision[](n);
        uint256 m = 0;
        for (uint256 i = 0; i < n; i++) {
            AccessDecision storage d = _decisions[_allDecisionKeys[i]];
            if (d.status == Status.Pending) {
                tmp[m++] = d;
            }
        }
        AccessDecision[] memory out = new AccessDecision[](m);
        for (uint256 i = 0; i < m; i++) {
            out[i] = tmp[i];
        }
        return out;
    }
}
