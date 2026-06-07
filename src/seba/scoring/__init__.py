"""Adversarial Audit Score (AAS) and per-defense detection evaluation."""

from __future__ import annotations

from seba.scoring.aas import (
    AASResult,
    DefenseDetector,
    compute_aas,
    score_defense_against_catalog,
)
from seba.scoring.detectors import (
    abac_reexecution_detector,
    mutable_log_detector,
    quorum_chain_detector,
    signed_chain_detector,
)

__all__ = [
    "AASResult",
    "DefenseDetector",
    "abac_reexecution_detector",
    "compute_aas",
    "mutable_log_detector",
    "quorum_chain_detector",
    "score_defense_against_catalog",
    "signed_chain_detector",
]
