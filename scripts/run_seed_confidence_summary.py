#!/usr/bin/env python3
"""Seed-level confidence / stability summary for SEBA-XAI.

Purpose: before any paper Results section is written, consolidate the
*across-seed* mean / std / min / max for the headline metrics so we can state
how stable each result is. This script does NOT run experiments. It reads the
existing seed-level raw CSVs under ``results/tables/`` and aggregates them.

Honesty rules enforced here:
- Every number is computed from a real seed-level row in an existing raw CSV.
- ``std`` is the sample std across seeds (ddof=1) when n_seeds >= 2, else 0.0
  with a ``std_defined`` flag = False, so a single-seed metric is never
  presented as if it had measured variance.
- A metric that has no seed-level source is NOT invented; it is simply absent
  and the limitation is noted in the iteration report.

Source raw tables consumed (verified seed columns):
  full_grid_raw.csv                          (seed, defense, attack, detected)
  adaptive_attack_summary.csv                (seed, attack, defense, detected)
  explanation_audit_quality.csv              (seed, ...quality rates...)
  nspi_compromised_signer_sensitivity_raw.csv(seed, flip_fraction, ...)
  nspi_targeted_compromised_signer_raw.csv   (seed, target_scope, ...)
  workload_policy_stress_raw.csv             (seed, arm, num_requests, ...)

Outputs:
  results/tables/seed_confidence_summary.csv  (tidy: one row per metric/group)
  results/tables/seed_confidence_raw.csv      (long: per-seed values used)
"""

from __future__ import annotations

import argparse
import statistics
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
TABLES = REPO_ROOT / "results" / "tables"

SUMMARY_FIELDS = [
    "source_table",
    "metric_family",
    "group",
    "metric",
    "n_seeds",
    "seeds",
    "mean",
    "std",
    "std_defined",
    "min",
    "max",
]


# ---------------------------------------------------------------------------
# Core stat helper.
# ---------------------------------------------------------------------------


def summarize(values: list[float], seeds: list[int]) -> dict[str, object]:
    """Across-seed summary. std is sample std (ddof=1) only when n>=2."""

    n = len(values)
    mean = statistics.fmean(values) if n else float("nan")
    if n >= 2:
        std = statistics.stdev(values)
        std_defined = True
    else:
        std = 0.0
        std_defined = False
    return {
        "n_seeds": n,
        "seeds": "|".join(str(s) for s in seeds),
        "mean": round(mean, 6),
        "std": round(std, 6),
        "std_defined": std_defined,
        "min": round(min(values), 6) if n else float("nan"),
        "max": round(max(values), 6) if n else float("nan"),
    }


def _row(source: str, family: str, group: str, metric: str, summ: dict) -> dict:
    return {
        "source_table": source,
        "metric_family": family,
        "group": group,
        "metric": metric,
        **summ,
    }


def _read(name: str) -> pd.DataFrame | None:
    path = TABLES / name
    if not path.exists():
        return None
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# Extractors. Each returns (summary_rows, raw_rows).
# raw_rows are long-form: source_table, group, metric, seed, value.
# ---------------------------------------------------------------------------


def _grouped_metric(
    df: pd.DataFrame,
    source: str,
    family: str,
    group_cols: list[str],
    value_col: str,
    metric_name: str,
    seed_col: str = "seed",
) -> tuple[list[dict], list[dict]]:
    summaries: list[dict] = []
    raws: list[dict] = []
    for keys, sub in df.groupby(group_cols):
        keys_t = keys if isinstance(keys, tuple) else (keys,)
        group = "|".join(f"{c}={v}" for c, v in zip(group_cols, keys_t, strict=True))
        sub_sorted = sub.sort_values(seed_col)
        seeds = [int(s) for s in sub_sorted[seed_col].tolist()]
        values = [float(v) for v in sub_sorted[value_col].tolist()]
        if not values:
            continue
        summaries.append(_row(source, family, group, metric_name, summarize(values, seeds)))
        for s, v in zip(seeds, values, strict=True):
            raws.append(
                {
                    "source_table": source,
                    "group": group,
                    "metric": metric_name,
                    "seed": s,
                    "value": round(v, 6),
                }
            )
    return summaries, raws


def extract_full_grid() -> tuple[list[dict], list[dict]]:
    df = _read("full_grid_raw.csv")
    if df is None:
        return [], []
    # Focus on the decisive attack: compromised_signer, every defense.
    cs = df[df["attack"] == "compromised_signer"]
    return _grouped_metric(
        cs, "full_grid_raw", "detection_compromised_signer",
        ["defense"], "detected", "detection_rate",
    )


def extract_adaptive() -> tuple[list[dict], list[dict]]:
    df = _read("adaptive_attack_summary.csv")
    if df is None:
        return [], []
    cs = df[df["attack"] == "compromised_signer"]
    return _grouped_metric(
        cs, "adaptive_attack_summary", "adaptive_compromised_signer",
        ["defense"], "detected", "detection_rate",
    )


def extract_quality() -> tuple[list[dict], list[dict]]:
    df = _read("explanation_audit_quality.csv")
    if df is None:
        return [], []
    metrics = [
        "trace_complete_rate",
        "decisive_attribute_full_text_coverage_rate",
        "counterfactual_coverage_rate",
        "counterfactual_validity_rate",
        "stable_decision_reason_row_rate",
        "audit_reconstruction_rate",
    ]
    summaries: list[dict] = []
    raws: list[dict] = []
    df = df.sort_values("seed")
    seeds = [int(s) for s in df["seed"].tolist()]
    for m in metrics:
        if m not in df.columns:
            continue
        values = [float(v) for v in df[m].tolist()]
        summaries.append(
            _row(
                "explanation_audit_quality",
                "xai_audit_quality",
                "all",
                m,
                summarize(values, seeds),
            )
        )
        for s, v in zip(seeds, values, strict=True):
            raws.append(
                {"source_table": "explanation_audit_quality", "group": "all",
                 "metric": m, "seed": s, "value": round(v, 6)}
            )
    return summaries, raws


def extract_sensitivity() -> tuple[list[dict], list[dict]]:
    df = _read("nspi_compromised_signer_sensitivity_raw.csv")
    if df is None:
        return [], []
    summaries: list[dict] = []
    raws: list[dict] = []
    for metric in (
        "nspi_global_detected",
        "nspi_per_station_detected",
        "trusted_policy_oracle_detected",
    ):
        if metric not in df.columns:
            continue
        s, r = _grouped_metric(
            df, "nspi_compromised_signer_sensitivity_raw", "global_sensitivity",
            ["flip_fraction_requested"], metric, metric,
        )
        summaries.extend(s)
        raws.extend(r)
    return summaries, raws


def extract_targeted() -> tuple[list[dict], list[dict]]:
    df = _read("nspi_targeted_compromised_signer_raw.csv")
    if df is None:
        return [], []
    summaries: list[dict] = []
    raws: list[dict] = []
    for metric in (
        "nspi_per_station_detected",
        "nspi_per_district_detected",
        "trusted_policy_oracle_detected",
    ):
        if metric not in df.columns:
            continue
        s, r = _grouped_metric(
            df, "nspi_targeted_compromised_signer_raw", "targeted_sensitivity",
            ["target_scope", "flip_fraction_requested"], metric, metric,
        )
        summaries.extend(s)
        raws.extend(r)
    return summaries, raws


def extract_stress() -> tuple[list[dict], list[dict]]:
    df = _read("workload_policy_stress_raw.csv")
    if df is None:
        return [], []
    df = df[df["status"] == "ok"]
    summaries: list[dict] = []
    raws: list[dict] = []
    metrics = [
        "cs_f25_nspi_global_detect",
        "cs_f25_trusted_oracle_detect",
        "cs_f25_signed_chain_detect",
        "cs_f10_nspi_global_detect",
        "cs_f10_nspi_per_station_detect",
        "cf_validity",
        "nspi_train_accuracy",
        "runtime_seconds",
    ]
    for metric in metrics:
        if metric not in df.columns:
            continue
        s, r = _grouped_metric(
            df, "workload_policy_stress_raw", "workload_stress",
            ["arm", "num_requests"], metric, metric,
        )
        summaries.extend(s)
        raws.extend(r)
    return summaries, raws


EXTRACTORS = (
    extract_full_grid,
    extract_adaptive,
    extract_quality,
    extract_sensitivity,
    extract_targeted,
    extract_stress,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=str(TABLES))
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_summaries: list[dict] = []
    all_raws: list[dict] = []
    for extractor in EXTRACTORS:
        summaries, raws = extractor()
        all_summaries.extend(summaries)
        all_raws.extend(raws)

    if not all_summaries:
        print("No seed-level source tables found. Run the upstream scripts first.")
        return 1

    summary_df = pd.DataFrame(all_summaries)[SUMMARY_FIELDS]
    raw_df = pd.DataFrame(all_raws)
    summary_path = out_dir / "seed_confidence_summary.csv"
    raw_path = out_dir / "seed_confidence_raw.csv"
    summary_df.to_csv(summary_path, index=False)
    raw_df.to_csv(raw_path, index=False)

    n_single = int((~summary_df["std_defined"]).sum())
    print(f"Wrote {summary_path} ({len(summary_df)} metric/group rows)")
    print(f"Wrote {raw_path} ({len(raw_df)} per-seed rows)")
    print(f"metric families: {sorted(summary_df['metric_family'].unique())}")
    if n_single:
        print(f"WARNING: {n_single} rows have n_seeds<2 (std not defined, reported as 0.0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
