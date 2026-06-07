"""Adaptive (NS-PI-aware) attacks.

These attacks model an attacker who knows NS-PI is deployed and tries to
keep the *learned* policy close to the *declared* one so the drift detector
stays quiet, while still violating policy in ways that benefit them.

Two adaptive attacks are implemented:

1. **Policy-skew corruption (`policy_skew_corruption`)** — flip a fraction
   of recent ``deny`` events to ``allow`` for one chosen
   ``requester_station_id``, simulating a corrupted enforcement node at
   that station. The attacker keeps the per-station shift small enough
   that the *global* JS divergence stays under the alarm threshold but
   the *per-station* one does not. This is the attack NS-PI per-group
   drift is meant to catch.

2. **Coordinated explanation laundering (`coordinated_laundering`)** —
   re-label many ``escalate`` events as ``allow`` while keeping the
   primary_reason_code unchanged, so a cursory audit sees ``allow`` and
   a stale rationale. Hash-chain defenses still detect because the hash
   moves; the point of the adaptive attack is to test whether NS-PI
   adds value *on top of* hash-chain.

These are deliberately published as separate functions and not mixed into
``ATTACK_CATALOG`` — they are evaluated by ``scripts/run_ablations.py``
against NS-PI specifically.
"""

from __future__ import annotations

from typing import Any

from seba.attacks.base import AttackResult, EventLog, copy_log, to_log
from seba.attacks.compromised_signer import compromised_signer

# ---------------------------------------------------------------------------
# 1. Policy-skew corruption (per-station ALLOW-rate shift).
# ---------------------------------------------------------------------------


NAME_SKEW = "policy_skew_corruption"
SEVERITY_SKEW = 5


def policy_skew_corruption(
    log: EventLog,
    rng: Any,
    *,
    flip_fraction: float = 0.20,
) -> AttackResult:
    """Flip ``flip_fraction`` of one station's deny events to allow.

    The default 20% flip is calibrated so the *global* allow rate moves by
    only ~2 percentage points (since one station holds ~1/30th of events),
    keeping the global drift alarm quiet. The per-station alarm should
    still fire.
    """

    rows = copy_log(log)
    station_counts: dict[str, int] = {}
    for r in rows:
        station_counts[str(r.get("requester_station_id", ""))] = (
            station_counts.get(str(r.get("requester_station_id", "")), 0) + 1
        )
    if not station_counts:
        return AttackResult(NAME_SKEW, SEVERITY_SKEW, log, affected_indices=())

    # Pick the station with the most denies so the flip has bite.
    target_station = max(
        station_counts,
        key=lambda s: sum(
            1
            for r in rows
            if r.get("requester_station_id") == s and r.get("decision") == "deny"
        ),
    )
    deny_indices = [
        i
        for i, r in enumerate(rows)
        if r.get("requester_station_id") == target_station and r.get("decision") == "deny"
    ]
    if not deny_indices:
        return AttackResult(NAME_SKEW, SEVERITY_SKEW, log, affected_indices=())

    n_flip = max(1, int(len(deny_indices) * flip_fraction))
    chosen = rng.choice(deny_indices, size=n_flip, replace=False)
    affected: list[int] = []
    for raw_idx in chosen:
        idx = int(raw_idx)
        rows[idx]["decision"] = "allow"
        rows[idx]["primary_reason_code"] = "ALLOW_ROUTINE_CONTEXTUAL_ACCESS"
        rows[idx]["__attack_policy_skew__"] = True
        affected.append(idx)

    return AttackResult(
        name=NAME_SKEW,
        severity=SEVERITY_SKEW,
        perturbed_log=to_log(rows),
        affected_indices=tuple(sorted(affected)),
        meta={
            "target_station": target_station,
            "n_flipped": len(affected),
            "flip_fraction": flip_fraction,
        },
    )


policy_skew_corruption.name = NAME_SKEW  # type: ignore[attr-defined]
policy_skew_corruption.severity = SEVERITY_SKEW  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# 2. Coordinated explanation laundering.
# ---------------------------------------------------------------------------


NAME_LAUNDER = "coordinated_laundering"
SEVERITY_LAUNDER = 4


def coordinated_laundering(
    log: EventLog,
    rng: Any,
    *,
    flip_fraction: float = 0.10,
) -> AttackResult:
    """Flip a fraction of ``escalate`` events to ``allow`` while leaving
    the reason code referencing escalation, so the ledger reads as
    ``allow`` but the rationale is stale."""

    rows = copy_log(log)
    indices = [i for i, r in enumerate(rows) if r.get("decision") == "escalate"]
    if not indices:
        return AttackResult(NAME_LAUNDER, SEVERITY_LAUNDER, log, affected_indices=())
    n = max(1, int(len(indices) * flip_fraction))
    chosen = rng.choice(indices, size=n, replace=False)
    affected: list[int] = []
    for raw_idx in chosen:
        idx = int(raw_idx)
        rows[idx]["decision"] = "allow"
        # primary_reason_code intentionally NOT updated.
        rows[idx]["__attack_coordinated_laundering__"] = True
        affected.append(idx)
    return AttackResult(
        name=NAME_LAUNDER,
        severity=SEVERITY_LAUNDER,
        perturbed_log=to_log(rows),
        affected_indices=tuple(sorted(affected)),
        meta={"n_flipped": len(affected), "flip_fraction": flip_fraction},
    )


coordinated_laundering.name = NAME_LAUNDER  # type: ignore[attr-defined]
coordinated_laundering.severity = SEVERITY_LAUNDER  # type: ignore[attr-defined]


ADAPTIVE_ATTACKS = (policy_skew_corruption, coordinated_laundering, compromised_signer)
