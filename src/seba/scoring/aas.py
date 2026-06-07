"""Adversarial Audit Score (AAS): severity-weighted detection rate."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

import numpy as np

from seba.attacks.base import Attack, AttackResult, EventLog
from seba.attacks.catalog import ATTACK_CATALOG

DefenseDetector = Callable[[EventLog, EventLog], bool]


@dataclass(frozen=True, slots=True)
class AASResult:
    """Adversarial Audit Score for one (defense, seed) cell.

    Attributes:
        defense: Defense identifier.
        per_attack: Mapping attack_name -> 1.0 (detected) or 0.0 (missed).
        severities: Mapping attack_name -> integer severity weight used.
        aas: Severity-weighted detection rate, normalized to [0, 1].
        unweighted: Plain detection rate (mean of per_attack values).
    """

    defense: str
    per_attack: dict[str, float]
    severities: dict[str, int]
    aas: float
    unweighted: float


def _is_metadata_inference(attack: Attack) -> bool:
    return attack.name == "metadata_inference"


def score_defense_against_catalog(
    defense_name: str,
    detector: DefenseDetector,
    clean_log: EventLog,
    seed: int,
    *,
    ledger_view: EventLog | None = None,
    attacks: Iterable[Attack] = ATTACK_CATALOG,
) -> AASResult:
    """Run every catalog attack against one defense.

    Args:
        defense_name: Identifier recorded in the result table.
        detector: Function ``(perturbed_log, clean_log) -> bool`` indicating
            whether the defense flags the perturbed log as tampered.
        clean_log: Untouched event log this defense protects.
        seed: Per-cell RNG seed for the attacks (use the run seed).
        ledger_view: Public ledger view of ``clean_log`` exposed to the
            metadata-inference attacker. Defaults to ``clean_log`` when the
            defense exposes the same fields a full audit log would; pass a
            minimized projection (e.g. dropping sensitive columns) to model
            a privacy-aware defense.
        attacks: Override the attack catalog (used by adaptive-attack tests).

    Returns:
        ``AASResult`` with per-attack outcomes and the aggregate AAS.
    """

    rng = np.random.default_rng(seed)
    per_attack: dict[str, float] = {}
    severities: dict[str, int] = {}

    for attack in attacks:
        result: AttackResult = attack(clean_log, rng)
        severities[attack.name] = result.severity

        if _is_metadata_inference(attack):
            # Re-run the attack against the defense's published ledger view.
            view = ledger_view if ledger_view is not None else clean_log
            inference_result: AttackResult = attack(view, rng)
            detected = bool(inference_result.meta.get("detected", False))
            per_attack[attack.name] = 1.0 if detected else 0.0
            continue

        # No-op attack (e.g. insufficient data) — count as detected since
        # the defense was never challenged.
        if not result.affected_indices:
            per_attack[attack.name] = 1.0
            continue

        per_attack[attack.name] = 1.0 if detector(result.perturbed_log, clean_log) else 0.0

    return AASResult(
        defense=defense_name,
        per_attack=per_attack,
        severities=severities,
        aas=compute_aas(per_attack, severities),
        unweighted=float(np.mean(list(per_attack.values()))) if per_attack else 0.0,
    )


def compute_aas(per_attack: dict[str, float], severities: dict[str, int]) -> float:
    """Severity-weighted detection rate in [0, 1]."""

    total_weight = sum(severities.get(name, 1) for name in per_attack)
    if total_weight <= 0:
        return 0.0
    weighted = sum(per_attack[name] * severities.get(name, 1) for name in per_attack)
    return weighted / total_weight
