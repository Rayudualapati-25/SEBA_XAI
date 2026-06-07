#!/usr/bin/env python3
"""Create mutable and signed append-only audit-log baselines for SEBA-XAI.

This is Step 3 of the prototype. It reads Step 2 labeled requests and writes:

- a mutable centralized audit log;
- a signed append-only hash-chain audit log;
- controlled tampered copies of both logs;
- verification results for each tamper case.

This is not a blockchain implementation. It is the required non-blockchain
baseline before comparing against a blockchain-style audit layer.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_RUN_ID = "20260527_step2_policy_oracle_seed42"
DEFAULT_RUN_ID = "20260527_step3_audit_baselines_seed42"
AUDIT_LOG_VERSION = "AUDIT-2026-05-STEP3"
GENESIS_HASH = "GENESIS"

# Demo-only deterministic key for reproducible research artifacts.
# This is not a production secret and must not be described as deployment-grade signing.
DEMO_SIGNING_KEY = b"seba-xai-demo-audit-key-not-for-production"

MUTABLE_LOG_FIELDS = [
    "event_sequence",
    "event_id",
    "timestamp_utc",
    "request_id",
    "requester_officer_hash",
    "requester_station_id",
    "target_record_hash",
    "decision",
    "primary_reason_code",
    "policy_version_evaluated",
    "request_content_hash",
    "decision_hash",
    "explanation_hash",
    "audit_anchor_hash",
]

SIGNED_LOG_FIELDS = MUTABLE_LOG_FIELDS + [
    "event_payload_hash",
    "previous_event_hash",
    "event_hash",
    "log_signature",
    "signature_algorithm",
    "audit_log_version",
]

TAMPER_CASES = [
    "changed_decision",
    "deleted_event",
    "changed_explanation_hash",
    "reordered_events",
]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sign_event(event_hash: str) -> str:
    return hmac.new(DEMO_SIGNING_KEY, event_hash.encode("utf-8"), hashlib.sha256).hexdigest()


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def build_mutable_log_rows(labeled_rows: List[Dict[str, str]]) -> List[Dict[str, object]]:
    audit_rows: List[Dict[str, object]] = []
    for index, row in enumerate(labeled_rows, start=1):
        event_id = stable_hash(
            {
                "event_sequence": index,
                "request_id": row["request_id"],
                "audit_anchor_hash": row["audit_anchor_hash"],
            }
        )[:24]
        audit_rows.append(
            {
                "event_sequence": index,
                "event_id": event_id,
                "timestamp_utc": row["timestamp_utc"],
                "request_id": row["request_id"],
                "requester_officer_hash": row["requester_officer_hash"],
                "requester_station_id": row["requester_station_id"],
                "target_record_hash": row["target_record_hash"],
                "decision": row["decision"],
                "primary_reason_code": row["primary_reason_code"],
                "policy_version_evaluated": row["policy_version_evaluated"],
                "request_content_hash": row["request_content_hash"],
                "decision_hash": row["decision_hash"],
                "explanation_hash": row["explanation_hash"],
                "audit_anchor_hash": row["audit_anchor_hash"],
            }
        )
    return audit_rows


def build_signed_hash_chain_rows(mutable_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    signed_rows: List[Dict[str, object]] = []
    previous_hash = GENESIS_HASH
    for row in mutable_rows:
        payload = {field: str(row[field]) for field in MUTABLE_LOG_FIELDS}
        payload_hash = stable_hash(payload)
        event_hash = stable_hash(
            {
                "event_sequence": payload["event_sequence"],
                "event_payload_hash": payload_hash,
                "previous_event_hash": previous_hash,
            }
        )
        signed_row = dict(payload)
        signed_row.update(
            {
                "event_payload_hash": payload_hash,
                "previous_event_hash": previous_hash,
                "event_hash": event_hash,
                "log_signature": sign_event(event_hash),
                "signature_algorithm": "HMAC-SHA256-DEMO",
                "audit_log_version": AUDIT_LOG_VERSION,
            }
        )
        signed_rows.append(signed_row)
        previous_hash = event_hash
    return signed_rows


def verify_mutable_log(rows: List[Dict[str, str]]) -> Dict[str, object]:
    errors: List[str] = []
    for index, row in enumerate(rows, start=1):
        missing = [field for field in MUTABLE_LOG_FIELDS if field not in row]
        if missing:
            errors.append(f"row {index}: missing fields {missing}")
            continue
        try:
            int(row["event_sequence"])
        except ValueError:
            errors.append(f"row {index}: event_sequence is not an integer")

    return {
        "valid": not errors,
        "error_count": len(errors),
        "first_error": errors[0] if errors else "",
        "note": "Mutable log has schema checks only; it has no internal tamper-evident chain.",
    }


def verify_signed_hash_chain(rows: List[Dict[str, str]]) -> Dict[str, object]:
    errors: List[str] = []
    previous_hash = GENESIS_HASH
    seen_event_ids = set()

    for index, row in enumerate(rows, start=1):
        missing = [field for field in SIGNED_LOG_FIELDS if field not in row]
        if missing:
            errors.append(f"row {index}: missing fields {missing}")
            continue

        event_id = row["event_id"]
        if event_id in seen_event_ids:
            errors.append(f"row {index}: duplicate event_id {event_id}")
        seen_event_ids.add(event_id)

        if str(row["event_sequence"]) != str(index):
            errors.append(
                f"row {index}: expected event_sequence {index}, found {row['event_sequence']}"
            )

        payload = {field: str(row[field]) for field in MUTABLE_LOG_FIELDS}
        expected_payload_hash = stable_hash(payload)
        if row["event_payload_hash"] != expected_payload_hash:
            errors.append(f"row {index}: event_payload_hash mismatch")

        if row["previous_event_hash"] != previous_hash:
            errors.append(f"row {index}: previous_event_hash mismatch")

        expected_event_hash = stable_hash(
            {
                "event_sequence": str(row["event_sequence"]),
                "event_payload_hash": expected_payload_hash,
                "previous_event_hash": row["previous_event_hash"],
            }
        )
        if row["event_hash"] != expected_event_hash:
            errors.append(f"row {index}: event_hash mismatch")

        expected_signature = sign_event(row["event_hash"])
        if row["log_signature"] != expected_signature:
            errors.append(f"row {index}: log_signature mismatch")

        previous_hash = row["event_hash"]

    return {
        "valid": not errors,
        "error_count": len(errors),
        "first_error": errors[0] if errors else "",
        "note": "Signed hash-chain verification recomputes payload hashes, previous links, event hashes, and demo signatures.",
    }


def tamper_rows(rows: List[Dict[str, object]], tamper_case: str) -> List[Dict[str, object]]:
    tampered = deepcopy(rows)
    if not tampered:
        return tampered

    if tamper_case == "changed_decision":
        target_index = min(10, len(tampered) - 1)
        current = str(tampered[target_index]["decision"])
        tampered[target_index]["decision"] = "allow" if current != "allow" else "deny"
        return tampered

    if tamper_case == "deleted_event":
        target_index = min(25, len(tampered) - 1)
        del tampered[target_index]
        return tampered

    if tamper_case == "changed_explanation_hash":
        target_index = min(40, len(tampered) - 1)
        tampered[target_index]["explanation_hash"] = "tampered_" + str(tampered[target_index]["explanation_hash"])[:55]
        return tampered

    if tamper_case == "reordered_events":
        if len(tampered) > 51:
            tampered[50], tampered[51] = tampered[51], tampered[50]
        return tampered

    raise ValueError(f"unknown tamper case: {tamper_case}")


def write_tampered_logs(
    artifacts_dir: Path,
    mutable_rows: List[Dict[str, object]],
    signed_rows: List[Dict[str, object]],
) -> Dict[str, Dict[str, Path]]:
    tamper_dir = artifacts_dir / "tampered_logs"
    paths: Dict[str, Dict[str, Path]] = {"mutable": {}, "signed_hash_chain": {}}
    for case in TAMPER_CASES:
        mutable_tampered = tamper_rows(mutable_rows, case)
        mutable_path = tamper_dir / "mutable" / f"{case}.csv"
        write_csv(mutable_path, mutable_tampered, MUTABLE_LOG_FIELDS)
        paths["mutable"][case] = mutable_path

        signed_tampered = tamper_rows(signed_rows, case)
        signed_path = tamper_dir / "signed_hash_chain" / f"{case}.csv"
        write_csv(signed_path, signed_tampered, SIGNED_LOG_FIELDS)
        paths["signed_hash_chain"][case] = signed_path
    return paths


def build_tamper_results(
    mutable_log_path: Path,
    signed_log_path: Path,
    tampered_paths: Dict[str, Dict[str, Path]],
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    original_hashes = {
        "mutable": file_sha256(mutable_log_path),
        "signed_hash_chain": file_sha256(signed_log_path),
    }
    original_verifications = {
        "mutable": verify_mutable_log(read_csv(mutable_log_path)),
        "signed_hash_chain": verify_signed_hash_chain(read_csv(signed_log_path)),
    }

    for log_type, path in [
        ("mutable", mutable_log_path),
        ("signed_hash_chain", signed_log_path),
    ]:
        verification = original_verifications[log_type]
        rows.append(
            {
                "log_type": log_type,
                "tamper_case": "original",
                "file": str(path),
                "expected_tampered": "false",
                "self_verification_valid": str(verification["valid"]).lower(),
                "self_verification_detected": "false",
                "reference_hash_changed": "false",
                "first_error": verification["first_error"],
                "error_count": verification["error_count"],
                "note": verification["note"],
            }
        )

    for log_type, cases in tampered_paths.items():
        verifier = verify_mutable_log if log_type == "mutable" else verify_signed_hash_chain
        for case, path in cases.items():
            verification = verifier(read_csv(path))
            self_detected = not bool(verification["valid"])
            rows.append(
                {
                    "log_type": log_type,
                    "tamper_case": case,
                    "file": str(path),
                    "expected_tampered": "true",
                    "self_verification_valid": str(verification["valid"]).lower(),
                    "self_verification_detected": str(self_detected).lower(),
                    "reference_hash_changed": str(file_sha256(path) != original_hashes[log_type]).lower(),
                    "first_error": verification["first_error"],
                    "error_count": verification["error_count"],
                    "note": verification["note"],
                }
            )
    return rows


def build_metrics(tamper_results: List[Dict[str, object]], event_count: int, input_file: Path) -> Dict[str, object]:
    tampered_rows = [row for row in tamper_results if row["expected_tampered"] == "true"]
    by_type: Dict[str, Dict[str, int]] = {}
    for log_type in sorted({str(row["log_type"]) for row in tampered_rows}):
        subset = [row for row in tampered_rows if row["log_type"] == log_type]
        detected = sum(1 for row in subset if row["self_verification_detected"] == "true")
        by_type[log_type] = {
            "tamper_cases": len(subset),
            "self_detected": detected,
            "self_detection_rate": detected / len(subset) if subset else 0.0,
        }
    return {
        "artifact_type": "audit_baseline_tamper_test",
        "result_claim": "tamper-detection result for deterministic prototype logs only",
        "input_file": str(input_file),
        "audit_log_version": AUDIT_LOG_VERSION,
        "events_logged": event_count,
        "tamper_cases": TAMPER_CASES,
        "self_detection_by_log_type": by_type,
        "important_interpretation": [
            "Mutable log self-verification checks only schema and cannot internally prove that a valid-looking row was changed.",
            "Signed hash-chain verification detects the injected changes because payload hashes, previous links, event hashes, or demo signatures no longer match.",
            "This is a local signed-log baseline, not a blockchain consensus result.",
        ],
        "limitations": [
            "Demo HMAC signing key is fixed for reproducibility and is not production-grade key management.",
            "Tamper cases are controlled synthetic manipulations.",
            "No distributed ledger, consensus, Hyperledger Fabric, or multi-party replication has been implemented in this step.",
            "No latency or throughput benchmark has been run in this step.",
        ],
    }


def summary_rows(tamper_results: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    tampered = [row for row in tamper_results if row["expected_tampered"] == "true"]
    for log_type in sorted({str(row["log_type"]) for row in tampered}):
        subset = [row for row in tampered if row["log_type"] == log_type]
        detected = sum(1 for row in subset if row["self_verification_detected"] == "true")
        rows.append(
            {
                "log_type": log_type,
                "tamper_cases": len(subset),
                "self_detected": detected,
                "self_not_detected": len(subset) - detected,
                "self_detection_rate": f"{detected / len(subset):.4f}" if subset else "0.0000",
            }
        )
    return rows


def data_dictionary_text() -> str:
    return """# Audit Baseline Output Data Dictionary

This file describes Step 3 audit-baseline outputs.

## Important Boundary

This step compares local log designs. It does not implement blockchain, consensus, or Hyperledger Fabric.

## Core Files

- `mutable_access_log.csv`: centralized mutable audit log baseline.
- `signed_hash_chain_log.csv`: append-only-style audit log with previous hashes and demo HMAC signatures.
- `tampered_logs/`: controlled changed, deleted, hash-modified, and reordered log files.
- `tamper_test_results.csv`: verification result for each original and tampered log.
- `audit_detection_summary.csv`: compact detection-rate table.

## Key Fields

| Field | Meaning |
|---|---|
| `event_sequence` | Position of the event in the audit log. |
| `event_id` | Deterministic synthetic event identifier. |
| `request_id` | Request being audited. |
| `decision` | Policy-oracle decision. |
| `request_content_hash` | Hash of Step 1 request content. |
| `decision_hash` | Hash of Step 2 decision-critical fields. |
| `explanation_hash` | Hash of Step 2 explanation artifact. |
| `audit_anchor_hash` | Combined hash prepared for later blockchain anchoring. |
| `event_payload_hash` | Hash of the audit event payload in the signed log. |
| `previous_event_hash` | Previous event hash in the signed log. |
| `event_hash` | Hash linking payload hash, previous hash, and sequence. |
| `log_signature` | Demo HMAC signature over `event_hash`. |

## Correct Interpretation

Mutable logs can be compared against an external reference file hash, but they cannot prove internal tampering by themselves. Signed hash-chain logs can detect the injected tampering through recomputed hashes and signatures.
"""


def run_readme_text(run_id: str, input_run_id: str, event_count: int) -> str:
    return f"""# Run {run_id}

Purpose: Step 3 mutable-log and signed hash-chain audit baselines.

Input run: `{input_run_id}`

Audit events written: `{event_count}`

## What This Run Contains

- `mutable_access_log.csv`
- `signed_hash_chain_log.csv`
- tampered copies of both logs
- tamper-verification results
- compact detection summary

## What This Run Does Not Contain

- No real police/CCTNS/ICJS/FIR data.
- No blockchain ledger or consensus.
- No Hyperledger Fabric deployment.
- No production-grade signing or key management.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/audit_baseline.py \\
  --input-run-id {input_run_id} \\
  --run-id {run_id}
```
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create SEBA-XAI audit baseline logs and tamper tests.")
    parser.add_argument("--input-run-id", default=DEFAULT_INPUT_RUN_ID)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--input-file", default="")
    parser.add_argument(
        "--results-summary-table",
        default=str(ROOT / "prototype" / "results" / "tables" / "audit_baseline_step3_summary.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_file = Path(args.input_file) if args.input_file else (
        ROOT / "prototype" / "runs" / args.input_run_id / "artifacts" / "labeled_access_requests.csv"
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
        "audit_log_version": AUDIT_LOG_VERSION,
        "step": "step_3_audit_baselines_and_tamper_tests",
        "synthetic_only": True,
        "raw_record_included": False,
        "blockchain_implemented": False,
    }
    write_yaml(run_dir / "config.yaml", config)

    labeled_rows = read_csv(input_file)
    mutable_rows = build_mutable_log_rows(labeled_rows)
    signed_rows = build_signed_hash_chain_rows(mutable_rows)

    mutable_log_path = artifacts_dir / "mutable_access_log.csv"
    signed_log_path = artifacts_dir / "signed_hash_chain_log.csv"
    write_csv(mutable_log_path, mutable_rows, MUTABLE_LOG_FIELDS)
    write_csv(signed_log_path, signed_rows, SIGNED_LOG_FIELDS)

    tampered_paths = write_tampered_logs(artifacts_dir, mutable_rows, signed_rows)
    tamper_results = build_tamper_results(mutable_log_path, signed_log_path, tampered_paths)
    detection_summary = summary_rows(tamper_results)

    tamper_results_path = artifacts_dir / "tamper_test_results.csv"
    detection_summary_path = artifacts_dir / "audit_detection_summary.csv"
    write_csv(
        tamper_results_path,
        tamper_results,
        [
            "log_type",
            "tamper_case",
            "file",
            "expected_tampered",
            "self_verification_valid",
            "self_verification_detected",
            "reference_hash_changed",
            "first_error",
            "error_count",
            "note",
        ],
    )
    write_csv(
        detection_summary_path,
        detection_summary,
        ["log_type", "tamper_cases", "self_detected", "self_not_detected", "self_detection_rate"],
    )
    write_csv(
        Path(args.results_summary_table),
        detection_summary,
        ["log_type", "tamper_cases", "self_detected", "self_not_detected", "self_detection_rate"],
    )

    metrics = build_metrics(tamper_results, len(mutable_rows), input_file)
    write_json(run_dir / "metrics.json", metrics)

    artifact_files = [
        "mutable_access_log.csv",
        "signed_hash_chain_log.csv",
        "tamper_test_results.csv",
        "audit_detection_summary.csv",
    ]
    manifest = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "input_file": str(input_file),
        "input_file_sha256": file_sha256(input_file),
        "audit_log_version": AUDIT_LOG_VERSION,
        "synthetic_only": True,
        "raw_record_included": False,
        "blockchain_implemented": False,
        "artifact_hashes": {
            filename: file_sha256(artifacts_dir / filename)
            for filename in artifact_files
        },
        "tampered_artifact_hashes": {
            f"{log_type}/{case}": file_sha256(path)
            for log_type, cases in tampered_paths.items()
            for case, path in cases.items()
        },
        "notes": [
            "This is a local audit-baseline run, not a blockchain implementation.",
            "Mutable log verification is schema-only and cannot internally detect valid-looking tampered rows.",
            "Signed hash-chain verification uses deterministic demo HMAC signatures for reproducibility.",
        ],
    }
    write_json(artifacts_dir / "dataset_manifest.json", manifest)
    (artifacts_dir / "README.md").write_text(run_readme_text(args.run_id, args.input_run_id, len(mutable_rows)), encoding="utf-8")
    (artifacts_dir / "data_dictionary.md").write_text(data_dictionary_text(), encoding="utf-8")

    signed_original = verify_signed_hash_chain(read_csv(signed_log_path))
    mutable_original = verify_mutable_log(read_csv(mutable_log_path))
    detection_counts = {
        row["log_type"]: {
            "self_detected": row["self_detected"],
            "tamper_cases": row["tamper_cases"],
            "self_detection_rate": row["self_detection_rate"],
        }
        for row in detection_summary
    }
    log_lines = [
        f"created_at_utc={created_at}",
        f"run_id={args.run_id}",
        f"input_file={input_file}",
        f"events_logged={len(mutable_rows)}",
        f"mutable_original_valid={mutable_original['valid']}",
        f"signed_original_valid={signed_original['valid']}",
        f"detection_counts={detection_counts}",
        f"decision_counts={dict(Counter(row['decision'] for row in mutable_rows))}",
        "status=success",
        "claim=audit_baseline_tamper_test_not_blockchain_result",
    ]
    (logs_dir / "audit_baseline.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Wrote audit-baseline run: {run_dir}")
    print(f"Audit events: {len(mutable_rows)}")
    print(f"Mutable original valid: {mutable_original['valid']}")
    print(f"Signed hash-chain original valid: {signed_original['valid']}")
    print(f"Detection summary: {detection_counts}")
    print(f"Summary table: {args.results_summary_table}")


if __name__ == "__main__":
    main()
