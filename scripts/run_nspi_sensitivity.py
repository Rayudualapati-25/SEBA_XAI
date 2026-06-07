#!/usr/bin/env python3
"""Sensitivity grid for NS-PI under compromised-signer corruption.

This script varies the compromised-signer flip fraction while keeping the
same five seed artifacts. It answers the reviewer question:

    "Does NS-PI only work when the attack is large, or does it also detect
    smaller policy-output corruption?"

Outputs:
    results/tables/nspi_compromised_signer_sensitivity_raw.csv
    results/tables/nspi_compromised_signer_sensitivity_summary.csv
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from seba.attacks.compromised_signer import compromised_signer
from seba.baselines import TrustedRawPolicyOracle
from seba.nspi import learn_policy
from seba.nspi.drift import drift_test, per_group_drift
from seba.nspi.learner import predict_with_policy
from seba.scoring.grid import discover_seeds, load_event_log

OUT_DIR = Path(__file__).resolve().parents[1] / "results" / "tables"
FLIP_FRACTIONS = (0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.35, 0.50)


def _per_station_alarm(
    clean_pred: list[str],
    perturbed_decisions: list[str],
    station_ids: list[str],
    seed: int,
) -> tuple[bool, int, int]:
    by_station_clean: dict[str, list[str]] = {}
    by_station_perturbed: dict[str, list[str]] = {}
    for station, decision in zip(station_ids, clean_pred, strict=True):
        by_station_clean.setdefault(station, []).append(decision)
    for station, decision in zip(station_ids, perturbed_decisions, strict=True):
        by_station_perturbed.setdefault(station, []).append(decision)

    reports = per_group_drift(
        by_station_clean,
        by_station_perturbed,
        classes=("allow", "deny", "escalate"),
        permutations=200,
        alpha=0.05,
        rng_seed=seed,
    )
    alarms = sum(1 for report in reports if report.alarm)
    return alarms > 0, alarms, len(reports)


def evaluate_sensitivity() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for assets in discover_seeds():
        clean_log = load_event_log(assets.signed_log_csv)
        labeled = pd.read_csv(assets.labeled_requests_csv)
        policy = learn_policy(labeled, max_depth=8, min_samples_leaf=10)
        clean_pred = predict_with_policy(policy, labeled).tolist()
        clean_decisions = [str(row.get("decision", "")) for row in clean_log]
        station_ids = [str(row.get("requester_station_id", "")) for row in clean_log]
        trusted_oracle = TrustedRawPolicyOracle.from_records(
            labeled.to_dict(orient="records")
        )

        for flip_fraction in FLIP_FRACTIONS:
            rng = np.random.default_rng(assets.seed)
            result = compromised_signer(
                clean_log,
                rng,
                flip_fraction=flip_fraction,
            )
            perturbed_decisions = [
                str(row.get("decision", "")) for row in result.perturbed_log
            ]
            global_report = drift_test(
                clean_pred,
                perturbed_decisions,
                classes=("allow", "deny", "escalate"),
                permutations=200,
                alpha=0.05,
                rng_seed=assets.seed,
            )
            per_alarm, stations_flagged, stations_evaluated = _per_station_alarm(
                clean_pred,
                perturbed_decisions,
                station_ids,
                assets.seed,
            )
            clean_log_allow_rate = clean_decisions.count("allow") / len(clean_decisions)
            reference_policy_allow_rate = clean_pred.count("allow") / len(clean_pred)
            perturbed_allow_rate = perturbed_decisions.count("allow") / len(
                perturbed_decisions
            )
            rows.append(
                {
                    "seed": assets.seed,
                    "flip_fraction_requested": flip_fraction,
                    "n_flipped": len(result.affected_indices),
                    "flip_fraction_actual": len(result.affected_indices)
                    / len(clean_log),
                    "clean_log_allow_rate": clean_log_allow_rate,
                    "reference_policy_allow_rate": reference_policy_allow_rate,
                    "perturbed_allow_rate": perturbed_allow_rate,
                    "allow_rate_delta_vs_clean_log": perturbed_allow_rate
                    - clean_log_allow_rate,
                    "allow_rate_delta_vs_reference": perturbed_allow_rate
                    - reference_policy_allow_rate,
                    "nspi_global_detected": int(global_report.alarm),
                    "nspi_global_js": global_report.observed_divergence,
                    "nspi_global_p": global_report.p_value,
                    "nspi_per_station_detected": int(per_alarm),
                    "stations_flagged": stations_flagged,
                    "stations_evaluated": stations_evaluated,
                    "nspi_any_detected": int(global_report.alarm or per_alarm),
                    "trusted_policy_oracle_detected": int(
                        trusted_oracle.detect(result.perturbed_log, clean_log)
                    ),
                }
            )
    return pd.DataFrame(rows)


def summarize(raw: pd.DataFrame) -> pd.DataFrame:
    return (
        raw.groupby("flip_fraction_requested")
        .agg(
            n_seeds=("seed", "nunique"),
            mean_n_flipped=("n_flipped", "mean"),
            mean_allow_rate_delta_vs_clean_log=(
                "allow_rate_delta_vs_clean_log",
                "mean",
            ),
            mean_allow_rate_delta_vs_reference=(
                "allow_rate_delta_vs_reference",
                "mean",
            ),
            nspi_global_detection_rate=("nspi_global_detected", "mean"),
            nspi_per_station_detection_rate=("nspi_per_station_detected", "mean"),
            nspi_any_detection_rate=("nspi_any_detected", "mean"),
            trusted_oracle_detection_rate=("trusted_policy_oracle_detected", "mean"),
            mean_global_js=("nspi_global_js", "mean"),
            mean_stations_flagged=("stations_flagged", "mean"),
        )
        .reset_index()
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = evaluate_sensitivity()
    summary = summarize(raw)

    raw_path = OUT_DIR / "nspi_compromised_signer_sensitivity_raw.csv"
    summary_path = OUT_DIR / "nspi_compromised_signer_sensitivity_summary.csv"
    raw.to_csv(raw_path, index=False)
    summary.to_csv(summary_path, index=False)
    print(f"wrote {raw_path} ({len(raw)} rows)")
    print(f"wrote {summary_path} ({len(summary)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
