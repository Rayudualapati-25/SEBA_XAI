"""Tests for the workload/policy-mix stress harness helpers.

These tests exercise the pure helper functions (matrix construction,
aggregation, realized-ratio measurement) without running the full
generate -> oracle -> audit pipeline, which is covered by the script's own
reproduction run and would be too slow for the unit suite.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_workload_policy_stress.py"


@pytest.fixture(scope="module")
def stress_module():
    spec = importlib.util.spec_from_file_location("run_workload_policy_stress", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_workload_policy_stress"] = module
    spec.loader.exec_module(module)
    return module


def test_baseline_weights_match_generator(stress_module) -> None:
    """The stress harness must mirror the generator's real SCENARIO_WEIGHTS so
    the 'baseline' arm is genuinely the default distribution."""

    sys.path.insert(0, str(REPO_ROOT / "prototype" / "synthetic_access_sim"))
    import generate_synthetic_requests as gen  # noqa: PLC0415

    assert stress_module.BASELINE_WEIGHTS == gen.SCENARIO_WEIGHTS
    # Every mix arm must keep the same number of scenario weights.
    for arm, weights in stress_module.MIX_ARMS.items():
        assert len(weights) == len(gen.SCENARIO_WEIGHTS), arm


def test_build_matrix_covers_sizes_and_mixes(stress_module) -> None:
    cells = stress_module.build_matrix(seeds=(7, 42), sizes=(500, 1000))
    arms = {c[0] for c in cells}
    # Size arm present for both sizes.
    assert "size_baseline" in arms
    # Every non-baseline mix arm present.
    for arm in stress_module.MIX_ARMS:
        if arm == "baseline":
            continue
        assert f"mix_{arm}" in arms
    # Size-arm cells = sizes x seeds = 2 x 2 = 4.
    size_cells = [c for c in cells if c[0] == "size_baseline"]
    assert len(size_cells) == 4


def test_realized_ratios_measures_distribution(stress_module) -> None:
    labeled = pd.DataFrame(
        {
            "record_sensitivity_level": ["CLASSIFIED", "HIGH", "LOW", "CLASSIFIED"],
            "requester_credential_status": ["ACTIVE", "REVOKED", "ACTIVE", "REVOKED"],
            "approval_token_status": ["MISSING", "PRESENT_VALID", "NOT_REQUIRED", "EXPIRED"],
            "cross_jurisdiction": ["true", "false", "true", "true"],
            "decision": ["allow", "deny", "escalate", "deny"],
        }
    )
    ratios = stress_module._realized_ratios(labeled)
    assert ratios["classified_ratio"] == 0.5
    assert ratios["revoked_credential_ratio"] == 0.5
    assert ratios["cross_jurisdiction_ratio"] == 0.75
    # approval missing = not in {NOT_REQUIRED, PRESENT_VALID} -> MISSING + EXPIRED.
    assert ratios["approval_missing_ratio"] == 0.5
    assert abs(ratios["allow_rate"] + ratios["deny_rate"] + ratios["escalate_rate"] - 1.0) < 1e-9


def test_aggregate_groups_by_arm_and_size(stress_module) -> None:
    rows = [
        {"arm": "size_baseline", "num_requests": 500, "seed": 7, "status": "ok",
         "classified_ratio": 0.2, "cf_validity": 1.0, "runtime_seconds": 2.0},
        {"arm": "size_baseline", "num_requests": 500, "seed": 42, "status": "ok",
         "classified_ratio": 0.3, "cf_validity": 0.9, "runtime_seconds": 2.2},
        {"arm": "mix_x", "num_requests": 1000, "seed": 7, "status": "error: boom"},
    ]
    summary = stress_module.aggregate(rows)
    assert not summary.empty
    base = summary[(summary["arm"] == "size_baseline") & (summary["num_requests"] == 500)]
    assert len(base) == 1
    assert abs(float(base["classified_ratio"].iloc[0]) - 0.25) < 1e-9
    assert int(base["n_seeds"].iloc[0]) == 2
    # The errored cell must be excluded from aggregation.
    assert "mix_x" not in set(summary["arm"])
