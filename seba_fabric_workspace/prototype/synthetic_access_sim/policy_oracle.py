#!/usr/bin/env python3
"""Apply deterministic policy rules and basic XAI explanations to access requests.

This is Step 2 of the SEBA-XAI prototype. It reads the synthetic request
workload from Step 1 and produces labeled allow/deny/escalate decisions.

The explanations are rule-trace explanations. They are intentionally simple
and deterministic so that future blockchain audit tests can verify stable
decision and explanation hashes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_RUN_ID = "20260527_step1_synthetic_requests_seed42"
DEFAULT_RUN_ID = "20260527_step2_policy_oracle_seed42"
POLICY_VERSION = "P-2026-05-STEP2-ORACLE"

ALLOWED_PURPOSES = {
    "INVESTIGATION",
    "SUPERVISION",
    "FORENSIC_REVIEW",
    "PROSECUTION_REVIEW",
    "COURT_PRODUCTION",
    "AUDIT",
    "EMERGENCY_RESPONSE",
}

ROUTINE_ACTIONS = {"VIEW", "DOWNLOAD"}
SENSITIVE_LEVELS = {"HIGH", "CLASSIFIED"}
PRIVACY_FLAGS = ("juvenile_flag", "victim_flag", "witness_flag")


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


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def evaluate_policy(row: Dict[str, str]) -> Dict[str, object]:
    """Evaluate one synthetic request using conservative policy precedence."""

    reasons: List[Dict[str, object]] = []
    positive_factors: List[str] = []

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
    sensitive_record = sensitivity in SENSITIVE_LEVELS
    privacy_sensitive = any(bool_value(row[flag]) for flag in PRIVACY_FLAGS)

    if credential != "ACTIVE":
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_INACTIVE_CREDENTIAL",
            message=f"credential status is {credential}",
            attributes=["requester_credential_status"],
        )

    if approval == "EXPIRED":
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_EXPIRED_APPROVAL_TOKEN",
            message="approval token is expired",
            attributes=["approval_token_status"],
        )

    if case_assignment == "STALE":
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_STALE_CASE_ASSIGNMENT",
            message="case assignment is stale",
            attributes=["case_assignment_status"],
        )

    if sealed and not court_or_prosecutor:
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_SEALED_RECORD_WITHOUT_COURT_CONTEXT",
            message="sealed record request has no court or prosecution context",
            attributes=["sealed_status", "court_or_prosecutor_request_flag"],
        )

    if sealed and court_or_prosecutor:
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_SEALED_RECORD_REVIEW_REQUIRED",
            message="sealed record has court or prosecution context but still requires review",
            attributes=["sealed_status", "court_or_prosecutor_request_flag", "approval_token_status"],
            required_approval="sealed_record_superior_review",
        )

    if purpose == "TRAINING" and (sensitive_record or privacy_sensitive):
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_TRAINING_PURPOSE_FOR_SENSITIVE_RECORD",
            message="training purpose is not accepted for sensitive police records",
            attributes=["purpose", "record_sensitivity_level", "juvenile_flag", "victim_flag", "witness_flag"],
        )

    if action == "APPROVE" and rank_level < 5:
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_APPROVAL_ACTION_WITHOUT_SUPERVISOR_RANK",
            message="approval action requires supervisor rank",
            attributes=["action", "requester_rank_level"],
        )

    if action == "UPDATE" and sensitive_record and rank_level < 4:
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_SENSITIVE_UPDATE_WITH_LOW_RANK",
            message="sensitive record update requires higher rank",
            attributes=["action", "record_sensitivity_level", "requester_rank_level"],
        )

    if action == "SHARE" and sensitivity == "CLASSIFIED" and approval != "PRESENT_VALID":
        add_reason(
            reasons,
            decision="deny",
            rule_id="DENY_CLASSIFIED_SHARE_WITHOUT_VALID_APPROVAL",
            message="classified sharing requires valid approval",
            attributes=["action", "record_sensitivity_level", "approval_token_status"],
        )

    if emergency:
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_EMERGENCY_REVIEW_REQUIRED",
            message="emergency access requires supervisory review",
            attributes=["emergency_flag", "purpose"],
            required_approval="superior_emergency_review",
        )

    if privacy_sensitive:
        active_flags = [flag for flag in PRIVACY_FLAGS if bool_value(row[flag])]
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_PRIVACY_SENSITIVE_RECORD",
            message="juvenile, victim, or witness-sensitive record requires review",
            attributes=active_flags,
            required_approval="sensitive_record_approval",
        )

    if cross_jurisdiction and sensitive_record:
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_CROSS_JURISDICTION_SENSITIVE_RECORD",
            message="sensitive record is requested across jurisdiction",
            attributes=["cross_jurisdiction", "record_sensitivity_level"],
            required_approval="cross_jurisdiction_superior_approval",
        )

    if sensitivity == "CLASSIFIED" and approval != "PRESENT_VALID":
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_CLASSIFIED_RECORD_APPROVAL_REQUIRED",
            message="classified record requires valid approval",
            attributes=["record_sensitivity_level", "approval_token_status"],
            required_approval="classified_record_approval",
        )

    if approval == "MISSING" and sensitive_record:
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_MISSING_APPROVAL_FOR_SENSITIVE_RECORD",
            message="sensitive record request is missing approval",
            attributes=["approval_token_status", "record_sensitivity_level"],
            required_approval="sensitive_record_approval",
        )

    if row["network_status"] == "STATION_NODE_DOWN" and not emergency:
        add_reason(
            reasons,
            decision="escalate",
            rule_id="ESCALATE_NODE_STATUS_DEGRADED",
            message="station node is down and request needs manual review",
            attributes=["network_status"],
            required_approval="manual_node_outage_review",
        )

    if credential == "ACTIVE":
        positive_factors.append("active credential")
    if case_assignment == "ASSIGNED":
        positive_factors.append("officer is assigned to the case")
    if not cross_jurisdiction:
        positive_factors.append("request is within jurisdiction")
    if purpose in ALLOWED_PURPOSES:
        positive_factors.append("purpose is recognized by policy")
    if action in ROUTINE_ACTIONS:
        positive_factors.append("requested action is routine")

    deny_reasons = [reason for reason in reasons if reason["decision"] == "deny"]
    escalate_reasons = [reason for reason in reasons if reason["decision"] == "escalate"]

    if deny_reasons:
        decision = "deny"
        selected_reasons = deny_reasons
    elif escalate_reasons:
        decision = "escalate"
        selected_reasons = escalate_reasons
    else:
        routine_allow = (
            credential == "ACTIVE"
            and purpose in ALLOWED_PURPOSES
            and action in ROUTINE_ACTIONS
            and sensitivity in {"LOW", "MEDIUM"}
            and (case_assignment == "ASSIGNED" or not cross_jurisdiction or court_or_prosecutor)
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
        else:
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

    primary_reason = str(selected_reasons[0]["rule_id"])
    decisive_attributes = sorted(
        {
            attribute
            for reason in selected_reasons
            for attribute in reason["attributes"]
        }
    )
    failed_rules = [str(reason["rule_id"]) for reason in reasons if reason["decision"] in {"deny", "escalate"}]
    required_approvals = sorted(
        {
            str(reason["required_approval"])
            for reason in selected_reasons
            if reason.get("required_approval")
        }
    )
    explanation = build_explanation(row, decision, selected_reasons, positive_factors)
    explanation_artifact = {
        "request_id": row["request_id"],
        "decision": decision,
        "policy_version": POLICY_VERSION,
        "primary_reason_code": primary_reason,
        "matched_rule_ids": [str(reason["rule_id"]) for reason in selected_reasons],
        "decisive_attributes": decisive_attributes,
        "supporting_factors": positive_factors,
        "explanation": explanation,
    }
    explanation_hash = stable_hash(explanation_artifact)
    decision_payload = {
        "request_id": row["request_id"],
        "request_content_hash": row["request_content_hash"],
        "decision": decision,
        "policy_version": POLICY_VERSION,
        "primary_reason_code": primary_reason,
        "decisive_attributes": decisive_attributes,
    }
    decision_hash = stable_hash(decision_payload)
    audit_anchor_hash = stable_hash(
        {
            "request_content_hash": row["request_content_hash"],
            "decision_hash": decision_hash,
            "explanation_hash": explanation_hash,
            "policy_version": POLICY_VERSION,
        }
    )

    return {
        "decision": decision,
        "primary_reason_code": primary_reason,
        "matched_rule_ids": "|".join(str(reason["rule_id"]) for reason in selected_reasons),
        "all_triggered_rule_ids": "|".join(str(reason["rule_id"]) for reason in reasons),
        "decisive_attributes": "|".join(decisive_attributes),
        "failed_or_review_rules": "|".join(failed_rules),
        "required_approval": "|".join(required_approvals) if required_approvals else "none",
        "xai_explanation": explanation,
        "xai_supporting_factors": "|".join(positive_factors) if positive_factors else "none",
        "policy_version_evaluated": POLICY_VERSION,
        "decision_hash": decision_hash,
        "explanation_hash": explanation_hash,
        "audit_anchor_hash": audit_anchor_hash,
        "explanation_artifact": explanation_artifact,
    }


def build_explanation(
    row: Dict[str, str],
    decision: str,
    selected_reasons: List[Dict[str, object]],
    positive_factors: List[str],
) -> str:
    reason_messages = [str(reason["message"]) for reason in selected_reasons[:3]]
    reason_text = "; ".join(reason_messages)
    base = {
        "allow": "Access was allowed",
        "deny": "Access was denied",
        "escalate": "Access was escalated for senior review",
    }[decision]
    context = (
        f"Requester role={row['requester_role']}, record type={row['target_record_type']}, "
        f"sensitivity={row['record_sensitivity_level']}, purpose={row['purpose']}."
    )
    support = ""
    if positive_factors:
        support = " Supporting factors: " + ", ".join(positive_factors[:4]) + "."
    return f"{base} because {reason_text}. {context}{support}"


def label_requests(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    labeled_rows: List[Dict[str, object]] = []
    explanation_artifacts: List[Dict[str, object]] = []
    for row in rows:
        evaluation = evaluate_policy(row)
        explanation_artifacts.append(evaluation.pop("explanation_artifact"))
        labeled = dict(row)
        labeled.update(evaluation)
        labeled_rows.append(labeled)
    return labeled_rows, explanation_artifacts


def build_summary_rows(labeled_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []

    def add_counter(group: str, counter: Counter) -> None:
        for value, count in sorted(counter.items(), key=lambda item: str(item[0])):
            rows.append({"summary_group": group, "value": value, "count": count})

    add_counter("decision", Counter(row["decision"] for row in labeled_rows))
    add_counter("decision_by_scenario", Counter(f"{row['scenario_type']}::{row['decision']}" for row in labeled_rows))
    add_counter("primary_reason_code", Counter(row["primary_reason_code"] for row in labeled_rows))
    add_counter("required_approval", Counter(row["required_approval"] for row in labeled_rows))
    add_counter("sensitivity_by_decision", Counter(f"{row['record_sensitivity_level']}::{row['decision']}" for row in labeled_rows))
    return rows


def build_metrics(labeled_rows: List[Dict[str, object]], input_file: Path) -> Dict[str, object]:
    return {
        "artifact_type": "policy_oracle_labels",
        "result_claim": "none; deterministic policy labels and explanations only",
        "input_file": str(input_file),
        "policy_version": POLICY_VERSION,
        "counts": {
            "requests_evaluated": len(labeled_rows),
            "decisions": dict(Counter(row["decision"] for row in labeled_rows)),
            "primary_reason_codes": dict(Counter(row["primary_reason_code"] for row in labeled_rows)),
            "required_approvals": dict(Counter(row["required_approval"] for row in labeled_rows)),
        },
        "hash_fields_created": [
            "decision_hash",
            "explanation_hash",
            "audit_anchor_hash",
        ],
        "xai_type": "deterministic rule-trace explanation",
        "limitations": [
            "This is a policy oracle, not a trained AI model.",
            "Explanations are rule-trace explanations, not SHAP/LIME/model-attribution explanations.",
            "Labels are generated from synthetic policy assumptions and are not real police access decisions.",
            "No blockchain ledger write has been implemented in this step.",
        ],
    }


def policy_rules() -> Dict[str, object]:
    return {
        "policy_version": POLICY_VERSION,
        "decision_precedence": ["deny", "escalate", "allow"],
        "deny_rules": [
            "DENY_INACTIVE_CREDENTIAL",
            "DENY_EXPIRED_APPROVAL_TOKEN",
            "DENY_STALE_CASE_ASSIGNMENT",
            "DENY_SEALED_RECORD_WITHOUT_COURT_CONTEXT",
            "DENY_TRAINING_PURPOSE_FOR_SENSITIVE_RECORD",
            "DENY_APPROVAL_ACTION_WITHOUT_SUPERVISOR_RANK",
            "DENY_SENSITIVE_UPDATE_WITH_LOW_RANK",
            "DENY_CLASSIFIED_SHARE_WITHOUT_VALID_APPROVAL",
        ],
        "escalation_rules": [
            "ESCALATE_EMERGENCY_REVIEW_REQUIRED",
            "ESCALATE_PRIVACY_SENSITIVE_RECORD",
            "ESCALATE_CROSS_JURISDICTION_SENSITIVE_RECORD",
            "ESCALATE_CLASSIFIED_RECORD_APPROVAL_REQUIRED",
            "ESCALATE_MISSING_APPROVAL_FOR_SENSITIVE_RECORD",
            "ESCALATE_SEALED_RECORD_REVIEW_REQUIRED",
            "ESCALATE_NODE_STATUS_DEGRADED",
            "ESCALATE_CONTEXTUAL_REVIEW_REQUIRED",
        ],
        "allow_rule": "ALLOW_ROUTINE_CONTEXTUAL_ACCESS",
        "raw_records_on_chain": False,
        "xai_type": "rule_trace",
    }


def write_jsonl(path: Path, rows: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply deterministic SEBA-XAI policy oracle labels.")
    parser.add_argument("--input-run-id", default=DEFAULT_INPUT_RUN_ID)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--input-file", default="")
    parser.add_argument(
        "--results-summary-table",
        default=str(ROOT / "prototype" / "results" / "tables" / "policy_oracle_step2_summary.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_file = Path(args.input_file) if args.input_file else (
        ROOT / "prototype" / "runs" / args.input_run_id / "artifacts" / "access_requests.csv"
    )
    run_dir = ROOT / "prototype" / "runs" / args.run_id
    artifacts_dir = run_dir / "artifacts"
    logs_dir = run_dir / "logs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    config = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "input_run_id": args.input_run_id,
        "input_file": str(input_file),
        "policy_version": POLICY_VERSION,
        "step": "step_2_policy_oracle_and_rule_trace_xai",
        "synthetic_only": True,
        "raw_record_included": False,
    }
    write_yaml(run_dir / "config.yaml", config)

    input_rows = read_csv(input_file)
    labeled_rows, explanation_artifacts = label_requests(input_rows)
    summary_rows = build_summary_rows(labeled_rows)
    metrics = build_metrics(labeled_rows, input_file)

    labeled_file = artifacts_dir / "labeled_access_requests.csv"
    summary_file = artifacts_dir / "policy_summary.csv"
    explanation_file = artifacts_dir / "explanation_artifacts.jsonl"
    rules_file = artifacts_dir / "policy_rules.json"

    write_csv(labeled_file, labeled_rows)
    write_csv(summary_file, summary_rows)
    write_csv(Path(args.results_summary_table), summary_rows)
    write_jsonl(explanation_file, explanation_artifacts)
    write_json(rules_file, policy_rules())
    write_json(run_dir / "metrics.json", metrics)

    artifact_files = [
        "labeled_access_requests.csv",
        "policy_summary.csv",
        "explanation_artifacts.jsonl",
        "policy_rules.json",
    ]
    manifest = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "input_file": str(input_file),
        "input_file_sha256": file_sha256(input_file),
        "policy_version": POLICY_VERSION,
        "synthetic_only": True,
        "raw_record_included": False,
        "artifact_hashes": {
            filename: file_sha256(artifacts_dir / filename)
            for filename in artifact_files
        },
        "notes": [
            "This run produces deterministic policy labels and rule-trace explanations.",
            "It is not a blockchain audit run and not a trained AI experiment.",
        ],
    }
    write_json(artifacts_dir / "dataset_manifest.json", manifest)
    (artifacts_dir / "README.md").write_text(run_readme_text(args.run_id, args.input_run_id, len(labeled_rows)), encoding="utf-8")
    (artifacts_dir / "data_dictionary.md").write_text(data_dictionary_text(), encoding="utf-8")

    log_lines = [
        f"created_at_utc={created_at}",
        f"run_id={args.run_id}",
        f"input_file={input_file}",
        f"requests_evaluated={len(labeled_rows)}",
        f"decision_counts={dict(Counter(row['decision'] for row in labeled_rows))}",
        "status=success",
        "claim=policy_labels_only_no_blockchain_or_trained_model_result",
    ]
    (logs_dir / "policy_oracle.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Wrote policy-oracle run: {run_dir}")
    print(f"Requests evaluated: {len(labeled_rows)}")
    print(f"Decision counts: {dict(Counter(row['decision'] for row in labeled_rows))}")
    print(f"Summary table: {args.results_summary_table}")


def run_readme_text(run_id: str, input_run_id: str, request_count: int) -> str:
    return f"""# Run {run_id}

Purpose: Step 2 deterministic policy oracle and basic XAI explanation generation.

Input run: `{input_run_id}`

Requests evaluated: `{request_count}`

## What This Run Contains

- `labeled_access_requests.csv` with `allow`, `deny`, or `escalate` decisions.
- `policy_summary.csv` with decision and reason-code counts.
- `explanation_artifacts.jsonl` with one structured explanation artifact per request.
- `policy_rules.json` with the rule IDs used by the oracle.
- Decision, explanation, and audit-anchor hashes for later blockchain testing.

## What This Run Does Not Contain

- No real police/CCTNS/ICJS/FIR data.
- No trained ML model.
- No SHAP/LIME explanation.
- No blockchain ledger write.
- No deployment or legal-compliance claim.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/policy_oracle.py \\
  --input-run-id {input_run_id} \\
  --run-id {run_id}
```
"""


def data_dictionary_text() -> str:
    return """# Policy Oracle Output Data Dictionary

This file describes the Step 2 policy-oracle output.

## Important Boundary

The output is based on synthetic access requests and deterministic policy assumptions. It is not a real police access-control decision log.

## Core Files

- `labeled_access_requests.csv`: Step 1 request fields plus policy and XAI fields.
- `explanation_artifacts.jsonl`: one structured explanation artifact per request.
- `policy_rules.json`: rule IDs and decision precedence.
- `policy_summary.csv`: counts for decisions, reason codes, approvals, and sensitivity groups.

## Added Fields

| Field | Meaning |
|---|---|
| `decision` | Policy oracle decision: `allow`, `deny`, or `escalate`. |
| `primary_reason_code` | Main rule responsible for the decision. |
| `matched_rule_ids` | Rule IDs used for the final decision. |
| `all_triggered_rule_ids` | All triggered rules before final precedence. |
| `decisive_attributes` | Request attributes that influenced the decision. |
| `failed_or_review_rules` | Deny or escalation rules triggered by the request. |
| `required_approval` | Approval category required if escalated. |
| `xai_explanation` | Human-readable rule-trace explanation. |
| `xai_supporting_factors` | Positive contextual factors found in the request. |
| `policy_version_evaluated` | Policy version used by the oracle. |
| `decision_hash` | SHA-256 hash of decision-critical fields. |
| `explanation_hash` | SHA-256 hash of the structured explanation artifact. |
| `audit_anchor_hash` | Hash combining request, decision, explanation, and policy version for future audit logging. |
"""


if __name__ == "__main__":
    main()
