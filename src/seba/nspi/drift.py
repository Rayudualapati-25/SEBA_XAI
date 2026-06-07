"""NS-PI drift detector.

Compares two decision distributions and decides whether they have drifted
beyond what could be explained by sampling noise. Used to compare:

  (declared_policy_predictions, learned_policy_predictions)
  (clean_log_predictions,        attacked_log_predictions)
  (period_t_predictions,         period_t_plus_1_predictions)

Method:
- Symmetric KL divergence (Jensen-Shannon-style) between the per-class
  rates of two label sequences over a partition of the data (whole set or
  per rule-group).
- Significance via permutation test: shuffle the joint labels B times,
  recompute the divergence, take the proportion >= observed.
- Alarm fires when ``p_value <= alpha`` *and* observed divergence is
  above an absolute floor (so trivially-different distributions on tiny
  partitions don't raise).

This is the *novel-mechanism* core. The first paper claim depends on
showing that this alarm:
- fires on adversarial logs from the Step-4 attack catalog,
- does NOT fire on clean multi-seed logs (false-positive rate <= alpha).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

DEFAULT_PERMUTATIONS = 500
DEFAULT_ALPHA = 0.05
DEFAULT_MIN_DIVERGENCE = 1e-3


# ---------------------------------------------------------------------------
# Data containers.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DriftReport:
    """Drift-test outcome for one comparison."""

    partition: str
    n_a: int
    n_b: int
    distribution_a: Mapping[str, float]
    distribution_b: Mapping[str, float]
    observed_divergence: float
    p_value: float
    alpha: float
    alarm: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "partition": self.partition,
            "n_a": int(self.n_a),
            "n_b": int(self.n_b),
            "distribution_a": {k: float(v) for k, v in self.distribution_a.items()},
            "distribution_b": {k: float(v) for k, v in self.distribution_b.items()},
            "observed_divergence": float(self.observed_divergence),
            "p_value": float(self.p_value),
            "alpha": float(self.alpha),
            "alarm": bool(self.alarm),
        }


# ---------------------------------------------------------------------------
# Distribution helpers.
# ---------------------------------------------------------------------------


def label_distribution(
    labels: Sequence[str], classes: Sequence[str], smoothing: float = 1e-9
) -> dict[str, float]:
    """Return Laplace-smoothed empirical distribution over ``classes``."""

    counts = {c: 0 for c in classes}
    for label in labels:
        if label in counts:
            counts[label] += 1
    n = len(labels)
    if n == 0:
        # Uniform fallback so divergence isn't undefined.
        return {c: 1.0 / len(classes) for c in classes}
    total = n + smoothing * len(classes)
    return {c: (counts[c] + smoothing) / total for c in classes}


def jensen_shannon_divergence(
    p: Mapping[str, float], q: Mapping[str, float]
) -> float:
    """Symmetric KL via the JS midpoint. Returns nats."""

    classes = sorted(set(p) | set(q))
    p_arr = np.asarray([p.get(c, 0.0) for c in classes], dtype=float)
    q_arr = np.asarray([q.get(c, 0.0) for c in classes], dtype=float)
    m = 0.5 * (p_arr + q_arr)

    def _kl(a: np.ndarray, b: np.ndarray) -> float:
        mask = (a > 0) & (b > 0)
        return float(np.sum(a[mask] * np.log(a[mask] / b[mask])))

    return 0.5 * (_kl(p_arr, m) + _kl(q_arr, m))


# ---------------------------------------------------------------------------
# Permutation test.
# ---------------------------------------------------------------------------


def drift_test(
    labels_a: Sequence[str],
    labels_b: Sequence[str],
    *,
    classes: Sequence[str] = ("allow", "deny", "escalate"),
    partition: str = "all",
    permutations: int = DEFAULT_PERMUTATIONS,
    alpha: float = DEFAULT_ALPHA,
    min_divergence: float = DEFAULT_MIN_DIVERGENCE,
    rng_seed: int = 2026,
) -> DriftReport:
    """Permutation test for distributional drift between two label sequences.

    Args:
        labels_a, labels_b: Two label sequences to compare.
        classes: Closed vocabulary of valid labels.
        partition: Free-form identifier reported back so caller can group
            results per rule, per seed, etc.
        permutations: Number of label-shuffling resamples.
        alpha: Significance threshold for the alarm.
        min_divergence: Absolute floor; tiny divergences on tiny partitions
            do not raise alarms even if the p-value is small.
        rng_seed: Reproducible permutation rng seed.

    Returns:
        ``DriftReport`` with observed divergence, p-value, and alarm flag.
    """

    p = label_distribution(labels_a, classes)
    q = label_distribution(labels_b, classes)
    observed = jensen_shannon_divergence(p, q)

    rng = np.random.default_rng(rng_seed)
    joined = np.concatenate(
        [np.asarray(labels_a, dtype=object), np.asarray(labels_b, dtype=object)]
    )
    n_a = len(labels_a)
    n_total = len(joined)

    if n_total < 2 or n_a == 0 or len(labels_b) == 0:
        return DriftReport(
            partition=partition,
            n_a=n_a,
            n_b=len(labels_b),
            distribution_a=p,
            distribution_b=q,
            observed_divergence=observed,
            p_value=1.0,
            alpha=alpha,
            alarm=False,
        )

    null_divs = np.empty(permutations, dtype=float)
    for i in range(permutations):
        idx = rng.permutation(n_total)
        shuffled = joined[idx]
        p_null = label_distribution(shuffled[:n_a].tolist(), classes)
        q_null = label_distribution(shuffled[n_a:].tolist(), classes)
        null_divs[i] = jensen_shannon_divergence(p_null, q_null)

    # +1 numerator/denominator: avoids p=0 when observed is strictly larger
    # than every shuffle, which would overclaim significance.
    p_value = float((np.sum(null_divs >= observed) + 1) / (permutations + 1))
    alarm = bool(p_value <= alpha and observed >= min_divergence)

    return DriftReport(
        partition=partition,
        n_a=n_a,
        n_b=len(labels_b),
        distribution_a=p,
        distribution_b=q,
        observed_divergence=observed,
        p_value=p_value,
        alpha=alpha,
        alarm=alarm,
    )


# ---------------------------------------------------------------------------
# Per rule-group convenience wrapper.
# ---------------------------------------------------------------------------


def per_group_drift(
    group_to_labels_a: Mapping[str, Sequence[str]],
    group_to_labels_b: Mapping[str, Sequence[str]],
    **kwargs: Any,
) -> list[DriftReport]:
    """Run drift_test once per partition key common to both maps."""

    keys = sorted(set(group_to_labels_a) & set(group_to_labels_b))
    return [
        drift_test(
            group_to_labels_a[key],
            group_to_labels_b[key],
            partition=key,
            **kwargs,
        )
        for key in keys
    ]
