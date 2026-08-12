// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "./PolicyTypes.sol";

/**
 * PolicyV1 — declarative policy tables, ported verbatim in meaning from the
 * chaincode's lib/policy/policyV1.js.
 *
 *  RBAC : which roles may perform which actions on which record types.
 *  ABAC : contextual exemptions (assignment, juvenile access).
 *  PBAC : policy versioning + who may resolve an escalation.
 *
 * RBAC is encoded as a bitmask over the RecordType enum: bit i is set when the
 * (role, action) pair permits record type i. `_ALL` is every real record type
 * (Fir..CourtOrder), the chaincode's `RECORD_TYPES`.
 */
library PolicyV1 {
    string internal constant POLICY_VERSION = "crime-policy-v1";

    function _bit(RecordType t) private pure returns (uint256) {
        return uint256(1) << uint256(uint8(t));
    }

    // Every real record type (excludes the None sentinel at index 0).
    function _all() private pure returns (uint256) {
        return
            _bit(RecordType.Fir) |
            _bit(RecordType.CaseDiary) |
            _bit(RecordType.Evidence) |
            _bit(RecordType.ForensicReport) |
            _bit(RecordType.WitnessStatement) |
            _bit(RecordType.Chargesheet) |
            _bit(RecordType.CourtOrder);
    }

    /**
     * RBAC base matrix. Returns the set of record types (as a bitmask) that
     * `role` may perform `action` on. An empty mask means the pair is denied
     * before any ABAC rule runs — the chaincode's "absent pair is a deny".
     */
    function rbacMask(Role role, Action action) internal pure returns (uint256) {
        if (role == Role.Constable) {
            if (action == Action.View) return _bit(RecordType.Fir);
            return 0;
        }
        if (role == Role.SubInspector) {
            if (action == Action.View)
                return
                    _bit(RecordType.Fir) |
                    _bit(RecordType.CaseDiary) |
                    _bit(RecordType.WitnessStatement);
            return 0;
        }
        if (role == Role.Inspector) {
            if (action == Action.View) return _all();
            if (action == Action.Annotate)
                return _bit(RecordType.Fir) | _bit(RecordType.CaseDiary);
            if (action == Action.Export)
                return
                    _bit(RecordType.Fir) |
                    _bit(RecordType.CaseDiary) |
                    _bit(RecordType.Chargesheet);
            return 0;
        }
        if (role == Role.Sho) {
            if (action == Action.View) return _all();
            if (action == Action.Annotate)
                return _bit(RecordType.Fir) | _bit(RecordType.CaseDiary);
            if (action == Action.Export) return _all();
            return 0;
        }
        if (role == Role.InvestigatingOfficer) {
            if (action == Action.View) return _all();
            if (action == Action.Annotate)
                return
                    _bit(RecordType.Fir) |
                    _bit(RecordType.CaseDiary) |
                    _bit(RecordType.Evidence);
            if (action == Action.Export)
                return
                    _bit(RecordType.Fir) |
                    _bit(RecordType.CaseDiary) |
                    _bit(RecordType.Evidence) |
                    _bit(RecordType.ForensicReport);
            return 0;
        }
        if (role == Role.LabAnalyst) {
            if (action == Action.View)
                return _bit(RecordType.Evidence) | _bit(RecordType.ForensicReport);
            if (action == Action.Annotate) return _bit(RecordType.ForensicReport);
            return 0;
        }
        if (role == Role.LabDirector) {
            if (action == Action.View)
                return _bit(RecordType.Evidence) | _bit(RecordType.ForensicReport);
            if (action == Action.Export) return _bit(RecordType.ForensicReport);
            return 0;
        }
        if (role == Role.PublicProsecutor) {
            if (action == Action.View) return _all();
            if (action == Action.Export)
                return _bit(RecordType.Chargesheet) | _bit(RecordType.CourtOrder);
            return 0;
        }
        if (role == Role.DefenseCounsel) {
            if (action == Action.View)
                return _bit(RecordType.Chargesheet) | _bit(RecordType.CourtOrder);
            return 0;
        }
        if (role == Role.Judge || role == Role.Magistrate) {
            if (action == Action.View) return _all();
            if (action == Action.Annotate) return _bit(RecordType.CourtOrder);
            if (action == Action.Export) return _all();
            return 0;
        }
        if (role == Role.CourtClerk) {
            if (action == Action.View)
                return _bit(RecordType.Chargesheet) | _bit(RecordType.CourtOrder);
            return 0;
        }
        if (role == Role.Auditor || role == Role.Ombudsman) {
            if (action == Action.View) return _all();
            return 0;
        }
        return 0; // Role.None or any unmapped role
    }

    function rbacAllows(
        Role role,
        Action action,
        RecordType t
    ) internal pure returns (bool) {
        return (rbacMask(role, action) & _bit(t)) != 0;
    }

    // Roles exempt from the case-assignment check (cross-case duty).
    function isAssignmentExempt(Role role) internal pure returns (bool) {
        return
            role == Role.Judge ||
            role == Role.Magistrate ||
            role == Role.Auditor ||
            role == Role.Ombudsman ||
            role == Role.PublicProsecutor ||
            role == Role.Sho;
    }

    // Roles allowed to see juvenile-flagged records without escalation.
    function isJuvenileAllowed(Role role) internal pure returns (bool) {
        return
            role == Role.InvestigatingOfficer ||
            role == Role.Judge ||
            role == Role.Magistrate ||
            role == Role.PublicProsecutor ||
            role == Role.Ombudsman;
    }

    // Roles that may resolve an escalated request.
    function isEscalationApprover(Role role) internal pure returns (bool) {
        return
            role == Role.Sho ||
            role == Role.Judge ||
            role == Role.Magistrate ||
            role == Role.Ombudsman;
    }

    // Clearance held by the subject, as a signed rank. Unset → -1, so a caller
    // with no clearance never clears a sensitivity gate (chaincode's `?? -1`).
    function clearanceRank(Clearance c) internal pure returns (int256) {
        if (c == Clearance.Low) return 0;
        if (c == Clearance.Medium) return 1;
        if (c == Clearance.High) return 2;
        return -1; // Unset
    }

    // Rank needed for a record's sensitivity (low/medium/high → 0/1/2).
    function sensitivityRank(Sensitivity s) internal pure returns (int256) {
        if (s == Sensitivity.Low) return 0;
        if (s == Sensitivity.Medium) return 1;
        return 2; // High
    }

    /**
     * Role → owning MSP. Used by the IdentityRegistry to reject nonsensical
     * assignments (a CourtMSP admin cannot mint a `constable`).
     */
    function roleBelongsToMsp(Msp msp, Role role) internal pure returns (bool) {
        if (msp == Msp.Police) {
            return
                role == Role.Constable ||
                role == Role.SubInspector ||
                role == Role.Inspector ||
                role == Role.Sho ||
                role == Role.InvestigatingOfficer;
        }
        if (msp == Msp.Forensics) {
            return role == Role.LabAnalyst || role == Role.LabDirector;
        }
        if (msp == Msp.Prosecution) {
            return role == Role.PublicProsecutor || role == Role.DefenseCounsel;
        }
        if (msp == Msp.Court) {
            return
                role == Role.Judge ||
                role == Role.Magistrate ||
                role == Role.CourtClerk;
        }
        if (msp == Msp.Audit) {
            return role == Role.Auditor || role == Role.Ombudsman;
        }
        return false;
    }
}
