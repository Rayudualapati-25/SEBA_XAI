"""Registry of all SEBA-XAI attacks. Single source of truth for the scorer.

The order here is the canonical scoring order so result tables are
reproducible across runs.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from seba.attacks.backdate import backdate_request
from seba.attacks.base import Attack
from seba.attacks.collusion import collude_block_signature
from seba.attacks.compromised_signer import compromised_signer
from seba.attacks.explanation_swap import swap_explanation_hash
from seba.attacks.metadata_inference import metadata_inference_attack
from seba.attacks.replay import replay_approval_token
from seba.attacks.revocation_race import revocation_race

ATTACK_CATALOG: tuple[Attack, ...] = (
    cast(Attack, replay_approval_token),
    cast(Attack, backdate_request),
    cast(Attack, swap_explanation_hash),
    cast(Attack, collude_block_signature),
    cast(Attack, revocation_race),
    cast(Attack, compromised_signer),
    cast(Attack, metadata_inference_attack),
)


_BY_NAME: Mapping[str, Attack] = {a.name: a for a in ATTACK_CATALOG}


def get_attack(name: str) -> Attack:
    if name not in _BY_NAME:
        raise KeyError(
            f"unknown attack '{name}'. Available: {sorted(_BY_NAME)}"
        )
    return _BY_NAME[name]
