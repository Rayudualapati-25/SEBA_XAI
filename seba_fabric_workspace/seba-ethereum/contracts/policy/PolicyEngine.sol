// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "./PolicyTypes.sol";
import "./PolicyV1.sol";

/**
 * PolicyEngine — the deterministic access-decision engine, ported one-to-one
 * from lib/policy/policyEngine.js.
 *
 * Rules run in a fixed order; the first terminal rule wins and names the
 * decisive attributes, so the returned Outcome is a reviewable explanation
 * rather than a bare yes/no. `evaluate` is a pure function of its inputs:
 * same subject + record + action + env always yields the same Outcome.
 *
 * String comparisons (jurisdiction) are done on keccak256 digests, since the
 * EVM has no native string equality.
 */
library PolicyEngine {
    using PolicyV1 for Role;

    function _eq(string memory a, string memory b) private pure returns (bool) {
        return keccak256(bytes(a)) == keccak256(bytes(b));
    }

    function _out(
        Decision decision,
        string memory reasonCode,
        string memory decisiveAttributes,
        string memory counterfactual
    ) private pure returns (Outcome memory) {
        return
            Outcome({
                decision: decision,
                reasonCode: reasonCode,
                decisiveAttributes: decisiveAttributes,
                counterfactual: counterfactual,
                policyVersion: PolicyV1.POLICY_VERSION
            });
    }

    function evaluate(
        Subject memory subject,
        RecordCtx memory record,
        Action action,
        EnvCtx memory env
    ) internal pure returns (Outcome memory) {
        // Rule 1 — credential state (PBAC: revocation handling).
        if (!subject.active) {
            return
                _out(
                    Decision.Deny,
                    "CRED_NOT_ACTIVE",
                    "subject.credentialStatus",
                    'decision would change if the requester credential status were "active"'
                );
        }

        // Rule 2 — purpose is mandatory and must be a declared purpose.
        if (env.purpose == Purpose.Unset) {
            return
                _out(
                    Decision.Deny,
                    "INVALID_PURPOSE",
                    "env.purpose",
                    "decision would change if a declared purpose were supplied"
                );
        }

        // Rule 3 — RBAC base matrix: role must permit this action on this type.
        if (!PolicyV1.rbacAllows(subject.role, action, record.recordType)) {
            return
                _out(
                    Decision.Deny,
                    "RBAC_NO_PERMISSION",
                    "subject.role,action,object.recordType",
                    "role has no permission for this action on this record type"
                );
        }

        // Rule 4 — sealed records escalate for everyone except the court.
        if (record.sealed_ && subject.msp != Msp.Court) {
            return
                _out(
                    Decision.Escalate,
                    "SEALED_RECORD",
                    "object.sealed,subject.mspId",
                    "decision would be evaluated normally if the record were not sealed"
                );
        }

        // Rule 5 — juvenile protection: restricted roles escalate.
        if (record.juvenile && !PolicyV1.isJuvenileAllowed(subject.role)) {
            return
                _out(
                    Decision.Escalate,
                    "JUVENILE_PROTECTED",
                    "object.juvenileFlag,subject.role",
                    "a supervisory approval is required because the record involves a juvenile"
                );
        }

        // Rule 6 — jurisdiction: cross-jurisdiction escalates unless it is an
        // emergency carrying an approval token (PBAC exception).
        if (
            !_eq(subject.jurisdiction, record.jurisdiction) &&
            !PolicyV1.isAssignmentExempt(subject.role)
        ) {
            if (env.emergencyFlag && env.hasApprovalToken) {
                return
                    _out(
                        Decision.Allow,
                        "EMERGENCY_CROSS_JURISDICTION",
                        "env.emergencyFlag,env.approvalToken,subject.jurisdiction,object.jurisdiction",
                        ""
                    );
            }
            return
                _out(
                    Decision.Escalate,
                    "CROSS_JURISDICTION",
                    "subject.jurisdiction,object.jurisdiction",
                    string.concat(
                        "decision would change if requester jurisdiction were '",
                        record.jurisdiction,
                        "'"
                    )
                );
        }

        // Rule 7 — case assignment (ABAC): non-exempt roles must be assigned.
        if (!PolicyV1.isAssignmentExempt(subject.role)) {
            if (!subject.assignedToCase) {
                return
                    _out(
                        Decision.Deny,
                        "NOT_ASSIGNED",
                        "subject.caseAssignments,object.caseId",
                        string.concat(
                            "decision would change if case '",
                            record.caseId,
                            "' were in the requester's assignments"
                        )
                    );
            }
        }

        // Rule 8 — sensitivity vs clearance: insufficient clearance escalates.
        int256 needed = PolicyV1.sensitivityRank(record.sensitivity);
        int256 held = PolicyV1.clearanceRank(subject.clearance);
        if (held < needed) {
            return
                _out(
                    Decision.Escalate,
                    "INSUFFICIENT_CLEARANCE",
                    "subject.clearance,object.sensitivityLevel",
                    "decision would change if requester clearance met the record's sensitivity"
                );
        }

        // Default — every gate passed.
        return
            _out(
                Decision.Allow,
                "POLICY_SATISFIED",
                "subject.role,subject.jurisdiction,subject.clearance,env.purpose",
                ""
            );
    }
}
