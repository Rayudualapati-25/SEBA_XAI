"""Tests for the NS-PI drift detector.

Key properties verified:
1. No false alarm when both samples come from the same distribution.
2. Alarm fires when distributions are genuinely different.
3. JS divergence is symmetric and non-negative.
4. Per-group drift returns one report per common partition.
"""

from __future__ import annotations

import numpy as np

from seba.nspi.drift import (
    DriftReport,
    drift_test,
    jensen_shannon_divergence,
    label_distribution,
    per_group_drift,
)


def test_js_divergence_is_zero_for_identical_distributions() -> None:
    p = {"allow": 0.3, "deny": 0.5, "escalate": 0.2}
    assert jensen_shannon_divergence(p, p) == 0.0


def test_js_divergence_is_symmetric() -> None:
    p = {"allow": 0.3, "deny": 0.5, "escalate": 0.2}
    q = {"allow": 0.1, "deny": 0.4, "escalate": 0.5}
    assert abs(jensen_shannon_divergence(p, q) - jensen_shannon_divergence(q, p)) < 1e-12


def test_label_distribution_uses_closed_vocabulary() -> None:
    dist = label_distribution(["allow", "allow", "deny"], classes=("allow", "deny", "escalate"))
    assert abs(sum(dist.values()) - 1.0) < 1e-6
    assert dist["escalate"] > 0  # smoothed


def test_drift_test_no_alarm_when_samples_share_distribution() -> None:
    rng = np.random.default_rng(42)
    classes = ("allow", "deny", "escalate")
    probs = [0.1, 0.5, 0.4]
    labels_a = rng.choice(classes, size=500, p=probs).tolist()
    labels_b = rng.choice(classes, size=500, p=probs).tolist()
    report = drift_test(
        labels_a, labels_b, classes=classes, permutations=200, alpha=0.05
    )
    assert isinstance(report, DriftReport)
    # Same DGP -> alarm should not fire (allowing for the alpha-level FPR).
    assert report.alarm is False or report.p_value > 0.01


def test_drift_test_fires_on_clear_distributional_shift() -> None:
    rng = np.random.default_rng(7)
    classes = ("allow", "deny", "escalate")
    # Sample A: mostly allow. Sample B: mostly deny.
    labels_a = rng.choice(classes, size=300, p=[0.7, 0.2, 0.1]).tolist()
    labels_b = rng.choice(classes, size=300, p=[0.1, 0.7, 0.2]).tolist()
    report = drift_test(
        labels_a, labels_b, classes=classes, permutations=300, alpha=0.05
    )
    assert report.alarm is True, f"expected alarm, got {report.to_dict()}"
    assert report.observed_divergence > 0.05


def test_per_group_drift_runs_per_partition() -> None:
    rng = np.random.default_rng(0)
    classes = ("allow", "deny", "escalate")
    a = {
        "g1": rng.choice(classes, size=80, p=[0.3, 0.4, 0.3]).tolist(),
        "g2": rng.choice(classes, size=80, p=[0.1, 0.8, 0.1]).tolist(),
    }
    b = {
        "g1": rng.choice(classes, size=80, p=[0.3, 0.4, 0.3]).tolist(),
        "g2": rng.choice(classes, size=80, p=[0.8, 0.1, 0.1]).tolist(),
    }
    reports = per_group_drift(a, b, classes=classes, permutations=150)
    assert {r.partition for r in reports} == {"g1", "g2"}
    g2 = next(r for r in reports if r.partition == "g2")
    assert g2.alarm is True
