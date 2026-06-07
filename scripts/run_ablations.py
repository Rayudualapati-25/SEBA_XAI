#!/usr/bin/env python3
"""Adaptive-attack + ablation evaluation for NS-PI.

Produces:
    results/tables/adaptive_attack_summary.csv
        Per (seed, attack, defense, scope) detection outcome under the two
        adaptive attacks in ``seba.attacks.adaptive``.

    results/tables/nspi_ablation.csv
        NS-PI ablation: drift only / counterfactual only / full pipeline
        on a held-out seed split (seeds 7, 21, 42 = train; 99, 123 = test).

The point of these tables is to show explicit failure modes — a paper with
no failure-mode table gets rejected for overclaiming.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from seba.attacks.adaptive import ADAPTIVE_ATTACKS
from seba.baselines import ct_log_detector, fabric_abac_detector
from seba.nspi import learn_policy
from seba.nspi.drift import drift_test, per_group_drift
from seba.nspi.learner import predict_with_policy
from seba.scoring.detectors import (
    abac_reexecution_detector,
    quorum_chain_detector,
    signed_chain_detector,
)
from seba.scoring.grid import discover_seeds, load_event_log


OUT_DIR = Path(__file__).resolve().parents[1] / "results" / "tables"


def _global_alarm(clean_pred, perturbed_decisions, seed: int) -> tuple[bool, float, float]:
    report = drift_test(
        clean_pred,
        perturbed_decisions,
        classes=("allow", "deny", "escalate"),
        permutations=200,
        alpha=0.05,
        rng_seed=seed,
    )
    return report.alarm, report.observed_divergence, report.p_value


def _per_station_alarm(
    clean_pred, perturbed_decisions, station_ids, seed: int
) -> tuple[bool, int, int]:
    by_station_clean: dict[str, list[str]] = {}
    by_station_perturbed: dict[str, list[str]] = {}
    for s, p in zip(station_ids, clean_pred):
        by_station_clean.setdefault(s, []).append(p)
    for s, p in zip(station_ids, perturbed_decisions):
        by_station_perturbed.setdefault(s, []).append(p)
    reports = per_group_drift(
        by_station_clean,
        by_station_perturbed,
        classes=("allow", "deny", "escalate"),
        permutations=200,
        alpha=0.05,
        rng_seed=seed,
    )
    alarms_raised = sum(1 for r in reports if r.alarm)
    return alarms_raised > 0, alarms_raised, len(reports)


def evaluate_adaptive() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for assets in discover_seeds():
        clean_log = load_event_log(assets.signed_log_csv)
        labeled = pd.read_csv(assets.labeled_requests_csv)
        policy = learn_policy(labeled, max_depth=8, min_samples_leaf=10)
        clean_pred = predict_with_policy(policy, labeled).tolist()
        station_ids = [str(r.get("requester_station_id", "")) for r in clean_log]
        rng = np.random.default_rng(assets.seed)

        for attack in ADAPTIVE_ATTACKS:
            result = attack(clean_log, rng)
            perturbed_decisions = [str(r.get("decision", "")) for r in result.perturbed_log]
            # Cryptographic defenses (all should detect because hashes break).
            crypto_detects = {
                "signed_chain": signed_chain_detector(result.perturbed_log, clean_log),
                "blockchain_style": quorum_chain_detector(result.perturbed_log, clean_log),
                "ct_log": ct_log_detector(result.perturbed_log, clean_log),
                "fabric_abac": fabric_abac_detector(result.perturbed_log, clean_log),
                "abac_reexec": abac_reexecution_detector(result.perturbed_log, clean_log),
            }
            global_alarm, global_div, global_p = _global_alarm(
                clean_pred, perturbed_decisions, assets.seed
            )
            per_alarm, per_count, total_groups = _per_station_alarm(
                clean_pred, perturbed_decisions, station_ids, assets.seed
            )
            for name, hit in crypto_detects.items():
                rows.append(
                    {
                        "seed": assets.seed,
                        "attack": attack.name,
                        "severity": attack.severity,
                        "defense": name,
                        "scope": "log-integrity",
                        "detected": int(bool(hit)),
                    }
                )
            rows.append(
                {
                    "seed": assets.seed,
                    "attack": attack.name,
                    "severity": attack.severity,
                    "defense": "nspi_drift_global",
                    "scope": "policy-distribution",
                    "detected": int(global_alarm),
                    "js_divergence": global_div,
                    "p_value": global_p,
                }
            )
            rows.append(
                {
                    "seed": assets.seed,
                    "attack": attack.name,
                    "severity": attack.severity,
                    "defense": "nspi_drift_per_station",
                    "scope": "policy-distribution",
                    "detected": int(per_alarm),
                    "stations_flagged": per_count,
                    "stations_evaluated": total_groups,
                }
            )
    return pd.DataFrame(rows)


def evaluate_nspi_ablation() -> pd.DataFrame:
    """Train/test split across seeds.

    Train on {7, 21, 42}, test on {99, 123}. For each test seed, learn the
    policy on the *clean* train data and apply NS-PI alarms on the test
    seed perturbed under the adaptive attacks. Ablate by enabling/disabling
    drift_global vs drift_per_station.
    """

    seeds = {a.seed: a for a in discover_seeds()}
    train_seeds = [s for s in (7, 21, 42) if s in seeds]
    test_seeds = [s for s in (99, 123) if s in seeds]
    if not train_seeds or not test_seeds:
        return pd.DataFrame()

    train_frames = []
    for s in train_seeds:
        train_frames.append(pd.read_csv(seeds[s].labeled_requests_csv))
    train_df = pd.concat(train_frames, ignore_index=True)
    policy = learn_policy(train_df, max_depth=8, min_samples_leaf=20)

    rows: list[dict[str, object]] = []
    for s in test_seeds:
        assets = seeds[s]
        clean_log = load_event_log(assets.signed_log_csv)
        labeled = pd.read_csv(assets.labeled_requests_csv)
        clean_pred = predict_with_policy(policy, labeled).tolist()
        station_ids = [str(r.get("requester_station_id", "")) for r in clean_log]
        rng = np.random.default_rng(s)

        for attack in ADAPTIVE_ATTACKS:
            result = attack(clean_log, rng)
            perturbed_decisions = [str(r.get("decision", "")) for r in result.perturbed_log]
            global_alarm, global_div, _ = _global_alarm(clean_pred, perturbed_decisions, s)
            per_alarm, per_count, total = _per_station_alarm(
                clean_pred, perturbed_decisions, station_ids, s
            )
            for variant_name, detected in (
                ("drift_global_only", global_alarm),
                ("drift_per_station_only", per_alarm),
                ("nspi_full_drift", global_alarm or per_alarm),
            ):
                rows.append(
                    {
                        "test_seed": s,
                        "attack": attack.name,
                        "variant": variant_name,
                        "detected": int(detected),
                        "global_divergence": global_div,
                        "stations_flagged": per_count,
                        "stations_evaluated": total,
                    }
                )
    return pd.DataFrame(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    adaptive = evaluate_adaptive()
    adaptive_path = OUT_DIR / "adaptive_attack_summary.csv"
    adaptive.to_csv(adaptive_path, index=False)
    print(f"wrote {adaptive_path} ({len(adaptive)} rows)")

    ablation = evaluate_nspi_ablation()
    ablation_path = OUT_DIR / "nspi_ablation.csv"
    ablation.to_csv(ablation_path, index=False)
    print(f"wrote {ablation_path} ({len(ablation)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
