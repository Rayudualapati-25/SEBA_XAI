#!/usr/bin/env python3
"""Build commitment-only Fabric audit events from SEBA-XAI policy output."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FORBIDDEN_OUTPUT_FIELDS = {
    "request_id",
    "requester_officer_id",
    "target_record_id",
    "target_case_id",
    "xai_explanation",
    "raw_record",
    "record_payload",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_event(row: dict[str, str], source_run: str, sequence: int) -> dict[str, Any]:
    decisive_attributes = [
        item for item in row.get("decisive_attributes", "").split("|") if item and item != "none"
    ]
    event = {
        "requestIdHash": stable_hash({"request_id": row["request_id"]}),
        "sourceRequestSequence": sequence,
        "policyVersion": row["policy_version_evaluated"],
        "decision": row["decision"],
        "primaryReasonCode": row["primary_reason_code"],
        "decisionHash": row["decision_hash"],
        "explanationHash": row["explanation_hash"],
        "recordCommitment": stable_hash({"target_record_hash": row["target_record_hash"]}),
        "auditAnchorHash": row["audit_anchor_hash"],
        "approvalReferenceHash": stable_hash({"required_approval": row.get("required_approval", "none")}),
        "attributeSetHash": stable_hash({"decisive_attributes": sorted(decisive_attributes)}),
        "sourcePrototypeRun": source_run,
        "createdAtUtc": row["timestamp_utc"],
        "rawRecordsOnChain": False,
    }
    event["localEventPayloadHash"] = stable_hash(event)
    return event


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Fabric audit events from SEBA-XAI policy labels.")
    parser.add_argument("--input", required=True, help="labeled_access_requests.csv from policy oracle")
    parser.add_argument("--run-dir", required=True, help="output run directory")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--source-run", default="20260527_step2_policy_oracle_seed42")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    run_dir = Path(args.run_dir)
    artifacts_dir = run_dir / "artifacts"
    logs_dir = run_dir / "logs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(input_path)
    selected = rows[: args.limit]
    events = [build_event(row, args.source_run, index + 1) for index, row in enumerate(selected)]

    forbidden_seen = sorted(FORBIDDEN_OUTPUT_FIELDS.intersection(events[0].keys())) if events else []
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    jsonl_path = artifacts_dir / "fabric_audit_events.jsonl"
    csv_path = artifacts_dir / "fabric_audit_events.csv"
    metrics_path = run_dir / "metrics.json"
    manifest_path = artifacts_dir / "manifest.json"

    write_jsonl(jsonl_path, events)
    write_csv(csv_path, events)

    metrics = {
        "artifact_type": "fabric_audit_event_preparation",
        "created_at_utc": created_at,
        "input_file": str(input_path),
        "input_file_sha256": file_sha256(input_path),
        "events_prepared": len(events),
        "decision_counts": dict(Counter(event["decision"] for event in events)),
        "raw_records_on_chain": False,
        "forbidden_output_fields_seen": forbidden_seen,
        "fabric_executed": False,
        "fabric_execution_note": "This preparation script does not submit events to Fabric; run scripts/04_submit_events.sh after the network is running.",
        "claim_supported": "commitment-only Fabric audit events can be prepared from synthetic SEBA-XAI policy output",
        "claim_not_supported_by_this_stage": "ledger commit is verified only by the separate Fabric submit artifact",
    }
    write_json(metrics_path, metrics)
    write_json(
        manifest_path,
        {
            "run_dir": str(run_dir),
            "created_at_utc": created_at,
            "artifacts": {
                "fabric_audit_events.jsonl": file_sha256(jsonl_path),
                "fabric_audit_events.csv": file_sha256(csv_path),
            },
            "synthetic_only": True,
            "raw_records_on_chain": False,
        },
    )

    log_lines = [
        f"created_at_utc={created_at}",
        f"input_file={input_path}",
        f"events_prepared={len(events)}",
        f"decisions={dict(Counter(event['decision'] for event in events))}",
        "fabric_executed=false_by_preparation_stage",
        "status=success",
    ]
    (logs_dir / "build_audit_events.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(jsonl_path)


if __name__ == "__main__":
    main()
