"""Per-defense detectors for the SEBA-XAI attack catalog.

A detector takes ``(perturbed_log, clean_log)`` and returns ``True`` iff the
defense flags the log as tampered. We compare against the clean log because
the comparison stands in for the defense's own internal cryptographic /
re-execution check (e.g. "the recomputed event_hash does not match the
recorded one"). Implementing each cryptographic check in full would
duplicate the prototype scripts; the abstract detector is faithful to the
*detection power* of each defense without re-deriving every hash.

Detector matrix:

                            mutable  signed   blockchain  abac-reexec
replay_approval_token         FALSE   TRUE      TRUE        TRUE
backdate_request              FALSE   TRUE      TRUE        TRUE
swap_explanation_hash         FALSE   TRUE      TRUE        TRUE
collude_block_signature       FALSE   FALSE     TRUE        FALSE
revocation_race               FALSE   TRUE      TRUE        TRUE (against canonical revocation log)
compromised_signer            FALSE   FALSE     FALSE       FALSE (validly re-signed output)
metadata_inference            n/a    n/a       n/a         n/a    (handled by scorer specially)
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from seba.attacks.base import EventLog

# Fields whose change a hash-chain detector notices because they are part
# of the event_payload_hash precomputed by the original Step 3 scripts.
_HASH_PROTECTED_FIELDS = (
    "timestamp_utc",
    "decision",
    "primary_reason_code",
    "explanation_hash",
    "decision_hash",
    "audit_anchor_hash",
    "request_content_hash",
)


def _has_resigned_valid_log(log: EventLog) -> bool:
    return any(bool(row.get("__attack_resigned_valid__")) for row in log)


def _has_compromised_policy_output(log: EventLog) -> bool:
    return any(bool(row.get("__attack_policy_output_compromised__")) for row in log)


def _row_differs(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    return any(a.get(field) != b.get(field) for field in _HASH_PROTECTED_FIELDS)


def mutable_log_detector(perturbed_log: EventLog, clean_log: EventLog) -> bool:
    """Mutable log: only flags schema breakage. By construction never detects."""

    # Even a mutable log fails its schema check if rows are added/removed.
    # A real mutable log keeps no integrity proof, so this is generous.
    return len(perturbed_log) != len(clean_log)


def signed_chain_detector(perturbed_log: EventLog, clean_log: EventLog) -> bool:
    """Signed hash-chain log: detects any modification to hash-protected fields,
    insertions, or deletions. Does NOT understand validator quorums or a
    validly re-signed corrupted log.
    """

    if len(perturbed_log) != len(clean_log):
        return True
    if _has_resigned_valid_log(perturbed_log):
        return False
    return any(
        _row_differs(p, c) for p, c in zip(perturbed_log, clean_log, strict=True)
    )


def quorum_chain_detector(perturbed_log: EventLog, clean_log: EventLog) -> bool:
    """Permissioned blockchain-style detector: signed-chain checks + quorum check."""

    if signed_chain_detector(perturbed_log, clean_log):
        return True
    if _has_resigned_valid_log(perturbed_log):
        return False
    # Reject any row that carries a sub-quorum signature attestation.
    for row in perturbed_log:
        quorum = row.get("__attack_collusion_quorum__")
        if quorum is not None and int(quorum) < 3:
            return True
    return False


def abac_reexecution_detector(perturbed_log: EventLog, clean_log: EventLog) -> bool:
    """ABAC re-execution: re-runs the policy from raw attributes.

    Detects anything that would change the recomputed decision OR that
    presents an obviously-stale credential. Does NOT detect validator
    collusion (it has no ledger-layer visibility). In the compromised-signer
    experiment, the canonical policy output itself is treated as compromised,
    so this audit-only proxy is intentionally blind; a separate independent
    raw-attribute oracle would be a stronger future baseline.
    """

    if len(perturbed_log) != len(clean_log):
        return True
    if _has_compromised_policy_output(perturbed_log):
        return False
    return any(
        p.get("decision") != c.get("decision")
        or p.get("primary_reason_code") != c.get("primary_reason_code")
        or p.get("timestamp_utc") != c.get("timestamp_utc")
        or bool(p.get("__attack_revocation_race__"))
        for p, c in zip(perturbed_log, clean_log, strict=True)
    )
