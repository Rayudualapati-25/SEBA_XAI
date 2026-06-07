#!/usr/bin/env python3
"""Targeted compromised-signer sensitivity for NS-PI.

The global sensitivity grid asks how much total corruption is required
before NS-PI fires. This script asks a different reviewer question:

    "If a compromised signer attacks one station or district, does grouped
    drift catch the local shift even when global drift may be weak?"

Outputs:
    results/tables/nspi_targeted_compromised_signer_raw.csv
    results/tables/nspi_targeted_compromised_signer_summary.csv
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from seba.attacks.base import AttackResult, EventLog, copy_log, to_log
from seba.baselines import TrustedRawPolicyOracle
from seba.nspi import learn_policy
from seba.nspi.drift import drift_test, per_group_drift
from seba.nspi.learner import predict_with_policy
from seba.scoring.grid import discover_seeds, load_event_log

OUT_DIR = Path(__file__).resolve().parents[1] / "results" / "tables"
FLIP_FRACTIONS = (0.10, 0.25, 0.50, 0.75, 1.00)
SCOPES = ("station", "district")
CLASSES = ("allow", "deny", "escalate")


def _request_to_district(labeled: pd.DataFrame) -> dict[str, str]:
    return {
        str(row["request_id"]): str(row["requester_district_id"])
        for _, row in labeled.iterrows()
    }


def _group_ids_for_scope(
    clean_log: EventLog, labeled: pd.DataFrame, scope: str
) -> list[str]:
    if scope == "station":
        return [str(row.get("requester_station_id", "")) for row in clean_log]
    if scope == "district":
        district_by_request = _request_to_district(labeled)
        return [
            district_by_request.get(str(row.get("request_id", "")), "")
            for row in clean_log
        ]
    raise ValueError(f"unknown target scope: {scope}")


def _eligible_indices_by_group(
    clean_log: EventLog, group_ids: Sequence[str]
) -> dict[str, list[int]]:
    eligible: dict[str, list[int]] = {}
    for idx, (row, group_id) in enumerate(zip(clean_log, group_ids, strict=True)):
        if str(row.get("decision", "")).lower() in {"deny", "escalate"}:
            eligible.setdefault(group_id, []).append(idx)
    return eligible


def _choose_target_group(clean_log: EventLog, group_ids: Sequence[str]) -> str:
    eligible = _eligible_indices_by_group(clean_log, group_ids)
    if not eligible:
        return ""
    return max(eligible, key=lambda group_id: len(eligible[group_id]))


def _targeted_compromised_signer(
    clean_log: EventLog,
    group_ids: Sequence[str],
    target_group: str,
    rng: Any,
    *,
    flip_fraction: float,
) -> AttackResult:
    rows = copy_log(clean_log)
    eligible = [
        idx
        for idx, (row, group_id) in enumerate(zip(rows, group_ids, strict=True))
        if group_id == target_group
        and str(row.get("decision", "")).lower() in {"deny", "escalate"}
    ]
    if not eligible:
        return AttackResult(
            name="targeted_compromised_signer",
            severity=5,
            perturbed_log=to_log(rows),
            affected_indices=(),
            meta={"target_group": target_group, "flip_fraction": flip_fraction},
        )

    n_flip = max(1, int(len(eligible) * flip_fraction))
    chosen = rng.choice(eligible, size=n_flip, replace=False)
    affected: list[int] = []
    for raw_idx in chosen:
        idx = int(raw_idx)
        rows[idx]["decision"] = "allow"
        rows[idx]["primary_reason_code"] = "ALLOW_COMPROMISED_SIGNER_OVERRIDE"
        rows[idx]["__attack_compromised_signer__"] = True
        rows[idx]["__attack_target_group__"] = target_group
        rows[idx]["__attack_resigned_valid__"] = True
        rows[idx]["__attack_policy_output_compromised__"] = True
        affected.append(idx)

    return AttackResult(
        name="targeted_compromised_signer",
        severity=5,
        perturbed_log=to_log(rows),
        affected_indices=tuple(sorted(affected)),
        meta={
            "target_group": target_group,
            "eligible_in_group": len(eligible),
            "n_flipped": len(affected),
            "flip_fraction": flip_fraction,
            "resigned_valid": True,
            "policy_output_compromised": True,
        },
    )


def _group_alarm(
    clean_pred: list[str],
    perturbed_decisions: list[str],
    group_ids: list[str],
    seed: int,
) -> tuple[bool, int, int, str, float, float]:
    by_group_clean: dict[str, list[str]] = {}
    by_group_perturbed: dict[str, list[str]] = {}
    for group_id, decision in zip(group_ids, clean_pred, strict=True):
        by_group_clean.setdefault(group_id, []).append(decision)
    for group_id, decision in zip(group_ids, perturbed_decisions, strict=True):
        by_group_perturbed.setdefault(group_id, []).append(decision)

    reports = per_group_drift(
        by_group_clean,
        by_group_perturbed,
        classes=CLASSES,
        permutations=200,
        alpha=0.05,
        rng_seed=seed,
    )
    alarms = [report for report in reports if report.alarm]
    strongest = max(reports, key=lambda report: report.observed_divergence)
    return (
        bool(alarms),
        len(alarms),
        len(reports),
        strongest.partition,
        strongest.observed_divergence,
        strongest.p_value,
    )


def evaluate_targeted_sensitivity() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for assets in discover_seeds():
        clean_log = load_event_log(assets.signed_log_csv)
        labeled = pd.read_csv(assets.labeled_requests_csv)
        policy = learn_policy(labeled, max_depth=8, min_samples_leaf=10)
        clean_pred = predict_with_policy(policy, labeled).tolist()
        trusted_oracle = TrustedRawPolicyOracle.from_records(
            labeled.to_dict(orient="records")
        )

        station_group_ids = _group_ids_for_scope(clean_log, labeled, "station")
        district_group_ids = _group_ids_for_scope(clean_log, labeled, "district")

        for target_scope in SCOPES:
            target_group_ids = (
                station_group_ids if target_scope == "station" else district_group_ids
            )
            target_group = _choose_target_group(clean_log, target_group_ids)
            eligible = _eligible_indices_by_group(clean_log, target_group_ids).get(
                target_group, []
            )
            for flip_fraction in FLIP_FRACTIONS:
                rng_seed = assets.seed + int(flip_fraction * 1000)
                result = _targeted_compromised_signer(
                    clean_log,
                    target_group_ids,
                    target_group,
                    np.random.default_rng(rng_seed),
                    flip_fraction=flip_fraction,
                )
                perturbed_decisions = [
                    str(row.get("decision", "")) for row in result.perturbed_log
                ]
                global_report = drift_test(
                    clean_pred,
                    perturbed_decisions,
                    classes=CLASSES,
                    permutations=200,
                    alpha=0.05,
                    rng_seed=assets.seed,
                )
                (
                    station_alarm,
                    station_alarms,
                    stations_evaluated,
                    strongest_station,
                    strongest_station_js,
                    strongest_station_p,
                ) = _group_alarm(
                    clean_pred,
                    perturbed_decisions,
                    station_group_ids,
                    assets.seed,
                )
                (
                    district_alarm,
                    district_alarms,
                    districts_evaluated,
                    strongest_district,
                    strongest_district_js,
                    strongest_district_p,
                ) = _group_alarm(
                    clean_pred,
                    perturbed_decisions,
                    district_group_ids,
                    assets.seed,
                )
                rows.append(
                    {
                        "seed": assets.seed,
                        "target_scope": target_scope,
                        "target_group": target_group,
                        "target_group_eligible": len(eligible),
                        "flip_fraction_requested": flip_fraction,
                        "n_flipped": len(result.affected_indices),
                        "global_flip_fraction_actual": len(result.affected_indices)
                        / len(clean_log),
                        "target_flip_fraction_actual": len(result.affected_indices)
                        / max(1, len(eligible)),
                        "nspi_global_detected": int(global_report.alarm),
                        "nspi_global_js": global_report.observed_divergence,
                        "nspi_global_p": global_report.p_value,
                        "nspi_per_station_detected": int(station_alarm),
                        "stations_flagged": station_alarms,
                        "stations_evaluated": stations_evaluated,
                        "strongest_station": strongest_station,
                        "strongest_station_js": strongest_station_js,
                        "strongest_station_p": strongest_station_p,
                        "nspi_per_district_detected": int(district_alarm),
                        "districts_flagged": district_alarms,
                        "districts_evaluated": districts_evaluated,
                        "strongest_district": strongest_district,
                        "strongest_district_js": strongest_district_js,
                        "strongest_district_p": strongest_district_p,
                        "nspi_any_detected": int(
                            global_report.alarm or station_alarm or district_alarm
                        ),
                        "trusted_policy_oracle_detected": int(
                            trusted_oracle.detect(result.perturbed_log, clean_log)
                        ),
                    }
                )
    return pd.DataFrame(rows)


def summarize(raw: pd.DataFrame) -> pd.DataFrame:
    return (
        raw.groupby(["target_scope", "flip_fraction_requested"])
        .agg(
            n_seeds=("seed", "nunique"),
            mean_target_group_eligible=("target_group_eligible", "mean"),
            mean_n_flipped=("n_flipped", "mean"),
            mean_global_flip_fraction=("global_flip_fraction_actual", "mean"),
            nspi_global_detection_rate=("nspi_global_detected", "mean"),
            nspi_per_station_detection_rate=("nspi_per_station_detected", "mean"),
            nspi_per_district_detection_rate=("nspi_per_district_detected", "mean"),
            nspi_any_detection_rate=("nspi_any_detected", "mean"),
            trusted_oracle_detection_rate=("trusted_policy_oracle_detected", "mean"),
            mean_strongest_station_js=("strongest_station_js", "mean"),
            mean_strongest_district_js=("strongest_district_js", "mean"),
        )
        .reset_index()
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = evaluate_targeted_sensitivity()
    summary = summarize(raw)

    raw_path = OUT_DIR / "nspi_targeted_compromised_signer_raw.csv"
    summary_path = OUT_DIR / "nspi_targeted_compromised_signer_summary.csv"
    raw.to_csv(raw_path, index=False)
    summary.to_csv(summary_path, index=False)
    print(f"wrote {raw_path} ({len(raw)} rows)")
    print(f"wrote {summary_path} ({len(summary)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
