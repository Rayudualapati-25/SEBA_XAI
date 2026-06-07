"""Revocation-race attack: request fires during the revocation propagation window.

A real revocation takes non-zero time to propagate across all enforcement
points. An attacker who knows their credential is about to be revoked may
race a sensitive request through *during* propagation, before the local
station's enforcement view is updated.

This attack flips a previously-denied event back to ``allow`` and marks the
credential status as ACTIVE, simulating a stale local view. The window
itself is encoded as metadata so scoring can verify whether the defense
recognized the staleness signal.

Detection criteria:
- Defenses that cross-check officer credential_status at evaluation time
  against a canonical revocation log detect.
- Hash-chain defenses detect because the recomputed decision_hash will not
  match.
- Mutable logs do NOT detect.
"""

from __future__ import annotations

from typing import Any

from seba.attacks.base import AttackResult, EventLog, copy_log, to_log

NAME = "revocation_race"
SEVERITY = 2


def revocation_race(log: EventLog, rng: Any) -> AttackResult:
    if not log:
        return AttackResult(NAME, SEVERITY, log, affected_indices=())

    rows = copy_log(log)
    deny_indices = [
        i
        for i, r in enumerate(rows)
        if str(r.get("decision")).lower() == "deny"
        and "CREDENTIAL" in str(r.get("primary_reason_code") or "")
    ]
    if not deny_indices:
        return AttackResult(NAME, SEVERITY, to_log(rows), affected_indices=())

    idx = int(rng.choice(deny_indices))
    rows[idx]["decision"] = "allow"
    rows[idx]["primary_reason_code"] = "ALLOW_ROUTINE_CONTEXTUAL_ACCESS"
    rows[idx]["__attack_revocation_race__"] = True

    return AttackResult(
        name=NAME,
        severity=SEVERITY,
        perturbed_log=to_log(rows),
        affected_indices=(idx,),
        meta={"flipped_index": idx},
    )


revocation_race.name = NAME  # type: ignore[attr-defined]
revocation_race.severity = SEVERITY  # type: ignore[attr-defined]
