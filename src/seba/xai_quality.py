"""Quality metrics for SEBA-XAI explanation and audit artifacts.

The metrics here are intentionally conservative. They do not claim that an
explanation is legally sufficient or human-validated. They only test whether
the prototype produces reviewable artifacts that can be checked from the
generated data:

- explanation trace completeness;
- decisive-attribute text coverage;
- counterfactual validity against the learned NS-PI policy;
- stability for repeated policy-equivalent contexts;
- audit reconstruction from request -> signed log -> block commitment.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from seba.nspi import explain_dataframe, learn_policy
from seba.nspi.learner import (
    BOOLEAN_COLUMNS,
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    LearnedPolicy,
    predict_with_policy,
)

REQUIRED_TRACE_FIELDS: tuple[str, ...] = (
    "decision",
    "primary_reason_code",
    "matched_rule_ids",
    "decisive_attributes",
    "xai_explanation",
    "policy_version_evaluated",
    "decision_hash",
    "explanation_hash",
    "audit_anchor_hash",
)

POLICY_CONTEXT_COLUMNS: tuple[str, ...] = (
    *CATEGORICAL_COLUMNS,
    *BOOLEAN_COLUMNS,
    *NUMERIC_COLUMNS,
)

ATTRIBUTE_TEXT_HINTS: dict[str, tuple[str, ...]] = {
    "action": ("action", "routine", "approve", "view"),
    "approval_token_status": ("approval", "token"),
    "case_assignment_status": ("assigned", "assignment", "case"),
    "court_or_prosecutor_request_flag": ("court", "prosecutor", "prosecution"),
    "cross_jurisdiction": ("cross jurisdiction", "jurisdiction"),
    "juvenile_flag": ("juvenile",),
    "purpose": ("purpose",),
    "record_sensitivity_level": ("sensitivity", "sensitive", "classified"),
    "requester_credential_status": ("credential",),
    "retention_status": ("retention", "archived"),
    "sealed_status": ("sealed",),
    "victim_flag": ("victim",),
    "witness_flag": ("witness",),
}


def split_pipe(value: Any) -> list[str]:
    """Split pipe-delimited artifact fields into non-empty strings."""

    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in text.split("|") if part.strip()]


def nonempty(value: Any) -> bool:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return False
    return bool(str(value).strip())


def explanation_trace_metrics(labeled: pd.DataFrame) -> dict[str, float]:
    """Measure whether each decision has the minimum review trace fields."""

    if labeled.empty:
        return {
            "trace_complete_rate": 0.0,
            "decisive_attribute_present_rate": 0.0,
            "decisive_attribute_text_coverage_mean": 0.0,
            "decisive_attribute_full_text_coverage_rate": 0.0,
        }

    complete = labeled.apply(
        lambda row: all(nonempty(row.get(field)) for field in REQUIRED_TRACE_FIELDS),
        axis=1,
    )
    attr_lists = labeled["decisive_attributes"].apply(split_pipe)
    has_attrs = attr_lists.apply(bool)
    coverage = [
        decisive_attribute_text_coverage(attrs, str(row.get("xai_explanation", "")), row)
        for attrs, (_, row) in zip(attr_lists, labeled.iterrows(), strict=True)
    ]
    coverage_series = pd.Series(coverage, index=labeled.index, dtype=float)

    return {
        "trace_complete_rate": float(complete.mean()),
        "decisive_attribute_present_rate": float(has_attrs.mean()),
        "decisive_attribute_text_coverage_mean": float(coverage_series.mean()),
        "decisive_attribute_full_text_coverage_rate": float((coverage_series == 1.0).mean()),
    }


def decisive_attribute_text_coverage(
    attributes: list[str], explanation: str, row: pd.Series
) -> float:
    """Fraction of decisive attributes reflected in the explanation text.

    This is a weak textual proxy, not a human explanation-quality score.
    It credits either the attribute phrase, a known phrase hint, or the row's
    concrete non-boolean value appearing in the explanation.
    """

    if not attributes:
        return 0.0
    text = _normalize(explanation)
    hits = 0
    for attr in attributes:
        hints = {attr.replace("_", " ")}
        hints.update(ATTRIBUTE_TEXT_HINTS.get(attr, ()))
        value = row.get(attr)
        if nonempty(value) and str(value).lower() not in {"true", "false"}:
            hints.add(str(value).replace("_", " "))
        if any(_normalize(hint) in text for hint in hints if hint):
            hits += 1
    return hits / len(attributes)


def counterfactual_metrics(
    labeled: pd.DataFrame,
    policy: LearnedPolicy | None = None,
    *,
    max_edits: int = 4,
) -> dict[str, float]:
    """Measure generated counterfactual coverage and replay validity."""

    if policy is None:
        policy = learn_policy(labeled, max_depth=8, min_samples_leaf=10)
    target_mask = labeled["decision"].isin({"deny", "escalate"})
    target_count = int(target_mask.sum())
    if target_count == 0:
        return {
            "counterfactual_target_count": 0.0,
            "counterfactual_generated_count": 0.0,
            "counterfactual_coverage_rate": 0.0,
            "counterfactual_validity_rate": 0.0,
            "counterfactual_mean_edits": 0.0,
        }

    cfs = explain_dataframe(policy, labeled, max_edits=max_edits)
    valid = 0
    edit_counts: list[int] = []
    for cf in cfs:
        edited = apply_counterfactual_edits(labeled, cf.request_index, cf.edits)
        predicted = str(predict_with_policy(policy, edited.iloc[[cf.request_index]])[0])
        valid += int(predicted == cf.proposed_decision)
        edit_counts.append(len(cf.edits))

    generated = len(cfs)
    return {
        "counterfactual_target_count": float(target_count),
        "counterfactual_generated_count": float(generated),
        "counterfactual_coverage_rate": float(generated / target_count),
        "counterfactual_validity_rate": float(valid / generated) if generated else 0.0,
        "counterfactual_mean_edits": float(np.mean(edit_counts)) if edit_counts else 0.0,
    }


def apply_counterfactual_edits(
    labeled: pd.DataFrame, request_index: int, edits: tuple[tuple[str, str], ...]
) -> pd.DataFrame:
    """Return a copy of ``labeled`` with one request edited."""

    edited = labeled.copy()
    for attr, value in edits:
        if attr not in edited.columns:
            continue
        replacement = _resolve_edit_value(edited, request_index, attr, value)
        edited.at[request_index, attr] = replacement
    return edited


def stability_metrics(labeled: pd.DataFrame) -> dict[str, float]:
    """Measure deterministic explanations for repeated policy contexts."""

    cols = [col for col in POLICY_CONTEXT_COLUMNS if col in labeled.columns]
    if not cols:
        return {
            "stability_duplicate_group_count": 0.0,
            "stability_duplicate_row_count": 0.0,
            "stable_decision_reason_group_rate": 0.0,
            "stable_decision_reason_row_rate": 0.0,
        }

    grouped = (
        labeled.groupby(cols, dropna=False)
        .agg(
            n=("request_id", "size"),
            decisions=("decision", "nunique"),
            reasons=("primary_reason_code", "nunique"),
        )
        .reset_index()
    )
    duplicate_groups = grouped[grouped["n"] > 1]
    if duplicate_groups.empty:
        return {
            "stability_duplicate_group_count": 0.0,
            "stability_duplicate_row_count": 0.0,
            "stable_decision_reason_group_rate": 0.0,
            "stable_decision_reason_row_rate": 0.0,
        }
    stable = duplicate_groups[
        (duplicate_groups["decisions"] == 1) & (duplicate_groups["reasons"] == 1)
    ]
    return {
        "stability_duplicate_group_count": float(len(duplicate_groups)),
        "stability_duplicate_row_count": float(duplicate_groups["n"].sum()),
        "stable_decision_reason_group_rate": float(len(stable) / len(duplicate_groups)),
        "stable_decision_reason_row_rate": float(stable["n"].sum() / duplicate_groups["n"].sum()),
    }


def audit_reconstruction_metrics(
    labeled: pd.DataFrame,
    signed_log: pd.DataFrame,
    block_index: pd.DataFrame,
    blocks_jsonl: Path,
) -> dict[str, float]:
    """Check whether an auditor can reconstruct key decision artifacts."""

    blocks = _load_blocks(blocks_jsonl)
    block_commitments = {
        str(block.get("block_hash", "")): set(block.get("event_commitment_hashes", []))
        for block in blocks
    }

    labeled_by_request = labeled.set_index("request_id", drop=False)
    block_by_event = block_index.set_index("event_id", drop=False)

    checks: list[bool] = []
    request_match = 0
    signed_hash_match = 0
    block_index_match = 0
    commitment_match = 0
    for _, event in signed_log.iterrows():
        request_id = str(event.get("request_id", ""))
        event_id = str(event.get("event_id", ""))
        if request_id not in labeled_by_request.index:
            checks.append(False)
            continue
        request_match += 1
        labeled_row = labeled_by_request.loc[request_id]
        hashes_match = all(
            str(event.get(field, "")) == str(labeled_row.get(field, ""))
            for field in (
                "decision_hash",
                "explanation_hash",
                "audit_anchor_hash",
                "policy_version_evaluated",
            )
        )
        signed_hash_match += int(hashes_match)

        if event_id not in block_by_event.index:
            checks.append(False)
            continue
        block_index_match += 1
        index_row = block_by_event.loc[event_id]
        block_hash = str(index_row.get("block_hash", ""))
        event_commitment = str(index_row.get("event_commitment_hash", ""))
        in_block = event_commitment in block_commitments.get(block_hash, set())
        commitment_match += int(in_block)
        checks.append(bool(hashes_match and in_block and block_hash))

    total = len(signed_log)
    return {
        "audit_event_count": float(total),
        "audit_request_join_rate": float(request_match / total) if total else 0.0,
        "audit_signed_hash_match_rate": float(signed_hash_match / total) if total else 0.0,
        "audit_block_index_join_rate": float(block_index_match / total) if total else 0.0,
        "audit_commitment_in_block_rate": float(commitment_match / total) if total else 0.0,
        "audit_reconstruction_rate": float(np.mean(checks)) if checks else 0.0,
    }


def evaluate_seed(
    *,
    seed: int,
    labeled_requests_csv: Path,
    signed_log_csv: Path,
    block_index_csv: Path,
    blocks_jsonl: Path,
) -> dict[str, float | int]:
    """Compute all explanation/audit metrics for one seed."""

    labeled = pd.read_csv(labeled_requests_csv)
    signed_log = pd.read_csv(signed_log_csv)
    block_index = pd.read_csv(block_index_csv)
    policy = learn_policy(labeled, max_depth=8, min_samples_leaf=10)

    row: dict[str, float | int] = {
        "seed": int(seed),
        "n_requests": int(len(labeled)),
    }
    row.update(explanation_trace_metrics(labeled))
    row.update(counterfactual_metrics(labeled, policy))
    row.update(stability_metrics(labeled))
    row.update(audit_reconstruction_metrics(labeled, signed_log, block_index, blocks_jsonl))
    return row


def summarize_quality(per_seed: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-seed metrics into mean/std summary rows."""

    metric_cols = [
        col for col in per_seed.columns if col not in {"seed", "n_requests"}
    ]
    rows = []
    for metric in metric_cols:
        values = pd.to_numeric(per_seed[metric], errors="coerce")
        rows.append(
            {
                "metric": metric,
                "mean": float(values.mean()),
                "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
                "min": float(values.min()),
                "max": float(values.max()),
                "n_seeds": int(per_seed["seed"].nunique()),
            }
        )
    return pd.DataFrame(rows)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def _resolve_edit_value(
    labeled: pd.DataFrame, request_index: int, attr: str, value: str
) -> object:
    if value == "<other>":
        current = str(labeled.at[request_index, attr])
        candidates = [
            str(candidate)
            for candidate in sorted(labeled[attr].dropna().astype(str).unique())
            if str(candidate) != current
        ]
        return candidates[0] if candidates else current
    if attr in BOOLEAN_COLUMNS:
        return str(value).lower() == "true"
    if attr in NUMERIC_COLUMNS:
        try:
            return int(value)
        except ValueError:
            return value
    return value


def _load_blocks(path: Path) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                blocks.append(json.loads(text))
    return blocks
