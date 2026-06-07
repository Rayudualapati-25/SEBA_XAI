"""Metadata-inference attack: train a model to recover sensitive labels from the ledger.

This is fundamentally different from the other attacks. It does NOT modify
the log; it tests whether an honest-but-curious auditor (or anyone with
read access to the ledger) can infer hidden sensitive attributes — here,
``record_sensitivity_level`` — from the *non-sensitive* columns that the
ledger leaves in clear.

The detection criterion is inverted: we want the *defense's published
ledger view* to make this attack do no better than majority-class baseline.

Returns an ``AttackResult`` whose ``meta`` carries:

- attacker_auroc:    AUROC of the inference classifier (one-vs-rest macro).
- baseline_auroc:    AUROC of always predicting the majority class (0.5).
- leakage_score:     max(0, attacker_auroc - baseline_auroc).
- detected:          True if leakage_score <= 0.05 (defense leaks ≤ 5%).
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

from seba.attacks.base import AttackResult, EventLog

NAME = "metadata_inference"
SEVERITY = 4
LEAKAGE_THRESHOLD = 0.05


def _ledger_to_frame(log: EventLog) -> pd.DataFrame:
    return pd.DataFrame([dict(row) for row in log])


def metadata_inference_attack(
    log: EventLog,
    rng: Any,
    feature_cols: tuple[str, ...] = (
        "requester_station_id",
        "decision",
        "primary_reason_code",
        "policy_version_evaluated",
    ),
    target_col: str = "record_sensitivity_level",
) -> AttackResult:
    """Train a logistic regression to recover ``target_col`` from ``feature_cols``.

    The defense passes if leakage_score <= ``LEAKAGE_THRESHOLD``. The full
    metadata ledger from Step 7 is expected to leak; the minimized ledger
    is expected to pass.
    """

    df = _ledger_to_frame(log)
    if target_col not in df.columns or df[target_col].nunique() < 2:
        # Target absent or constant — the attacker has nothing to recover.
        # Treat as a defense win (leakage = 0).
        return AttackResult(
            name=NAME,
            severity=SEVERITY,
            perturbed_log=log,
            affected_indices=(),
            meta={
                "skipped": True,
                "reason": f"target column '{target_col}' missing or constant",
                "attacker_auroc": 0.5,
                "baseline_auroc": 0.5,
                "leakage_score": 0.0,
                "detected": True,
            },
        )

    features_present = [c for c in feature_cols if c in df.columns]
    if not features_present:
        return AttackResult(
            name=NAME,
            severity=SEVERITY,
            perturbed_log=log,
            affected_indices=(),
            meta={
                "skipped": True,
                "reason": "no feature columns present (defense is minimized)",
                "attacker_auroc": 0.5,
                "baseline_auroc": 0.5,
                "leakage_score": 0.0,
                "detected": True,
            },
        )

    seed = int(rng.integers(0, 2**31 - 1))
    x_train, x_test, y_train, y_test = train_test_split(
        df[features_present].astype(str),
        df[target_col].astype(str),
        test_size=0.3,
        random_state=seed,
        stratify=df[target_col] if df[target_col].value_counts().min() >= 2 else None,
    )

    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    x_train_enc = encoder.fit_transform(x_train)
    x_test_enc = encoder.transform(x_test)

    classes = sorted(df[target_col].unique())
    if len(classes) < 2:
        return AttackResult(
            name=NAME, severity=SEVERITY, perturbed_log=log, affected_indices=(),
            meta={"skipped": True, "reason": "only one class"},
        )

    # scikit-learn 1.7+ removed the multi_class kwarg; auto-OvR is the default.
    clf = LogisticRegression(max_iter=200)
    clf.fit(x_train_enc, y_train)
    proba = clf.predict_proba(x_test_enc)

    try:
        if len(classes) == 2:
            # Binary case: roc_auc_score wants the positive-class column.
            pos_idx = list(clf.classes_).index(classes[-1])
            attacker_auroc = float(roc_auc_score(y_test, proba[:, pos_idx]))
        else:
            attacker_auroc = float(
                roc_auc_score(
                    y_test, proba, multi_class="ovr", average="macro", labels=classes
                )
            )
    except ValueError:
        # Test split missing a class — fall back to chance.
        attacker_auroc = 0.5

    baseline_auroc = 0.5
    leakage = max(0.0, attacker_auroc - baseline_auroc)
    detected = leakage <= LEAKAGE_THRESHOLD

    return AttackResult(
        name=NAME,
        severity=SEVERITY,
        perturbed_log=log,
        affected_indices=(),
        meta={
            "attacker_auroc": attacker_auroc,
            "baseline_auroc": baseline_auroc,
            "leakage_score": leakage,
            "leakage_threshold": LEAKAGE_THRESHOLD,
            "detected": detected,
            "features_used": features_present,
            "target_col": target_col,
            "n_classes": len(classes),
        },
    )


metadata_inference_attack.name = NAME  # type: ignore[attr-defined]
metadata_inference_attack.severity = SEVERITY  # type: ignore[attr-defined]
