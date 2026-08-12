// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "../policy/PolicyTypes.sol";
import "../policy/PolicyEngine.sol";

/**
 * Test-only wrapper exposing the internal PolicyEngine.evaluate as an external
 * pure function, so the deterministic decision logic can be unit-tested in
 * isolation — the EVM equivalent of the chaincode's policyEngine.test.js.
 * Not part of the deployed system.
 */
contract PolicyEngineHarness {
    function evaluate(
        Subject calldata subject,
        RecordCtx calldata record,
        Action action,
        EnvCtx calldata env
    ) external pure returns (Outcome memory) {
        return PolicyEngine.evaluate(subject, record, action, env);
    }
}
