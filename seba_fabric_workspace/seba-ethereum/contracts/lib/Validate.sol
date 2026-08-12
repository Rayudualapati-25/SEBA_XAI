// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * Validate — on-chain equivalents of the chaincode's SAFE_ID guard.
 *
 * The chaincode used the regex /^[A-Za-z0-9._-]{1,128}$/ to keep caller
 * identifiers free of separators and injection characters before they became
 * ledger keys. We reproduce it byte-by-byte so recordId/evidenceId/caseId/epoch
 * are constrained identically on the EVM.
 */
library Validate {
    /** True when `s` matches /^[A-Za-z0-9._-]{1,128}$/. */
    function isSafeId(string memory s) internal pure returns (bool) {
        bytes memory b = bytes(s);
        if (b.length == 0 || b.length > 128) {
            return false;
        }
        for (uint256 i = 0; i < b.length; i++) {
            bytes1 c = b[i];
            bool ok = (c >= 0x30 && c <= 0x39) || // 0-9
                (c >= 0x41 && c <= 0x5a) || // A-Z
                (c >= 0x61 && c <= 0x7a) || // a-z
                c == 0x2e || // .
                c == 0x5f || // _
                c == 0x2d; //   -
            if (!ok) {
                return false;
            }
        }
        return true;
    }

    function requireSafeId(string memory s, string memory field) internal pure {
        require(isSafeId(s), string.concat(field, " has invalid format"));
    }
}
