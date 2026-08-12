// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "./policy/PolicyTypes.sol";
import "./lib/Validate.sol";
import "./identity/IdentityRegistry.sol";

/**
 * RecordRegistry — crime-record registry, ported from lib/recordContract.js.
 *
 * The ledger (here, contract storage) holds minimized metadata plus a SHA-256
 * commitment (`payloadHash`) to the real record, which stays in agency
 * off-chain storage. Nothing sensitive is written on-chain.
 *
 * PRIVACY NOTE — this differs from Fabric on purpose. Fabric put evidence
 * free-text detail in a member-only private data collection (Police+Forensics).
 * A public L1 has no private state: every byte here is world-readable. So this
 * port keeps ONLY the public hash commitment on-chain and drops the private
 * detail path entirely — evidence detail must live fully off-chain. See README.
 */
contract RecordRegistry {
    using Validate for string;

    struct Record {
        bool exists;
        string recordId;
        string caseId;
        RecordType recordType;
        Sensitivity sensitivity;
        bool juvenile;
        bool witness;
        string owningStation;
        string jurisdiction;
        bytes32 payloadHash; // sha256 digest of the off-chain payload
        string offchainUri;
        bool sealed_;
        Msp owningMsp;
        Role createdByRole;
        uint256 createdAt;
        address createdBy;
    }

    // A version log entry — the EVM equivalent of Fabric's getHistoryForKey.
    struct RecordVersion {
        bool sealed_;
        Role changedByRole;
        address changedBy;
        uint256 timestamp;
        string note; // "created" | "sealed" | "unsealed"
    }

    struct Evidence {
        bool exists;
        string recordId;
        string evidenceId;
        bytes32 evidenceHash;
        Msp labMsp;
        Role attachedByRole;
        address attachedBy;
        uint256 attachedAt;
    }

    IdentityRegistry public immutable identity;

    mapping(bytes32 => Record) private _records; // keccak(recordId)
    mapping(bytes32 => RecordVersion[]) private _history; // keccak(recordId)
    mapping(bytes32 => Evidence) private _evidence; // keccak(recordId,evidenceId)
    mapping(bytes32 => string[]) private _evidenceIds; // keccak(recordId) -> ids
    bytes32[] private _allRecordKeys;
    mapping(bytes32 => string) private _recordIdByKey;

    event RecordCreated(string recordId, string caseId, RecordType recordType);
    event EvidenceAttached(string recordId, string evidenceId);
    event RecordSealed(string recordId);
    event RecordUnsealed(string recordId);

    constructor(IdentityRegistry _identity) {
        identity = _identity;
    }

    function _key(string memory recordId) private pure returns (bytes32) {
        return keccak256(bytes(recordId));
    }

    function _evKey(
        string memory recordId,
        string memory evidenceId
    ) private pure returns (bytes32) {
        return keccak256(abi.encodePacked(recordId, "\x00", evidenceId));
    }

    function _requireMsp(Msp expected, string memory action) private view {
        require(
            identity.mspOf(msg.sender) == expected,
            string.concat("unauthorized: wrong MSP for ", action)
        );
    }

    function _isRecordCreatorRole(Role r) private pure returns (bool) {
        return
            r == Role.Constable ||
            r == Role.SubInspector ||
            r == Role.Inspector ||
            r == Role.Sho ||
            r == Role.InvestigatingOfficer;
    }

    // ── Writes ──────────────────────────────────────────────────────────────

    /** Police officers file a new record. Payload never touches the chain. */
    function createCaseRecord(
        string calldata recordId,
        string calldata caseId,
        RecordType recordType,
        Sensitivity sensitivity,
        bool juvenile,
        bool witness,
        string calldata owningStation,
        string calldata jurisdiction,
        bytes32 payloadHash,
        string calldata offchainUri
    ) external {
        _requireMsp(Msp.Police, "CreateCaseRecord");
        Role role = identity.roleOf(msg.sender);
        require(
            _isRecordCreatorRole(role),
            "unauthorized: role may not file records"
        );

        recordId.requireSafeId("recordId");
        caseId.requireSafeId("caseId");
        require(recordType != RecordType.None, "recordType is required");
        require(payloadHash != bytes32(0), "payloadHash is required");
        require(bytes(offchainUri).length > 0, "offchainUri is required");
        require(bytes(jurisdiction).length > 0, "jurisdiction is required");
        require(bytes(owningStation).length > 0, "owningStation is required");

        bytes32 k = _key(recordId);
        require(!_records[k].exists, "record already exists");

        _records[k] = Record({
            exists: true,
            recordId: recordId,
            caseId: caseId,
            recordType: recordType,
            sensitivity: sensitivity,
            juvenile: juvenile,
            witness: witness,
            owningStation: owningStation,
            jurisdiction: jurisdiction,
            payloadHash: payloadHash,
            offchainUri: offchainUri,
            sealed_: false,
            owningMsp: Msp.Police,
            createdByRole: role,
            createdAt: block.timestamp,
            createdBy: msg.sender
        });
        _allRecordKeys.push(k);
        _recordIdByKey[k] = recordId;
        _history[k].push(
            RecordVersion({
                sealed_: false,
                changedByRole: role,
                changedBy: msg.sender,
                timestamp: block.timestamp,
                note: "created"
            })
        );

        emit RecordCreated(recordId, caseId, recordType);
    }

    /**
     * Forensics attaches an evidence commitment. Only the SHA-256 hash is
     * stored — the public part of the chaincode's AttachEvidenceHash. There is
     * no on-chain private-detail path on a public chain (see contract header).
     */
    function attachEvidenceHash(
        string calldata recordId,
        string calldata evidenceId,
        bytes32 evidenceHash
    ) external {
        _requireMsp(Msp.Forensics, "AttachEvidenceHash");
        Role role = identity.roleOf(msg.sender);
        require(
            role == Role.LabAnalyst || role == Role.LabDirector,
            "unauthorized: role may not attach evidence"
        );
        evidenceId.requireSafeId("evidenceId");
        require(evidenceHash != bytes32(0), "evidenceHash is required");
        require(_records[_key(recordId)].exists, "record does not exist");

        bytes32 ek = _evKey(recordId, evidenceId);
        require(!_evidence[ek].exists, "evidence already attached");

        _evidence[ek] = Evidence({
            exists: true,
            recordId: recordId,
            evidenceId: evidenceId,
            evidenceHash: evidenceHash,
            labMsp: Msp.Forensics,
            attachedByRole: role,
            attachedBy: msg.sender,
            attachedAt: block.timestamp
        });
        _evidenceIds[_key(recordId)].push(evidenceId);
        emit EvidenceAttached(recordId, evidenceId);
    }

    function sealRecord(string calldata recordId) external {
        _setSealed(recordId, true);
    }

    function unsealRecord(string calldata recordId) external {
        _setSealed(recordId, false);
    }

    function _setSealed(string calldata recordId, bool sealed_) private {
        _requireMsp(Msp.Court, sealed_ ? "SealRecord" : "UnsealRecord");
        Role role = identity.roleOf(msg.sender);
        require(
            role == Role.Judge || role == Role.Magistrate,
            "unauthorized: role may not seal records"
        );

        bytes32 k = _key(recordId);
        Record storage rec = _records[k];
        require(rec.exists, "record does not exist");
        require(
            rec.sealed_ != sealed_,
            sealed_ ? "record is already sealed" : "record is already unsealed"
        );

        rec.sealed_ = sealed_;
        _history[k].push(
            RecordVersion({
                sealed_: sealed_,
                changedByRole: role,
                changedBy: msg.sender,
                timestamp: block.timestamp,
                note: sealed_ ? "sealed" : "unsealed"
            })
        );
        if (sealed_) {
            emit RecordSealed(recordId);
        } else {
            emit RecordUnsealed(recordId);
        }
    }

    // ── Views ────────────────────────────────────────────────────────────────

    function recordExists(string calldata recordId) external view returns (bool) {
        return _records[_key(recordId)].exists;
    }

    function getRecord(
        string calldata recordId
    ) external view returns (Record memory) {
        Record memory r = _records[_key(recordId)];
        require(r.exists, "record does not exist");
        return r;
    }

    /** Compact object attributes for the policy engine (used by AccessManager). */
    function getRecordCtx(
        string memory recordId
    ) external view returns (bool exists, RecordCtx memory ctx) {
        Record storage r = _records[_key(recordId)];
        exists = r.exists;
        ctx = RecordCtx({
            recordType: r.recordType,
            sensitivity: r.sensitivity,
            juvenile: r.juvenile,
            sealed_: r.sealed_,
            jurisdiction: r.jurisdiction,
            caseId: r.caseId
        });
    }

    function getPayloadHash(
        string calldata recordId
    ) external view returns (bool exists, bytes32 payloadHash) {
        Record storage r = _records[_key(recordId)];
        return (r.exists, r.payloadHash);
    }

    function getRecordHistory(
        string calldata recordId
    ) external view returns (RecordVersion[] memory) {
        return _history[_key(recordId)];
    }

    function listEvidence(
        string calldata recordId
    ) external view returns (Evidence[] memory) {
        string[] storage ids = _evidenceIds[_key(recordId)];
        Evidence[] memory out = new Evidence[](ids.length);
        for (uint256 i = 0; i < ids.length; i++) {
            out[i] = _evidence[_evKey(recordId, ids[i])];
        }
        return out;
    }

    function getEvidence(
        string calldata recordId,
        string calldata evidenceId
    ) external view returns (Evidence memory) {
        Evidence memory e = _evidence[_evKey(recordId, evidenceId)];
        require(e.exists, "evidence does not exist");
        return e;
    }

    function recordCount() external view returns (uint256) {
        return _allRecordKeys.length;
    }

    /**
     * Allow-listed metadata search — the EVM equivalent of the chaincode's
     * QueryRecords CouchDB rich query. Callers pass a filter with presence
     * flags; only the fields they enable are matched. Returns matching
     * recordIds. As a `view`, iteration costs the caller nothing off-chain.
     * Finding a record grants no access — that still requires RequestAccess.
     */
    struct RecordFilter {
        bool byCaseId;
        string caseId;
        bool byRecordType;
        RecordType recordType;
        bool bySensitivity;
        Sensitivity sensitivity;
        bool byJurisdiction;
        string jurisdiction;
        bool bySealed;
        bool sealed_;
    }

    function queryRecords(
        RecordFilter calldata f
    ) external view returns (string[] memory) {
        require(
            f.byCaseId ||
                f.byRecordType ||
                f.bySensitivity ||
                f.byJurisdiction ||
                f.bySealed,
            "search: at least one filter is required"
        );

        uint256 n = _allRecordKeys.length;
        string[] memory tmp = new string[](n);
        uint256 m = 0;
        for (uint256 i = 0; i < n; i++) {
            Record storage r = _records[_allRecordKeys[i]];
            if (f.byCaseId && keccak256(bytes(r.caseId)) != keccak256(bytes(f.caseId)))
                continue;
            if (f.byRecordType && r.recordType != f.recordType) continue;
            if (f.bySensitivity && r.sensitivity != f.sensitivity) continue;
            if (
                f.byJurisdiction &&
                keccak256(bytes(r.jurisdiction)) != keccak256(bytes(f.jurisdiction))
            ) continue;
            if (f.bySealed && r.sealed_ != f.sealed_) continue;
            tmp[m++] = r.recordId;
        }

        string[] memory out = new string[](m);
        for (uint256 i = 0; i < m; i++) {
            out[i] = tmp[i];
        }
        return out;
    }
}
