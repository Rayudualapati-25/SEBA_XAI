#!/usr/bin/env python3
"""Run configured PBAC/ABAC policy ablations for SEBA-XAI.

This is Step 8 of the prototype. It moves the access-control dimensions into a
structured JSON policy file and evaluates how decisions change when important
policy groups are removed.

The Step 2 policy oracle remains the deterministic reference label for the
synthetic workload. Results must be read as policy-oracle consistency, not
real police access-control accuracy.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN_ID = "20260528_step8_policy_config_ablation_seed42"
DEFAULT_STEP1_RUN_ID = "20260527_step1_synthetic_requests_seed42"
DEFAULT_STEP2_RUN_ID = "20260527_step2_policy_oracle_seed42"
DEFAULT_POLICY_CONFIG = ROOT / "prototype" / "synthetic_access_sim" / "policies" / "seba_xai_policy_v1.json"

PREDICTION_FIELDS = [
    "method_id",
    "request_id",
    "scenario_type",
    "oracle_decision",
    "predicted_decision",
    "correct",
    "false_allow",
    "false_deny",
    "false_escalate",
    "reason_code",
    "matched_rule_ids",
    "enabled_rule_groups",
    "disabled_rule_groups",
]

COMPARISON_FIELDS = [
    "method_id",
    "method_name",
    "method_type",
    "mode",
    "requests",
    "accuracy",
    "correct_count",
    "false_allow_count",
    "false_deny_count",
    "false_escalate_count",
    "oracle_allow_recall",
    "oracle_deny_recall",
    "oracle_escalate_recall",
    "predicted_allow_count",
    "predicted_deny_count",
    "predicted_escalate_count",
    "decision_latency_ms_p50_total",
    "enabled_rule_group_count",
    "enabled_rule_groups",
    "disabled_rule_groups",
    "status",
    "scope_note",
]

SCENARIO_FIELDS = [
    "method_id",
    "scenario_type",
    "requests",
    "accuracy",
    "correct_count",
    "false_allow_count",
    "false_deny_count",
    "false_escalate_count",
]

ABLATION_EFFECT_FIELDS = [
    "method_id",
    "method_name",
    "method_type",
    "disabled_rule_groups",
    "accuracy_drop_from_full",
    "false_allow_delta_from_full",
    "false_deny_delta_from_full",
    "false_escalate_delta_from_full",
    "extra_errors_vs_full",
    "interpretation",
]

RULE_GROUP_FIELDS = [
    "rule_group",
    "description",
    "rule_ids",
]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def bool_value(raw: object) -> bool:
    return str(raw).strip().lower() == "true"


def int_value(raw: object, default: int = 0) -> int:
    try:
        return int(str(raw))
    except (TypeError, ValueError):
        return default


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def write_yaml(path: Path, values: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in values.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, (int, float)):
            rendered = str(value)
        else:
            rendered = f'"{value}"'
        lines.append(f"{key}: {rendered}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def p50(values: List[float]) -> float:
    if not values:
        return 0.0
    return statistics.median(values)


def list_value(config: Dict[str, object], key: str) -> List[str]:
    return [str(item) for item in config.get(key, [])]


def rule_group_ids(config: Dict[str, object]) -> List[str]:
    groups = config.get("rule_groups", {})
    if not isinstance(groups, dict):
        return []
    return sorted(str(key) for key in groups.keys())


def method_disabled_groups(method: Dict[str, object]) -> set[str]:
    return {str(item) for item in method.get("disabled_rule_groups", [])}


def enabled_groups_for(config: Dict[str, object], method: Dict[str, object]) -> List[str]:
    if method.get("mode") == "rbac":
        return ["rbac_role_action"]
    disabled = method_disabled_groups(method)
    return [group for group in rule_group_ids(config) if group not in disabled]


def group_enabled(enabled_groups: set[str], group: str) -> bool:
    return group in enabled_groups


def add_reason(
    reasons: List[Dict[str, object]],
    *,
    decision: str,
    rule_id: str,
    message: str,
    attributes: Iterable[str],
    required_approval: str = "",
) -> None:
    reasons.append(
        {
            "decision": decision,
            "rule_id": rule_id,
            "message": message,
            "attributes": list(attributes),
            "required_approval": required_approval,
        }
    )


def rbac_decision(row: Dict[str, str], config: Dict[str, object]) -> Dict[str, object]:
    role_actions = config.get("role_actions", {})
    if not isinstance(role_actions, dict):
        role_actions = {}
    thresholds = config.get("thresholds", {})
    if not isinstance(thresholds, dict):
        thresholds = {}

    credential = row["requester_credential_status"]
    role = row["requester_role"]
    rank = int_value(row["requester_rank_level"])
    action = row["action"]
    purpose = row["purpose"]
    supervisor_min_rank = int_value(thresholds.get("supervisor_min_rank", 5), 5)

    if credential != "ACTIVE":
        decision, reason = "deny", "RBAC_DENY_INACTIVE_CREDENTIAL"
    elif purpose == "TRAINING":
        decision, reason = "deny", "RBAC_DENY_TRAINING_PURPOSE"
    elif action == "APPROVE" and rank < supervisor_min_rank:
        decision, reason = "deny", "RBAC_DENY_APPROVAL_REQUIRES_SUPERVISOR"
    elif action in {str(item) for item in role_actions.get(role, ["VIEW"])}:
        decision, reason = "allow", "RBAC_ALLOW_ROLE_ACTION"
    else:
        decision, reason = "deny", "RBAC_DENY_ROLE_ACTION"

    return {
        "decision": decision,
        "reason_code": reason,
        "matched_rule_ids": [reason],
    }


def configured_policy_decision(
    row: Dict[str, str],
    config: Dict[str, object],
    enabled_groups: set[str],
) -> Dict[str, object]:
    reasons: List[Dict[str, object]] = []

    allowed_purposes = set(list_value(config, "allowed_purposes"))
    routine_actions = set(list_value(config, "routine_actions"))
    sensitive_levels = set(list_value(config, "sensitive_levels"))
    privacy_flags = tuple(list_value(config, "privacy_flags"))
    thresholds = config.get("thresholds", {})
    if not isinstance(thresholds, dict):
        thresholds = {}

    credential = row["requester_credential_status"]
    approval = row["approval_token_status"]
    sensitivity = row["record_sensitivity_level"]
    rank_level = int_value(row["requester_rank_level"])
    purpose = row["purpose"]
    action = row["action"]
    case_assignment = row["case_assignment_status"]
    cross_jurisdiction = bool_value(row["cross_jurisdiction"])
    court_or_prosecutor = bool_value(row["court_or_prosecutor_request_flag"])
    emergency = bool_value(row["emergency_flag"])
    sealed = row["sealed_status"] == "SEALED"
    sensitive_record = group_enabled(enabled_groups, "sensitivity") and sensitivity in sensitive_levels
    privacy_sensitive = group_enabled(enabled_groups, "privacy") and any(bool_value(row[flag]) for flag in privacy_flags)
    supervisor_min_rank = int_value(thresholds.get("supervisor_min_rank", 5), 5)
    sensitive_update_min_rank = int_value(thresholds.get("sensitive_update_min_rank", 4), 4)

    if group_enabled(enabled_groups, "credential") and credential != "ACTIVE":
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_INACTIVE_CREDENTIAL",
            message=f"credential status is {credential}",
            attributes=["requester_credential_status"],
        )

    if group_enabled(enabled_groups, "approval") and approval == "EXPIRED":
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_EXPIRED_APPROVAL_TOKEN",
            message="approval token is expired",
            attributes=["approval_token_status"],
        )

    if group_enabled(enabled_groups, "assignment") and case_assignment == "STALE":
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_STALE_CASE_ASSIGNMENT",
            message="case assignment is stale",
            attributes=["case_assignment_status"],
        )

    if group_enabled(enabled_groups, "sealed_record") and sealed and not court_or_prosecutor:
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_SEALED_RECORD_WITHOUT_COURT_CONTEXT",
            message="sealed record request has no court or prosecution context",
            attributes=["sealed_status", "court_or_prosecutor_request_flag"],
        )

    if group_enabled(enabled_groups, "sealed_record") and sealed and court_or_prosecutor:
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_SEALED_RECORD_REVIEW_REQUIRED",
            message="sealed record has court or prosecution context but still requires review",
            attributes=["sealed_status", "court_or_prosecutor_request_flag", "approval_token_status"],
            required_approval="sealed_record_superior_review",
        )

    if group_enabled(enabled_groups, "purpose") and purpose == "TRAINING" and (sensitive_record or privacy_sensitive):
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_TRAINING_PURPOSE_FOR_SENSITIVE_RECORD",
            message="training purpose is not accepted for sensitive police records",
            attributes=["purpose", "record_sensitivity_level", "juvenile_flag", "victim_flag", "witness_flag"],
        )

    if group_enabled(enabled_groups, "action_rank") and action == "APPROVE" and rank_level < supervisor_min_rank:
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_APPROVAL_ACTION_WITHOUT_SUPERVISOR_RANK",
            message="approval action requires supervisor rank",
            attributes=["action", "requester_rank_level"],
        )

    if group_enabled(enabled_groups, "action_rank") and action == "UPDATE" and sensitive_record and rank_level < sensitive_update_min_rank:
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_SENSITIVE_UPDATE_WITH_LOW_RANK",
            message="sensitive record update requires higher rank",
            attributes=["action", "record_sensitivity_level", "requester_rank_level"],
        )

    if group_enabled(enabled_groups, "approval") and sensitive_record and action == "SHARE" and sensitivity == "CLASSIFIED" and approval != "PRESENT_VALID":
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_CLASSIFIED_SHARE_WITHOUT_VALID_APPROVAL",
            message="classified sharing requires valid approval",
            attributes=["action", "record_sensitivity_level", "approval_token_status"],
        )

    if group_enabled(enabled_groups, "emergency") and emergency:
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_EMERGENCY_REVIEW_REQUIRED",
            message="emergency access requires supervisory review",
            attributes=["emergency_flag", "purpose"],
            required_approval="superior_emergency_review",
        )

    if privacy_sensitive:
        active_flags = [flag for flag in privacy_flags if bool_value(row[flag])]
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_PRIVACY_SENSITIVE_RECORD",
            message="juvenile, victim, or witness-sensitive record requires review",
            attributes=active_flags,
            required_approval="sensitive_record_approval",
        )

    if group_enabled(enabled_groups, "jurisdiction") and cross_jurisdiction and sensitive_record:
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_CROSS_JURISDICTION_SENSITIVE_RECORD",
            message="sensitive record is requested across jurisdiction",
            attributes=["cross_jurisdiction", "record_sensitivity_level"],
            required_approval="cross_jurisdiction_superior_approval",
        )

    if group_enabled(enabled_groups, "approval") and sensitive_record and sensitivity == "CLASSIFIED" and approval != "PRESENT_VALID":
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_CLASSIFIED_RECORD_APPROVAL_REQUIRED",
            message="classified record requires valid approval",
            attributes=["record_sensitivity_level", "approval_token_status"],
            required_approval="classified_record_approval",
        )

    if group_enabled(enabled_groups, "approval") and sensitive_record and approval == "MISSING":
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_MISSING_APPROVAL_FOR_SENSITIVE_RECORD",
            message="sensitive record request is missing approval",
            attributes=["approval_token_status", "record_sensitivity_level"],
            required_approval="sensitive_record_approval",
        )

    if group_enabled(enabled_groups, "network") and row["network_status"] == "STATION_NODE_DOWN" and not emergency:
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_NODE_STATUS_DEGRADED",
            message="station node is down and request needs manual review",
            attributes=["network_status"],
            required_approval="manual_node_outage_review",
        )

    deny_reasons = [reason for reason in reasons if reason["decision"] == "deny"]
    escalate_reasons = [reason for reason in reasons if reason["decision"] == "escalate"]

    if deny_reasons:
        decision = "deny"
        selected_reasons = deny_reasons
    elif escalate_reasons:
        decision = "escalate"
        selected_reasons = escalate_reasons
    else:
        credential_ok = credential == "ACTIVE" if group_enabled(enabled_groups, "credential") else True
        purpose_ok = purpose in allowed_purposes if group_enabled(enabled_groups, "purpose") else True
        action_ok = action in routine_actions
        sensitivity_ok = sensitivity in {"LOW", "MEDIUM"} if group_enabled(enabled_groups, "sensitivity") else True
        assignment_ok = case_assignment == "ASSIGNED" if group_enabled(enabled_groups, "assignment") else False
        jurisdiction_ok = not cross_jurisdiction if group_enabled(enabled_groups, "jurisdiction") else True
        routine_context_ok = assignment_ok or jurisdiction_ok or court_or_prosecutor
        routine_allow = (
            group_enabled(enabled_groups, "routine_allow")
            and credential_ok
            and purpose_ok
            and action_ok
            and sensitivity_ok
            and routine_context_ok
        )
        if routine_allow:
            decision = "allow"
            add_reason(
                reasons,
                decision="allow",
                rule_id="ALLOW_ROUTINE_CONTEXTUAL_ACCESS",
                message="request satisfies routine contextual access conditions",
                attributes=[
                    "requester_credential_status",
                    "case_assignment_status",
                    "cross_jurisdiction",
                    "purpose",
                    "action",
                    "record_sensitivity_level",
                ],
            )
            selected_reasons = [reasons[-1]]
        elif group_enabled(enabled_groups, "fallback_review"):
            decision = "escalate"
            add_reason(
                reasons,
                decision="escalate",
                rule_id="ESCALATE_CONTEXTUAL_REVIEW_REQUIRED",
                message="request does not satisfy routine allow conditions",
                attributes=[
                    "case_assignment_status",
                    "cross_jurisdiction",
                    "purpose",
                    "action",
                    "record_sensitivity_level",
                ],
                required_approval="contextual_superior_review",
            )
            selected_reasons = [reasons[-1]]
        else:
            decision = "allow"
            add_reason(
                reasons,
                decision="allow",
                rule_id="ABLATION_ALLOW_NO_FALLBACK_REVIEW",
                message="fallback review is disabled in this ablation",
                attributes=["fallback_review"],
            )
            selected_reasons = [reasons[-1]]

    return {
        "decision": decision,
        "reason_code": str(selected_reasons[0]["rule_id"]),
        "matched_rule_ids": [str(reason["rule_id"]) for reason in selected_reasons],
    }


def evaluate_method(row: Dict[str, str], config: Dict[str, object], method: Dict[str, object]) -> Dict[str, object]:
    if method.get("mode") == "rbac":
        return rbac_decision(row, config)
    return configured_policy_decision(row, config, set(enabled_groups_for(config, method)))


def build_predictions(
    request_rows: List[Dict[str, str]],
    labeled_by_request: Dict[str, Dict[str, str]],
    config: Dict[str, object],
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    methods = config.get("ablation_methods", [])
    if not isinstance(methods, list):
        methods = []

    for method in methods:
        if not isinstance(method, dict):
            continue
        enabled_groups = enabled_groups_for(config, method)
        disabled_groups = sorted(method_disabled_groups(method))
        for request in request_rows:
            oracle_row = labeled_by_request[request["request_id"]]
            predicted = evaluate_method(request, config, method)
            oracle_decision = oracle_row["decision"]
            predicted_decision = str(predicted["decision"])
            rows.append(
                {
                    "method_id": method["method_id"],
                    "request_id": request["request_id"],
                    "scenario_type": request["scenario_type"],
                    "oracle_decision": oracle_decision,
                    "predicted_decision": predicted_decision,
                    "correct": str(predicted_decision == oracle_decision).lower(),
                    "false_allow": str(predicted_decision == "allow" and oracle_decision != "allow").lower(),
                    "false_deny": str(predicted_decision == "deny" and oracle_decision != "deny").lower(),
                    "false_escalate": str(predicted_decision == "escalate" and oracle_decision != "escalate").lower(),
                    "reason_code": predicted["reason_code"],
                    "matched_rule_ids": "|".join(str(rule_id) for rule_id in predicted["matched_rule_ids"]),
                    "enabled_rule_groups": "|".join(enabled_groups),
                    "disabled_rule_groups": "|".join(disabled_groups) if disabled_groups else "none",
                }
            )
    return rows


def recall_for(rows: List[Dict[str, object]], label: str) -> float:
    label_rows = [row for row in rows if row["oracle_decision"] == label]
    if not label_rows:
        return 0.0
    correct = sum(1 for row in label_rows if row["predicted_decision"] == label)
    return correct / len(label_rows)


def measure_method_latencies(
    request_rows: List[Dict[str, str]],
    config: Dict[str, object],
    repeats: int,
) -> Dict[str, float]:
    methods = [method for method in config.get("ablation_methods", []) if isinstance(method, dict)]
    totals: Dict[str, List[float]] = {str(method["method_id"]): [] for method in methods}
    for _ in range(repeats):
        for method in methods:
            method_id = str(method["method_id"])
            start = time.perf_counter_ns()
            for request in request_rows:
                evaluate_method(request, config, method)
            totals[method_id].append((time.perf_counter_ns() - start) / 1_000_000)
    return {method_id: p50(values) for method_id, values in totals.items()}


def build_comparison(
    prediction_rows: List[Dict[str, object]],
    config: Dict[str, object],
    latencies: Dict[str, float],
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    methods = [method for method in config.get("ablation_methods", []) if isinstance(method, dict)]
    by_method: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for row in prediction_rows:
        by_method[str(row["method_id"])].append(row)

    for method in methods:
        method_id = str(method["method_id"])
        subset = by_method[method_id]
        total = len(subset)
        correct = sum(1 for row in subset if row["correct"] == "true")
        false_allow = sum(1 for row in subset if row["false_allow"] == "true")
        false_deny = sum(1 for row in subset if row["false_deny"] == "true")
        false_escalate = sum(1 for row in subset if row["false_escalate"] == "true")
        predicted_counts = Counter(str(row["predicted_decision"]) for row in subset)
        enabled_groups = enabled_groups_for(config, method)
        disabled_groups = sorted(method_disabled_groups(method))
        rows.append(
            {
                "method_id": method_id,
                "method_name": method["method_name"],
                "method_type": method["method_type"],
                "mode": method["mode"],
                "requests": total,
                "accuracy": f"{correct / total:.4f}" if total else "0.0000",
                "correct_count": correct,
                "false_allow_count": false_allow,
                "false_deny_count": false_deny,
                "false_escalate_count": false_escalate,
                "oracle_allow_recall": f"{recall_for(subset, 'allow'):.4f}",
                "oracle_deny_recall": f"{recall_for(subset, 'deny'):.4f}",
                "oracle_escalate_recall": f"{recall_for(subset, 'escalate'):.4f}",
                "predicted_allow_count": predicted_counts.get("allow", 0),
                "predicted_deny_count": predicted_counts.get("deny", 0),
                "predicted_escalate_count": predicted_counts.get("escalate", 0),
                "decision_latency_ms_p50_total": f"{latencies.get(method_id, 0.0):.6f}",
                "enabled_rule_group_count": len(enabled_groups),
                "enabled_rule_groups": "|".join(enabled_groups),
                "disabled_rule_groups": "|".join(disabled_groups) if disabled_groups else "none",
                "status": "proposed" if method_id == "full_configured_pbac" else str(method["method_type"]),
                "scope_note": method["description"],
            }
        )
    return rows


def build_scenario_breakdown(prediction_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    grouped: Dict[Tuple[str, str], List[Dict[str, object]]] = defaultdict(list)
    for row in prediction_rows:
        grouped[(str(row["method_id"]), str(row["scenario_type"]))].append(row)

    for (method_id, scenario), subset in sorted(grouped.items()):
        total = len(subset)
        correct = sum(1 for row in subset if row["correct"] == "true")
        false_allow = sum(1 for row in subset if row["false_allow"] == "true")
        false_deny = sum(1 for row in subset if row["false_deny"] == "true")
        false_escalate = sum(1 for row in subset if row["false_escalate"] == "true")
        rows.append(
            {
                "method_id": method_id,
                "scenario_type": scenario,
                "requests": total,
                "accuracy": f"{correct / total:.4f}" if total else "0.0000",
                "correct_count": correct,
                "false_allow_count": false_allow,
                "false_deny_count": false_deny,
                "false_escalate_count": false_escalate,
            }
        )
    return rows


def row_by_method(rows: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    return {str(row["method_id"]): row for row in rows}


def build_ablation_effects(comparison_rows: List[Dict[str, object]], config: Dict[str, object]) -> List[Dict[str, object]]:
    by_method = row_by_method(comparison_rows)
    full = by_method["full_configured_pbac"]
    full_accuracy = float(full["accuracy"])
    full_false_allow = int(full["false_allow_count"])
    full_false_deny = int(full["false_deny_count"])
    full_false_escalate = int(full["false_escalate_count"])
    full_errors = int(full["requests"]) - int(full["correct_count"])
    method_defs = {
        str(method["method_id"]): method
        for method in config.get("ablation_methods", [])
        if isinstance(method, dict)
    }

    rows: List[Dict[str, object]] = []
    for comparison in comparison_rows:
        method_id = str(comparison["method_id"])
        method = method_defs[method_id]
        accuracy = float(comparison["accuracy"])
        false_allow_delta = int(comparison["false_allow_count"]) - full_false_allow
        false_deny_delta = int(comparison["false_deny_count"]) - full_false_deny
        false_escalate_delta = int(comparison["false_escalate_count"]) - full_false_escalate
        errors = int(comparison["requests"]) - int(comparison["correct_count"])
        extra_errors = errors - full_errors
        if method_id == "full_configured_pbac":
            interpretation = "Reference configured policy; should match Step 2 oracle if configuration and evaluator are aligned."
        elif false_allow_delta > 0:
            interpretation = "Removal increases false allows, which is high risk for sensitive access governance."
        elif false_deny_delta > 0:
            interpretation = "Removal increases false denials, which may block legitimate work."
        elif false_escalate_delta > 0:
            interpretation = "Removal increases unnecessary escalations."
        else:
            interpretation = "No additional error against the configured reference in this synthetic workload."
        disabled_groups = sorted(method_disabled_groups(method))
        rows.append(
            {
                "method_id": method_id,
                "method_name": method["method_name"],
                "method_type": method["method_type"],
                "disabled_rule_groups": "|".join(disabled_groups) if disabled_groups else "none",
                "accuracy_drop_from_full": f"{full_accuracy - accuracy:.4f}",
                "false_allow_delta_from_full": false_allow_delta,
                "false_deny_delta_from_full": false_deny_delta,
                "false_escalate_delta_from_full": false_escalate_delta,
                "extra_errors_vs_full": extra_errors,
                "interpretation": interpretation,
            }
        )
    return rows


def build_rule_group_rows(config: Dict[str, object]) -> List[Dict[str, object]]:
    groups = config.get("rule_groups", {})
    if not isinstance(groups, dict):
        return []
    rows: List[Dict[str, object]] = []
    for group_id, details in sorted(groups.items()):
        if not isinstance(details, dict):
            details = {}
        rows.append(
            {
                "rule_group": group_id,
                "description": details.get("description", ""),
                "rule_ids": "|".join(str(rule_id) for rule_id in details.get("rule_ids", [])),
            }
        )
    return rows


def build_metrics(
    comparison_rows: List[Dict[str, object]],
    ablation_rows: List[Dict[str, object]],
    input_files: Dict[str, Path],
    config: Dict[str, object],
) -> Dict[str, object]:
    by_method = row_by_method(comparison_rows)
    full = by_method["full_configured_pbac"]
    highest_false_allow = max(comparison_rows, key=lambda row: int(row["false_allow_count"]))
    return {
        "artifact_type": "configured_policy_ablation_experiment",
        "result_claim": "synthetic policy-oracle consistency and policy-group ablation only",
        "policy_version": config.get("policy_version", ""),
        "input_files": {key: str(path) for key, path in input_files.items()},
        "method_count": len(comparison_rows),
        "request_count": int(full["requests"]),
        "full_configured_policy_accuracy": full["accuracy"],
        "full_configured_policy_false_allows": int(full["false_allow_count"]),
        "highest_false_allow_method_id": highest_false_allow["method_id"],
        "highest_false_allow_count": int(highest_false_allow["false_allow_count"]),
        "ablation_effects": ablation_rows,
        "important_interpretation": [
            "The Step 2 policy oracle is the reference label; these are not real police access-control labels.",
            "False allows are treated as the highest-risk error because they represent access granted where the reference policy would deny or escalate.",
            "Ablation rows show which policy dimensions matter under the synthetic workload.",
        ],
        "limitations": [
            "Policy rules are synthetic and conservative; they are not official CCTNS, ICJS, or police rules.",
            "The configured evaluator is still local Python logic over a JSON policy structure, not a production policy engine such as OPA or XACML.",
            "No legal compliance or operational deployment claim is made.",
            "No human expert labels or real police access decisions are used.",
        ],
    }


def data_dictionary_text() -> str:
    return """# Policy Ablation Data Dictionary

This file describes Step 8 outputs.

## Important Boundary

The Step 2 policy oracle is used as the deterministic reference label. The
reported accuracy values mean agreement with the synthetic oracle, not real
police access-control accuracy.

## Core Files

- `policy_config_snapshot.json`: policy configuration used for this run.
- `policy_rule_group_summary.csv`: configured rule groups and rule IDs.
- `policy_ablation_predictions.csv`: per-request prediction for every method.
- `policy_ablation_comparison.csv`: one row per baseline/proposed/ablation method.
- `policy_ablation_by_scenario.csv`: per-scenario error breakdown.
- `policy_ablation_effects.csv`: error deltas relative to full configured PBAC.

## Key Fields

| Field | Meaning |
|---|---|
| `false_allow_count` | Method allowed a request that the reference policy did not allow. |
| `false_deny_count` | Method denied a request that the reference policy did not deny. |
| `false_escalate_count` | Method escalated a request that the reference policy did not escalate. |
| `disabled_rule_groups` | Policy dimensions removed for the ablation. |
| `accuracy_drop_from_full` | Difference from the full configured policy row. |
| `decision_latency_ms_p50_total` | Local median total time to evaluate all synthetic requests. |

## Correct Interpretation

This step helps justify the security/access-control pillar by showing the
effect of removing approval, assignment, sealed-record, privacy, jurisdiction,
sensitivity, emergency/network, and fallback-review rules.
"""


def run_readme_text(run_id: str, policy_version: object, request_count: int, method_count: int) -> str:
    return f"""# Run {run_id}

Purpose: Step 8 configured PBAC/ABAC policy ablation.

Policy version: `{policy_version}`

Synthetic requests evaluated: `{request_count}`

Methods compared: `{method_count}`

## What This Run Contains

- configured policy snapshot;
- rule-group summary;
- per-request predictions;
- method comparison table;
- scenario-level error table;
- ablation effects relative to full configured PBAC.

## What This Run Does Not Contain

- No real CCTNS, ICJS, FIR, police, victim, witness, or case data.
- No official Indian police access-control policy.
- No legal-compliance proof.
- No production policy engine.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/policy_ablation.py \\
  --run-id {run_id}
```
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SEBA-XAI configured policy ablations.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--step1-run-id", default=DEFAULT_STEP1_RUN_ID)
    parser.add_argument("--step2-run-id", default=DEFAULT_STEP2_RUN_ID)
    parser.add_argument("--policy-config", default=str(DEFAULT_POLICY_CONFIG))
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument(
        "--prototype-results-summary-table",
        default=str(ROOT / "prototype" / "results" / "tables" / "policy_ablation_step8_comparison.csv"),
    )
    parser.add_argument(
        "--root-results-summary-table",
        default=str(ROOT / "results" / "tables" / "policy_ablation_step8_comparison.csv"),
    )
    parser.add_argument("--experiment-run-record", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = ROOT / "prototype" / "runs" / args.run_id
    artifacts_dir = run_dir / "artifacts"
    logs_dir = run_dir / "logs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    request_file = ROOT / "prototype" / "runs" / args.step1_run_id / "artifacts" / "access_requests.csv"
    labeled_file = ROOT / "prototype" / "runs" / args.step2_run_id / "artifacts" / "labeled_access_requests.csv"
    policy_config_file = Path(args.policy_config)
    input_files = {
        "request_file": request_file,
        "labeled_file": labeled_file,
        "policy_config_file": policy_config_file,
    }

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    config = read_json(policy_config_file)
    run_config = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "step1_run_id": args.step1_run_id,
        "step2_run_id": args.step2_run_id,
        "policy_config": str(policy_config_file),
        "policy_version": config.get("policy_version", ""),
        "repeats": args.repeats,
        "step": "step_8_policy_config_ablation",
        "synthetic_only": True,
        "oracle_ground_truth": "step2_policy_oracle_labels",
    }
    write_yaml(run_dir / "config.yaml", run_config)

    request_rows = read_csv(request_file)
    labeled_rows = read_csv(labeled_file)
    labeled_by_request = {row["request_id"]: row for row in labeled_rows}

    prediction_rows = build_predictions(request_rows, labeled_by_request, config)
    latencies = measure_method_latencies(request_rows, config, args.repeats)
    comparison_rows = build_comparison(prediction_rows, config, latencies)
    scenario_rows = build_scenario_breakdown(prediction_rows)
    ablation_rows = build_ablation_effects(comparison_rows, config)
    rule_group_rows = build_rule_group_rows(config)

    config_snapshot_path = artifacts_dir / "policy_config_snapshot.json"
    rule_group_path = artifacts_dir / "policy_rule_group_summary.csv"
    predictions_path = artifacts_dir / "policy_ablation_predictions.csv"
    comparison_path = artifacts_dir / "policy_ablation_comparison.csv"
    scenario_path = artifacts_dir / "policy_ablation_by_scenario.csv"
    effects_path = artifacts_dir / "policy_ablation_effects.csv"

    write_json(config_snapshot_path, config)
    write_csv(rule_group_path, rule_group_rows, RULE_GROUP_FIELDS)
    write_csv(predictions_path, prediction_rows, PREDICTION_FIELDS)
    write_csv(comparison_path, comparison_rows, COMPARISON_FIELDS)
    write_csv(Path(args.prototype_results_summary_table), comparison_rows, COMPARISON_FIELDS)
    write_csv(Path(args.root_results_summary_table), comparison_rows, COMPARISON_FIELDS)
    write_csv(scenario_path, scenario_rows, SCENARIO_FIELDS)
    write_csv(effects_path, ablation_rows, ABLATION_EFFECT_FIELDS)

    metrics = build_metrics(comparison_rows, ablation_rows, input_files, config)
    write_json(run_dir / "metrics.json", metrics)

    artifact_files = [
        "policy_config_snapshot.json",
        "policy_rule_group_summary.csv",
        "policy_ablation_predictions.csv",
        "policy_ablation_comparison.csv",
        "policy_ablation_by_scenario.csv",
        "policy_ablation_effects.csv",
    ]
    manifest = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "policy_version": config.get("policy_version", ""),
        "synthetic_only": True,
        "oracle_ground_truth": "step2_policy_oracle_labels",
        "input_hashes": {key: file_sha256(path) for key, path in input_files.items()},
        "artifact_hashes": {
            filename: file_sha256(artifacts_dir / filename)
            for filename in artifact_files
        },
        "notes": [
            "This run evaluates policy ablations against the deterministic Step 2 oracle.",
            "Accuracy means policy-oracle consistency only.",
            "The configured policy is a research prototype, not an official police policy.",
        ],
    }
    write_json(artifacts_dir / "dataset_manifest.json", manifest)
    (artifacts_dir / "README.md").write_text(
        run_readme_text(args.run_id, config.get("policy_version", ""), len(request_rows), len(comparison_rows)),
        encoding="utf-8",
    )
    (artifacts_dir / "data_dictionary.md").write_text(data_dictionary_text(), encoding="utf-8")

    experiment_run_record_path = (
        Path(args.experiment_run_record)
        if args.experiment_run_record
        else ROOT / "experiments" / "runs" / f"{args.run_id}.json"
    )
    write_json(
        experiment_run_record_path,
        {
            "run_id": args.run_id,
            "created_at_utc": created_at,
            "prototype_run_dir": str(run_dir),
            "summary_table": str(args.root_results_summary_table),
            "artifact_type": "step_8_policy_config_ablation",
            "result_claim": metrics["result_claim"],
            "synthetic_only": True,
            "limitations": metrics["limitations"],
        },
    )

    full_row = row_by_method(comparison_rows)["full_configured_pbac"]
    highest_false_allow = max(comparison_rows, key=lambda row: int(row["false_allow_count"]))
    log_lines = [
        f"created_at_utc={created_at}",
        f"run_id={args.run_id}",
        f"requests={len(request_rows)}",
        f"methods={len(comparison_rows)}",
        f"full_configured_pbac_accuracy={full_row['accuracy']}",
        f"highest_false_allow_method={highest_false_allow['method_id']}",
        f"highest_false_allow_count={highest_false_allow['false_allow_count']}",
        "status=success",
        "claim=synthetic_policy_ablation_only",
    ]
    (logs_dir / "policy_ablation.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Wrote policy-ablation run: {run_dir}")
    print(f"Requests: {len(request_rows)}")
    print(f"Methods: {len(comparison_rows)}")
    print(f"Full configured PBAC accuracy: {full_row['accuracy']}")
    print(f"Highest false-allow method: {highest_false_allow['method_id']} ({highest_false_allow['false_allow_count']})")
    print(f"Summary table: {args.prototype_results_summary_table}")


if __name__ == "__main__":
    main()
