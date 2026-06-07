#!/usr/bin/env python3
"""Aggregate per-seed prototype metrics into multi-seed summary tables.

Reads metrics.json from every prototype/runs/<DATE>_step{1,2,3,4}_*_seed<N>/
directory, groups by step + metric, and writes:

    results/tables/multi_seed_summary.csv

with mean, std, min, max, and a 95% bootstrap CI (2000 resamples) for every
numeric metric across the available seeds.

This replaces the n=1 numbers in the existing paper-evidence tables. After
this step, no result in the repo is allowed to be reported without variance.

Usage:
    python3 scripts/aggregate_seeds.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "prototype" / "runs"
OUT_DIR = REPO_ROOT / "results" / "tables"
OUT_CSV = OUT_DIR / "multi_seed_summary.csv"

SEED_DIR_RE = re.compile(r"^(?P<date>\d{8})_step(?P<step>\d+)_.*_seed(?P<seed>\d+)$")

BOOTSTRAP_RESAMPLES = 2000
RNG_SEED_FOR_BOOTSTRAP = 2026


# ---------------------------------------------------------------------------
# Metric extractors. One per pipeline step. Each returns a flat
# dict[metric_name, float] from a parsed metrics.json.
# ---------------------------------------------------------------------------


def extract_step1(metrics: dict) -> dict[str, float]:
    """Synthetic request generator metrics."""

    counts = metrics.get("counts") or {}
    total_requests = float(counts.get("access_requests", 0) or 1)
    out: dict[str, float] = {
        "step1.requests_generated": float(counts.get("access_requests", 0)),
        "step1.num_officers": float(counts.get("officers", 0)),
        "step1.num_records": float(counts.get("records", 0)),
        "step1.num_cases": float(counts.get("cases", 0)),
        "step1.num_stations": float(counts.get("stations", 0)),
    }
    cred = metrics.get("credential_status_counts") or {}
    out["step1.revoked_credential_rate"] = float(cred.get("REVOKED", 0)) / total_requests
    xj = metrics.get("cross_jurisdiction_counts") or {}
    xj_true = float(xj.get("true", 0))
    xj_total = xj_true + float(xj.get("false", 0)) or 1
    out["step1.cross_jurisdiction_rate"] = xj_true / xj_total
    sens = metrics.get("request_sensitivity_counts") or {}
    sens_total = float(sum(sens.values()) or 1)
    out["step1.classified_rate"] = float(sens.get("CLASSIFIED", 0)) / sens_total
    out["step1.high_sensitivity_rate"] = float(sens.get("HIGH", 0)) / sens_total
    return out


def extract_step2(metrics: dict) -> dict[str, float]:
    """Policy oracle decision distribution."""

    counts = metrics.get("counts") or {}
    decisions = counts.get("decisions") or {}
    total = float(sum(decisions.values()) or 1)
    return {
        "step2.allow_rate": decisions.get("allow", 0) / total,
        "step2.deny_rate": decisions.get("deny", 0) / total,
        "step2.escalate_rate": decisions.get("escalate", 0) / total,
        "step2.requests_evaluated": float(counts.get("requests_evaluated", 0)),
    }


def extract_step3(metrics: dict) -> dict[str, float]:
    """Audit-baseline tamper-detection rates."""

    det = metrics.get("self_detection_by_log_type") or {}
    return {
        "step3.mutable.detection_rate": float(det.get("mutable", {}).get("self_detection_rate", 0.0)),
        "step3.signed_chain.detection_rate": float(
            det.get("signed_hash_chain", {}).get("self_detection_rate", 0.0)
        ),
        "step3.events_logged": float(metrics.get("events_logged", 0)),
    }


def extract_step4(metrics: dict) -> dict[str, float]:
    """Permissioned blockchain-style audit detection rates."""

    td = metrics.get("tamper_detection") or {}
    return {
        "step4.blockchain.detection_rate": float(td.get("detection_rate", 0.0)),
        "step4.block_count": float(metrics.get("block_count", 0)),
        "step4.event_count": float(metrics.get("event_count", 0)),
    }


EXTRACTORS: dict[int, callable] = {
    1: extract_step1,
    2: extract_step2,
    3: extract_step3,
    4: extract_step4,
}


# ---------------------------------------------------------------------------
# Discovery + bootstrap.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RunRef:
    seed: int
    step: int
    path: Path


def discover_runs() -> list[RunRef]:
    runs: list[RunRef] = []
    for child in sorted(RUNS_DIR.iterdir()):
        if not child.is_dir():
            continue
        m = SEED_DIR_RE.match(child.name)
        if not m:
            continue
        metrics_path = child / "metrics.json"
        if not metrics_path.exists():
            continue
        runs.append(
            RunRef(seed=int(m["seed"]), step=int(m["step"]), path=metrics_path)
        )
    return runs


def bootstrap_ci(values: list[float], confidence: float = 0.95) -> tuple[float, float]:
    """Percentile bootstrap CI on the mean. Returns (low, high)."""

    if len(values) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(RNG_SEED_FOR_BOOTSTRAP)
    arr = np.asarray(values, dtype=float)
    resampled_means = rng.choice(arr, size=(BOOTSTRAP_RESAMPLES, arr.size), replace=True).mean(axis=1)
    alpha = (1 - confidence) / 2
    low = float(np.quantile(resampled_means, alpha))
    high = float(np.quantile(resampled_means, 1 - alpha))
    return (low, high)


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------


def main() -> int:
    runs = discover_runs()
    if not runs:
        print("No run directories found under prototype/runs/", file=sys.stderr)
        return 1

    # metric_name -> list of (seed, value)
    by_metric: dict[str, list[tuple[int, float]]] = defaultdict(list)
    seeds_per_step: dict[int, set[int]] = defaultdict(set)

    for run in runs:
        extractor = EXTRACTORS.get(run.step)
        if extractor is None:
            continue
        try:
            metrics = json.loads(run.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"WARN: skipping {run.path}: {exc}", file=sys.stderr)
            continue
        for name, value in extractor(metrics).items():
            by_metric[name].append((run.seed, value))
        seeds_per_step[run.step].add(run.seed)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for metric in sorted(by_metric):
        observations = sorted(by_metric[metric])
        seeds = [s for s, _ in observations]
        values = [v for _, v in observations]
        n = len(values)
        if n == 0:
            continue
        mu = mean(values)
        sd = pstdev(values) if n > 1 else 0.0
        lo, hi = bootstrap_ci(values)
        rows.append(
            {
                "metric": metric,
                "n_seeds": str(n),
                "seeds": "|".join(str(s) for s in seeds),
                "mean": f"{mu:.6f}",
                "std": f"{sd:.6f}",
                "min": f"{min(values):.6f}",
                "max": f"{max(values):.6f}",
                "ci95_low": f"{lo:.6f}",
                "ci95_high": f"{hi:.6f}",
            }
        )

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "metric",
                "n_seeds",
                "seeds",
                "mean",
                "std",
                "min",
                "max",
                "ci95_low",
                "ci95_high",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUT_CSV} ({len(rows)} metrics)")
    for step in sorted(seeds_per_step):
        seeds = sorted(seeds_per_step[step])
        print(f"  step {step}: {len(seeds)} seeds -> {seeds}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
