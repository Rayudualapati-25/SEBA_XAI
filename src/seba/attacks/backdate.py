"""Backdating attack: shift a request's timestamp earlier than revocation.

The attacker takes an event that occurred *after* an officer's credential
was revoked and rewrites the ``timestamp_utc`` to a value before revocation,
so that a naive temporal policy would conclude the credential was still
valid at request time.

Detection criteria:
- Hash-chain defenses detect because ``event_payload_hash`` changes when
  ``timestamp_utc`` changes.
- Defenses that re-derive ``request_content_hash`` from raw fields also
  detect because the request hash will no longer match.
- Mutable logs do NOT detect.
"""

from __future__ import annotations

from typing import Any

from seba.attacks.base import AttackResult, EventLog, copy_log, to_log

NAME = "backdate_request"
SEVERITY = 3


def backdate_request(log: EventLog, rng: Any) -> AttackResult:
    if len(log) < 4:
        return AttackResult(NAME, SEVERITY, log, affected_indices=())

    rows = copy_log(log)
    idx = int(rng.integers(len(rows) // 2, len(rows)))
    # Replace the timestamp with one earlier in the run.
    earlier_idx = int(rng.integers(0, max(1, len(rows) // 2)))
    rows[idx]["timestamp_utc"] = rows[earlier_idx].get("timestamp_utc", rows[idx]["timestamp_utc"])
    rows[idx]["__attack_backdate_source__"] = earlier_idx

    return AttackResult(
        name=NAME,
        severity=SEVERITY,
        perturbed_log=to_log(rows),
        affected_indices=(idx,),
        meta={"target_index": idx, "borrowed_timestamp_from": earlier_idx},
    )


backdate_request.name = NAME  # type: ignore[attr-defined]
backdate_request.severity = SEVERITY  # type: ignore[attr-defined]
