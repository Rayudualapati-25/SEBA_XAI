#!/usr/bin/env python3
"""Workload and policy-mix stress test for SEBA-XAI.

Reviewer question this answers:

    Do the SEBA-XAI results (especially the compromised_signer asymmetry and
    the NS-PI drift behaviour) survive changes in workload size and in the
    sensitive-record / cross-jurisdiction / revoked-credential / approval
    policy mix, or are they only true for the single 1000-request synthetic
    setting?

Design (honest about what is and is not a real knob):

- Workload SIZE is varied with the generator's real ``--num-requests`` CLI
  argument: 500, 1000, 2500, 5000.
- Policy MIX is varied by overriding the generator's module-level
  ``SCENARIO_WEIGHTS`` in-process before calling its ``main()``. This re-runs
  the *real, tested* generation logic with a different, explicitly documented
  scenario-weight vector. It does NOT fabricate rows. The generator does not
  expose per-ratio CLI flags, so scenario weights are the honest proxy:
    * cross_jurisdiction ratio  <- weight of ``cross_jurisdiction_sensitive``
    * revoked-credential ratio  <- weight of ``revoked_credential``
    * approval missing/invalid  <- weight of ``expired_approval_token``
    * classified-record ratio   <- INDIRECT proxy: boosting the sensitive
                                   scenarios (cross-jurisdiction, juvenile,
                                   sealed) raises the classified share. This
                                   is an indirect knob and is reported as the
                                   realized ratio so the effect is visible.

Each cell reports the *realized* ratios measured from the generated workload,
so the reader can confirm the knob actually moved the distribution rather than
trusting the intended weight.

Metrics per cell:
- decision base rates (allow/deny/escalate)
- realized policy-mix ratios
- compromised_signer detection at flip 0.25 and 0.10 by:
    signed_chain (expected 0 = blind by construction),
    NS-PI global drift, NS-PI per-station drift, trusted raw-attribute oracle
- counterfactual coverage and validity on deny/escalate rows
- NS-PI learner train accuracy (does the rule learner still fit at this size)
- wall-clock runtime

Determinism: every cell uses a fixed integer seed. Intermediate per-cell run
directories under prototype/runs/ are deleted after metrics are extracted so
the repo is not polluted; only the result tables persist.

Outputs:
- results/tables/workload_policy_stress_raw.csv     (one row per cell)
- results/tables/workload_policy_stress_summary.csv (aggregated per arm/size)
"""

from __future__ import annotations

import argparse
import csv
import importlib
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "prototype" / "synthetic_access_sim"
RUNS_DIR = REPO_ROOT / "prototype" / "runs"
OUT_DIR = REPO_ROOT / "results" / "tables"

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(REPO_ROOT / "src"))

from seba.attacks.compromised_signer import compromised_signer  # noqa: E402
from seba.baselines.trusted_oracle import TrustedRawPolicyOracle  # noqa: E402
from seba.nspi.counterfactual import explain_request  # noqa: E402
from seba.nspi.drift import drift_test, per_group_drift  # noqa: E402
from seba.nspi.learner import learn_policy, predict_with_policy  # noqa: E402
from seba.scoring.detectors import signed_chain_detector  # noqa: E402

CLASSES = ("allow", "deny", "escalate")
DEFAULT_SEEDS = (7, 21, 42, 99, 123)
DEFAULT_SIZES = (500, 1000, 2500, 5000)

# Baseline scenario weights (must match generate_synthetic_requests.SCENARIO_WEIGHTS).
# Order: normal, cross_jurisdiction, revoked, stale, juvenile, emergency,
#        court, sealed, expired_approval, random.
BASELINE_WEIGHTS = [20, 14, 8, 10, 9, 8, 8, 8, 7, 8]

# Policy-mix arms: each overrides the scenario weight vector.
MIX_ARMS = {
    "baseline": BASELINE_WEIGHTS,
    "high_cross_jurisdiction": [20, 40, 8, 10, 9, 8, 8, 8, 7, 8],
    "high_revoked_credential": [20, 14, 30, 10, 9, 8, 8, 8, 7, 8],
    "high_approval_missing": [20, 14, 8, 10, 9, 8, 8, 8, 30, 8],
    "high_classified_proxy": [10, 30, 8, 8, 25, 8, 8, 25, 7, 8],
}

CF_SAMPLE_CAP = 150  # cap deny/escalate rows scanned for counterfactual validity


# ---------------------------------------------------------------------------
# Workload generation + labelling pipeline (reuses the prototype scripts).
# ---------------------------------------------------------------------------


def _generate_workload(run_id: str, seed: int, num_requests: int, weights: list[int]) -> None:
    """Generate a synthetic workload in-process with overridden scenario weights."""

    gen = importlib.import_module("generate_synthetic_requests")
    original = list(gen.SCENARIO_WEIGHTS)
    saved_argv = sys.argv
    try:
        gen.SCENARIO_WEIGHTS = list(weights)
        sys.argv = [
            "generate_synthetic_requests.py",
            "--run-id",
            run_id,
            "--seed",
            str(seed),
            "--num-requests",
            str(num_requests),
        ]
        gen.main()
    finally:
        gen.SCENARIO_WEIGHTS = original
        sys.argv = saved_argv


def _run_step(script: str, input_run_id: str, run_id: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(SIM_DIR / script),
            "--input-run-id",
            input_run_id,
            "--run-id",
            run_id,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _load_event_log(path: Path) -> tuple[dict, ...]:
    df = pd.read_csv(path)
    return tuple(df.to_dict(orient="records"))


# ---------------------------------------------------------------------------
# Per-cell metric computation.
# ---------------------------------------------------------------------------


def _realized_ratios(labeled: pd.DataFrame) -> dict[str, float]:
    n = len(labeled) or 1

    def frac(mask: pd.Series) -> float:
        return float(mask.sum()) / n

    sens = labeled["record_sensitivity_level"].astype(str)
    cred = labeled["requester_credential_status"].astype(str)
    approval = labeled["approval_token_status"].astype(str)
    crossj = labeled["cross_jurisdiction"].astype(str).str.lower()
    decision = labeled["decision"].astype(str)
    return {
        "classified_ratio": frac(sens == "CLASSIFIED"),
        "high_or_classified_ratio": frac(sens.isin(["HIGH", "CLASSIFIED"])),
        "cross_jurisdiction_ratio": frac(crossj == "true"),
        "revoked_credential_ratio": frac(cred == "REVOKED"),
        "approval_missing_ratio": frac(~approval.isin(["NOT_REQUIRED", "PRESENT_VALID"])),
        "allow_rate": frac(decision == "allow"),
        "deny_rate": frac(decision == "deny"),
        "escalate_rate": frac(decision == "escalate"),
    }


def _compromised_signer_metrics(
    clean_log: tuple[dict, ...],
    clean_pred: list[str],
    station_ids: list[str],
    labeled: pd.DataFrame,
    seed: int,
    flip_fraction: float,
) -> dict[str, int]:
    rng = np.random.default_rng(seed)
    res = compromised_signer(clean_log, rng, flip_fraction=flip_fraction)
    perturbed_decisions = [str(r.get("decision", "")) for r in res.perturbed_log]

    # NS-PI global drift: clean learned predictions vs perturbed observed decisions.
    global_report = drift_test(
        clean_pred,
        perturbed_decisions,
        classes=CLASSES,
        permutations=200,
        alpha=0.05,
        rng_seed=seed,
    )

    # NS-PI per-station drift.
    clean_by_station: dict[str, list[str]] = {}
    pert_by_station: dict[str, list[str]] = {}
    for station, cp, pp in zip(station_ids, clean_pred, perturbed_decisions, strict=False):
        clean_by_station.setdefault(station, []).append(cp)
        pert_by_station.setdefault(station, []).append(pp)
    station_reports = per_group_drift(
        clean_by_station,
        pert_by_station,
        classes=CLASSES,
        permutations=200,
        alpha=0.05,
        rng_seed=seed,
    )
    per_station_alarm = int(any(r.alarm for r in station_reports))

    # Cryptographic sanity (should be blind by construction).
    signed_detect = int(signed_chain_detector(res.perturbed_log, clean_log))

    # Trusted raw-attribute oracle (independent uncompromised request view).
    oracle = TrustedRawPolicyOracle.from_records(labeled.to_dict(orient="records"))
    oracle_detect = int(oracle.detect(res.perturbed_log, clean_log))

    return {
        "signed_chain_detect": signed_detect,
        "nspi_global_detect": int(global_report.alarm),
        "nspi_per_station_detect": per_station_alarm,
        "trusted_oracle_detect": oracle_detect,
        "n_flipped": len(res.affected_indices),
        "global_js_divergence": round(float(global_report.observed_divergence), 6),
    }


def _counterfactual_metrics(policy, labeled: pd.DataFrame) -> dict[str, float]:
    target_idx = labeled.index[labeled["decision"].isin(["deny", "escalate"])].tolist()
    if not target_idx:
        return {"cf_coverage": 0.0, "cf_validity": 0.0, "cf_sampled": 0}

    sample = target_idx[:CF_SAMPLE_CAP]
    covered = 0
    valid = 0
    for idx in sample:
        cf = explain_request(policy, labeled, request_index=int(idx), max_edits=3)
        if cf is None or not cf.edits:
            continue
        covered += 1
        # Replay: apply edits to a 1-row copy, re-predict with learned policy.
        # Cast to object first so string edits never trip pandas dtype warnings
        # when the source column was inferred as bool/numeric.
        row = labeled.loc[[idx]].copy().astype(object)
        for attr, value in cf.edits:
            if attr in row.columns:
                row.at[idx, attr] = value
        pred = predict_with_policy(policy, row)
        if len(pred) and str(pred[0]) == "allow":
            valid += 1

    coverage = covered / len(sample) if sample else 0.0
    validity = valid / covered if covered else 0.0
    return {
        "cf_coverage": round(coverage, 4),
        "cf_validity": round(validity, 4),
        "cf_sampled": len(sample),
    }


def run_cell(arm: str, num_requests: int, weights: list[int], seed: int) -> dict:
    tag = f"zz_stress_{arm}_n{num_requests}_s{seed}"
    s1 = f"{tag}_step1"
    s2 = f"{tag}_step2"
    s3 = f"{tag}_step3"
    start = time.perf_counter()
    row: dict[str, object] = {
        "arm": arm,
        "num_requests": num_requests,
        "seed": seed,
        "status": "ok",
    }
    try:
        _generate_workload(s1, seed, num_requests, weights)
        _run_step("policy_oracle.py", s1, s2)
        _run_step("audit_baseline.py", s2, s3)

        labeled = pd.read_csv(RUNS_DIR / s2 / "artifacts" / "labeled_access_requests.csv")
        clean_log = _load_event_log(RUNS_DIR / s3 / "artifacts" / "signed_hash_chain_log.csv")

        row.update(_realized_ratios(labeled))

        policy = learn_policy(labeled, max_depth=8, min_samples_leaf=10)
        clean_pred = [str(x) for x in predict_with_policy(policy, labeled)]
        truth = labeled["decision"].astype(str).tolist()
        matches = [p == d for p, d in zip(clean_pred, truth, strict=True)]
        row["nspi_train_accuracy"] = round(float(np.mean(matches)), 4)

        station_ids = [str(r.get("requester_station_id", "")) for r in clean_log]
        for f in (0.25, 0.10):
            m = _compromised_signer_metrics(
                clean_log, clean_pred, station_ids, labeled, seed, f
            )
            suffix = f"f{int(f * 100):02d}"
            for k, v in m.items():
                row[f"cs_{suffix}_{k}"] = v

        row.update(_counterfactual_metrics(policy, labeled))
        row["n_stations"] = len({s for s in station_ids if s})
    except Exception as exc:  # noqa: BLE001 - record failure, keep matrix going
        row["status"] = f"error: {type(exc).__name__}: {exc}"
    finally:
        for run_id in (s1, s2, s3):
            shutil.rmtree(RUNS_DIR / run_id, ignore_errors=True)
        row["runtime_seconds"] = round(time.perf_counter() - start, 2)
    return row


# ---------------------------------------------------------------------------
# Matrix driver + aggregation.
# ---------------------------------------------------------------------------


def build_matrix(
    seeds: tuple[int, ...], sizes: tuple[int, ...]
) -> list[tuple[str, int, list[int], int]]:
    cells: list[tuple[str, int, list[int], int]] = []
    # Size arm: baseline mix, vary num_requests.
    for size in sizes:
        for seed in seeds:
            cells.append(("size_baseline", size, BASELINE_WEIGHTS, seed))
    # Mix arm: vary scenario weights at N=1000.
    for arm, weights in MIX_ARMS.items():
        if arm == "baseline":
            continue  # already covered by size arm at N=1000
        for seed in seeds:
            cells.append((f"mix_{arm}", 1000, weights, seed))
    return cells


def aggregate(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame([r for r in rows if r.get("status") == "ok"])
    if df.empty:
        return pd.DataFrame()
    metric_cols = [
        "classified_ratio",
        "cross_jurisdiction_ratio",
        "revoked_credential_ratio",
        "approval_missing_ratio",
        "allow_rate",
        "deny_rate",
        "escalate_rate",
        "nspi_train_accuracy",
        "cs_f25_signed_chain_detect",
        "cs_f25_nspi_global_detect",
        "cs_f25_nspi_per_station_detect",
        "cs_f25_trusted_oracle_detect",
        "cs_f10_nspi_global_detect",
        "cs_f10_nspi_per_station_detect",
        "cs_f10_trusted_oracle_detect",
        "cf_coverage",
        "cf_validity",
        "runtime_seconds",
    ]
    present = [c for c in metric_cols if c in df.columns]
    grouped = (
        df.groupby(["arm", "num_requests"])[present]
        .mean()
        .reset_index()
        .sort_values(["arm", "num_requests"])
    )
    grouped["n_seeds"] = (
        df.groupby(["arm", "num_requests"])["seed"].nunique().reset_index(drop=True)
    )
    return grouped.round(4)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    for r in rows:
        for k in r:
            if k not in fieldnames:
                fieldnames.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--sizes", type=int, nargs="+", default=list(DEFAULT_SIZES))
    parser.add_argument(
        "--max-size",
        type=int,
        default=5000,
        help="Drop size-arm cells above this (set 2500 if 5000 is too slow).",
    )
    args = parser.parse_args()

    sizes = tuple(s for s in args.sizes if s <= args.max_size)
    seeds = tuple(args.seeds)
    cells = build_matrix(seeds, sizes)

    print(f"Running {len(cells)} stress cells (seeds={seeds}, sizes={sizes})")
    rows: list[dict] = []
    for i, (arm, size, weights, seed) in enumerate(cells, 1):
        row = run_cell(arm, size, weights, seed)
        rows.append(row)
        print(
            f"  [{i}/{len(cells)}] {arm} n={size} seed={seed} "
            f"status={row['status']} runtime={row.get('runtime_seconds')}s"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = OUT_DIR / "workload_policy_stress_raw.csv"
    summary_path = OUT_DIR / "workload_policy_stress_summary.csv"
    write_csv(raw_path, rows)
    summary = aggregate(rows)
    if not summary.empty:
        summary.to_csv(summary_path, index=False)

    n_ok = sum(1 for r in rows if r.get("status") == "ok")
    print(f"\nDone: {n_ok}/{len(rows)} cells ok")
    print(f"  raw     -> {raw_path}")
    print(f"  summary -> {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
