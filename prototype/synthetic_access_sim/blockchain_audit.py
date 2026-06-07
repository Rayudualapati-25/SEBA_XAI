#!/usr/bin/env python3
"""Simulate a permissioned blockchain-style audit layer for SEBA-XAI.

This is Step 4 of the prototype. It reads the Step 3 signed audit events,
groups them into blocks, computes Merkle roots, adds deterministic validator
and quorum signatures, and tests whether tampering is detected.

This is not Hyperledger Fabric, not PoW, not PoS, and not a production
blockchain. It is a local permissioned PoA/PBFT-style audit abstraction that
keeps only audit commitments and metadata in the chain.
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
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_RUN_ID = "20260527_step3_audit_baselines_seed42"
DEFAULT_RUN_ID = "20260527_step4_permissioned_blockchain_audit_seed42"
CHAIN_VERSION = "CHAIN-2026-05-STEP4"
GENESIS_BLOCK_HASH = "GENESIS_BLOCK"
DEFAULT_BLOCK_SIZE = 50
QUORUM_THRESHOLD = 3


VALIDATORS = [
    {
        "validator_id": "POLICE_AUDIT_NODE",
        "agency_type": "POLICE",
        "description": "Synthetic state police audit node",
    },
    {
        "validator_id": "FORENSIC_AUDIT_NODE",
        "agency_type": "FORENSIC",
        "description": "Synthetic forensic-services audit node",
    },
    {
        "validator_id": "PROSECUTION_AUDIT_NODE",
        "agency_type": "PROSECUTION",
        "description": "Synthetic prosecution audit node",
    },
    {
        "validator_id": "COURT_ICJS_AUDIT_NODE",
        "agency_type": "COURT_ICJS",
        "description": "Synthetic court/ICJS-style audit node",
    },
]

EVENT_COMMITMENT_FIELDS = [
    "event_sequence",
    "event_id",
    "request_id",
    "requester_station_id",
    "target_record_hash",
    "decision",
    "primary_reason_code",
    "policy_version_evaluated",
    "request_content_hash",
    "decision_hash",
    "explanation_hash",
    "audit_anchor_hash",
    "event_hash",
]

BLOCK_INDEX_FIELDS = [
    "block_number",
    "event_sequence",
    "event_id",
    "request_id",
    "event_commitment_hash",
    "block_hash",
    "merkle_root",
    "validator_id",
]

TAMPER_CASES = [
    "changed_event_commitment",
    "deleted_event_commitment",
    "changed_merkle_root",
    "changed_validator_signature",
    "reordered_blocks",
]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def validator_key(validator_id: str) -> bytes:
    return f"seba-xai-demo-validator-key::{validator_id}".encode("utf-8")


def sign_with_validator(validator_id: str, payload_hash: str) -> str:
    return hmac.new(validator_key(validator_id), payload_hash.encode("utf-8"), hashlib.sha256).hexdigest()


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


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def chunked(rows: List[Dict[str, str]], size: int) -> Iterable[List[Dict[str, str]]]:
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def merkle_root(hashes: List[str]) -> str:
    if not hashes:
        return stable_hash({"empty": True})
    current = list(hashes)
    while len(current) > 1:
        if len(current) % 2 == 1:
            current.append(current[-1])
        current = [
            stable_hash({"left": current[index], "right": current[index + 1]})
            for index in range(0, len(current), 2)
        ]
    return current[0]


def event_commitment(row: Dict[str, str]) -> Dict[str, str]:
    return {field: str(row[field]) for field in EVENT_COMMITMENT_FIELDS}


def choose_validator(block_number: int) -> Dict[str, str]:
    return VALIDATORS[(block_number - 1) % len(VALIDATORS)]


def choose_quorum_validators(block_number: int) -> List[Dict[str, str]]:
    start = (block_number - 1) % len(VALIDATORS)
    return [VALIDATORS[(start + offset) % len(VALIDATORS)] for offset in range(QUORUM_THRESHOLD)]


def block_payload(block: Dict[str, object]) -> Dict[str, object]:
    return {
        "block_number": block["block_number"],
        "timestamp_utc": block["timestamp_utc"],
        "chain_version": block["chain_version"],
        "consensus_model": block["consensus_model"],
        "validator_id": block["validator_id"],
        "validator_agency_type": block["validator_agency_type"],
        "previous_block_hash": block["previous_block_hash"],
        "event_count": block["event_count"],
        "first_event_sequence": block["first_event_sequence"],
        "last_event_sequence": block["last_event_sequence"],
        "event_commitment_hashes": block["event_commitment_hashes"],
        "merkle_root": block["merkle_root"],
    }


def compute_block_hash(block_payload_hash: str, validator_signature: str, quorum_signature_hash: str) -> str:
    return stable_hash(
        {
            "block_payload_hash": block_payload_hash,
            "validator_signature": validator_signature,
            "quorum_signature_hash": quorum_signature_hash,
        }
    )


def build_block(
    block_number: int,
    events: List[Dict[str, str]],
    previous_block_hash: str,
) -> Dict[str, object]:
    validator = choose_validator(block_number)
    quorum_validators = choose_quorum_validators(block_number)
    commitments = [event_commitment(row) for row in events]
    commitment_hashes = [stable_hash(commitment) for commitment in commitments]

    block: Dict[str, object] = {
        "block_number": block_number,
        "timestamp_utc": events[-1]["timestamp_utc"],
        "chain_version": CHAIN_VERSION,
        "consensus_model": "permissioned_poa_quorum_simulation",
        "validator_id": validator["validator_id"],
        "validator_agency_type": validator["agency_type"],
        "previous_block_hash": previous_block_hash,
        "event_count": len(events),
        "first_event_sequence": int(events[0]["event_sequence"]),
        "last_event_sequence": int(events[-1]["event_sequence"]),
        "event_commitment_hashes": commitment_hashes,
        "merkle_root": merkle_root(commitment_hashes),
    }
    payload_hash = stable_hash(block_payload(block))
    validator_signature = sign_with_validator(str(block["validator_id"]), payload_hash)
    endorsements = [
        {
            "validator_id": quorum_validator["validator_id"],
            "agency_type": quorum_validator["agency_type"],
            "signature": sign_with_validator(quorum_validator["validator_id"], payload_hash),
        }
        for quorum_validator in quorum_validators
    ]
    quorum_signature_hash = stable_hash(endorsements)
    block.update(
        {
            "block_payload_hash": payload_hash,
            "validator_signature": validator_signature,
            "quorum_threshold": QUORUM_THRESHOLD,
            "quorum_endorsements": endorsements,
            "quorum_signature_hash": quorum_signature_hash,
            "block_hash": compute_block_hash(payload_hash, validator_signature, quorum_signature_hash),
        }
    )
    return block


def build_chain(rows: List[Dict[str, str]], block_size: int) -> List[Dict[str, object]]:
    blocks: List[Dict[str, object]] = []
    previous_hash = GENESIS_BLOCK_HASH
    for block_number, events in enumerate(chunked(rows, block_size), start=1):
        block = build_block(block_number, events, previous_hash)
        blocks.append(block)
        previous_hash = str(block["block_hash"])
    return blocks


def build_block_event_index(blocks: List[Dict[str, object]], signed_rows: List[Dict[str, str]]) -> List[Dict[str, object]]:
    rows_by_sequence = {int(row["event_sequence"]): row for row in signed_rows}
    index_rows: List[Dict[str, object]] = []
    for block in blocks:
        first_sequence = int(block["first_event_sequence"])
        for offset, event_hash in enumerate(block["event_commitment_hashes"]):
            sequence = first_sequence + offset
            source_row = rows_by_sequence[sequence]
            index_rows.append(
                {
                    "block_number": block["block_number"],
                    "event_sequence": sequence,
                    "event_id": source_row["event_id"],
                    "request_id": source_row["request_id"],
                    "event_commitment_hash": event_hash,
                    "block_hash": block["block_hash"],
                    "merkle_root": block["merkle_root"],
                    "validator_id": block["validator_id"],
                }
            )
    return index_rows


def validator_ids() -> set[str]:
    return {validator["validator_id"] for validator in VALIDATORS}


def verify_chain(blocks: List[Dict[str, object]]) -> Dict[str, object]:
    errors: List[str] = []
    previous_hash = GENESIS_BLOCK_HASH
    allowed_validators = validator_ids()

    for expected_number, block in enumerate(blocks, start=1):
        prefix = f"block {expected_number}"
        required_fields = [
            "block_number",
            "timestamp_utc",
            "chain_version",
            "consensus_model",
            "validator_id",
            "validator_agency_type",
            "previous_block_hash",
            "event_count",
            "first_event_sequence",
            "last_event_sequence",
            "event_commitment_hashes",
            "merkle_root",
            "block_payload_hash",
            "validator_signature",
            "quorum_threshold",
            "quorum_endorsements",
            "quorum_signature_hash",
            "block_hash",
        ]
        missing = [field for field in required_fields if field not in block]
        if missing:
            errors.append(f"{prefix}: missing fields {missing}")
            continue

        if int(block["block_number"]) != expected_number:
            errors.append(f"{prefix}: expected block_number {expected_number}, found {block['block_number']}")

        if block["validator_id"] not in allowed_validators:
            errors.append(f"{prefix}: unknown validator_id {block['validator_id']}")

        if block["previous_block_hash"] != previous_hash:
            errors.append(f"{prefix}: previous_block_hash mismatch")

        commitment_hashes = [str(value) for value in block["event_commitment_hashes"]]
        if int(block["event_count"]) != len(commitment_hashes):
            errors.append(f"{prefix}: event_count mismatch")

        if int(block["last_event_sequence"]) - int(block["first_event_sequence"]) + 1 != int(block["event_count"]):
            errors.append(f"{prefix}: event sequence range does not match event_count")

        expected_merkle_root = merkle_root(commitment_hashes)
        if block["merkle_root"] != expected_merkle_root:
            errors.append(f"{prefix}: merkle_root mismatch")

        expected_payload_hash = stable_hash(block_payload(block))
        if block["block_payload_hash"] != expected_payload_hash:
            errors.append(f"{prefix}: block_payload_hash mismatch")

        expected_validator_signature = sign_with_validator(str(block["validator_id"]), str(block["block_payload_hash"]))
        if block["validator_signature"] != expected_validator_signature:
            errors.append(f"{prefix}: validator_signature mismatch")

        endorsements = block["quorum_endorsements"]
        if not isinstance(endorsements, list):
            errors.append(f"{prefix}: quorum_endorsements is not a list")
            endorsements = []
        endorsement_validators = [str(item.get("validator_id", "")) for item in endorsements if isinstance(item, dict)]
        if len(set(endorsement_validators)) < int(block["quorum_threshold"]):
            errors.append(f"{prefix}: quorum threshold not met")
        for endorsement in endorsements:
            if not isinstance(endorsement, dict):
                errors.append(f"{prefix}: malformed endorsement")
                continue
            validator_id = str(endorsement.get("validator_id", ""))
            if validator_id not in allowed_validators:
                errors.append(f"{prefix}: unknown endorsement validator {validator_id}")
                continue
            expected_signature = sign_with_validator(validator_id, str(block["block_payload_hash"]))
            if endorsement.get("signature") != expected_signature:
                errors.append(f"{prefix}: endorsement signature mismatch for {validator_id}")

        expected_quorum_hash = stable_hash(endorsements)
        if block["quorum_signature_hash"] != expected_quorum_hash:
            errors.append(f"{prefix}: quorum_signature_hash mismatch")

        expected_block_hash = compute_block_hash(
            str(block["block_payload_hash"]),
            str(block["validator_signature"]),
            str(block["quorum_signature_hash"]),
        )
        if block["block_hash"] != expected_block_hash:
            errors.append(f"{prefix}: block_hash mismatch")

        previous_hash = str(block["block_hash"])

    return {
        "valid": not errors,
        "error_count": len(errors),
        "first_error": errors[0] if errors else "",
        "note": "Permissioned blockchain-style verification checks block links, Merkle roots, validator signatures, and quorum endorsements.",
    }


def tamper_chain(blocks: List[Dict[str, object]], tamper_case: str) -> List[Dict[str, object]]:
    tampered = deepcopy(blocks)
    if not tampered:
        return tampered

    if tamper_case == "changed_event_commitment":
        target = min(2, len(tampered) - 1)
        hashes = list(tampered[target]["event_commitment_hashes"])
        hashes[0] = "tampered_" + str(hashes[0])[:55]
        tampered[target]["event_commitment_hashes"] = hashes
        return tampered

    if tamper_case == "deleted_event_commitment":
        target = min(3, len(tampered) - 1)
        hashes = list(tampered[target]["event_commitment_hashes"])
        if hashes:
            del hashes[0]
        tampered[target]["event_commitment_hashes"] = hashes
        return tampered

    if tamper_case == "changed_merkle_root":
        target = min(4, len(tampered) - 1)
        tampered[target]["merkle_root"] = "tampered_" + str(tampered[target]["merkle_root"])[:55]
        return tampered

    if tamper_case == "changed_validator_signature":
        target = min(5, len(tampered) - 1)
        tampered[target]["validator_signature"] = "tampered_" + str(tampered[target]["validator_signature"])[:55]
        return tampered

    if tamper_case == "reordered_blocks":
        if len(tampered) > 7:
            tampered[6], tampered[7] = tampered[7], tampered[6]
        return tampered

    raise ValueError(f"unknown tamper case: {tamper_case}")


def write_tampered_chains(artifacts_dir: Path, blocks: List[Dict[str, object]]) -> Dict[str, Path]:
    tamper_dir = artifacts_dir / "tampered_chains"
    paths: Dict[str, Path] = {}
    for case in TAMPER_CASES:
        tampered = tamper_chain(blocks, case)
        path = tamper_dir / f"{case}.jsonl"
        write_jsonl(path, tampered)
        paths[case] = path
    return paths


def build_tamper_results(original_chain_path: Path, tampered_paths: Dict[str, Path]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    original = read_jsonl(original_chain_path)
    original_verification = verify_chain(original)
    original_hash = file_sha256(original_chain_path)
    rows.append(
        {
            "chain_type": "permissioned_blockchain_style",
            "tamper_case": "original",
            "file": str(original_chain_path),
            "expected_tampered": "false",
            "verification_valid": str(original_verification["valid"]).lower(),
            "verification_detected": "false",
            "reference_hash_changed": "false",
            "first_error": original_verification["first_error"],
            "error_count": original_verification["error_count"],
            "note": original_verification["note"],
        }
    )

    for case, path in tampered_paths.items():
        verification = verify_chain(read_jsonl(path))
        rows.append(
            {
                "chain_type": "permissioned_blockchain_style",
                "tamper_case": case,
                "file": str(path),
                "expected_tampered": "true",
                "verification_valid": str(verification["valid"]).lower(),
                "verification_detected": str((not verification["valid"])).lower(),
                "reference_hash_changed": str(file_sha256(path) != original_hash).lower(),
                "first_error": verification["first_error"],
                "error_count": verification["error_count"],
                "note": verification["note"],
            }
        )
    return rows


def build_summary_rows(tamper_results: List[Dict[str, object]]) -> List[Dict[str, object]]:
    tampered = [row for row in tamper_results if row["expected_tampered"] == "true"]
    detected = sum(1 for row in tampered if row["verification_detected"] == "true")
    return [
        {
            "chain_type": "permissioned_blockchain_style",
            "tamper_cases": len(tampered),
            "detected": detected,
            "not_detected": len(tampered) - detected,
            "detection_rate": f"{detected / len(tampered):.4f}" if tampered else "0.0000",
        }
    ]


def build_comparison_rows(step3_summary_file: Path, step4_summary_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    comparison: List[Dict[str, object]] = []
    if step3_summary_file.exists():
        for row in read_csv(step3_summary_file):
            comparison.append(
                {
                    "method": row["log_type"],
                    "tamper_cases": row["tamper_cases"],
                    "detected": row["self_detected"],
                    "not_detected": row["self_not_detected"],
                    "detection_rate": row["self_detection_rate"],
                    "scope": "step3 local log baseline",
                }
            )
    for row in step4_summary_rows:
        comparison.append(
            {
                "method": row["chain_type"],
                "tamper_cases": row["tamper_cases"],
                "detected": row["detected"],
                "not_detected": row["not_detected"],
                "detection_rate": row["detection_rate"],
                "scope": "step4 permissioned blockchain-style simulation",
            }
        )
    return comparison


def build_metrics(blocks: List[Dict[str, object]], event_count: int, tamper_results: List[Dict[str, object]], input_file: Path) -> Dict[str, object]:
    tampered = [row for row in tamper_results if row["expected_tampered"] == "true"]
    detected = sum(1 for row in tampered if row["verification_detected"] == "true")
    return {
        "artifact_type": "permissioned_blockchain_style_audit_simulation",
        "result_claim": "tamper-detection result for deterministic simulated permissioned audit chain only",
        "input_file": str(input_file),
        "chain_version": CHAIN_VERSION,
        "consensus_model": "permissioned_poa_quorum_simulation",
        "blockchain_type": "permissioned; PoA/PBFT-style validator simulation; not PoW or PoS",
        "validator_count": len(VALIDATORS),
        "quorum_threshold": QUORUM_THRESHOLD,
        "event_count": event_count,
        "block_count": len(blocks),
        "tamper_cases": TAMPER_CASES,
        "tamper_detection": {
            "tamper_cases": len(tampered),
            "detected": detected,
            "not_detected": len(tampered) - detected,
            "detection_rate": detected / len(tampered) if tampered else 0.0,
        },
        "important_interpretation": [
            "This step demonstrates a blockchain-style audit abstraction over existing signed audit-event commitments.",
            "The chain stores hashes and audit metadata, not raw police records or raw explanation text.",
            "This is not Hyperledger Fabric and does not prove deployment-grade blockchain security.",
        ],
        "limitations": [
            "Validator signatures use deterministic demo HMAC keys for reproducible local testing.",
            "No network, consensus latency, Byzantine node behavior, chaincode, channel privacy, or Fabric MSP is implemented.",
            "Tamper cases are controlled synthetic manipulations.",
            "A compromised quorum signing key scenario is not tested in this step.",
        ],
    }


def validator_set() -> Dict[str, object]:
    return {
        "chain_version": CHAIN_VERSION,
        "consensus_model": "permissioned_poa_quorum_simulation",
        "quorum_threshold": QUORUM_THRESHOLD,
        "validators": VALIDATORS,
        "important_boundary": "Demo validators and keys are for deterministic local prototype testing only.",
    }


def data_dictionary_text() -> str:
    return """# Permissioned Blockchain-Style Audit Output Data Dictionary

This file describes Step 4 outputs.

## Important Boundary

This step is a local permissioned blockchain-style simulation. It is not Hyperledger Fabric, not a deployed blockchain, not PoW, and not PoS.

## Core Files

- `permissioned_audit_blocks.jsonl`: simulated permissioned audit-chain blocks.
- `block_event_index.csv`: maps audit events to block numbers and commitment hashes.
- `validator_set.json`: synthetic validator set and quorum rule.
- `tampered_chains/`: controlled tampered chain files.
- `blockchain_tamper_test_results.csv`: verification result for original and tampered chains.
- `blockchain_detection_summary.csv`: compact chain-detection summary.
- `comparison_with_step3_signed_log.csv`: comparison with Step 3 mutable and signed-log baselines.

## Key Block Fields

| Field | Meaning |
|---|---|
| `block_number` | Sequential block number. |
| `previous_block_hash` | Hash link to previous block. |
| `event_commitment_hashes` | Hash commitments to signed audit events. |
| `merkle_root` | Merkle root over event commitments. |
| `validator_id` | Permissioned validator that proposes/signs the block. |
| `block_payload_hash` | Hash of block content before signatures. |
| `validator_signature` | Demo validator HMAC signature over block payload hash. |
| `quorum_endorsements` | Demo quorum signatures from known validators. |
| `block_hash` | Final block hash binding payload and signatures. |

## Correct Interpretation

This layer gives a blockchain-style audit structure for the prototype. It stores audit commitments only. Raw police records and raw explanation text stay off-chain.
"""


def run_readme_text(run_id: str, input_run_id: str, block_count: int, event_count: int) -> str:
    return f"""# Run {run_id}

Purpose: Step 4 permissioned blockchain-style audit simulation.

Input run: `{input_run_id}`

Audit events committed: `{event_count}`

Blocks created: `{block_count}`

## What This Run Contains

- permissioned audit blocks;
- event-to-block index;
- synthetic validator set;
- controlled tampered chain files;
- chain verification results;
- comparison with Step 3 log baselines.

## What This Run Does Not Contain

- No real police/CCTNS/ICJS/FIR data.
- No raw record content on-chain.
- No raw XAI explanation text on-chain.
- No Hyperledger Fabric deployment.
- No real network consensus.
- No PoW or PoS.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/blockchain_audit.py \\
  --input-run-id {input_run_id} \\
  --run-id {run_id}
```
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a permissioned blockchain-style audit simulation.")
    parser.add_argument("--input-run-id", default=DEFAULT_INPUT_RUN_ID)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--input-file", default="")
    parser.add_argument("--block-size", type=int, default=DEFAULT_BLOCK_SIZE)
    parser.add_argument(
        "--step3-summary-file",
        default=str(ROOT / "prototype" / "results" / "tables" / "audit_baseline_step3_summary.csv"),
    )
    parser.add_argument(
        "--results-summary-table",
        default=str(ROOT / "prototype" / "results" / "tables" / "blockchain_audit_step4_summary.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_file = Path(args.input_file) if args.input_file else (
        ROOT / "prototype" / "runs" / args.input_run_id / "artifacts" / "signed_hash_chain_log.csv"
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
        "chain_version": CHAIN_VERSION,
        "block_size": args.block_size,
        "consensus_model": "permissioned_poa_quorum_simulation",
        "step": "step_4_permissioned_blockchain_style_audit",
        "synthetic_only": True,
        "raw_record_included": False,
        "raw_explanation_included": False,
        "hyperledger_fabric_implemented": False,
    }
    write_yaml(run_dir / "config.yaml", config)

    signed_rows = read_csv(input_file)
    blocks = build_chain(signed_rows, args.block_size)
    event_index_rows = build_block_event_index(blocks, signed_rows)
    chain_path = artifacts_dir / "permissioned_audit_blocks.jsonl"
    event_index_path = artifacts_dir / "block_event_index.csv"
    validator_set_path = artifacts_dir / "validator_set.json"

    write_jsonl(chain_path, blocks)
    write_csv(event_index_path, event_index_rows, BLOCK_INDEX_FIELDS)
    write_json(validator_set_path, validator_set())

    tampered_paths = write_tampered_chains(artifacts_dir, blocks)
    tamper_results = build_tamper_results(chain_path, tampered_paths)
    summary = build_summary_rows(tamper_results)
    comparison = build_comparison_rows(Path(args.step3_summary_file), summary)

    tamper_results_path = artifacts_dir / "blockchain_tamper_test_results.csv"
    detection_summary_path = artifacts_dir / "blockchain_detection_summary.csv"
    comparison_path = artifacts_dir / "comparison_with_step3_signed_log.csv"
    write_csv(
        tamper_results_path,
        tamper_results,
        [
            "chain_type",
            "tamper_case",
            "file",
            "expected_tampered",
            "verification_valid",
            "verification_detected",
            "reference_hash_changed",
            "first_error",
            "error_count",
            "note",
        ],
    )
    write_csv(
        detection_summary_path,
        summary,
        ["chain_type", "tamper_cases", "detected", "not_detected", "detection_rate"],
    )
    write_csv(
        Path(args.results_summary_table),
        summary,
        ["chain_type", "tamper_cases", "detected", "not_detected", "detection_rate"],
    )
    write_csv(
        comparison_path,
        comparison,
        ["method", "tamper_cases", "detected", "not_detected", "detection_rate", "scope"],
    )

    metrics = build_metrics(blocks, len(signed_rows), tamper_results, input_file)
    write_json(run_dir / "metrics.json", metrics)

    artifact_files = [
        "permissioned_audit_blocks.jsonl",
        "block_event_index.csv",
        "validator_set.json",
        "blockchain_tamper_test_results.csv",
        "blockchain_detection_summary.csv",
        "comparison_with_step3_signed_log.csv",
    ]
    manifest = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "input_file": str(input_file),
        "input_file_sha256": file_sha256(input_file),
        "chain_version": CHAIN_VERSION,
        "block_size": args.block_size,
        "synthetic_only": True,
        "raw_record_included": False,
        "raw_explanation_included": False,
        "hyperledger_fabric_implemented": False,
        "artifact_hashes": {
            filename: file_sha256(artifacts_dir / filename)
            for filename in artifact_files
        },
        "tampered_artifact_hashes": {
            case: file_sha256(path)
            for case, path in tampered_paths.items()
        },
        "notes": [
            "This is a local permissioned blockchain-style simulation, not a deployed blockchain.",
            "The chain stores audit commitments only, not raw sensitive records.",
            "Validator signatures use deterministic demo HMAC keys.",
        ],
    }
    write_json(artifacts_dir / "dataset_manifest.json", manifest)
    (artifacts_dir / "README.md").write_text(run_readme_text(args.run_id, args.input_run_id, len(blocks), len(signed_rows)), encoding="utf-8")
    (artifacts_dir / "data_dictionary.md").write_text(data_dictionary_text(), encoding="utf-8")

    original_verification = verify_chain(read_jsonl(chain_path))
    log_lines = [
        f"created_at_utc={created_at}",
        f"run_id={args.run_id}",
        f"input_file={input_file}",
        f"events_committed={len(signed_rows)}",
        f"blocks_created={len(blocks)}",
        f"block_size={args.block_size}",
        f"original_chain_valid={original_verification['valid']}",
        f"detection_summary={summary}",
        "status=success",
        "claim=permissioned_blockchain_style_simulation_not_deployed_blockchain",
    ]
    (logs_dir / "blockchain_audit.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Wrote permissioned blockchain-style audit run: {run_dir}")
    print(f"Events committed: {len(signed_rows)}")
    print(f"Blocks created: {len(blocks)}")
    print(f"Original chain valid: {original_verification['valid']}")
    print(f"Detection summary: {summary}")
    print(f"Summary table: {args.results_summary_table}")


if __name__ == "__main__":
    main()
