"""Replay attack: reuse a valid approval-token event after its window expired.

Picks a random event whose decision was ``allow`` and duplicates it with a
new ``event_sequence`` but the original ``decision_hash`` and approval
metadata, simulating an attacker who captured an approval token and replays
it against a later request that should have required fresh approval.

Detection criteria:
- Hash-chain defenses detect because ``previous_event_hash`` no longer
  matches the actual prior chain head.
- ABAC defenses with explicit nonce/expiry tracking detect because the
  approval token is outside its valid window.
- Mutable logs do NOT detect by construction.
"""

from __future__ import annotations

from typing import Any

from seba.attacks.base import AttackResult, EventLog, copy_log, to_log

NAME = "replay_approval_token"
SEVERITY = 3


def replay_approval_token(log: EventLog, rng: Any) -> AttackResult:
    if len(log) < 2:
        return AttackResult(NAME, SEVERITY, log, affected_indices=())

    rows = copy_log(log)
    allow_indices = [i for i, r in enumerate(rows) if str(r.get("decision")).lower() == "allow"]
    if not allow_indices:
        return AttackResult(NAME, SEVERITY, to_log(rows), affected_indices=())

    source = int(rng.choice(allow_indices))
    # Insert the cloned event at a random position after the source.
    insert_at = int(rng.integers(source + 1, len(rows) + 1))
    cloned = dict(rows[source])
    cloned["event_sequence"] = len(rows) + 1
    cloned["event_id"] = cloned.get("event_id", "") + "-REPLAY"
    # Mark the replay with a tag for analysis (defenses do not see this).
    cloned["__attack_replay_source__"] = source
    rows.insert(insert_at, cloned)
    # Re-number event_sequence to preserve invariants downstream.
    for i, r in enumerate(rows):
        r["event_sequence"] = i + 1

    return AttackResult(
        name=NAME,
        severity=SEVERITY,
        perturbed_log=to_log(rows),
        affected_indices=(insert_at,),
        meta={"source_index": source, "insert_index": insert_at},
    )


replay_approval_token.name = NAME  # type: ignore[attr-defined]
replay_approval_token.severity = SEVERITY  # type: ignore[attr-defined]
