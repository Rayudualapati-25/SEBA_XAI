// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "./policy/PolicyTypes.sol";
import "./lib/Validate.sol";
import "./lib/ExplanationLib.sol";
import "./identity/IdentityRegistry.sol";
import "./RecordRegistry.sol";
import "./AccessManager.sol";

/**
 * AuditRegistry — verification and reconstruction for reviewers, ported from
 * lib/auditContract.js.
 *
 * Verification always recomputes from on-chain state and compares against what
 * the caller claims to hold off-chain — never claim-vs-claim. It also anchors
 * the head hash of the off-chain access log (who searched / who read what),
 * which is kept off-chain as a hash chain because writing a transaction per
 * read would be far too slow; anchoring binds that chain to immutable state.
 */
contract AuditRegistry {
    using Validate for string;

    struct Anchor {
        bool exists;
        string epoch;
        uint256 seqNo;
        bytes32 headHash;
        uint256 entryCount;
        Msp anchoredByMsp;
        address anchoredBy;
        uint256 anchoredAt;
    }

    IdentityRegistry public immutable identity;
    RecordRegistry public immutable records;
    AccessManager public immutable access;

    Anchor private _latest;
    Anchor[] private _anchors;

    event AccessLogAnchored(uint256 seqNo, bytes32 headHash);

    constructor(
        IdentityRegistry _identity,
        RecordRegistry _records,
        AccessManager _access
    ) {
        identity = _identity;
        records = _records;
        access = _access;
    }

    // ── Verification ──────────────────────────────────────────────────────────

    /**
     * Verify that an explanation artifact a reviewer holds off-chain still
     * matches the hash committed at decision time. The stored hash comes from
     * AccessManager state; only the artifact under test comes from the caller.
     */
    function verifyExplanation(
        string calldata recordId,
        uint256 decisionId,
        string calldata decision,
        string calldata reasonCode,
        string calldata decisiveAttributes,
        string calldata counterfactual,
        string calldata policyVersion
    )
        external
        view
        returns (bool match_, bytes32 storedHash, bytes32 computedHash)
    {
        (bool exists, bytes32 stored) = access.getExplanationHash(
            recordId,
            decisionId
        );
        require(exists, "access decision does not exist");
        computedHash = ExplanationLib.hashExplanation(
            decision,
            reasonCode,
            decisiveAttributes,
            counterfactual,
            policyVersion
        );
        return (computedHash == stored, stored, computedHash);
    }

    /**
     * Verify an off-chain record payload against its on-chain commitment. The
     * claimed hash is computed by the client over the payload it holds; the
     * reference hash always comes from RecordRegistry state.
     */
    function verifyRecordPayload(
        string calldata recordId,
        bytes32 payloadHash
    ) external view returns (bool match_, bytes32 storedHash) {
        (bool exists, bytes32 stored) = records.getPayloadHash(recordId);
        require(exists, "record does not exist");
        return (stored == payloadHash, stored);
    }

    // ── Access-log anchoring ───────────────────────────────────────────────────

    /**
     * Commit the head hash of the off-chain access log. Oversight function, so
     * AuditMSP only. The sequence number must advance within an epoch, else an
     * attacker could re-anchor an older head to hide later entries. A new epoch
     * (the log was recreated) may restart the sequence — allowed, but never
     * hidden: every anchor stays in `_anchors` for auditors to see.
     */
    function anchorAccessLog(
        uint256 seqNo,
        bytes32 headHash,
        uint256 entryCount,
        string calldata epoch
    ) external {
        require(
            identity.mspOf(msg.sender) == Msp.Audit,
            "unauthorized: AnchorAccessLog requires AuditMSP"
        );
        require(seqNo >= 1, "seqNo must be a positive integer");
        require(entryCount >= 1, "entryCount must be a positive integer");
        require(headHash != bytes32(0), "headHash is required");
        epoch.requireSafeId("epoch");

        if (
            _latest.exists &&
            keccak256(bytes(_latest.epoch)) == keccak256(bytes(epoch)) &&
            seqNo <= _latest.seqNo
        ) {
            revert("seqNo must advance within an epoch");
        }

        Anchor memory a = Anchor({
            exists: true,
            epoch: epoch,
            seqNo: seqNo,
            headHash: headHash,
            entryCount: entryCount,
            anchoredByMsp: Msp.Audit,
            anchoredBy: msg.sender,
            anchoredAt: block.timestamp
        });
        _latest = a;
        _anchors.push(a);
        emit AccessLogAnchored(seqNo, headHash);
    }

    function getLatestAccessLogAnchor() external view returns (Anchor memory) {
        return _latest; // .exists == false when never anchored
    }

    /** Every anchor ever written, oldest first (the chaincode's key history). */
    function getAccessLogAnchors() external view returns (Anchor[] memory) {
        return _anchors;
    }

    // ── Reconstruction ─────────────────────────────────────────────────────────

    /**
     * Full reconstruction trace for one record: current metadata, its version
     * history, and every access decision with explanations. Reviewer orgs only
     * (Audit, Court, Prosecution).
     */
    function getAuditTrail(
        string calldata recordId
    )
        external
        view
        returns (
            RecordRegistry.Record memory record,
            RecordRegistry.RecordVersion[] memory history,
            AccessManager.AccessDecision[] memory decisions
        )
    {
        Msp m = identity.mspOf(msg.sender);
        require(
            m == Msp.Audit || m == Msp.Court || m == Msp.Prosecution,
            "unauthorized: GetAuditTrail requires a reviewer MSP"
        );
        record = records.getRecord(recordId);
        history = records.getRecordHistory(recordId);
        decisions = access.queryDecisionsByRecord(recordId);
    }
}
