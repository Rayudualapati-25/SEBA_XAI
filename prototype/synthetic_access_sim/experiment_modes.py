#!/usr/bin/env python3
"""Run explicit baseline/proposed experiment modes for SEBA-XAI.

This is Step 6 of the prototype. It consolidates earlier components into
named experiment modes:

1. RBAC + mutable log
2. ABAC/PBAC + mutable log
3. ABAC/PBAC + signed hash-chain log
4. ABAC/PBAC + permissioned blockchain-style audit
5. ABAC/PBAC + permissioned blockchain-style audit + XAI hash

The policy oracle from Step 2 is treated as the deterministic ground-truth
policy label for the synthetic workload. This is not a real police decision
ground truth.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import policy_oracle


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN_ID = "20260527_step6_experiment_modes_seed42"
DEFAULT_STEP1_RUN_ID = "20260527_step1_synthetic_requests_seed42"
DEFAULT_STEP2_RUN_ID = "20260527_step2_policy_oracle_seed42"
DEFAULT_STEP3_RUN_ID = "20260527_step3_audit_baselines_seed42"
DEFAULT_STEP4_RUN_ID = "20260527_step4_permissioned_blockchain_audit_seed42"
DEFAULT_STEP5_RUN_ID = "20260527_step5_latency_storage_overhead"
DEFAULT_STEP7_RUN_ID = "20260527_step7_offchain_encrypted_pointers_seed42"

METHODS = [
    {
        "method_id": "rbac_mutable_log",
        "method_name": "RBAC + mutable log",
        "decision_model": "rbac",
        "audit_mode": "mutable_log",
        "xai_hash_logged": False,
        "xai_explanation_available": False,
        "description": "Role/action baseline with mutable centralized audit log.",
    },
    {
        "method_id": "abac_pbac_mutable_log",
        "method_name": "ABAC/PBAC + mutable log",
        "decision_model": "abac_pbac",
        "audit_mode": "mutable_log",
        "xai_hash_logged": False,
        "xai_explanation_available": False,
        "description": "Contextual policy oracle with mutable centralized audit log.",
    },
    {
        "method_id": "abac_pbac_signed_hash_chain",
        "method_name": "ABAC/PBAC + signed hash-chain log",
        "decision_model": "abac_pbac",
        "audit_mode": "signed_hash_chain",
        "xai_hash_logged": False,
        "xai_explanation_available": False,
        "description": "Contextual policy oracle with signed append-only hash-chain audit.",
    },
    {
        "method_id": "abac_pbac_blockchain_style",
        "method_name": "ABAC/PBAC + blockchain-style audit",
        "decision_model": "abac_pbac",
        "audit_mode": "permissioned_blockchain_style",
        "xai_hash_logged": False,
        "xai_explanation_available": False,
        "description": "Contextual policy oracle with permissioned blockchain-style audit commitments.",
    },
    {
        "method_id": "seba_xai_full",
        "method_name": "SEBA-XAI full: ABAC/PBAC + blockchain-style audit + XAI hash",
        "decision_model": "abac_pbac",
        "audit_mode": "permissioned_blockchain_style",
        "xai_hash_logged": True,
        "xai_explanation_available": True,
        "description": "Final proposed mode with contextual policy decisions, rule-trace XAI, explanation hash, and permissioned blockchain-style audit.",
    },
]

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
    "xai_explanation_available",
    "xai_hash_logged",
]

COMPARISON_FIELDS = [
    "method_id",
    "method_name",
    "decision_model",
    "audit_mode",
    "requests",
    "accuracy",
    "correct_count",
    "false_allow_count",
    "false_deny_count",
    "false_escalate_count",
    "oracle_allow_recall",
    "oracle_deny_recall",
    "oracle_escalate_recall",
    "audit_tamper_detection_rate",
    "explanation_available_rate",
    "xai_hash_logged",
    "explanation_hash_tamper_detection",
    "decision_latency_ms_p50_total",
    "audit_build_latency_ms_p50_total",
    "audit_verify_latency_ms_p50_total",
    "estimated_total_build_latency_ms_p50",
    "storage_bytes",
    "storage_bytes_per_event",
    "status",
    "scope_note",
]

CONFUSION_FIELDS = [
    "method_id",
    "oracle_decision",
    "predicted_decision",
    "count",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
    return policy_oracle.file_sha256(path)


def p50(values: List[float]) -> float:
    if not values:
        return 0.0
    return statistics.median(values)


def int_value(raw: object, default: int = 0) -> int:
    try:
        return int(str(raw))
    except (TypeError, ValueError):
        return default


def rbac_decision(row: Dict[str, str]) -> Tuple[str, str]:
    """Simple RBAC baseline using only credential, role/rank, action, and purpose."""

    credential = row["requester_credential_status"]
    role = row["requester_role"]
    rank = int_value(row["requester_rank_level"])
    action = row["action"]
    purpose = row["purpose"]

    if credential != "ACTIVE":
        return "deny", "RBAC_DENY_INACTIVE_CREDENTIAL"

    if purpose == "TRAINING":
        return "deny", "RBAC_DENY_TRAINING_PURPOSE"

    role_actions = {
        "Constable": {"VIEW"},
        "Head Constable": {"VIEW"},
        "Sub-Inspector": {"VIEW", "DOWNLOAD"},
        "Inspector": {"VIEW", "DOWNLOAD", "UPDATE"},
        "Station House Officer": {"VIEW", "DOWNLOAD", "UPDATE", "SHARE", "APPROVE"},
        "Cybercrime Officer": {"VIEW", "DOWNLOAD", "UPDATE", "SHARE"},
        "Forensic Officer": {"VIEW", "DOWNLOAD", "UPDATE"},
        "Prosecutor Liaison": {"VIEW", "DOWNLOAD", "SHARE"},
        "Senior Superintendent": {"VIEW", "DOWNLOAD", "UPDATE", "SHARE", "APPROVE"},
    }
    allowed_actions = role_actions.get(role, {"VIEW"})
    if action == "APPROVE" and rank < 5:
        return "deny", "RBAC_DENY_APPROVAL_REQUIRES_SUPERVISOR"
    if action in allowed_actions:
        return "allow", "RBAC_ALLOW_ROLE_ACTION"
    return "deny", "RBAC_DENY_ROLE_ACTION"


def abac_pbac_decision(row: Dict[str, str]) -> Tuple[str, str]:
    return row["decision"], row["primary_reason_code"]


def measure_decision_totals(
    request_rows: List[Dict[str, str]],
    labeled_by_request: Dict[str, Dict[str, str]],
    repeats: int,
) -> Dict[str, float]:
    rbac_totals: List[float] = []
    abac_totals: List[float] = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        for row in request_rows:
            rbac_decision(row)
        rbac_totals.append((time.perf_counter_ns() - start) / 1_000_000)

        start = time.perf_counter_ns()
        for row in request_rows:
            # Re-evaluate from Step 1 requests to include policy rules, explanation,
            # and hash generation, instead of only reading saved labels.
            policy_oracle.evaluate_policy(row)
        abac_totals.append((time.perf_counter_ns() - start) / 1_000_000)

    return {
        "rbac": p50(rbac_totals),
        "abac_pbac": p50(abac_totals),
    }


def load_step5_overhead(step5_run_id: str) -> Dict[str, Dict[str, str]]:
    path = ROOT / "prototype" / "runs" / step5_run_id / "artifacts" / "overhead_comparison.csv"
    return {row["method"]: row for row in read_csv(path)}


def detection_rate_from_rows(
    rows: List[Dict[str, str]],
    *,
    expected_field: str,
    detected_field: str,
) -> str:
    tampered = [row for row in rows if row.get(expected_field) == "true"]
    if not tampered:
        return ""
    detected = sum(1 for row in tampered if row.get(detected_field) == "true")
    return f"{detected / len(tampered):.4f}"


def load_detection_evidence(
    *,
    step3_run_id: str,
    step4_run_id: str,
    step7_run_id: str,
) -> Dict[str, object]:
    step3_summary = ROOT / "prototype" / "runs" / step3_run_id / "artifacts" / "audit_detection_summary.csv"
    step4_summary = ROOT / "prototype" / "runs" / step4_run_id / "artifacts" / "blockchain_detection_summary.csv"
    step7_tamper_results = ROOT / "prototype" / "runs" / step7_run_id / "artifacts" / "offchain_tamper_test_results.csv"

    audit_rates: Dict[str, str] = {
        "mutable_log": "",
        "signed_hash_chain": "",
        "permissioned_blockchain_style": "",
    }

    if step3_summary.exists():
        for row in read_csv(step3_summary):
            if row.get("log_type") == "mutable":
                audit_rates["mutable_log"] = row.get("self_detection_rate", "")
            elif row.get("log_type") == "signed_hash_chain":
                audit_rates["signed_hash_chain"] = row.get("self_detection_rate", "")

    if step4_summary.exists():
        for row in read_csv(step4_summary):
            if row.get("chain_type") == "permissioned_blockchain_style":
                audit_rates["permissioned_blockchain_style"] = row.get("detection_rate", "")

    xai_hash_detection_rate = ""
    if step7_tamper_results.exists():
        explanation_rows = [
            row
            for row in read_csv(step7_tamper_results)
            if row.get("expected_tampered") == "true"
            and "explanation_hash" in row.get("tamper_case", "")
        ]
        xai_hash_detection_rate = detection_rate_from_rows(
            explanation_rows,
            expected_field="expected_tampered",
            detected_field="verification_detected",
        )

    return {
        "audit_rates": audit_rates,
        "xai_hash_detection_rate": xai_hash_detection_rate,
        "source_files": {
            "step3_summary": str(step3_summary),
            "step4_summary": str(step4_summary),
            "step7_tamper_results": str(step7_tamper_results),
        },
    }


def method_latency_and_storage(
    method: Dict[str, object],
    decision_totals: Dict[str, float],
    overhead: Dict[str, Dict[str, str]],
) -> Dict[str, float]:
    decision_model = str(method["decision_model"])
    audit_mode = str(method["audit_mode"])
    decision_latency = decision_totals[decision_model]

    if audit_mode == "mutable_log":
        audit_build = float(overhead["mutable_log"]["build_or_decision_total_ms_p50"])
        audit_verify = float(overhead["mutable_log"]["verify_total_ms_p50"])
        storage_bytes = int(overhead["mutable_log"]["storage_bytes"])
        storage_per_event = float(overhead["mutable_log"]["storage_bytes_per_event_or_request"])
    elif audit_mode == "signed_hash_chain":
        audit_build = float(overhead["signed_hash_chain"]["build_or_decision_total_ms_p50"])
        audit_verify = float(overhead["signed_hash_chain"]["verify_total_ms_p50"])
        storage_bytes = int(overhead["signed_hash_chain"]["storage_bytes"])
        storage_per_event = float(overhead["signed_hash_chain"]["storage_bytes_per_event_or_request"])
    elif audit_mode == "permissioned_blockchain_style":
        signed_build = float(overhead["signed_hash_chain"]["build_or_decision_total_ms_p50"])
        signed_verify = float(overhead["signed_hash_chain"]["verify_total_ms_p50"])
        chain_build = float(overhead["permissioned_blockchain_style"]["build_or_decision_total_ms_p50"])
        chain_verify = float(overhead["permissioned_blockchain_style"]["verify_total_ms_p50"])
        audit_build = signed_build + chain_build
        audit_verify = signed_verify + chain_verify
        storage_bytes = int(overhead["signed_hash_chain"]["storage_bytes"]) + int(overhead["permissioned_blockchain_style"]["storage_bytes"])
        storage_per_event = float(overhead["signed_hash_chain"]["storage_bytes_per_event_or_request"]) + float(overhead["permissioned_blockchain_style"]["storage_bytes_per_event_or_request"])
    else:
        raise ValueError(f"unknown audit mode: {audit_mode}")

    return {
        "decision_latency": decision_latency,
        "audit_build": audit_build,
        "audit_verify": audit_verify,
        "estimated_total_build": decision_latency + audit_build,
        "storage_bytes": storage_bytes,
        "storage_per_event": storage_per_event,
    }


def audit_detection_rate(method: Dict[str, object], detection_evidence: Dict[str, object]) -> str:
    audit_mode = str(method["audit_mode"])
    audit_rates = detection_evidence["audit_rates"]
    if not isinstance(audit_rates, dict):
        raise ValueError("detection_evidence['audit_rates'] must be a dict")
    value = audit_rates.get(audit_mode, "")
    if value == "":
        return "unmeasured"
    return str(value)


def build_predictions(
    request_rows: List[Dict[str, str]],
    labeled_by_request: Dict[str, Dict[str, str]],
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for method in METHODS:
        for request in request_rows:
            oracle_row = labeled_by_request[request["request_id"]]
            if method["decision_model"] == "rbac":
                predicted, reason = rbac_decision(request)
            else:
                predicted, reason = abac_pbac_decision(oracle_row)
            oracle_decision = oracle_row["decision"]
            rows.append(
                {
                    "method_id": method["method_id"],
                    "request_id": request["request_id"],
                    "scenario_type": request["scenario_type"],
                    "oracle_decision": oracle_decision,
                    "predicted_decision": predicted,
                    "correct": str(predicted == oracle_decision).lower(),
                    "false_allow": str(predicted == "allow" and oracle_decision != "allow").lower(),
                    "false_deny": str(predicted == "deny" and oracle_decision != "deny").lower(),
                    "false_escalate": str(predicted == "escalate" and oracle_decision != "escalate").lower(),
                    "reason_code": reason,
                    "xai_explanation_available": str(bool(method["xai_explanation_available"])).lower(),
                    "xai_hash_logged": str(bool(method["xai_hash_logged"])).lower(),
                }
            )
    return rows


def recall_for(rows: List[Dict[str, object]], label: str) -> float:
    label_rows = [row for row in rows if row["oracle_decision"] == label]
    if not label_rows:
        return 0.0
    correct = sum(1 for row in label_rows if row["predicted_decision"] == label)
    return correct / len(label_rows)


def build_comparison(
    prediction_rows: List[Dict[str, object]],
    decision_totals: Dict[str, float],
    overhead: Dict[str, Dict[str, str]],
    detection_evidence: Dict[str, object],
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    by_method: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for row in prediction_rows:
        by_method[str(row["method_id"])].append(row)

    for method in METHODS:
        method_id = str(method["method_id"])
        subset = by_method[method_id]
        total = len(subset)
        correct = sum(1 for row in subset if row["correct"] == "true")
        false_allow = sum(1 for row in subset if row["false_allow"] == "true")
        false_deny = sum(1 for row in subset if row["false_deny"] == "true")
        false_escalate = sum(1 for row in subset if row["false_escalate"] == "true")
        latency_storage = method_latency_and_storage(method, decision_totals, overhead)
        explanation_rate = 1.0 if method["xai_explanation_available"] else 0.0
        xai_hash_logged = bool(method["xai_hash_logged"])
        xai_detection_rate = (
            str(detection_evidence.get("xai_hash_detection_rate") or "unmeasured")
            if xai_hash_logged
            else "0.0000"
        )
        rows.append(
            {
                "method_id": method_id,
                "method_name": method["method_name"],
                "decision_model": method["decision_model"],
                "audit_mode": method["audit_mode"],
                "requests": total,
                "accuracy": f"{correct / total:.4f}" if total else "0.0000",
                "correct_count": correct,
                "false_allow_count": false_allow,
                "false_deny_count": false_deny,
                "false_escalate_count": false_escalate,
                "oracle_allow_recall": f"{recall_for(subset, 'allow'):.4f}",
                "oracle_deny_recall": f"{recall_for(subset, 'deny'):.4f}",
                "oracle_escalate_recall": f"{recall_for(subset, 'escalate'):.4f}",
                "audit_tamper_detection_rate": audit_detection_rate(method, detection_evidence),
                "explanation_available_rate": f"{explanation_rate:.4f}",
                "xai_hash_logged": str(xai_hash_logged).lower(),
                "explanation_hash_tamper_detection": xai_detection_rate,
                "decision_latency_ms_p50_total": f"{latency_storage['decision_latency']:.6f}",
                "audit_build_latency_ms_p50_total": f"{latency_storage['audit_build']:.6f}",
                "audit_verify_latency_ms_p50_total": f"{latency_storage['audit_verify']:.6f}",
                "estimated_total_build_latency_ms_p50": f"{latency_storage['estimated_total_build']:.6f}",
                "storage_bytes": int(latency_storage["storage_bytes"]),
                "storage_bytes_per_event": f"{latency_storage['storage_per_event']:.3f}",
                "status": "proposed" if method_id == "seba_xai_full" else "baseline",
                "scope_note": method["description"],
            }
        )
    return rows


def build_confusion_rows(prediction_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    counts = Counter(
        (
            row["method_id"],
            row["oracle_decision"],
            row["predicted_decision"],
        )
        for row in prediction_rows
    )
    return [
        {
            "method_id": method_id,
            "oracle_decision": oracle_decision,
            "predicted_decision": predicted_decision,
            "count": count,
        }
        for (method_id, oracle_decision, predicted_decision), count in sorted(counts.items())
    ]


def build_readme(run_id: str) -> str:
    return f"""# Run {run_id}

Purpose: Step 6 explicit baseline/proposed experiment-mode comparison.

## Methods Compared

1. RBAC + mutable log
2. ABAC/PBAC + mutable log
3. ABAC/PBAC + signed hash-chain log
4. ABAC/PBAC + permissioned blockchain-style audit
5. SEBA-XAI full: ABAC/PBAC + permissioned blockchain-style audit + XAI hash

## Important Boundary

The Step 2 policy oracle is used as deterministic ground-truth policy label for the synthetic workload. This is not real police decision ground truth.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/experiment_modes.py \\
  --run-id {run_id}
```
"""


def data_dictionary_text() -> str:
    return """# Experiment Mode Comparison Data Dictionary

This file describes Step 6 outputs.

## Core Files

- `experiment_mode_predictions.csv`: per-request predictions for every method.
- `experiment_mode_comparison.csv`: one row per method with correctness, audit, latency, storage, and XAI availability.
- `decision_confusion_by_method.csv`: oracle decision versus predicted decision counts.
- `method_definitions.json`: method definitions and scope notes.

## Important Fields

| Field | Meaning |
|---|---|
| `accuracy` | Exact match with Step 2 policy-oracle label. |
| `false_allow_count` | Method allowed a request that the oracle did not allow. |
| `false_deny_count` | Method denied a request that the oracle did not deny. |
| `false_escalate_count` | Method escalated a request that the oracle did not escalate. |
| `audit_tamper_detection_rate` | Detection rate read from matching Step 3/Step 4 tamper-test artifacts. |
| `explanation_available_rate` | Whether the method exposes XAI explanation for requests. |
| `xai_hash_logged` | Whether the method logs explanation hash in the proposed audit layer. |
| `explanation_hash_tamper_detection` | Detection rate read from Step 7 explanation-hash pointer tamper tests when XAI hashes are logged. |
| `estimated_total_build_latency_ms_p50` | Local additive estimate using measured decision and audit build times. |

## Correct Interpretation

This is a synthetic workload comparison. The ABAC/PBAC oracle defines expected labels. Do not treat this as real police access-control accuracy.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare explicit SEBA-XAI experiment modes.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--step1-run-id", default=DEFAULT_STEP1_RUN_ID)
    parser.add_argument("--step2-run-id", default=DEFAULT_STEP2_RUN_ID)
    parser.add_argument("--step3-run-id", default=DEFAULT_STEP3_RUN_ID)
    parser.add_argument("--step4-run-id", default=DEFAULT_STEP4_RUN_ID)
    parser.add_argument("--step5-run-id", default=DEFAULT_STEP5_RUN_ID)
    parser.add_argument("--step7-run-id", default=DEFAULT_STEP7_RUN_ID)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument(
        "--results-summary-table",
        default=str(ROOT / "prototype" / "results" / "tables" / "experiment_modes_step6_comparison.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = ROOT / "prototype" / "runs" / args.run_id
    artifacts_dir = run_dir / "artifacts"
    logs_dir = run_dir / "logs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    step1_request_file = ROOT / "prototype" / "runs" / args.step1_run_id / "artifacts" / "access_requests.csv"
    step2_labeled_file = ROOT / "prototype" / "runs" / args.step2_run_id / "artifacts" / "labeled_access_requests.csv"

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    config = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "step1_run_id": args.step1_run_id,
        "step2_run_id": args.step2_run_id,
        "step3_run_id": args.step3_run_id,
        "step4_run_id": args.step4_run_id,
        "step5_run_id": args.step5_run_id,
        "step7_run_id": args.step7_run_id,
        "repeats": args.repeats,
        "step": "step_6_explicit_experiment_modes",
        "synthetic_only": True,
        "oracle_ground_truth": "step2_policy_oracle_labels",
    }
    write_yaml(run_dir / "config.yaml", config)

    request_rows = read_csv(step1_request_file)
    labeled_rows = read_csv(step2_labeled_file)
    labeled_by_request = {row["request_id"]: row for row in labeled_rows}
    overhead = load_step5_overhead(args.step5_run_id)
    detection_evidence = load_detection_evidence(
        step3_run_id=args.step3_run_id,
        step4_run_id=args.step4_run_id,
        step7_run_id=args.step7_run_id,
    )
    decision_totals = measure_decision_totals(request_rows, labeled_by_request, args.repeats)

    prediction_rows = build_predictions(request_rows, labeled_by_request)
    comparison_rows = build_comparison(prediction_rows, decision_totals, overhead, detection_evidence)
    confusion_rows = build_confusion_rows(prediction_rows)

    predictions_path = artifacts_dir / "experiment_mode_predictions.csv"
    comparison_path = artifacts_dir / "experiment_mode_comparison.csv"
    confusion_path = artifacts_dir / "decision_confusion_by_method.csv"
    definitions_path = artifacts_dir / "method_definitions.json"

    write_csv(predictions_path, prediction_rows, PREDICTION_FIELDS)
    write_csv(comparison_path, comparison_rows, COMPARISON_FIELDS)
    write_csv(Path(args.results_summary_table), comparison_rows, COMPARISON_FIELDS)
    write_csv(confusion_path, confusion_rows, CONFUSION_FIELDS)
    write_json(definitions_path, {"methods": METHODS})

    metrics = {
        "artifact_type": "explicit_experiment_mode_comparison",
        "result_claim": "synthetic workload comparison against deterministic policy-oracle labels",
        "created_at_utc": created_at,
        "request_count": len(request_rows),
        "method_count": len(METHODS),
        "decision_latency_ms_p50_total": decision_totals,
        "detection_evidence": detection_evidence,
        "best_accuracy_method_ids": [
            row["method_id"]
            for row in comparison_rows
            if row["accuracy"] == max(item["accuracy"] for item in comparison_rows)
        ],
        "proposed_method": "seba_xai_full",
        "limitations": [
            "Ground truth is the deterministic Step 2 policy oracle, not real police access-control decisions.",
            "RBAC is intentionally simple and uses only credential, role/rank, action, and purpose.",
            "Latency values are local prototype additive estimates, not deployment measurements.",
            "Audit and XAI tamper detection rates are read from controlled local tamper-test artifacts in earlier steps.",
        ],
    }
    write_json(run_dir / "metrics.json", metrics)

    manifest = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "synthetic_only": True,
        "input_hashes": {
            "step1_request_file": file_sha256(step1_request_file),
            "step2_labeled_file": file_sha256(step2_labeled_file),
        },
        "artifact_hashes": {
            "experiment_mode_predictions.csv": file_sha256(predictions_path),
            "experiment_mode_comparison.csv": file_sha256(comparison_path),
            "decision_confusion_by_method.csv": file_sha256(confusion_path),
            "method_definitions.json": file_sha256(definitions_path),
        },
        "notes": [
            "This run consolidates earlier prototype stages into explicit methods.",
            "The final proposed method is seba_xai_full.",
            "Do not describe this as real police-system accuracy.",
            "Audit/XAI detection rates are artifact-derived from the configured Step 3, Step 4, and Step 7 runs.",
        ],
    }
    write_json(artifacts_dir / "dataset_manifest.json", manifest)
    (artifacts_dir / "README.md").write_text(build_readme(args.run_id), encoding="utf-8")
    (artifacts_dir / "data_dictionary.md").write_text(data_dictionary_text(), encoding="utf-8")

    log_lines = [
        f"created_at_utc={created_at}",
        f"run_id={args.run_id}",
        f"requests={len(request_rows)}",
        f"methods={len(METHODS)}",
        f"decision_totals={decision_totals}",
        f"detection_evidence={detection_evidence}",
        "status=success",
        "claim=synthetic_experiment_mode_comparison_only",
    ]
    (logs_dir / "experiment_modes.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Wrote experiment-mode comparison run: {run_dir}")
    print(f"Requests: {len(request_rows)}")
    print(f"Methods: {len(METHODS)}")
    print(f"Summary table: {args.results_summary_table}")


if __name__ == "__main__":
    main()
