"""Shared types for the SEBA-XAI attack catalog.

Conventions:

- An audit log is a tuple of immutable ``EventRow`` records (dicts cast to
  ``MappingProxyType`` would be cleaner, but plain ``dict`` is kept for
  CSV interop). Attacks produce *new* tuples — they never mutate input.
- Each attack carries a ``severity`` weight (1–5). The Adversarial Audit
  Score (AAS) is a severity-weighted detection rate.
- Each attack records the *indices* of events it touched so the defense
  evaluator can verify whether the defense detected exactly those events
  versus only some, versus none.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

EventRow = Mapping[str, Any]
EventLog = tuple[EventRow, ...]


@dataclass(frozen=True, slots=True)
class AttackResult:
    """Outcome of applying one attack to one clean audit log.

    Attributes:
        name: Stable attack identifier (matches the catalog key).
        severity: Integer weight in 1..5 used by the AAS scorer.
        perturbed_log: New event log after the attack (immutable tuple).
        affected_indices: Sorted tuple of event indices that the attack
            modified, deleted, or fabricated. A defense is considered to
            have ``detected`` the attack if it flags at least one of these
            indices (recall=1) or if it raises a global tamper alarm.
        meta: Free-form key/value metadata used by analysis scripts only.
    """

    name: str
    severity: int
    perturbed_log: EventLog
    affected_indices: tuple[int, ...]
    meta: Mapping[str, Any] = field(default_factory=dict)


class Attack(Protocol):
    """Callable signature every attack implements."""

    name: str
    severity: int

    def __call__(self, log: EventLog, rng: Any) -> AttackResult: ...


# ---------------------------------------------------------------------------
# Helpers used by individual attack implementations.
# ---------------------------------------------------------------------------


def copy_log(log: EventLog) -> list[dict[str, Any]]:
    """Return a deep-enough mutable copy of an event log.

    Each row is rebuilt as a fresh dict so subsequent in-place edits inside
    the attack function do not mutate the caller's data.
    """

    return [dict(row) for row in log]


def to_log(rows: list[dict[str, Any]]) -> EventLog:
    """Freeze a mutable list of rows back into an immutable EventLog."""

    return tuple(dict(row) for row in rows)
