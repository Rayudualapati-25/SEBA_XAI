"""Shared pytest fixtures for the seba test suite."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SEED42_RUN = REPO_ROOT / "prototype" / "runs" / "20260527_step1_synthetic_requests_seed42"


@pytest.fixture(scope="session")
def seed42_artifacts() -> Path:
    """Path to the seed-42 Step-1 artifacts directory."""

    artifacts = SEED42_RUN / "artifacts"
    if not artifacts.exists():
        pytest.skip(f"seed-42 run artifacts not found at {artifacts}")
    return artifacts


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into a list of column->value dicts."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.fixture(scope="session")
def access_request_rows(seed42_artifacts: Path) -> list[dict[str, str]]:
    return read_csv_rows(seed42_artifacts / "access_requests.csv")


@pytest.fixture(scope="session")
def officer_rows(seed42_artifacts: Path) -> list[dict[str, str]]:
    return read_csv_rows(seed42_artifacts / "officers.csv")


@pytest.fixture(scope="session")
def record_rows(seed42_artifacts: Path) -> list[dict[str, str]]:
    return read_csv_rows(seed42_artifacts / "records.csv")


@pytest.fixture(scope="session")
def station_rows(seed42_artifacts: Path) -> list[dict[str, str]]:
    return read_csv_rows(seed42_artifacts / "stations.csv")
