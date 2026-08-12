// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "../policy/PolicyTypes.sol";

/**
 * ExplanationLib — canonical hashing of an explanation artifact.
 *
 * The chaincode hashed the explanation object (sorted-key JSON → SHA-256) so a
 * reviewer holding the artifact off-chain could later prove it matched what was
 * committed at decision time. We keep the same SHA-256 primitive and define ONE
 * on-chain encoding used by both the writer (AccessManager) and the verifier
 * (AuditRegistry), so a client that reconstructs the same fields recomputes the
 * same digest.
 */
library ExplanationLib {
    function decisionString(
        Decision d
    ) internal pure returns (string memory) {
        if (d == Decision.Allow) return "allow";
        if (d == Decision.Deny) return "deny";
        return "escalate";
    }

    /** SHA-256 over the abi-encoded explanation fields (deterministic order). */
    function hashExplanation(
        string memory decision,
        string memory reasonCode,
        string memory decisiveAttributes,
        string memory counterfactual,
        string memory policyVersion
    ) internal pure returns (bytes32) {
        return
            sha256(
                abi.encode(
                    decision,
                    reasonCode,
                    decisiveAttributes,
                    counterfactual,
                    policyVersion
                )
            );
    }

    function hashOutcome(Outcome memory o) internal pure returns (bytes32) {
        return
            hashExplanation(
                decisionString(o.decision),
                o.reasonCode,
                o.decisiveAttributes,
                o.counterfactual,
                o.policyVersion
            );
    }
}
