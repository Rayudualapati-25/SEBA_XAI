#!/usr/bin/env python3
"""Validate SEBA-XAI Fabric audit events before blockchain submission."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "requestIdHash",
    "policyVersion",
    "decision",
    "primaryReasonCode",
    "decisionHash",
    "explanationHash",
    "recordCommitment",
    "auditAnchorHash",
    "approvalReferenceHash",
    "attributeSetHash",
    "sourcePrototypeRun",
    "createdAtUtc",
    "localEventPayloadHash",
}

HASH_FIELDS = {
    "requestIdHash",
    "decisionHash",
    "explanationHash",
    "recordCommitment",
    "auditAnchorHash",
    "approvalReferenceHash",
    "attributeSetHash",
    "localEventPayloadHash",
}

FORBIDDEN_FIELDS = {
    "request_id",
    "requester_officer_id",
    "requester_name",
    "target_record_id",
    "target_case_id",
    "xai_explanation",
    "raw_record",
    "record_payload",
    "victim_name",
    "witness_name",
    "juvenile_name",
}

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if line:
                row = json.loads(line)
                row["_line_number"] = line_number
                rows.append(row)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def validate_event(event: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    line = event.get("_line_number", "?")

    missing = sorted(field for field in REQUIRED_FIELDS if field not in event)
    if missing:
        errors.append(f"line {line}: missing required fields {missing}")

    forbidden = sorted(field for field in FORBIDDEN_FIELDS if field in event)
    if forbidden:
        errors.append(f"line {line}: forbidden raw/sensitive fields present {forbidden}")

    if event.get("decision") not in {"allow", "deny", "escalate"}:
        errors.append(f"line {line}: invalid decision {event.get('decision')}")

    if event.get("rawRecordsOnChain") is not False:
        errors.append(f"line {line}: rawRecordsOnChain must be false")

    for field in HASH_FIELDS:
        value = str(event.get(field, ""))
        if not SHA256_RE.match(value):
            errors.append(f"line {line}: {field} is not a SHA-256 hex value")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Fabric audit event JSONL.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    events = read_jsonl(input_path)

    errors: list[str] = []
    seen_request_hashes: set[str] = set()
    duplicates: list[str] = []
    for event in events:
        errors.extend(validate_event(event))
        request_hash = str(event.get("requestIdHash", ""))
        if request_hash in seen_request_hashes:
            duplicates.append(request_hash)
        seen_request_hashes.add(request_hash)

    if duplicates:
        errors.append(f"duplicate requestIdHash values: {sorted(set(duplicates))}")

    report = {
        "artifact_type": "fabric_audit_event_validation",
        "input": str(input_path),
        "events_checked": len(events),
        "all_valid": not errors,
        "errors": errors,
        "decision_counts": dict(Counter(event.get("decision") for event in events)),
        "raw_records_on_chain": False,
    }

    if args.output:
        write_json(Path(args.output), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
