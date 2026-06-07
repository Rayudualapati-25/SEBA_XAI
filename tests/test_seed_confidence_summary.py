"""Tests for scripts/run_seed_confidence_summary.py.

These tests cover the pure aggregation helpers. They intentionally do not run
the upstream experiment scripts; the CLI reproduction path verifies that the
real CSV artifacts can be regenerated.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_seed_confidence_summary.py"


@pytest.fixture(scope="module")
def confidence_module():
    spec = importlib.util.spec_from_file_location("run_seed_confidence_summary", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_seed_confidence_summary"] = module
    spec.loader.exec_module(module)
    return module


def test_summarize_uses_sample_std_when_multiple_seeds(confidence_module) -> None:
    summary = confidence_module.summarize([1.0, 0.0, 1.0], [7, 42, 123])

    assert summary["n_seeds"] == 3
    assert summary["seeds"] == "7|42|123"
    assert summary["mean"] == 0.666667
    assert summary["std"] == 0.57735
    assert summary["std_defined"] is True
    assert summary["min"] == 0.0
    assert summary["max"] == 1.0


def test_summarize_marks_single_seed_std_as_undefined(confidence_module) -> None:
    summary = confidence_module.summarize([0.75], [99])

    assert summary["n_seeds"] == 1
    assert summary["std"] == 0.0
    assert summary["std_defined"] is False
    assert summary["mean"] == 0.75


def test_grouped_metric_emits_summary_and_long_raw_rows(confidence_module) -> None:
    frame = pd.DataFrame(
        {
            "seed": [42, 7, 123, 7],
            "defense": ["nspi", "nspi", "nspi", "signed"],
            "detected": [1, 0, 1, 0],
        }
    )

    summaries, raws = confidence_module._grouped_metric(
        frame,
        "toy_source",
        "toy_family",
        ["defense"],
        "detected",
        "detection_rate",
    )

    by_group = {row["group"]: row for row in summaries}
    assert by_group["defense=nspi"]["n_seeds"] == 3
    assert by_group["defense=nspi"]["mean"] == 0.666667
    assert by_group["defense=signed"]["std_defined"] is False

    nspi_raw = [row for row in raws if row["group"] == "defense=nspi"]
    assert [row["seed"] for row in nspi_raw] == [7, 42, 123]
    assert [row["value"] for row in nspi_raw] == [0.0, 1.0, 1.0]


def test_quality_extractor_reads_expected_artifact(confidence_module) -> None:
    summaries, raws = confidence_module.extract_quality()

    metrics = {row["metric"] for row in summaries}
    assert "trace_complete_rate" in metrics
    assert "counterfactual_validity_rate" in metrics
    assert "audit_reconstruction_rate" in metrics
    assert summaries
    assert raws
