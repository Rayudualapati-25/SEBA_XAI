"""NS-PI learner: induce an interpretable rule list from audit traces.

Design choices and *why*:

- We use a shallow ``sklearn.tree.DecisionTreeClassifier`` (max_depth bounded
  by config, typically 6–10) over engineered binary attributes drawn from
  the access-request schema. Each root-to-leaf path becomes one rule.
  Rationale: Rudin 2019 — interpretable-by-design beats post-hoc explanation
  for high-stakes decisions. A rule list is the simplest form of
  interpretable model that still captures interactions among ABAC attributes.

- The learned policy is exported as JSON in a schema-compatible projection
  of the declared policy (``prototype/synthetic_access_sim/policies/
  seba_xai_policy_v1.json``). Specifically, we record per-rule:
  ``conditions``, ``decision``, ``support``, ``confidence``, and the
  ``decisive_attributes`` (the column names that appear in the rule's
  path). The drift detector in ``seba.nspi.drift`` consumes this artifact.

- Feature engineering is intentionally tabular and policy-relevant. We do
  not embed the request text. The features mirror the attributes named in
  the declared policy so the learned vs. declared comparison is apples-to-
  apples.

The learner does NOT touch the audit ledger directly — its input is a
labeled trace produced by Step 2 of the prototype. This separation lets
NS-PI run against (a) the original oracle, (b) replayed/perturbed logs from
the attack catalog, and (c) other defenses' published views.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, _tree

# Columns from labeled_access_requests.csv we expose to the learner.
# Categorical columns are one-hot encoded; boolean columns are passed
# through as 0/1; rank_level is binned.
CATEGORICAL_COLUMNS: tuple[str, ...] = (
    "requester_role",
    "requester_agency",
    "requester_clearance_level",
    "requester_credential_status",
    "case_assignment_status",
    "target_case_type",
    "target_record_type",
    "target_owner_agency",
    "record_sensitivity_level",
    "sealed_status",
    "retention_status",
    "purpose",
    "action",
    "approval_token_status",
    "time_window",
    "network_status",
    "request_channel",
)

BOOLEAN_COLUMNS: tuple[str, ...] = (
    "victim_flag",
    "witness_flag",
    "juvenile_flag",
    "evidence_media_flag",
    "same_station",
    "same_district",
    "same_state",
    "cross_jurisdiction",
    "emergency_flag",
    "court_or_prosecutor_request_flag",
)

NUMERIC_COLUMNS: tuple[str, ...] = ("requester_rank_level",)

LABEL_COLUMN = "decision"
DEFAULT_MAX_DEPTH = 8
DEFAULT_MIN_SAMPLES_LEAF = 10
RANDOM_SEED = 2026


# ---------------------------------------------------------------------------
# Policy artifact types.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LearnedRule:
    """One rule in a learned policy.

    Attributes:
        rule_id: Stable identifier (``rule_0``, ``rule_1``, ...).
        conditions: Sequence of ``(feature, op, threshold)`` triples in the
            order the decision tree visited them. ``op`` is one of
            ``<=`` / ``>``.
        decision: Predicted decision label (``allow`` / ``deny`` /
            ``escalate``).
        support: Number of training samples that landed in this leaf.
        confidence: Fraction of the leaf's samples whose label matches
            ``decision``.
        decisive_attributes: Sorted tuple of unique base attribute names
            that appear in ``conditions``.
    """

    rule_id: str
    conditions: tuple[tuple[str, str, float], ...]
    decision: str
    support: int
    confidence: float
    decisive_attributes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "conditions": [
                {"feature": f, "op": op, "threshold": float(t)}
                for f, op, t in self.conditions
            ],
            "decision": self.decision,
            "support": int(self.support),
            "confidence": float(self.confidence),
            "decisive_attributes": list(self.decisive_attributes),
        }


@dataclass(frozen=True, slots=True)
class LearnedPolicy:
    """Output of NS-PI training.

    A learned policy is a sorted list of rules + a fallback decision used
    when no rule fires (which should not happen for a complete decision
    tree, but the field is included so the policy schema is robust).
    """

    rules: tuple[LearnedRule, ...]
    fallback_decision: str
    feature_names: tuple[str, ...]
    classes: tuple[str, ...]
    learner_version: str = "NSPI-2026-05-v1"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "learner_version": self.learner_version,
            "fallback_decision": self.fallback_decision,
            "feature_names": list(self.feature_names),
            "classes": list(self.classes),
            "metadata": dict(self.metadata),
            "rules": [r.to_dict() for r in self.rules],
        }

    def to_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


# ---------------------------------------------------------------------------
# Feature engineering.
# ---------------------------------------------------------------------------


def encode_features(df: pd.DataFrame) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """Project a labeled-request DataFrame into a numeric feature frame.

    Returns the feature frame and the tuple of feature column names. The
    feature names embed the source column for downstream interpretation:
    e.g. ``cat:purpose=INVESTIGATION`` or ``bool:juvenile_flag``.
    """

    pieces: list[pd.DataFrame] = []
    feature_names: list[str] = []

    for col in BOOLEAN_COLUMNS:
        if col not in df.columns:
            continue
        series = df[col].astype(str).str.lower().map({"true": 1, "false": 0}).fillna(0).astype(int)
        feature = f"bool:{col}"
        pieces.append(series.rename(feature).to_frame())
        feature_names.append(feature)

    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        feature = f"num:{col}"
        pieces.append(series.rename(feature).to_frame())
        feature_names.append(feature)

    for col in CATEGORICAL_COLUMNS:
        if col not in df.columns:
            continue
        dummies = pd.get_dummies(df[col].astype(str), prefix=f"cat:{col}", prefix_sep="=")
        dummies = dummies.astype(int)
        pieces.append(dummies)
        feature_names.extend(dummies.columns.tolist())

    if not pieces:
        return pd.DataFrame(index=df.index), ()

    features = pd.concat(pieces, axis=1)
    return features, tuple(features.columns.tolist())


# ---------------------------------------------------------------------------
# Rule extraction from a fitted DecisionTreeClassifier.
# ---------------------------------------------------------------------------


def _extract_rules(
    tree: DecisionTreeClassifier,
    feature_names: Sequence[str],
    classes: Sequence[str],
) -> list[LearnedRule]:
    rules: list[LearnedRule] = []
    t = tree.tree_

    def recurse(node: int, path: list[tuple[str, str, float]]) -> None:
        if t.feature[node] == _tree.TREE_UNDEFINED:
            # Leaf.
            class_counts = t.value[node][0]
            best = int(np.argmax(class_counts))
            support = int(class_counts.sum())
            confidence = float(class_counts[best] / support) if support else 0.0
            decisive_attrs = sorted({_base_attribute(f) for f, _, _ in path})
            rules.append(
                LearnedRule(
                    rule_id=f"rule_{len(rules)}",
                    conditions=tuple(path),
                    decision=str(classes[best]),
                    support=support,
                    confidence=confidence,
                    decisive_attributes=tuple(decisive_attrs),
                )
            )
            return
        feature_name = feature_names[t.feature[node]]
        threshold = float(t.threshold[node])
        recurse(t.children_left[node], path + [(feature_name, "<=", threshold)])
        recurse(t.children_right[node], path + [(feature_name, ">", threshold)])

    recurse(0, [])
    return rules


def _base_attribute(feature_name: str) -> str:
    """Strip the encoding prefix from a feature name.

    ``cat:purpose=INVESTIGATION`` -> ``purpose``
    ``bool:juvenile_flag``        -> ``juvenile_flag``
    ``num:requester_rank_level``  -> ``requester_rank_level``
    """

    head, _, tail = feature_name.partition(":")
    base = tail if head in {"cat", "bool", "num"} else feature_name
    return base.split("=", 1)[0]


# ---------------------------------------------------------------------------
# Public learner API.
# ---------------------------------------------------------------------------


def learn_policy(
    labeled_requests: pd.DataFrame,
    *,
    label_column: str = LABEL_COLUMN,
    max_depth: int = DEFAULT_MAX_DEPTH,
    min_samples_leaf: int = DEFAULT_MIN_SAMPLES_LEAF,
    random_state: int = RANDOM_SEED,
) -> LearnedPolicy:
    """Induce a rule list from labeled access requests.

    Args:
        labeled_requests: DataFrame whose columns include the engineered
            attributes listed in ``CATEGORICAL_COLUMNS`` / ``BOOLEAN_COLUMNS``
            / ``NUMERIC_COLUMNS`` and the label column.
        label_column: Column holding ``allow`` / ``deny`` / ``escalate``.
        max_depth: Maximum depth of the underlying decision tree.
        min_samples_leaf: Minimum support per learned rule.
        random_state: Tree fit seed.

    Returns:
        ``LearnedPolicy`` whose rules can be serialized to JSON and fed
        into the drift detector.
    """

    if label_column not in labeled_requests.columns:
        raise ValueError(
            f"label column '{label_column}' missing from labeled_requests"
        )

    features, feature_names = encode_features(labeled_requests)
    labels = labeled_requests[label_column].astype(str).values
    if features.empty:
        raise ValueError("encode_features produced an empty frame")

    clf = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
        class_weight="balanced",
    )
    clf.fit(features.values, labels)

    rules = _extract_rules(clf, feature_names, clf.classes_)
    fallback = str(clf.classes_[np.argmax(np.bincount(np.searchsorted(clf.classes_, labels)))])

    return LearnedPolicy(
        rules=tuple(rules),
        fallback_decision=fallback,
        feature_names=feature_names,
        classes=tuple(str(c) for c in clf.classes_),
        metadata={
            "n_samples": int(len(labels)),
            "n_features": int(len(feature_names)),
            "max_depth": int(max_depth),
            "min_samples_leaf": int(min_samples_leaf),
            "training_accuracy": float(clf.score(features.values, labels)),
        },
    )


def predict_with_policy(
    policy: LearnedPolicy, labeled_requests: pd.DataFrame
) -> np.ndarray:
    """Return ``LearnedPolicy.rules`` predictions for each row.

    Walks each rule in order; the first one whose conditions all hold is
    fired. Falls back to ``policy.fallback_decision`` only if no rule
    matches (shouldn't happen for a complete tree).
    """

    features, _ = encode_features(labeled_requests)
    # Re-align to the policy's training-time feature set; any missing
    # column is treated as 0, any extra column is dropped.
    for name in policy.feature_names:
        if name not in features.columns:
            features[name] = 0
    features = features[list(policy.feature_names)]

    predictions: list[str] = []
    for _, row in features.iterrows():
        fired = None
        for rule in policy.rules:
            if _rule_matches(rule, row):
                fired = rule
                break
        predictions.append(fired.decision if fired else policy.fallback_decision)
    return np.asarray(predictions, dtype=object)


def _rule_matches(rule: LearnedRule, row: pd.Series) -> bool:
    for feature, op, threshold in rule.conditions:
        value = float(row.get(feature, 0))
        if op == "<=":
            if not value <= threshold:
                return False
        elif op == ">":
            if not value > threshold:
                return False
        else:
            raise ValueError(f"unknown op {op!r} in rule {rule.rule_id}")
    return True
