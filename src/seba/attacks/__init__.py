"""Adversarial attacks against SEBA-XAI access-governance defenses.

Each attack is a pure function:

    attack(clean_log, rng) -> AttackResult

where ``AttackResult`` carries the perturbed log, a severity weight, and the
ground-truth label that any defense ought to detect. The catalog of available
attacks is declared in ``catalog.py`` so the scorer can enumerate them
deterministically.

This module is the *external* ground truth that replaces the tautological
"policy oracle scores itself" evaluation in the original prototype.
"""

from __future__ import annotations

from seba.attacks.backdate import backdate_request
from seba.attacks.base import Attack, AttackResult, EventRow
from seba.attacks.catalog import ATTACK_CATALOG, get_attack
from seba.attacks.collusion import collude_block_signature
from seba.attacks.compromised_signer import compromised_signer
from seba.attacks.explanation_swap import swap_explanation_hash
from seba.attacks.metadata_inference import metadata_inference_attack
from seba.attacks.replay import replay_approval_token
from seba.attacks.revocation_race import revocation_race

__all__ = [
    "ATTACK_CATALOG",
    "Attack",
    "AttackResult",
    "EventRow",
    "backdate_request",
    "compromised_signer",
    "collude_block_signature",
    "get_attack",
    "metadata_inference_attack",
    "replay_approval_token",
    "revocation_race",
    "swap_explanation_hash",
]
