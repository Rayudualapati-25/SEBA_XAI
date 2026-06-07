"""Full evaluation grid: every (defense, attack, seed) cell.

This is the harness used by ``scripts/run_full_grid.py``. It runs all
catalog attacks against all registered defenses across all available
multi-seed audit logs, producing one long CSV row per cell.

Defenses included:
    mutable_log        Step 3 mutable centralized log.
    signed_chain       Step 3 signed hash-chain log.
    blockchain_style   Step 4 permissioned PoA-style audit.
    abac_reexec        Re-execute the ABAC oracle from raw attributes.
    ct_log             Certificate Transparency baseline.
    fabric_abac        Hyperledger Fabric + ABAC baseline.
    nspi_drift         NS-PI drift detector (per-defense alarm signal).
                       Records a separate boolean per cell that the
                       analysis script can combine with any other defense.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from seba.attacks.base import EventLog
from seba.attacks.catalog import ATTACK_CATALOG
from seba.baselines import TrustedRawPolicyOracle, ct_log_detector, fabric_abac_detector
from seba.nspi import learn_policy
from seba.nspi.drift import drift_test
from seba.nspi.learner import predict_with_policy
from seba.scoring.aas import DefenseDetector, score_defense_against_catalog
from seba.scoring.detectors import (
    abac_reexecution_detector,
    mutable_log_detector,
    quorum_chain_detector,
    signed_chain_detector,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNS_DIR = REPO_ROOT / "prototype" / "runs"
OUT_DIR = REPO_ROOT / "results" / "tables"

DEFENSES: dict[str, DefenseDetector] = {
    "mutable_log": mutable_log_detector,
    "signed_chain": signed_chain_detector,
    "blockchain_style": quorum_chain_detector,
    "abac_reexec": abac_reexecution_detector,
    "ct_log": ct_log_detector,
    "fabric_abac": fabric_abac_detector,
}

SEED_DIR_RE = re.compile(r"^(?P<date>\d{8})_step3_audit_baselines_seed(?P<seed>\d+)$")


@dataclass(frozen=True)
class SeedAssets:
    seed: int
    signed_log_csv: Path
    labeled_requests_csv: Path


# ---------------------------------------------------------------------------
# Discovery.
# ---------------------------------------------------------------------------


def discover_seeds() -> list[SeedAssets]:
    assets: list[SeedAssets] = []
    for child in sorted(RUNS_DIR.iterdir()):
        m = SEED_DIR_RE.match(child.name)
        if not m:
            continue
        seed = int(m["seed"])
        signed_log = child / "artifacts" / "signed_hash_chain_log.csv"
        # Locate the matching Step-2 labeled artifact.
        date = m["date"]
        labeled = (
            RUNS_DIR
            / f"{date}_step2_policy_oracle_seed{seed}"
            / "artifacts"
            / "labeled_access_requests.csv"
        )
        if not signed_log.exists() or not labeled.exists():
            continue
        assets.append(
            SeedAssets(
                seed=seed,
                signed_log_csv=signed_log,
                labeled_requests_csv=labeled,
            )
        )
    return assets


def load_event_log(path: Path) -> EventLog:
    df = pd.read_csv(path)
    return tuple(df.to_dict(orient="records"))


# ---------------------------------------------------------------------------
# Per-seed scoring.
# ---------------------------------------------------------------------------


def score_seed(assets: SeedAssets) -> list[dict[str, object]]:
    clean_log = load_event_log(assets.signed_log_csv)
    rows: list[dict[str, object]] = []

    labeled = pd.read_csv(assets.labeled_requests_csv)
    trusted_oracle = TrustedRawPolicyOracle.from_records(
        labeled.to_dict(orient="records")
    )
    seed_defenses: dict[str, DefenseDetector] = {
        **DEFENSES,
        "trusted_policy_oracle": trusted_oracle.detect,
    }

    # Standard defenses scored via the AAS harness.
    for name, detector in seed_defenses.items():
        result = score_defense_against_catalog(
            defense_name=name,
            detector=detector,
            clean_log=clean_log,
            seed=assets.seed,
        )
        for attack_name, detected in result.per_attack.items():
            rows.append(
                {
                    "seed": assets.seed,
                    "defense": name,
                    "attack": attack_name,
                    "severity": result.severities[attack_name],
                    "detected": int(detected),
                    "aas": result.aas,
                    "unweighted": result.unweighted,
                }
            )

    # NS-PI drift detector. We train on clean labels and then test against
    # each attacked log's predicted distribution via JS divergence.
    policy = learn_policy(labeled, max_depth=8, min_samples_leaf=10)
    clean_pred = predict_with_policy(policy, labeled).tolist()

    rng = np.random.default_rng(assets.seed)
    for attack in ATTACK_CATALOG:
        if attack.name == "metadata_inference":
            # Drift detector is not designed to detect ledger-only attacks.
            rows.append(
                {
                    "seed": assets.seed,
                    "defense": "nspi_drift",
                    "attack": attack.name,
                    "severity": attack.severity,
                    "detected": 0,
                    "aas": 0.0,
                    "unweighted": 0.0,
                }
            )
            continue

        attack_result = attack(clean_log, rng)
        if not attack_result.affected_indices:
            rows.append(
                {
                    "seed": assets.seed,
                    "defense": "nspi_drift",
                    "attack": attack.name,
                    "severity": attack.severity,
                    "detected": 1,
                    "aas": 0.0,
                    "unweighted": 0.0,
                }
            )
            continue
        # Project the perturbed log back into the labeled-requests space.
        # We can't re-derive every Step-2 field from the perturbed audit
        # log alone, so we use the perturbed decisions directly as the
        # "observed" sample and the policy's clean predictions as the
        # reference sample.
        perturbed_decisions = [
            str(r.get("decision", "")) for r in attack_result.perturbed_log
        ]
        report = drift_test(
            clean_pred,
            perturbed_decisions,
            classes=("allow", "deny", "escalate"),
            permutations=200,
            alpha=0.05,
            rng_seed=assets.seed,
        )
        rows.append(
            {
                "seed": assets.seed,
                "defense": "nspi_drift",
                "attack": attack.name,
                "severity": attack.severity,
                "detected": int(report.alarm),
                "aas": float(report.observed_divergence),
                "unweighted": float(report.p_value),
            }
        )

    return rows


# ---------------------------------------------------------------------------
# Aggregation.
# ---------------------------------------------------------------------------


def aggregate(rows: list[dict[str, object]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.DataFrame(rows)
    grouped = (
        df.groupby(["defense", "attack"])
        .agg(
            n_seeds=("seed", "nunique"),
            detection_rate=("detected", "mean"),
            detection_std=("detected", "std"),
            severity=("severity", "first"),
        )
        .reset_index()
    )
    # Weighted AAS per defense: severity-weighted mean detection over attacks.
    def _aas_for(defense: str) -> float:
        sub = grouped[grouped["defense"] == defense]
        weight = sub["severity"].sum()
        if weight == 0:
            return 0.0
        return float((sub["detection_rate"] * sub["severity"]).sum() / weight)

    summary = (
        df.groupby(["defense", "seed"])
        .apply(
            lambda g: (g["detected"] * g["severity"]).sum() / g["severity"].sum()
            if g["severity"].sum() > 0
            else 0.0,
            include_groups=False,
        )
        .reset_index(name="aas")
    )
    aas_summary = summary.groupby("defense")["aas"].agg(["mean", "std", "min", "max"]).reset_index()
    aas_summary.columns = ["defense", "aas_mean", "aas_std", "aas_min", "aas_max"]
    return grouped, aas_summary


# ---------------------------------------------------------------------------
# Public entry point used by the script.
# ---------------------------------------------------------------------------


def run_grid(out_dir: Path = OUT_DIR) -> dict[str, Path]:
    seeds = discover_seeds()
    if not seeds:
        raise RuntimeError(
            "No seed assets found. Run scripts/run_multi_seed.sh first."
        )
    rows: list[dict[str, object]] = []
    for assets in seeds:
        rows.extend(score_seed(assets))

    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "full_grid_raw.csv"
    detail_path = out_dir / "full_grid_per_attack.csv"
    summary_path = out_dir / "full_grid_aas_by_defense.csv"

    pd.DataFrame(rows).to_csv(raw_path, index=False)
    detail, summary = aggregate(rows)
    detail.to_csv(detail_path, index=False)
    summary.to_csv(summary_path, index=False)
    return {"raw": raw_path, "per_attack": detail_path, "aas_summary": summary_path}
