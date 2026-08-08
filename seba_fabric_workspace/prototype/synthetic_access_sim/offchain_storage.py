#!/usr/bin/env python3
"""Simulate off-chain encrypted records and metadata-minimized ledger pointers.

This is Step 7 of the SEBA-XAI prototype. It adds the missing storage/privacy
piece after the policy oracle, XAI hashes, signed audit log, and
permissioned-blockchain-style audit simulation.

The script creates:

- encrypted synthetic payload envelopes for records kept off-chain;
- per-request pointer commitments that can be audited without raw records;
- a full-metadata ledger view and a minimized commitment ledger view;
- schema-level metadata-exposure metrics;
- controlled tamper tests for payload and pointer integrity.

Important boundary: the encryption uses a deterministic demo stream based on
HMAC-SHA256 so the run is reproducible with only the Python standard library.
It must not be described as production-grade encryption or key management.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN_ID = "20260527_step7_offchain_encrypted_pointers_seed42"
DEFAULT_STEP1_RUN_ID = "20260527_step1_synthetic_requests_seed42"
DEFAULT_STEP2_RUN_ID = "20260527_step2_policy_oracle_seed42"
DEFAULT_STEP4_RUN_ID = "20260527_step4_permissioned_blockchain_audit_seed42"

STORE_VERSION = "OFFCHAIN-2026-05-STEP7"
PAYLOAD_SCHEMA_VERSION = "SYNTHETIC_RECORD_PAYLOAD_V1"
MINIMIZATION_PROFILE = "SEBA-XAI-MIN-METADATA-V1"
DEMO_ENCRYPTION_KEY = b"seba-xai-demo-offchain-key-not-for-production"

STORAGE_NODES = [
    "STATE_POLICE_RECORD_VAULT_A",
    "STATE_POLICE_RECORD_VAULT_B",
    "FORENSIC_RECORD_VAULT",
    "PROSECUTION_RECORD_VAULT",
]

STORE_FIELDS = [
    "record_pointer_id",
    "record_hash",
    "payload_hash",
    "ciphertext_hash",
    "encryption_nonce",
    "encryption_key_id",
    "encryption_algorithm",
    "payload_schema_version",
    "ciphertext_hex",
    "synthetic_only",
    "raw_payload_in_ledger",
]

POINTER_FIELDS = [
    "request_id",
    "target_record_hash",
    "record_pointer_id",
    "payload_hash",
    "ciphertext_hash",
    "storage_node_id",
    "encryption_key_id",
    "decision_hash",
    "explanation_hash",
    "policy_version_evaluated",
    "block_number",
    "block_hash",
    "event_commitment_hash",
    "pointer_commitment_hash",
    "synthetic_only",
    "raw_record_included",
]

POINTER_COMMITMENT_FIELDS = [
    "request_id",
    "target_record_hash",
    "record_pointer_id",
    "payload_hash",
    "ciphertext_hash",
    "storage_node_id",
    "encryption_key_id",
    "decision_hash",
    "explanation_hash",
    "policy_version_evaluated",
    "block_number",
    "block_hash",
    "event_commitment_hash",
]

FULL_LEDGER_FIELDS = [
    "request_id",
    "timestamp_utc",
    "requester_role",
    "requester_station_id",
    "requester_district_id",
    "requester_agency",
    "target_case_type",
    "target_record_type",
    "target_station_id",
    "target_district_id",
    "record_sensitivity_level",
    "victim_flag",
    "witness_flag",
    "juvenile_flag",
    "evidence_media_flag",
    "sealed_status",
    "purpose",
    "action",
    "decision",
    "primary_reason_code",
    "required_approval",
    "record_pointer_id",
    "payload_hash",
    "ciphertext_hash",
    "explanation_hash",
    "block_number",
    "block_hash",
]

MINIMIZED_LEDGER_FIELDS = [
    "event_ref_hash",
    "request_commitment_hash",
    "requester_context_hash",
    "record_pointer_hash",
    "target_record_commitment_hash",
    "policy_context_hash",
    "decision_hash",
    "explanation_hash",
    "pointer_commitment_hash",
    "payload_hash",
    "ciphertext_hash",
    "block_number",
    "block_hash",
    "policy_version_evaluated",
    "minimization_profile",
]

LEAKAGE_FIELDS = [
    "ledger_design",
    "total_events",
    "column_count",
    "clear_sensitive_columns",
    "hashed_or_commitment_columns",
    "unique_clear_station_ids",
    "unique_clear_roles",
    "unique_clear_record_types",
    "unique_clear_case_types",
    "unique_clear_sensitivity_levels",
    "privacy_flag_columns_visible",
    "sealed_status_visible",
    "decision_visible",
    "reason_code_visible",
    "purpose_visible",
    "action_visible",
    "requester_station_visible",
    "target_station_visible",
    "metadata_exposure_score",
    "interpretation",
]

TAMPER_RESULT_FIELDS = [
    "artifact_type",
    "tamper_case",
    "expected_tampered",
    "store_valid",
    "pointer_valid",
    "verification_detected",
    "first_error",
    "error_count",
    "tampered_file",
    "note",
]

STORAGE_FIELDS = [
    "artifact",
    "rows",
    "storage_bytes",
    "bytes_per_row",
    "note",
]

SUMMARY_FIELDS = [
    "metric",
    "value",
    "interpretation",
]

DIRECT_METADATA_FIELDS = [
    "requester_role",
    "requester_station_id",
    "requester_district_id",
    "requester_agency",
    "target_case_type",
    "target_record_type",
    "target_station_id",
    "target_district_id",
    "record_sensitivity_level",
    "victim_flag",
    "witness_flag",
    "juvenile_flag",
    "evidence_media_flag",
    "sealed_status",
    "purpose",
    "action",
    "decision",
    "primary_reason_code",
    "required_approval",
]

PRIVACY_FLAG_FIELDS = [
    "victim_flag",
    "witness_flag",
    "juvenile_flag",
    "evidence_media_flag",
]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
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


def write_jsonl(path: Path, rows: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def read_jsonl(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


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


def keystream(nonce_hex: str, length: int) -> bytes:
    nonce = bytes.fromhex(nonce_hex)
    output = bytearray()
    counter = 0
    while len(output) < length:
        block = hmac.new(
            DEMO_ENCRYPTION_KEY,
            nonce + counter.to_bytes(8, "big"),
            hashlib.sha256,
        ).digest()
        output.extend(block)
        counter += 1
    return bytes(output[:length])


def xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def encrypt_payload(payload: Dict[str, object], nonce_hex: str) -> str:
    plaintext = canonical_json(payload).encode("utf-8")
    ciphertext = xor_bytes(plaintext, keystream(nonce_hex, len(plaintext)))
    return ciphertext.hex()


def decrypt_payload(ciphertext_hex: str, nonce_hex: str) -> Dict[str, object]:
    ciphertext = bytes.fromhex(ciphertext_hex)
    plaintext = xor_bytes(ciphertext, keystream(nonce_hex, len(ciphertext)))
    return json.loads(plaintext.decode("utf-8"))


def record_pointer_id(record: Dict[str, str]) -> str:
    return stable_hash(
        {
            "store_version": STORE_VERSION,
            "record_hash": record["record_hash"],
            "record_id": record["record_id"],
        }
    )[:24]


def encryption_key_id(record: Dict[str, str]) -> str:
    return "demo-key-" + stable_hash(
        {
            "store_version": STORE_VERSION,
            "state_id": record["state_id"],
            "owner_agency": record["owner_agency"],
        }
    )[:12]


def storage_node_for(record_hash: str) -> str:
    index = int(record_hash[:8], 16) % len(STORAGE_NODES)
    return STORAGE_NODES[index]


def synthetic_payload(record: Dict[str, str]) -> Dict[str, object]:
    return {
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION,
        "synthetic_notice": "Synthetic placeholder only. No real FIR, victim, witness, or case content is present.",
        "record_id": record["record_id"],
        "record_hash": record["record_hash"],
        "case_id": record["case_id"],
        "case_type": record["case_type"],
        "record_type": record["record_type"],
        "originating_station_id": record["originating_station_id"],
        "district_id": record["district_id"],
        "state_id": record["state_id"],
        "sensitivity_level": record["sensitivity_level"],
        "privacy_flags": {
            "victim_flag": record["victim_flag"],
            "witness_flag": record["witness_flag"],
            "juvenile_flag": record["juvenile_flag"],
            "evidence_media_flag": record["evidence_media_flag"],
        },
        "sealed_status": record["sealed_status"],
        "placeholder_sections": [
            {
                "section": "summary",
                "text": f"Synthetic {record['record_type']} placeholder for {record['case_type']}.",
            },
            {
                "section": "handling_note",
                "text": "Access must be governed through policy, audit, and explanation commitments.",
            },
        ],
    }


def build_offchain_store(records: List[Dict[str, str]]) -> List[Dict[str, object]]:
    store_rows: List[Dict[str, object]] = []
    for record in records:
        payload = synthetic_payload(record)
        payload_hash = stable_hash(payload)
        nonce_hex = stable_hash(
            {
                "store_version": STORE_VERSION,
                "record_hash": record["record_hash"],
                "purpose": "deterministic-demo-nonce",
            }
        )[:32]
        ciphertext_hex = encrypt_payload(payload, nonce_hex)
        ciphertext_hash = raw_sha256(bytes.fromhex(ciphertext_hex))
        store_rows.append(
            {
                "record_pointer_id": record_pointer_id(record),
                "record_hash": record["record_hash"],
                "payload_hash": payload_hash,
                "ciphertext_hash": ciphertext_hash,
                "encryption_nonce": nonce_hex,
                "encryption_key_id": encryption_key_id(record),
                "encryption_algorithm": "DEMO-HMAC-SHA256-XOR-STREAM",
                "payload_schema_version": PAYLOAD_SCHEMA_VERSION,
                "ciphertext_hex": ciphertext_hex,
                "synthetic_only": "true",
                "raw_payload_in_ledger": "false",
            }
        )
    return store_rows


def block_index_by_request(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    return {row["request_id"]: row for row in rows}


def pointer_commitment(row: Dict[str, object]) -> str:
    return stable_hash({field: str(row[field]) for field in POINTER_COMMITMENT_FIELDS})


def add_field_mismatch(
    errors: List[str],
    *,
    prefix: str,
    field: str,
    actual: object,
    expected: object,
    source: str,
) -> None:
    if str(actual) != str(expected):
        errors.append(f"{prefix}: {field} does not match {source}")


def build_pointer_rows(
    labeled_rows: List[Dict[str, str]],
    store_by_record_hash: Dict[str, Dict[str, object]],
    block_index: Dict[str, Dict[str, str]],
) -> List[Dict[str, object]]:
    pointer_rows: List[Dict[str, object]] = []
    for labeled in labeled_rows:
        store_row = store_by_record_hash[labeled["target_record_hash"]]
        block_row = block_index.get(labeled["request_id"], {})
        pointer_row: Dict[str, object] = {
            "request_id": labeled["request_id"],
            "target_record_hash": labeled["target_record_hash"],
            "record_pointer_id": store_row["record_pointer_id"],
            "payload_hash": store_row["payload_hash"],
            "ciphertext_hash": store_row["ciphertext_hash"],
            "storage_node_id": storage_node_for(labeled["target_record_hash"]),
            "encryption_key_id": store_row["encryption_key_id"],
            "decision_hash": labeled["decision_hash"],
            "explanation_hash": labeled["explanation_hash"],
            "policy_version_evaluated": labeled["policy_version_evaluated"],
            "block_number": block_row.get("block_number", ""),
            "block_hash": block_row.get("block_hash", ""),
            "event_commitment_hash": block_row.get("event_commitment_hash", ""),
            "synthetic_only": "true",
            "raw_record_included": "false",
        }
        pointer_row["pointer_commitment_hash"] = pointer_commitment(pointer_row)
        pointer_rows.append(pointer_row)
    return pointer_rows


def pointer_by_request(pointer_rows: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    return {str(row["request_id"]): row for row in pointer_rows}


def build_full_metadata_ledger(
    labeled_rows: List[Dict[str, str]],
    pointer_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    pointers = pointer_by_request(pointer_rows)
    rows: List[Dict[str, object]] = []
    for labeled in labeled_rows:
        pointer = pointers[labeled["request_id"]]
        rows.append(
            {
                "request_id": labeled["request_id"],
                "timestamp_utc": labeled["timestamp_utc"],
                "requester_role": labeled["requester_role"],
                "requester_station_id": labeled["requester_station_id"],
                "requester_district_id": labeled["requester_district_id"],
                "requester_agency": labeled["requester_agency"],
                "target_case_type": labeled["target_case_type"],
                "target_record_type": labeled["target_record_type"],
                "target_station_id": labeled["target_station_id"],
                "target_district_id": labeled["target_district_id"],
                "record_sensitivity_level": labeled["record_sensitivity_level"],
                "victim_flag": labeled["victim_flag"],
                "witness_flag": labeled["witness_flag"],
                "juvenile_flag": labeled["juvenile_flag"],
                "evidence_media_flag": labeled["evidence_media_flag"],
                "sealed_status": labeled["sealed_status"],
                "purpose": labeled["purpose"],
                "action": labeled["action"],
                "decision": labeled["decision"],
                "primary_reason_code": labeled["primary_reason_code"],
                "required_approval": labeled["required_approval"],
                "record_pointer_id": pointer["record_pointer_id"],
                "payload_hash": pointer["payload_hash"],
                "ciphertext_hash": pointer["ciphertext_hash"],
                "explanation_hash": pointer["explanation_hash"],
                "block_number": pointer["block_number"],
                "block_hash": pointer["block_hash"],
            }
        )
    return rows


def build_minimized_ledger(
    labeled_rows: List[Dict[str, str]],
    pointer_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    pointers = pointer_by_request(pointer_rows)
    rows: List[Dict[str, object]] = []
    for labeled in labeled_rows:
        pointer = pointers[labeled["request_id"]]
        rows.append(
            {
                "event_ref_hash": stable_hash(
                    {
                        "request_id": labeled["request_id"],
                        "block_hash": pointer["block_hash"],
                        "event_commitment_hash": pointer["event_commitment_hash"],
                    }
                ),
                "request_commitment_hash": labeled["request_content_hash"],
                "requester_context_hash": stable_hash(
                    {
                        "requester_officer_hash": labeled["requester_officer_hash"],
                        "requester_station_id": labeled["requester_station_id"],
                        "requester_role": labeled["requester_role"],
                        "requester_agency": labeled["requester_agency"],
                    }
                ),
                "record_pointer_hash": stable_hash(
                    {
                        "record_pointer_id": pointer["record_pointer_id"],
                        "storage_node_id": pointer["storage_node_id"],
                    }
                ),
                "target_record_commitment_hash": labeled["target_record_hash"],
                "policy_context_hash": stable_hash(
                    {
                        "policy_version": labeled["policy_version_evaluated"],
                        "primary_reason_code": labeled["primary_reason_code"],
                        "required_approval": labeled["required_approval"],
                        "decision": labeled["decision"],
                    }
                ),
                "decision_hash": labeled["decision_hash"],
                "explanation_hash": labeled["explanation_hash"],
                "pointer_commitment_hash": pointer["pointer_commitment_hash"],
                "payload_hash": pointer["payload_hash"],
                "ciphertext_hash": pointer["ciphertext_hash"],
                "block_number": pointer["block_number"],
                "block_hash": pointer["block_hash"],
                "policy_version_evaluated": labeled["policy_version_evaluated"],
                "minimization_profile": MINIMIZATION_PROFILE,
            }
        )
    return rows


def unique_values(rows: List[Dict[str, object]], fields: Iterable[str]) -> set[str]:
    values: set[str] = set()
    for row in rows:
        for field in fields:
            if field in row:
                values.add(str(row[field]))
    return values


def metadata_leakage_row(ledger_design: str, rows: List[Dict[str, object]]) -> Dict[str, object]:
    columns = list(rows[0].keys()) if rows else []
    clear_sensitive = [field for field in DIRECT_METADATA_FIELDS if field in columns]
    hashed_or_commitment = [
        field
        for field in columns
        if field.endswith("_hash") or "commitment" in field or field.endswith("_pointer_hash")
    ]
    exposure_score = len(clear_sensitive) / len(DIRECT_METADATA_FIELDS) if DIRECT_METADATA_FIELDS else 0.0
    direct_station_fields = [
        field
        for field in ["requester_station_id", "target_station_id", "requester_district_id", "target_district_id"]
        if field in columns
    ]
    interpretation = (
        "High schema-level metadata exposure because clear policy context is visible."
        if clear_sensitive
        else "Reduced schema-level exposure because sensitive context is represented by hashes/commitments. This is not a formal privacy proof."
    )
    return {
        "ledger_design": ledger_design,
        "total_events": len(rows),
        "column_count": len(columns),
        "clear_sensitive_columns": len(clear_sensitive),
        "hashed_or_commitment_columns": len(hashed_or_commitment),
        "unique_clear_station_ids": len(unique_values(rows, direct_station_fields)),
        "unique_clear_roles": len(unique_values(rows, ["requester_role"])) if "requester_role" in columns else 0,
        "unique_clear_record_types": len(unique_values(rows, ["target_record_type"])) if "target_record_type" in columns else 0,
        "unique_clear_case_types": len(unique_values(rows, ["target_case_type"])) if "target_case_type" in columns else 0,
        "unique_clear_sensitivity_levels": len(unique_values(rows, ["record_sensitivity_level"])) if "record_sensitivity_level" in columns else 0,
        "privacy_flag_columns_visible": sum(1 for field in PRIVACY_FLAG_FIELDS if field in columns),
        "sealed_status_visible": str("sealed_status" in columns).lower(),
        "decision_visible": str("decision" in columns).lower(),
        "reason_code_visible": str("primary_reason_code" in columns).lower(),
        "purpose_visible": str("purpose" in columns).lower(),
        "action_visible": str("action" in columns).lower(),
        "requester_station_visible": str("requester_station_id" in columns).lower(),
        "target_station_visible": str("target_station_id" in columns).lower(),
        "metadata_exposure_score": f"{exposure_score:.4f}",
        "interpretation": interpretation,
    }


def verify_store_rows(store_rows: List[Dict[str, object]]) -> Dict[str, object]:
    errors: List[str] = []
    seen_pointers: set[str] = set()
    for index, row in enumerate(store_rows, start=1):
        missing = [field for field in STORE_FIELDS if field not in row]
        if missing:
            errors.append(f"store row {index}: missing fields {missing}")
            continue
        pointer_id = str(row["record_pointer_id"])
        if pointer_id in seen_pointers:
            errors.append(f"store row {index}: duplicate record_pointer_id {pointer_id}")
        seen_pointers.add(pointer_id)

        try:
            ciphertext_bytes = bytes.fromhex(str(row["ciphertext_hex"]))
        except ValueError:
            errors.append(f"store row {index}: ciphertext_hex is not valid hex")
            continue

        expected_ciphertext_hash = raw_sha256(ciphertext_bytes)
        if row["ciphertext_hash"] != expected_ciphertext_hash:
            errors.append(f"store row {index}: ciphertext_hash mismatch")

        try:
            payload = decrypt_payload(str(row["ciphertext_hex"]), str(row["encryption_nonce"]))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"store row {index}: decrypt/parse failed: {exc}")
            continue

        expected_payload_hash = stable_hash(payload)
        if row["payload_hash"] != expected_payload_hash:
            errors.append(f"store row {index}: payload_hash mismatch")

    return {
        "valid": not errors,
        "error_count": len(errors),
        "first_error": errors[0] if errors else "",
        "note": "Store verification decrypts synthetic payloads and recomputes payload and ciphertext hashes.",
    }


def verify_pointer_rows(
    pointer_rows: List[Dict[str, object]],
    store_rows: List[Dict[str, object]],
    labeled_rows: List[Dict[str, str]] | None = None,
    block_rows: List[Dict[str, str]] | None = None,
) -> Dict[str, object]:
    errors: List[str] = []
    store_by_pointer = {str(row["record_pointer_id"]): row for row in store_rows}
    labeled_by_request = (
        {str(row["request_id"]): row for row in labeled_rows}
        if labeled_rows is not None
        else None
    )
    block_by_request = (
        {str(row["request_id"]): row for row in block_rows}
        if block_rows is not None
        else None
    )
    seen_requests: set[str] = set()

    for index, row in enumerate(pointer_rows, start=1):
        prefix = f"pointer row {index}"
        missing = [field for field in POINTER_FIELDS if field not in row]
        if missing:
            errors.append(f"{prefix}: missing fields {missing}")
            continue

        request_id = str(row["request_id"])
        if request_id in seen_requests:
            errors.append(f"{prefix}: duplicate request_id {request_id}")
        seen_requests.add(request_id)

        expected_commitment = pointer_commitment(row)
        if row["pointer_commitment_hash"] != expected_commitment:
            errors.append(f"{prefix}: pointer_commitment_hash mismatch")

        store_row = store_by_pointer.get(str(row["record_pointer_id"]))
        if store_row is None:
            errors.append(f"{prefix}: missing off-chain store entry")
            continue

        add_field_mismatch(
            errors,
            prefix=prefix,
            field="target_record_hash",
            actual=row["target_record_hash"],
            expected=store_row["record_hash"],
            source="off-chain store record_hash",
        )
        if row["payload_hash"] != store_row["payload_hash"]:
            errors.append(f"{prefix}: payload_hash does not match store")

        if row["ciphertext_hash"] != store_row["ciphertext_hash"]:
            errors.append(f"{prefix}: ciphertext_hash does not match store")

        add_field_mismatch(
            errors,
            prefix=prefix,
            field="encryption_key_id",
            actual=row["encryption_key_id"],
            expected=store_row["encryption_key_id"],
            source="off-chain store encryption_key_id",
        )
        add_field_mismatch(
            errors,
            prefix=prefix,
            field="storage_node_id",
            actual=row["storage_node_id"],
            expected=storage_node_for(str(row["target_record_hash"])),
            source="deterministic storage-node assignment",
        )

        if labeled_by_request is not None:
            labeled = labeled_by_request.get(request_id)
            if labeled is None:
                errors.append(f"{prefix}: missing Step 2 labeled request anchor")
            else:
                for field in [
                    "target_record_hash",
                    "decision_hash",
                    "explanation_hash",
                    "policy_version_evaluated",
                ]:
                    add_field_mismatch(
                        errors,
                        prefix=prefix,
                        field=field,
                        actual=row[field],
                        expected=labeled[field],
                        source="Step 2 labeled request artifact",
                    )

        if block_by_request is not None:
            block_row = block_by_request.get(request_id)
            if block_row is None:
                errors.append(f"{prefix}: missing Step 4 block-index anchor")
            else:
                for field in ["block_number", "block_hash", "event_commitment_hash"]:
                    add_field_mismatch(
                        errors,
                        prefix=prefix,
                        field=field,
                        actual=row[field],
                        expected=block_row[field],
                        source="Step 4 block-event index artifact",
                    )

    return {
        "valid": not errors,
        "error_count": len(errors),
        "first_error": errors[0] if errors else "",
        "note": "Pointer verification recomputes pointer commitments, checks store hash references, and anchors decision/XAI/block references to Step 2 and Step 4 artifacts when provided.",
    }


def tamper_store_rows(store_rows: List[Dict[str, object]], tamper_case: str) -> List[Dict[str, object]]:
    tampered = deepcopy(store_rows)
    if not tampered:
        return tampered
    target = min(12, len(tampered) - 1)

    if tamper_case == "changed_ciphertext":
        ciphertext = str(tampered[target]["ciphertext_hex"])
        replacement = "0" if ciphertext[0] != "0" else "1"
        tampered[target]["ciphertext_hex"] = replacement + ciphertext[1:]
        return tampered

    if tamper_case == "changed_payload_hash":
        tampered[target]["payload_hash"] = "tampered_" + str(tampered[target]["payload_hash"])[:55]
        return tampered

    if tamper_case == "deleted_store_record":
        del tampered[target]
        return tampered

    raise ValueError(f"unknown store tamper case: {tamper_case}")


def tamper_pointer_rows(pointer_rows: List[Dict[str, object]], tamper_case: str) -> List[Dict[str, object]]:
    tampered = deepcopy(pointer_rows)
    if not tampered:
        return tampered
    target = min(20, len(tampered) - 1)

    if tamper_case == "changed_pointer_commitment":
        tampered[target]["pointer_commitment_hash"] = "tampered_" + str(tampered[target]["pointer_commitment_hash"])[:55]
        return tampered

    if tamper_case == "changed_payload_hash_in_pointer":
        tampered[target]["payload_hash"] = "tampered_" + str(tampered[target]["payload_hash"])[:55]
        return tampered

    if tamper_case == "changed_explanation_hash_in_pointer":
        tampered[target]["explanation_hash"] = "tampered_" + str(tampered[target]["explanation_hash"])[:55]
        return tampered

    if tamper_case == "changed_explanation_hash_recomputed_commitment":
        tampered[target]["explanation_hash"] = "tampered_" + str(tampered[target]["explanation_hash"])[:55]
        tampered[target]["pointer_commitment_hash"] = pointer_commitment(tampered[target])
        return tampered

    if tamper_case == "changed_event_commitment_recomputed_pointer":
        tampered[target]["event_commitment_hash"] = "tampered_" + str(tampered[target]["event_commitment_hash"])[:55]
        tampered[target]["pointer_commitment_hash"] = pointer_commitment(tampered[target])
        return tampered

    if tamper_case == "changed_storage_node":
        tampered[target]["storage_node_id"] = "UNAUTHORIZED_RECORD_VAULT"
        return tampered

    if tamper_case == "changed_storage_node_recomputed_commitment":
        tampered[target]["storage_node_id"] = "UNAUTHORIZED_RECORD_VAULT"
        tampered[target]["pointer_commitment_hash"] = pointer_commitment(tampered[target])
        return tampered

    raise ValueError(f"unknown pointer tamper case: {tamper_case}")


def build_tamper_results(
    artifacts_dir: Path,
    store_rows: List[Dict[str, object]],
    pointer_rows: List[Dict[str, object]],
    labeled_rows: List[Dict[str, str]],
    block_rows: List[Dict[str, str]],
) -> List[Dict[str, object]]:
    tamper_dir = artifacts_dir / "tampered_artifacts"
    rows: List[Dict[str, object]] = []

    original_store = verify_store_rows(store_rows)
    original_pointers = verify_pointer_rows(pointer_rows, store_rows, labeled_rows, block_rows)
    rows.append(
        {
            "artifact_type": "original",
            "tamper_case": "original",
            "expected_tampered": "false",
            "store_valid": str(original_store["valid"]).lower(),
            "pointer_valid": str(original_pointers["valid"]).lower(),
            "verification_detected": "false",
            "first_error": original_store["first_error"] or original_pointers["first_error"],
            "error_count": int(original_store["error_count"]) + int(original_pointers["error_count"]),
            "tampered_file": "",
            "note": "Original off-chain store and pointer table should verify cleanly.",
        }
    )

    for case in ["changed_ciphertext", "changed_payload_hash", "deleted_store_record"]:
        tampered_store = tamper_store_rows(store_rows, case)
        path = tamper_dir / "store" / f"{case}.jsonl"
        write_jsonl(path, tampered_store)
        store_result = verify_store_rows(tampered_store)
        pointer_result = verify_pointer_rows(pointer_rows, tampered_store, labeled_rows, block_rows)
        detected = (not bool(store_result["valid"])) or (not bool(pointer_result["valid"]))
        rows.append(
            {
                "artifact_type": "offchain_store",
                "tamper_case": case,
                "expected_tampered": "true",
                "store_valid": str(store_result["valid"]).lower(),
                "pointer_valid": str(pointer_result["valid"]).lower(),
                "verification_detected": str(detected).lower(),
                "first_error": store_result["first_error"] or pointer_result["first_error"],
                "error_count": int(store_result["error_count"]) + int(pointer_result["error_count"]),
                "tampered_file": str(path),
                "note": "Tamper test for encrypted off-chain payload envelope.",
            }
        )

    for case in [
        "changed_pointer_commitment",
        "changed_payload_hash_in_pointer",
        "changed_explanation_hash_in_pointer",
        "changed_explanation_hash_recomputed_commitment",
        "changed_event_commitment_recomputed_pointer",
        "changed_storage_node",
        "changed_storage_node_recomputed_commitment",
    ]:
        tampered_pointers = tamper_pointer_rows(pointer_rows, case)
        path = tamper_dir / "pointers" / f"{case}.csv"
        write_csv(path, tampered_pointers, POINTER_FIELDS)
        store_result = verify_store_rows(store_rows)
        pointer_result = verify_pointer_rows(tampered_pointers, store_rows, labeled_rows, block_rows)
        detected = (not bool(store_result["valid"])) or (not bool(pointer_result["valid"]))
        rows.append(
            {
                "artifact_type": "pointer_table",
                "tamper_case": case,
                "expected_tampered": "true",
                "store_valid": str(store_result["valid"]).lower(),
                "pointer_valid": str(pointer_result["valid"]).lower(),
                "verification_detected": str(detected).lower(),
                "first_error": store_result["first_error"] or pointer_result["first_error"],
                "error_count": int(store_result["error_count"]) + int(pointer_result["error_count"]),
                "tampered_file": str(path),
                "note": "Tamper test for request-to-record pointer commitments.",
            }
        )

    return rows


def storage_rows(paths_and_counts: List[Tuple[str, Path, int, str]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for name, path, count, note in paths_and_counts:
        size = path.stat().st_size
        rows.append(
            {
                "artifact": name,
                "rows": count,
                "storage_bytes": size,
                "bytes_per_row": f"{size / count:.3f}" if count else "0.000",
                "note": note,
            }
        )
    return rows


def build_summary_rows(
    record_count: int,
    pointer_count: int,
    leakage_rows: List[Dict[str, object]],
    tamper_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    full = next(row for row in leakage_rows if row["ledger_design"] == "full_metadata_ledger")
    minimized = next(row for row in leakage_rows if row["ledger_design"] == "minimized_commitment_ledger")
    tampered = [row for row in tamper_rows if row["expected_tampered"] == "true"]
    detected = sum(1 for row in tampered if row["verification_detected"] == "true")
    return [
        {
            "metric": "offchain_record_payloads",
            "value": record_count,
            "interpretation": "Synthetic record payload envelopes stored off-chain.",
        },
        {
            "metric": "request_pointer_commitments",
            "value": pointer_count,
            "interpretation": "Access requests linked to off-chain payload hashes and audit blocks.",
        },
        {
            "metric": "full_metadata_clear_sensitive_columns",
            "value": full["clear_sensitive_columns"],
            "interpretation": "Clear contextual fields visible in the intentionally overexposed ledger view.",
        },
        {
            "metric": "minimized_metadata_clear_sensitive_columns",
            "value": minimized["clear_sensitive_columns"],
            "interpretation": "Clear contextual fields visible after commitment-based minimization.",
        },
        {
            "metric": "full_metadata_exposure_score",
            "value": full["metadata_exposure_score"],
            "interpretation": "Schema-level exposure score; not a formal privacy metric.",
        },
        {
            "metric": "minimized_metadata_exposure_score",
            "value": minimized["metadata_exposure_score"],
            "interpretation": "Schema-level exposure score; not a formal privacy metric.",
        },
        {
            "metric": "tamper_cases_detected",
            "value": f"{detected}/{len(tampered)}",
            "interpretation": "Controlled payload and pointer tampering detected by anchored local verification.",
        },
        {
            "metric": "raw_payloads_on_ledger",
            "value": "false",
            "interpretation": "Raw synthetic payloads are kept out of both ledger views.",
        },
    ]


def build_metrics(
    record_count: int,
    pointer_count: int,
    leakage_rows: List[Dict[str, object]],
    tamper_rows: List[Dict[str, object]],
    input_files: Dict[str, Path],
) -> Dict[str, object]:
    tampered = [row for row in tamper_rows if row["expected_tampered"] == "true"]
    detected = sum(1 for row in tampered if row["verification_detected"] == "true")
    return {
        "artifact_type": "offchain_encrypted_pointer_and_metadata_leakage_simulation",
        "result_claim": "synthetic off-chain storage, pointer integrity, and schema-level metadata exposure comparison only",
        "store_version": STORE_VERSION,
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION,
        "minimization_profile": MINIMIZATION_PROFILE,
        "input_files": {key: str(path) for key, path in input_files.items()},
        "counts": {
            "offchain_record_payloads": record_count,
            "request_pointer_commitments": pointer_count,
            "ledger_events": pointer_count,
        },
        "metadata_leakage": leakage_rows,
        "tamper_detection": {
            "tamper_cases": len(tampered),
            "detected": detected,
            "not_detected": len(tampered) - detected,
            "detection_rate": detected / len(tampered) if tampered else 0.0,
        },
        "important_interpretation": [
            "This step models the SEBA-XAI design principle that raw records remain off-chain.",
            "The minimized ledger stores commitments and hashes instead of clear role, station, sensitivity, purpose, action, decision, and reason-code metadata.",
            "Pointer verification anchors decision hashes, XAI hashes, and block references back to generated Step 2 and Step 4 artifacts.",
            "The metadata score is a schema-level exposure measure, not differential privacy, anonymity, or a legal-compliance proof.",
        ],
        "limitations": [
            "Encryption is a deterministic demo construction for reproducibility, not production-grade cryptography.",
            "No real CCTNS, ICJS, FIR, victim, witness, or police record is included.",
            "No key rotation, hardware security module, access-token exchange, or distributed storage service is implemented.",
            "Metadata linkage through stable hashes is not fully eliminated and would require stronger privacy analysis in a real system.",
        ],
    }


def data_dictionary_text() -> str:
    return """# Off-Chain Storage And Metadata Leakage Data Dictionary

This file describes Step 7 outputs.

## Important Boundary

The encrypted store is a deterministic prototype simulation using a demo key.
It is not production encryption, key management, legal compliance, or a real
police data store.

## Core Files

- `offchain_record_store.jsonl`: encrypted synthetic record payload envelopes.
- `offchain_pointer_table.csv`: request-to-record pointer commitments.
- `full_metadata_ledger.csv`: intentionally overexposed ledger design for comparison.
- `minimized_commitment_ledger.csv`: commitment-based minimized ledger design.
- `metadata_leakage_comparison.csv`: schema-level metadata exposure comparison.
    - `offchain_tamper_test_results.csv`: controlled payload/pointer tamper tests, including recomputed pointer-commitment cases.
- `storage_overhead_offchain.csv`: local artifact sizes.

## Key Fields

| Field | Meaning |
|---|---|
| `record_pointer_id` | Synthetic pointer to an off-chain payload envelope. |
| `payload_hash` | Hash of the decrypted synthetic payload. |
| `ciphertext_hash` | Hash of the encrypted payload bytes. |
| `pointer_commitment_hash` | Hash binding the request, payload hash, XAI hash, decision hash, and audit block reference. |
| `explanation_hash` | Hash of the Step 2 XAI artifact. Raw explanation text is not stored in the ledger views. |
| `metadata_exposure_score` | Fraction of predefined sensitive metadata columns visible in clear text. This is not a formal privacy metric. |

## Correct Interpretation

    Step 7 supports the architecture claim that SEBA-XAI can keep raw records
    off-chain while logging verifiable commitments. Pointer verification checks
    local consistency and anchors decision/XAI/block references to the generated
    Step 2 and Step 4 artifacts. It also shows why metadata minimization matters:
    a ledger that stores only hashes can still verify integrity with less direct
    exposure than a ledger containing clear role, station, sensitivity, purpose,
    action, decision, and reason-code fields.
"""


def run_readme_text(run_id: str, record_count: int, pointer_count: int) -> str:
    return f"""# Run {run_id}

Purpose: Step 7 off-chain encrypted storage/pointer simulation and metadata-leakage analysis.

Synthetic off-chain payloads: `{record_count}`

Request pointer commitments: `{pointer_count}`

## What This Run Contains

- encrypted synthetic record payload envelopes;
- request-to-record pointer commitments;
- full metadata versus minimized commitment ledger views;
- metadata-exposure comparison;
- controlled payload and pointer tamper tests.

## What This Run Does Not Contain

- No real police, CCTNS, ICJS, FIR, victim, witness, or case records.
- No production encryption or key management.
- No legal-compliance proof.
- No deployed storage service or Hyperledger Fabric private data collection.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/offchain_storage.py \\
  --run-id {run_id}
```
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate SEBA-XAI off-chain storage and metadata minimization.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--step1-run-id", default=DEFAULT_STEP1_RUN_ID)
    parser.add_argument("--step2-run-id", default=DEFAULT_STEP2_RUN_ID)
    parser.add_argument("--step4-run-id", default=DEFAULT_STEP4_RUN_ID)
    parser.add_argument(
        "--prototype-results-summary-table",
        default=str(ROOT / "prototype" / "results" / "tables" / "offchain_storage_step7_summary.csv"),
    )
    parser.add_argument(
        "--root-results-summary-table",
        default=str(ROOT / "results" / "tables" / "offchain_storage_step7_summary.csv"),
    )
    parser.add_argument(
        "--experiment-run-record",
        default="",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = ROOT / "prototype" / "runs" / args.run_id
    artifacts_dir = run_dir / "artifacts"
    logs_dir = run_dir / "logs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    records_file = ROOT / "prototype" / "runs" / args.step1_run_id / "artifacts" / "records.csv"
    labeled_file = ROOT / "prototype" / "runs" / args.step2_run_id / "artifacts" / "labeled_access_requests.csv"
    block_index_file = ROOT / "prototype" / "runs" / args.step4_run_id / "artifacts" / "block_event_index.csv"
    input_files = {
        "records_file": records_file,
        "labeled_file": labeled_file,
        "block_index_file": block_index_file,
    }

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    config = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "step1_run_id": args.step1_run_id,
        "step2_run_id": args.step2_run_id,
        "step4_run_id": args.step4_run_id,
        "store_version": STORE_VERSION,
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION,
        "minimization_profile": MINIMIZATION_PROFILE,
        "step": "step_7_offchain_storage_and_metadata_leakage",
        "synthetic_only": True,
        "raw_record_included": False,
        "production_encryption": False,
    }
    write_yaml(run_dir / "config.yaml", config)

    records = read_csv(records_file)
    labeled_rows = read_csv(labeled_file)
    block_rows = read_csv(block_index_file)
    block_index = block_index_by_request(block_rows)

    store_rows = build_offchain_store(records)
    store_by_record_hash = {str(row["record_hash"]): row for row in store_rows}
    pointer_rows = build_pointer_rows(labeled_rows, store_by_record_hash, block_index)
    full_ledger_rows = build_full_metadata_ledger(labeled_rows, pointer_rows)
    minimized_ledger_rows = build_minimized_ledger(labeled_rows, pointer_rows)
    leakage_rows = [
        metadata_leakage_row("full_metadata_ledger", full_ledger_rows),
        metadata_leakage_row("minimized_commitment_ledger", minimized_ledger_rows),
    ]
    tamper_rows = build_tamper_results(artifacts_dir, store_rows, pointer_rows, labeled_rows, block_rows)

    store_path = artifacts_dir / "offchain_record_store.jsonl"
    pointer_path = artifacts_dir / "offchain_pointer_table.csv"
    full_ledger_path = artifacts_dir / "full_metadata_ledger.csv"
    minimized_ledger_path = artifacts_dir / "minimized_commitment_ledger.csv"
    leakage_path = artifacts_dir / "metadata_leakage_comparison.csv"
    tamper_path = artifacts_dir / "offchain_tamper_test_results.csv"
    storage_path = artifacts_dir / "storage_overhead_offchain.csv"
    summary_path = artifacts_dir / "offchain_storage_summary.csv"

    write_jsonl(store_path, store_rows)
    write_csv(pointer_path, pointer_rows, POINTER_FIELDS)
    write_csv(full_ledger_path, full_ledger_rows, FULL_LEDGER_FIELDS)
    write_csv(minimized_ledger_path, minimized_ledger_rows, MINIMIZED_LEDGER_FIELDS)
    write_csv(leakage_path, leakage_rows, LEAKAGE_FIELDS)
    write_csv(tamper_path, tamper_rows, TAMPER_RESULT_FIELDS)

    storage_comparison = storage_rows(
        [
            ("offchain_record_store.jsonl", store_path, len(store_rows), "Encrypted synthetic payload envelopes."),
            ("offchain_pointer_table.csv", pointer_path, len(pointer_rows), "Private request-to-record pointer commitments."),
            ("full_metadata_ledger.csv", full_ledger_path, len(full_ledger_rows), "Overexposed ledger view for comparison."),
            ("minimized_commitment_ledger.csv", minimized_ledger_path, len(minimized_ledger_rows), "Minimized commitment-based ledger view."),
        ]
    )
    write_csv(storage_path, storage_comparison, STORAGE_FIELDS)

    summary_rows = build_summary_rows(len(store_rows), len(pointer_rows), leakage_rows, tamper_rows)
    write_csv(summary_path, summary_rows, SUMMARY_FIELDS)
    write_csv(Path(args.prototype_results_summary_table), summary_rows, SUMMARY_FIELDS)
    write_csv(Path(args.root_results_summary_table), summary_rows, SUMMARY_FIELDS)

    metrics = build_metrics(len(store_rows), len(pointer_rows), leakage_rows, tamper_rows, input_files)
    write_json(run_dir / "metrics.json", metrics)

    artifact_files = [
        "offchain_record_store.jsonl",
        "offchain_pointer_table.csv",
        "full_metadata_ledger.csv",
        "minimized_commitment_ledger.csv",
        "metadata_leakage_comparison.csv",
        "offchain_tamper_test_results.csv",
        "storage_overhead_offchain.csv",
        "offchain_storage_summary.csv",
    ]
    manifest = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "input_hashes": {key: file_sha256(path) for key, path in input_files.items()},
        "store_version": STORE_VERSION,
        "synthetic_only": True,
        "raw_record_included": False,
        "raw_payload_in_ledger": False,
        "production_encryption": False,
        "artifact_hashes": {
            filename: file_sha256(artifacts_dir / filename)
            for filename in artifact_files
        },
        "notes": [
            "This is an off-chain storage and metadata-minimization simulation.",
            "Raw synthetic payloads are encrypted in offchain_record_store.jsonl and are not placed in ledger views.",
            "Demo encryption is deterministic and not production-grade.",
        ],
    }
    write_json(artifacts_dir / "dataset_manifest.json", manifest)
    (artifacts_dir / "README.md").write_text(run_readme_text(args.run_id, len(store_rows), len(pointer_rows)), encoding="utf-8")
    (artifacts_dir / "data_dictionary.md").write_text(data_dictionary_text(), encoding="utf-8")

    experiment_run_record_path = (
        Path(args.experiment_run_record)
        if args.experiment_run_record
        else ROOT / "experiments" / "runs" / f"{args.run_id}.json"
    )
    experiment_record = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "prototype_run_dir": str(run_dir),
        "summary_table": str(args.root_results_summary_table),
        "artifact_type": "step_7_offchain_storage_and_metadata_leakage",
        "result_claim": metrics["result_claim"],
        "synthetic_only": True,
        "limitations": metrics["limitations"],
    }
    write_json(experiment_run_record_path, experiment_record)

    original_store_verification = verify_store_rows(store_rows)
    original_pointer_verification = verify_pointer_rows(pointer_rows, store_rows, labeled_rows, block_rows)
    tampered = [row for row in tamper_rows if row["expected_tampered"] == "true"]
    detected = sum(1 for row in tampered if row["verification_detected"] == "true")
    log_lines = [
        f"created_at_utc={created_at}",
        f"run_id={args.run_id}",
        f"records={len(store_rows)}",
        f"request_pointers={len(pointer_rows)}",
        f"store_valid={original_store_verification['valid']}",
        f"pointers_valid={original_pointer_verification['valid']}",
        f"tamper_detected={detected}/{len(tampered)}",
        f"metadata_leakage={leakage_rows}",
        "status=success",
        "claim=offchain_storage_and_metadata_exposure_simulation_only",
    ]
    (logs_dir / "offchain_storage.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Wrote off-chain storage run: {run_dir}")
    print(f"Off-chain record payloads: {len(store_rows)}")
    print(f"Request pointer commitments: {len(pointer_rows)}")
    print(f"Tamper detected: {detected}/{len(tampered)}")
    print(f"Summary table: {args.prototype_results_summary_table}")


if __name__ == "__main__":
    main()
