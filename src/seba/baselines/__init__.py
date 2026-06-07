"""Literature baselines re-implemented for direct comparison.

Each baseline exposes the same ``DefenseDetector`` interface as the
in-house defenses in ``seba.scoring.detectors``, so the AAS scorer can
treat them uniformly.

The implementations are deliberately minimal — the point is to faithfully
capture the *detection power* of each published design, not to reproduce
the wire protocol. Simplifications are documented in each module.
"""

from __future__ import annotations

from seba.baselines.ct_log import CTLog, ct_log_detector
from seba.baselines.fabric_abac import FabricABACLedger, fabric_abac_detector
from seba.baselines.trusted_oracle import TrustedPolicyDecision, TrustedRawPolicyOracle

__all__ = [
    "CTLog",
    "FabricABACLedger",
    "TrustedPolicyDecision",
    "TrustedRawPolicyOracle",
    "ct_log_detector",
    "fabric_abac_detector",
]
