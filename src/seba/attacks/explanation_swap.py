"""Explanation-swap attack: swap two events' ``explanation_hash`` values.

The attacker leaves every other field intact but exchanges the
``explanation_hash`` (and the human-readable reason code where present)
between two events with different decisions. This simulates an insider who
wants the audit trail to show a different rationale than what actually
fired.

Detection criteria:
- Defenses that hash the explanation *together with* the decision (Step 3
  signed log, blockchain audit) detect because ``event_payload_hash``
  changes for both rows.
- Mutable logs do NOT detect.
- ABAC re-execution detects because the recomputed reason code disagrees
  with the recorded one.
"""

from __future__ import annotations

from typing import Any

from seba.attacks.base import AttackResult, EventLog, copy_log, to_log

NAME = "swap_explanation_hash"
SEVERITY = 2


def swap_explanation_hash(log: EventLog, rng: Any) -> AttackResult:
    if len(log) < 2:
        return AttackResult(NAME, SEVERITY, log, affected_indices=())

    rows = copy_log(log)
    # Pick two events with different primary_reason_code so the swap is
    # actually a semantic alteration, not a no-op.
    distinct_pairs = []
    n = len(rows)
    for _ in range(20):
        a, b = int(rng.integers(0, n)), int(rng.integers(0, n))
        if a == b:
            continue
        if rows[a].get("primary_reason_code") != rows[b].get("primary_reason_code"):
            distinct_pairs.append((a, b))
            break
    if not distinct_pairs:
        return AttackResult(NAME, SEVERITY, to_log(rows), affected_indices=())

    a, b = distinct_pairs[0]
    for field in ("explanation_hash", "primary_reason_code"):
        rows[a][field], rows[b][field] = rows[b].get(field), rows[a].get(field)
    rows[a]["__attack_explanation_swap_with__"] = b
    rows[b]["__attack_explanation_swap_with__"] = a

    return AttackResult(
        name=NAME,
        severity=SEVERITY,
        perturbed_log=to_log(rows),
        affected_indices=tuple(sorted((a, b))),
        meta={"pair": [a, b]},
    )


swap_explanation_hash.name = NAME  # type: ignore[attr-defined]
swap_explanation_hash.severity = SEVERITY  # type: ignore[attr-defined]
