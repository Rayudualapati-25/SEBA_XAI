"""Tests for the NS-PI rule-list learner.

Runs the learner on the seed-42 Step-2 labeled artifacts and verifies:
- the learned policy fits the deterministic oracle with high accuracy
  (since the oracle IS deterministic, a tree of sufficient depth should
  recover it exactly or very near it),
- emitted rules are interpretable (few decisive attributes per rule),
- the predict function round-trips on the training data.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from seba.nspi import learn_policy, predict_with_policy

REPO_ROOT = Path(__file__).resolve().parents[1]
LABELED_RUN = (
    REPO_ROOT
    / "prototype"
    / "runs"
    / "20260527_step2_policy_oracle_seed42"
    / "artifacts"
    / "labeled_access_requests.csv"
)


@pytest.fixture(scope="module")
def labeled_seed42() -> pd.DataFrame:
    if not LABELED_RUN.exists():
        pytest.skip(f"labeled run not found: {LABELED_RUN}")
    return pd.read_csv(LABELED_RUN)


def test_learner_recovers_oracle_with_high_accuracy(labeled_seed42) -> None:
    policy = learn_policy(labeled_seed42, max_depth=10, min_samples_leaf=5)
    preds = predict_with_policy(policy, labeled_seed42)
    accuracy = float((preds == labeled_seed42["decision"].values).mean())
    # The oracle is deterministic; a depth-10 tree over the right features
    # must achieve very high accuracy on its own training data.
    assert accuracy >= 0.85, f"expected >= 0.85 train accuracy, got {accuracy:.3f}"


def test_learned_policy_serializes_to_json(tmp_path, labeled_seed42) -> None:
    policy = learn_policy(labeled_seed42, max_depth=6, min_samples_leaf=20)
    out = tmp_path / "learned_policy.json"
    policy.to_json(out)
    payload = json.loads(out.read_text())
    assert payload["learner_version"].startswith("NSPI-")
    assert payload["rules"], "policy must have at least one rule"
    for rule in payload["rules"]:
        assert rule["decision"] in {"allow", "deny", "escalate"}
        assert isinstance(rule["confidence"], float)
        assert 0.0 <= rule["confidence"] <= 1.0


def test_rules_are_interpretable(labeled_seed42) -> None:
    """Interpretability gate: median number of decisive attributes per
    rule must be small (rule list, not opaque tree)."""

    policy = learn_policy(labeled_seed42, max_depth=8, min_samples_leaf=10)
    decisive_lengths = [len(r.decisive_attributes) for r in policy.rules]
    median = float(np.median(decisive_lengths))
    assert median <= 6, f"median rule uses {median} decisive attributes — too dense"


def test_predict_returns_one_label_per_row(labeled_seed42) -> None:
    policy = learn_policy(labeled_seed42, max_depth=4, min_samples_leaf=20)
    preds = predict_with_policy(policy, labeled_seed42)
    assert len(preds) == len(labeled_seed42)
    assert set(preds).issubset({"allow", "deny", "escalate"})
