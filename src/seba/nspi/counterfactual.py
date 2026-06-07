"""NS-PI counterfactual explanations.

For any request whose learned-policy decision is ``deny`` or ``escalate``,
search the minimal-edit set of attributes that would have flipped the
decision to ``allow``. This is the only place in the NS-PI pipeline that
earns the "X" in XAI — it produces officer-facing 1-line explanations like:

    "Would have been allowed if purpose = INVESTIGATION."

Algorithm:
- The learned policy is a tree-derived rule list. For each ALLOW rule, we
  compute the *symbolic conditions* that the rule requires, then check the
  minimum number of attribute edits the candidate request would need to
  satisfy those conditions. The cheapest allow-rule wins.
- Each "edit" is a single (attribute, new_value) override. For boolean
  features the new value is the negation; for categorical features it is
  the rule's required category; for numeric features it is the smallest
  integer move past the threshold.
- We cap the search at ``max_edits`` (default 3). If no allow rule is
  reachable within the cap, we return ``None``.

Limitations stated up front so the paper doesn't overclaim:
- Counterfactuals respect *the learned policy*, not the declared policy.
  They tell the officer what would have changed NS-PI's decision, which
  may differ from what would change the deployed ABAC engine's decision.
- We do not enforce attribute-level feasibility constraints (e.g. an
  officer cannot freely change their own rank). The output is an
  explanation hint for a human reviewer, not an actionable instruction.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd

from seba.nspi.learner import (
    LearnedPolicy,
    LearnedRule,
    encode_features,
)


@dataclass(frozen=True, slots=True)
class Counterfactual:
    """Minimal-edit suggestion that would flip a denied request to allow.

    Attributes:
        request_index: Index of the row in the input DataFrame.
        original_decision: Decision the learned policy produced.
        proposed_decision: Always ``allow`` (the search target).
        edits: Tuple of ``(attribute, value)`` pairs to apply.
        explanation: One-line officer-facing sentence.
    """

    request_index: int
    original_decision: str
    proposed_decision: str
    edits: tuple[tuple[str, str], ...]
    explanation: str


# ---------------------------------------------------------------------------
# Edit-cost computation.
# ---------------------------------------------------------------------------


def _decompose_feature(feature_name: str) -> tuple[str, str, str]:
    """Return (encoding, base_attribute, category_or_empty)."""

    head, _, tail = feature_name.partition(":")
    if head not in {"cat", "bool", "num"}:
        return ("raw", feature_name, "")
    base, _, category = tail.partition("=")
    return (head, base, category)


def _edits_to_satisfy(rule: LearnedRule, encoded_row: pd.Series) -> list[tuple[str, str]]:
    """Edits in (attribute, target_value) form needed to fire ``rule``."""

    edits: list[tuple[str, str]] = []
    grouped_cat_targets: dict[str, str] = {}

    for feature, op, threshold in rule.conditions:
        encoding, base, category = _decompose_feature(feature)
        value = float(encoded_row.get(feature, 0))
        if encoding == "cat":
            # Categorical features are one-hot columns. A "feature > 0.5"
            # condition means we need the category set. A "feature <= 0.5"
            # condition means the value should NOT be this category — but
            # we only enforce positive conditions here; negative conditions
            # are implied by the chosen positive one. This is a reasonable
            # simplification because each request has exactly one category
            # value per base attribute.
            if op == ">" and value <= threshold:
                grouped_cat_targets[base] = category
            elif op == "<=" and value > threshold:
                # We need to change the category to anything except this one.
                grouped_cat_targets.setdefault(base, "<other>")
        elif encoding == "bool":
            bool_target = 1 if op == ">" else 0
            if int(value) != bool_target:
                edits.append((base, "true" if bool_target else "false"))
        elif encoding == "num":
            if op == "<=" and not value <= threshold:
                edits.append((base, str(int(threshold))))
            elif op == ">" and not value > threshold:
                edits.append((base, str(int(threshold) + 1)))

    for base, target in grouped_cat_targets.items():
        edits.append((base, target))
    return edits


# ---------------------------------------------------------------------------
# Search.
# ---------------------------------------------------------------------------


def explain_request(
    policy: LearnedPolicy,
    labeled_requests: pd.DataFrame,
    request_index: int,
    *,
    target_decision: str = "allow",
    max_edits: int = 3,
) -> Counterfactual | None:
    """Find the cheapest edit set that flips ``request_index`` to ``target_decision``."""

    features, _ = encode_features(labeled_requests)
    for name in policy.feature_names:
        if name not in features.columns:
            features[name] = 0
    encoded_row = features.iloc[request_index]
    original = str(labeled_requests.iloc[request_index].get("decision", "?"))

    candidate_rules = [r for r in policy.rules if r.decision == target_decision]
    best: Counterfactual | None = None
    best_cost = max_edits + 1

    for rule in candidate_rules:
        edits = _edits_to_satisfy(rule, encoded_row)
        if not edits or len(edits) > max_edits:
            continue
        if len(edits) < best_cost:
            best_cost = len(edits)
            best = Counterfactual(
                request_index=request_index,
                original_decision=original,
                proposed_decision=target_decision,
                edits=tuple(edits),
                explanation=_render_explanation(target_decision, edits),
            )

    return best


def _render_explanation(target: str, edits: list[tuple[str, str]]) -> str:
    if not edits:
        return f"Already would have been {target}."
    parts = [f"{attr} = {value}" for attr, value in edits]
    joined = " and ".join(parts)
    return f"Would have been {target} if {joined}."


def explain_dataframe(
    policy: LearnedPolicy,
    labeled_requests: pd.DataFrame,
    *,
    only_for_decisions: Iterable[str] = ("deny", "escalate"),
    target_decision: str = "allow",
    max_edits: int = 3,
) -> list[Counterfactual]:
    """Generate counterfactuals for every row whose decision is in ``only_for_decisions``."""

    target_indices = labeled_requests.index[
        labeled_requests["decision"].isin(set(only_for_decisions))
    ].tolist()
    results: list[Counterfactual] = []
    for idx in target_indices:
        cf = explain_request(
            policy,
            labeled_requests,
            request_index=int(idx),
            target_decision=target_decision,
            max_edits=max_edits,
        )
        if cf is not None:
            results.append(cf)
    return results
