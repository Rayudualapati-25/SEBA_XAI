"""Smoke test for scripts/aggregate_seeds.py."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "aggregate_seeds.py"


@pytest.fixture(scope="module")
def aggregator_module():
    spec = importlib.util.spec_from_file_location("aggregate_seeds", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Register before exec so @dataclass can resolve cls.__module__.
    sys.modules["aggregate_seeds"] = module
    spec.loader.exec_module(module)
    return module


def test_discover_runs_finds_at_least_five_seeds(aggregator_module) -> None:
    runs = aggregator_module.discover_runs()
    assert runs, "no runs discovered — multi-seed sweep must run first"
    seeds = {r.seed for r in runs}
    # Original seed 42 + the four added by run_multi_seed.sh.
    assert {7, 21, 42, 99, 123}.issubset(seeds), (
        f"expected seeds 7,21,42,99,123 to be discovered, got {sorted(seeds)}"
    )


def test_bootstrap_ci_brackets_mean(aggregator_module) -> None:
    values = [0.10, 0.11, 0.12, 0.10, 0.13]
    low, high = aggregator_module.bootstrap_ci(values)
    mean_value = sum(values) / len(values)
    assert low <= mean_value <= high


def test_bootstrap_ci_returns_nan_with_one_observation(aggregator_module) -> None:
    low, high = aggregator_module.bootstrap_ci([0.5])
    assert math.isnan(low) and math.isnan(high)


def test_extractors_return_dicts(aggregator_module) -> None:
    fake_step2 = {
        "counts": {
            "decisions": {"allow": 100, "deny": 400, "escalate": 500},
            "requests_evaluated": 1000,
        }
    }
    out = aggregator_module.extract_step2(fake_step2)
    assert out["step2.allow_rate"] == 0.1
    assert out["step2.deny_rate"] == 0.4
    assert out["step2.escalate_rate"] == 0.5
    assert out["step2.requests_evaluated"] == 1000.0
