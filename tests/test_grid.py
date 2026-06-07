"""Integration test for the full evaluation grid harness."""

from __future__ import annotations

import pandas as pd
import pytest

from seba.scoring.grid import aggregate, discover_seeds, load_event_log, score_seed


@pytest.fixture(scope="module")
def seed_assets():
    seeds = discover_seeds()
    if not seeds:
        pytest.skip("no seed assets discovered — run scripts/run_multi_seed.sh")
    return seeds


def test_discover_finds_five_seeds(seed_assets) -> None:
    found = {a.seed for a in seed_assets}
    assert {7, 21, 42, 99, 123}.issubset(found), f"got {found}"


def test_load_event_log_returns_immutable_tuple(seed_assets) -> None:
    log = load_event_log(seed_assets[0].signed_log_csv)
    assert isinstance(log, tuple)
    assert len(log) > 0
    assert isinstance(log[0], dict)


def test_score_seed_produces_one_row_per_defense_attack_pair(seed_assets) -> None:
    # Score a single seed to keep the test under 5 seconds.
    rows = score_seed(seed_assets[0])
    df = pd.DataFrame(rows)
    assert not df.empty
    # 7 registered defenses + 1 (nspi_drift) = 8 defenses, 7 attacks => 56 rows.
    assert len(df) == 8 * 7
    assert set(df["defense"]) == {
        "mutable_log",
        "signed_chain",
        "blockchain_style",
        "abac_reexec",
        "ct_log",
        "fabric_abac",
        "trusted_policy_oracle",
        "nspi_drift",
    }


def test_aggregate_returns_detail_and_summary(seed_assets) -> None:
    rows = score_seed(seed_assets[0])
    detail, summary = aggregate(rows)
    assert {"defense", "attack", "detection_rate"}.issubset(detail.columns)
    assert {"defense", "aas_mean"}.issubset(summary.columns)
    assert summary["aas_mean"].between(0.0, 1.0).all()
