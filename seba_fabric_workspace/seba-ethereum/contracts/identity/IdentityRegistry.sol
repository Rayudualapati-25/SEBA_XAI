// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "../policy/PolicyTypes.sol";
import "../policy/PolicyV1.sol";

/**
 * IdentityRegistry — the EVM stand-in for Fabric's MSP + X.509 attributes.
 *
 * On Fabric, every caller arrived with a certificate carrying `role`,
 * `jurisdiction`, `clearance`, `credentialStatus` and `caseAssignments`, issued
 * by their organisation's CA. A public Ethereum chain has none of that: an
 * address is just an address. This registry restores the model.
 *
 * Trust model (mirrors per-org CAs):
 *   - the deployer is the root `owner`;
 *   - the owner appoints one admin address per MSP;
 *   - an MSP admin registers and maintains ONLY identities within its own MSP,
 *     and can only grant roles that belong to that MSP (roleBelongsToMsp).
 *
 * This is where the chaincode's `getCaller`, `requireMsp` and `requireRole`
 * live now; the record/access/audit contracts read caller attributes from here
 * by `msg.sender`, never from call arguments.
 */
contract IdentityRegistry {
    struct Identity {
        bool registered;
        Msp msp;
        Role role;
        string station;
        string jurisdiction;
        Clearance clearance;
        bool active; // credentialStatus == "active"
    }

    address public owner;
    mapping(Msp => address) public mspAdmin;
    mapping(address => Identity) private _identities;
    // keccak256(caseId) => assigned, per subject address.
    mapping(address => mapping(bytes32 => bool)) private _caseAssigned;

    event OwnerTransferred(address indexed from, address indexed to);
    event MspAdminSet(Msp indexed msp, address indexed admin);
    event IdentityRegistered(address indexed who, Msp indexed msp, Role role);
    event IdentityUpdated(address indexed who);
    event IdentityDeactivated(address indexed who);
    event IdentityActivated(address indexed who);
    event CaseAssigned(address indexed who, string caseId);
    event CaseRevoked(address indexed who, string caseId);

    constructor() {
        owner = msg.sender;
        emit OwnerTransferred(address(0), msg.sender);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "identity: caller is not owner");
        _;
    }

    /** Owner, or the admin appointed for `msp`, may administer that MSP. */
    modifier onlyMspAdmin(Msp msp) {
        require(
            msg.sender == owner || msg.sender == mspAdmin[msp],
            "identity: caller is not an admin for this MSP"
        );
        _;
    }

    function transferOwnership(address to) external onlyOwner {
        require(to != address(0), "identity: zero owner");
        emit OwnerTransferred(owner, to);
        owner = to;
    }

    function setMspAdmin(Msp msp, address admin) external onlyOwner {
        require(msp != Msp.None, "identity: invalid MSP");
        mspAdmin[msp] = admin;
        emit MspAdminSet(msp, admin);
    }

    /**
     * Register (or overwrite) an identity within `msp`. The role must belong to
     * that MSP. Newly registered identities start active.
     */
    function registerIdentity(
        address who,
        Msp msp,
        Role role,
        string calldata station,
        string calldata jurisdiction,
        Clearance clearance
    ) external onlyMspAdmin(msp) {
        require(who != address(0), "identity: zero subject");
        require(msp != Msp.None, "identity: invalid MSP");
        require(role != Role.None, "identity: invalid role");
        require(
            PolicyV1.roleBelongsToMsp(msp, role),
            "identity: role does not belong to MSP"
        );

        _identities[who] = Identity({
            registered: true,
            msp: msp,
            role: role,
            station: station,
            jurisdiction: jurisdiction,
            clearance: clearance,
            active: true
        });
        emit IdentityRegistered(who, msp, role);
    }

    /** Update the mutable attributes of an existing identity within its MSP. */
    function updateAttributes(
        address who,
        Role role,
        string calldata station,
        string calldata jurisdiction,
        Clearance clearance
    ) external {
        Identity storage id = _identities[who];
        require(id.registered, "identity: not registered");
        require(
            msg.sender == owner || msg.sender == mspAdmin[id.msp],
            "identity: caller is not an admin for this MSP"
        );
        require(role != Role.None, "identity: invalid role");
        require(
            PolicyV1.roleBelongsToMsp(id.msp, role),
            "identity: role does not belong to MSP"
        );
        id.role = role;
        id.station = station;
        id.jurisdiction = jurisdiction;
        id.clearance = clearance;
        emit IdentityUpdated(who);
    }

    /** Revocation: flips credentialStatus away from "active" (rule 1 deny). */
    function setActive(address who, bool active) external {
        Identity storage id = _identities[who];
        require(id.registered, "identity: not registered");
        require(
            msg.sender == owner || msg.sender == mspAdmin[id.msp],
            "identity: caller is not an admin for this MSP"
        );
        id.active = active;
        if (active) {
            emit IdentityActivated(who);
        } else {
            emit IdentityDeactivated(who);
        }
    }

    function assignCase(address who, string calldata caseId) external {
        Identity storage id = _identities[who];
        require(id.registered, "identity: not registered");
        require(
            msg.sender == owner || msg.sender == mspAdmin[id.msp],
            "identity: caller is not an admin for this MSP"
        );
        _caseAssigned[who][keccak256(bytes(caseId))] = true;
        emit CaseAssigned(who, caseId);
    }

    function revokeCase(address who, string calldata caseId) external {
        Identity storage id = _identities[who];
        require(id.registered, "identity: not registered");
        require(
            msg.sender == owner || msg.sender == mspAdmin[id.msp],
            "identity: caller is not an admin for this MSP"
        );
        _caseAssigned[who][keccak256(bytes(caseId))] = false;
        emit CaseRevoked(who, caseId);
    }

    // ── Views used by the other contracts (the old getCaller/requireX) ──────

    function getIdentity(address who) external view returns (Identity memory) {
        return _identities[who];
    }

    function isRegistered(address who) external view returns (bool) {
        return _identities[who].registered;
    }

    function mspOf(address who) external view returns (Msp) {
        return _identities[who].msp;
    }

    function roleOf(address who) external view returns (Role) {
        return _identities[who].role;
    }

    function isAssignedToCase(
        address who,
        string memory caseId
    ) external view returns (bool) {
        return _caseAssigned[who][keccak256(bytes(caseId))];
    }

    /**
     * Build the policy Subject for `who` against a specific record's caseId.
     * This is the on-chain `getCaller` — attributes come only from registry
     * state keyed by the signed sender, never from request arguments.
     */
    function subjectFor(
        address who,
        string memory caseId
    ) external view returns (Subject memory) {
        Identity storage id = _identities[who];
        return
            Subject({
                msp: id.msp,
                role: id.role,
                jurisdiction: id.jurisdiction,
                clearance: id.clearance,
                active: id.active,
                assignedToCase: _caseAssigned[who][keccak256(bytes(caseId))]
            });
    }

    /** Throw unless `who` is a registered member of one of `allowed`. */
    function requireMsp(
        address who,
        Msp[] memory allowed,
        string memory action
    ) external view {
        Msp m = _identities[who].msp;
        for (uint256 i = 0; i < allowed.length; i++) {
            if (m == allowed[i]) {
                return;
            }
        }
        revert(string.concat("unauthorized: wrong MSP for ", action));
    }
}
