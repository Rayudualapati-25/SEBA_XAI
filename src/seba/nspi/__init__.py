"""NS-PI: Neuro-Symbolic Policy Induction.

Learns an interpretable rule list from labeled access-governance audit
traces and uses it for drift detection and counterfactual explanation.

This package implements the *novel mechanism* the first paper rests on.
The locked contribution sentence in ``CONTRIBUTION.md`` requires three
pieces:

    learner.py        Rule-list learner producing a portable policy JSON.
    drift.py          KL-divergence drift detector between declared
                      and learned policies (Step 7).
    counterfactual.py Minimal-edit explanation generator (Step 8).
"""

from __future__ import annotations

from seba.nspi.counterfactual import (
    Counterfactual,
    explain_dataframe,
    explain_request,
)
from seba.nspi.drift import (
    DriftReport,
    drift_test,
    jensen_shannon_divergence,
    per_group_drift,
)
from seba.nspi.learner import (
    LearnedPolicy,
    LearnedRule,
    encode_features,
    learn_policy,
    predict_with_policy,
)

__all__ = [
    "Counterfactual",
    "DriftReport",
    "LearnedPolicy",
    "LearnedRule",
    "drift_test",
    "encode_features",
    "explain_dataframe",
    "explain_request",
    "jensen_shannon_divergence",
    "learn_policy",
    "per_group_drift",
    "predict_with_policy",
]
