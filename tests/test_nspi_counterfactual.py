"""Tests for the NS-PI counterfactual generator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from seba.nspi import (
    Counterfactual,
    explain_dataframe,
    explain_request,
    learn_policy,
)

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


@pytest.fixture(scope="module")
def policy(labeled_seed42):
    return learn_policy(labeled_seed42, max_depth=8, min_samples_leaf=10)


def test_explain_request_returns_counterfactual_when_possible(policy, labeled_seed42) -> None:
    deny_indices = labeled_seed42.index[labeled_seed42["decision"] == "deny"].tolist()
    assert deny_indices, "fixture must contain at least one deny"
    cf = explain_request(policy, labeled_seed42, request_index=int(deny_indices[0]), max_edits=4)
    if cf is None:
        pytest.skip("no counterfactual within max_edits — acceptable for some rows")
    assert isinstance(cf, Counterfactual)
    assert cf.proposed_decision == "allow"
    assert 1 <= len(cf.edits) <= 4
    assert cf.explanation.startswith("Would have been ")


def test_explanation_string_lists_each_edit(policy, labeled_seed42) -> None:
    deny_indices = labeled_seed42.index[labeled_seed42["decision"] == "deny"].tolist()
    for idx in deny_indices[:50]:
        cf = explain_request(policy, labeled_seed42, request_index=int(idx), max_edits=5)
        if cf is None:
            continue
        for attr, _ in cf.edits:
            assert attr in cf.explanation, (
                f"explanation '{cf.explanation}' missing edit attribute '{attr}'"
            )
        # We found at least one usable counterfactual.
        return
    pytest.skip("no counterfactual within max_edits on the first 50 deny rows")


def test_explain_dataframe_returns_list_of_counterfactuals(policy, labeled_seed42) -> None:
    sample = labeled_seed42.head(200).reset_index(drop=True)
    cfs = explain_dataframe(policy, sample, max_edits=4)
    assert isinstance(cfs, list)
    if cfs:
        assert all(isinstance(cf, Counterfactual) for cf in cfs)
        assert all(cf.proposed_decision == "allow" for cf in cfs)
