"""Tests for explanation and audit quality metrics."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from seba.nspi import learn_policy
from seba.xai_quality import (
    audit_reconstruction_metrics,
    counterfactual_metrics,
    explanation_trace_metrics,
    stability_metrics,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
STEP2 = (
    REPO_ROOT
    / "prototype"
    / "runs"
    / "20260527_step2_policy_oracle_seed42"
    / "artifacts"
)
STEP3 = (
    REPO_ROOT
    / "prototype"
    / "runs"
    / "20260527_step3_audit_baselines_seed42"
    / "artifacts"
)
STEP4 = (
    REPO_ROOT
    / "prototype"
    / "runs"
    / "20260527_step4_permissioned_blockchain_audit_seed42"
    / "artifacts"
)


@pytest.fixture(scope="module")
def labeled_seed42() -> pd.DataFrame:
    path = STEP2 / "labeled_access_requests.csv"
    if not path.exists():
        pytest.skip(f"missing fixture: {path}")
    return pd.read_csv(path)


def test_explanation_trace_metrics_are_bounded(labeled_seed42: pd.DataFrame) -> None:
    metrics = explanation_trace_metrics(labeled_seed42)
    for key, value in metrics.items():
        assert 0.0 <= value <= 1.0, key
    assert metrics["trace_complete_rate"] > 0.9
    assert metrics["decisive_attribute_present_rate"] > 0.9


def test_counterfactual_metrics_replay_generated_edits(labeled_seed42: pd.DataFrame) -> None:
    policy = learn_policy(labeled_seed42, max_depth=8, min_samples_leaf=10)
    metrics = counterfactual_metrics(labeled_seed42.head(200).copy(), policy)
    assert metrics["counterfactual_target_count"] > 0
    assert metrics["counterfactual_generated_count"] >= 0
    assert 0.0 <= metrics["counterfactual_coverage_rate"] <= 1.0
    assert 0.0 <= metrics["counterfactual_validity_rate"] <= 1.0


def test_stability_metrics_have_duplicate_context_counts(
    labeled_seed42: pd.DataFrame,
) -> None:
    metrics = stability_metrics(labeled_seed42)
    assert metrics["stability_duplicate_group_count"] >= 0
    assert metrics["stability_duplicate_row_count"] >= 0
    assert 0.0 <= metrics["stable_decision_reason_group_rate"] <= 1.0
    assert 0.0 <= metrics["stable_decision_reason_row_rate"] <= 1.0


def test_audit_reconstruction_metrics_link_signed_log_to_blocks(
    labeled_seed42: pd.DataFrame,
) -> None:
    signed_path = STEP3 / "signed_hash_chain_log.csv"
    block_index_path = STEP4 / "block_event_index.csv"
    blocks_path = STEP4 / "permissioned_audit_blocks.jsonl"
    if not signed_path.exists() or not block_index_path.exists() or not blocks_path.exists():
        pytest.skip("missing audit artifacts")

    metrics = audit_reconstruction_metrics(
        labeled_seed42,
        pd.read_csv(signed_path),
        pd.read_csv(block_index_path),
        blocks_path,
    )
    assert metrics["audit_event_count"] == len(labeled_seed42)
    assert metrics["audit_request_join_rate"] == 1.0
    assert metrics["audit_signed_hash_match_rate"] == 1.0
    assert metrics["audit_block_index_join_rate"] == 1.0
    assert metrics["audit_commitment_in_block_rate"] == 1.0
    assert metrics["audit_reconstruction_rate"] == 1.0
