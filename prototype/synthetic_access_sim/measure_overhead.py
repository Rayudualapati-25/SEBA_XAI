#!/usr/bin/env python3
"""Measure local latency and storage overhead for the SEBA-XAI prototype.

This is Step 5 of the prototype. It measures local execution overhead for:

- policy-oracle + rule-trace XAI decision generation;
- mutable log creation/write and schema verification;
- signed hash-chain creation/write and verification;
- permissioned blockchain-style block creation/write and verification;
- storage size of the generated artifacts.

These are local prototype measurements. They are not deployment-performance,
network-consensus, or Hyperledger Fabric benchmark claims.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

import audit_baseline
import blockchain_audit
import policy_oracle


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN_ID = "20260527_step5_latency_storage_overhead"
DEFAULT_STEP1_RUN_ID = "20260527_step1_synthetic_requests_seed42"
DEFAULT_STEP2_RUN_ID = "20260527_step2_policy_oracle_seed42"
DEFAULT_STEP3_RUN_ID = "20260527_step3_audit_baselines_seed42"
DEFAULT_STEP4_RUN_ID = "20260527_step4_permissioned_blockchain_audit_seed42"


LATENCY_SUMMARY_FIELDS = [
    "component",
    "operation",
    "unit",
    "count",
    "repeats",
    "total_ms_p50",
    "total_ms_p95",
    "total_ms_p99",
    "ms_per_unit_p50",
    "throughput_units_per_sec_p50",
    "note",
]

STORAGE_FIELDS = [
    "component",
    "artifact",
    "file_count",
    "bytes",
    "kilobytes",
    "events_or_requests",
    "bytes_per_event_or_request",
    "note",
]

COMPARISON_FIELDS = [
    "method",
    "events_or_requests",
    "build_or_decision_total_ms_p50",
    "verify_total_ms_p50",
    "storage_bytes",
    "storage_bytes_per_event_or_request",
    "tamper_detection_rate",
    "scope_note",
]

LATENCY_SAMPLE_FIELDS = [
    "component",
    "operation",
    "sample_id",
    "latency_ms",
    "unit",
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


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


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


def file_sha256(path: Path) -> str:
    return policy_oracle.file_sha256(path)


def percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * pct
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = index - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction


def timed_call(fn: Callable[[], object]) -> Tuple[object, float]:
    start = time.perf_counter_ns()
    result = fn()
    end = time.perf_counter_ns()
    return result, (end - start) / 1_000_000


def summarize_samples(
    *,
    component: str,
    operation: str,
    unit: str,
    count: int,
    samples_ms: List[float],
    note: str,
) -> Dict[str, object]:
    p50 = percentile(samples_ms, 0.50)
    p95 = percentile(samples_ms, 0.95)
    p99 = percentile(samples_ms, 0.99)
    throughput = 1000.0 / p50 if p50 > 0 and count else 0.0
    return {
        "component": component,
        "operation": operation,
        "unit": unit,
        "count": count,
        "repeats": len(samples_ms),
        "total_ms_p50": f"{p50:.6f}",
        "total_ms_p95": f"{p95:.6f}",
        "total_ms_p99": f"{p99:.6f}",
        "ms_per_unit_p50": f"{p50:.6f}",
        "throughput_units_per_sec_p50": f"{throughput:.2f}",
        "note": note,
    }


def summarize_aggregate(
    *,
    component: str,
    operation: str,
    unit: str,
    count: int,
    total_samples_ms: List[float],
    note: str,
) -> Dict[str, object]:
    p50 = percentile(total_samples_ms, 0.50)
    p95 = percentile(total_samples_ms, 0.95)
    p99 = percentile(total_samples_ms, 0.99)
    avg_per_unit = p50 / count if count else 0.0
    throughput = (count / (p50 / 1000.0)) if p50 > 0 else 0.0
    return {
        "component": component,
        "operation": operation,
        "unit": unit,
        "count": count,
        "repeats": len(total_samples_ms),
        "total_ms_p50": f"{p50:.6f}",
        "total_ms_p95": f"{p95:.6f}",
        "total_ms_p99": f"{p99:.6f}",
        "ms_per_unit_p50": f"{avg_per_unit:.6f}",
        "throughput_units_per_sec_p50": f"{throughput:.2f}",
        "note": note,
    }


def measured_signed_hash_chain_rows(mutable_rows: List[Dict[str, object]]) -> Tuple[List[Dict[str, object]], List[float]]:
    signed_rows: List[Dict[str, object]] = []
    event_latencies_ms: List[float] = []
    previous_hash = audit_baseline.GENESIS_HASH
    for row in mutable_rows:
        start = time.perf_counter_ns()
        payload = {field: str(row[field]) for field in audit_baseline.MUTABLE_LOG_FIELDS}
        payload_hash = audit_baseline.stable_hash(payload)
        event_hash = audit_baseline.stable_hash(
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
                "log_signature": audit_baseline.sign_event(event_hash),
                "signature_algorithm": "HMAC-SHA256-DEMO",
                "audit_log_version": audit_baseline.AUDIT_LOG_VERSION,
            }
        )
        signed_rows.append(signed_row)
        previous_hash = event_hash
        end = time.perf_counter_ns()
        event_latencies_ms.append((end - start) / 1_000_000)
    return signed_rows, event_latencies_ms


def measured_blockchain_blocks(
    signed_rows: List[Dict[str, str]],
    block_size: int,
) -> Tuple[List[Dict[str, object]], List[float]]:
    blocks: List[Dict[str, object]] = []
    block_latencies_ms: List[float] = []
    previous_hash = blockchain_audit.GENESIS_BLOCK_HASH
    for block_number, events in enumerate(blockchain_audit.chunked(signed_rows, block_size), start=1):
        start = time.perf_counter_ns()
        block = blockchain_audit.build_block(block_number, events, previous_hash)
        end = time.perf_counter_ns()
        blocks.append(block)
        block_latencies_ms.append((end - start) / 1_000_000)
        previous_hash = str(block["block_hash"])
    return blocks, block_latencies_ms


def storage_row(
    *,
    component: str,
    artifact: str,
    paths: List[Path],
    count: int,
    note: str,
) -> Dict[str, object]:
    total_bytes = sum(path.stat().st_size for path in paths if path.exists())
    return {
        "component": component,
        "artifact": artifact,
        "file_count": len(paths),
        "bytes": total_bytes,
        "kilobytes": f"{total_bytes / 1024:.3f}",
        "events_or_requests": count,
        "bytes_per_event_or_request": f"{total_bytes / count:.3f}" if count else "0.000",
        "note": note,
    }


def path_size(paths: List[Path]) -> int:
    return sum(path.stat().st_size for path in paths if path.exists())


def load_tamper_detection_rates(
    step3_artifacts: Path,
    step4_artifacts: Path,
) -> Dict[str, str]:
    rates = {
        "mutable_log": "",
        "signed_hash_chain": "",
        "permissioned_blockchain_style": "",
    }
    step3_summary = step3_artifacts / "audit_detection_summary.csv"
    if step3_summary.exists():
        for row in read_csv(step3_summary):
            if row.get("log_type") == "mutable":
                rates["mutable_log"] = row.get("self_detection_rate", "")
            elif row.get("log_type") == "signed_hash_chain":
                rates["signed_hash_chain"] = row.get("self_detection_rate", "")

    step4_summary = step4_artifacts / "blockchain_detection_summary.csv"
    if step4_summary.exists():
        for row in read_csv(step4_summary):
            if row.get("chain_type") == "permissioned_blockchain_style":
                rates["permissioned_blockchain_style"] = row.get("detection_rate", "")
    return rates


def build_readme(run_id: str, request_count: int, event_count: int, block_count: int) -> str:
    return f"""# Run {run_id}

Purpose: Step 5 local latency and storage-overhead measurement.

Requests measured: `{request_count}`

Audit events measured: `{event_count}`

Blocks measured: `{block_count}`

## What This Run Contains

- latency summary table;
- per-request decision latency samples;
- signed-event latency samples;
- block-creation latency samples;
- storage overhead table;
- comparison table across policy/XAI, mutable log, signed hash-chain, and blockchain-style audit.

## What This Run Does Not Claim

- No deployment performance claim.
- No network consensus benchmark.
- No Hyperledger Fabric benchmark.
- No real police/CCTNS/ICJS/FIR data.

## Reproduce

```bash
python3 prototype/synthetic_access_sim/measure_overhead.py \\
  --run-id {run_id}
```
"""


def data_dictionary_text() -> str:
    return """# Latency And Storage Overhead Data Dictionary

This file describes Step 5 outputs.

## Important Boundary

These measurements are local prototype measurements on the current machine. They are useful for comparing prototype components, but they are not deployment or Hyperledger Fabric benchmarks.

## Core Files

- `latency_summary.csv`: p50/p95/p99 timing summary for each component.
- `latency_samples.csv`: per-request/per-event/per-block sample timings.
- `storage_overhead.csv`: file-size overhead of generated artifacts.
- `overhead_comparison.csv`: compact comparison table for paper notes.

## Important Metrics

| Field | Meaning |
|---|---|
| `total_ms_p50` | Median total time across repeated aggregate runs, or median sample latency for per-unit operations. |
| `ms_per_unit_p50` | Median total divided by count for aggregate operations, or median sample latency for per-unit operations. |
| `throughput_units_per_sec_p50` | Approximate local throughput from median timing. |
| `bytes_per_event_or_request` | Storage size divided by request/event count. |

## Correct Interpretation

Use these numbers as local overhead evidence only. Do not describe them as real police-system performance or blockchain-network performance.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure local SEBA-XAI prototype latency and storage overhead.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--step1-run-id", default=DEFAULT_STEP1_RUN_ID)
    parser.add_argument("--step2-run-id", default=DEFAULT_STEP2_RUN_ID)
    parser.add_argument("--step3-run-id", default=DEFAULT_STEP3_RUN_ID)
    parser.add_argument("--step4-run-id", default=DEFAULT_STEP4_RUN_ID)
    parser.add_argument("--block-size", type=int, default=blockchain_audit.DEFAULT_BLOCK_SIZE)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument(
        "--results-summary-table",
        default=str(ROOT / "prototype" / "results" / "tables" / "latency_storage_step5_summary.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = ROOT / "prototype" / "runs" / args.run_id
    artifacts_dir = run_dir / "artifacts"
    logs_dir = run_dir / "logs"
    measured_dir = artifacts_dir / "measured_outputs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    measured_dir.mkdir(parents=True, exist_ok=True)

    step1_request_file = ROOT / "prototype" / "runs" / args.step1_run_id / "artifacts" / "access_requests.csv"
    step2_labeled_file = ROOT / "prototype" / "runs" / args.step2_run_id / "artifacts" / "labeled_access_requests.csv"
    step3_artifacts = ROOT / "prototype" / "runs" / args.step3_run_id / "artifacts"
    step4_artifacts = ROOT / "prototype" / "runs" / args.step4_run_id / "artifacts"
    step3_signed_file = step3_artifacts / "signed_hash_chain_log.csv"
    step4_chain_file = step4_artifacts / "permissioned_audit_blocks.jsonl"

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    config = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "step1_run_id": args.step1_run_id,
        "step2_run_id": args.step2_run_id,
        "step3_run_id": args.step3_run_id,
        "step4_run_id": args.step4_run_id,
        "block_size": args.block_size,
        "repeats": args.repeats,
        "step": "step_5_latency_storage_overhead",
        "synthetic_only": True,
        "local_measurement_only": True,
    }
    write_yaml(run_dir / "config.yaml", config)

    request_rows = policy_oracle.read_csv(step1_request_file)
    labeled_rows = policy_oracle.read_csv(step2_labeled_file)
    signed_rows_existing = audit_baseline.read_csv(step3_signed_file)
    blocks_existing = blockchain_audit.read_jsonl(step4_chain_file)

    latency_summary: List[Dict[str, object]] = []
    latency_samples: List[Dict[str, object]] = []

    decision_latencies_ms: List[float] = []
    for row in request_rows:
        _, elapsed_ms = timed_call(lambda current=row: policy_oracle.evaluate_policy(current))
        decision_latencies_ms.append(elapsed_ms)
        latency_samples.append(
            {
                "component": "policy_oracle_xai",
                "operation": "evaluate_one_request",
                "sample_id": row["request_id"],
                "latency_ms": f"{elapsed_ms:.6f}",
                "unit": "request",
            }
        )
    latency_summary.append(
        summarize_samples(
            component="policy_oracle_xai",
            operation="evaluate_one_request",
            unit="request",
            count=len(request_rows),
            samples_ms=decision_latencies_ms,
            note="Includes deterministic policy decision, rule-trace explanation, and decision/explanation/audit hashes.",
        )
    )
    policy_oracle_total_ms: List[float] = []
    for _ in range(args.repeats):
        _, elapsed_ms = timed_call(
            lambda rows=request_rows: [
                policy_oracle.evaluate_policy(row)
                for row in rows
            ]
        )
        policy_oracle_total_ms.append(elapsed_ms)
    latency_summary.append(
        summarize_aggregate(
            component="policy_oracle_xai",
            operation="evaluate_all_requests",
            unit="request",
            count=len(request_rows),
            total_samples_ms=policy_oracle_total_ms,
            note="Repeated aggregate timing for deterministic policy decision, rule-trace explanation, and hash generation.",
        )
    )

    mutable_create_write_totals: List[float] = []
    mutable_verify_totals: List[float] = []
    signed_create_write_totals: List[float] = []
    signed_verify_totals: List[float] = []
    signed_event_latencies_ms: List[float] = []

    last_mutable_rows: List[Dict[str, object]] = []
    last_signed_rows: List[Dict[str, object]] = []
    for repeat in range(1, args.repeats + 1):
        repeat_dir = measured_dir / f"repeat_{repeat:02d}"
        repeat_dir.mkdir(parents=True, exist_ok=True)

        def build_write_mutable() -> List[Dict[str, object]]:
            rows = audit_baseline.build_mutable_log_rows(labeled_rows)
            audit_baseline.write_csv(repeat_dir / "mutable_access_log.csv", rows, audit_baseline.MUTABLE_LOG_FIELDS)
            return rows

        mutable_rows, elapsed_ms = timed_call(build_write_mutable)
        last_mutable_rows = mutable_rows
        mutable_create_write_totals.append(elapsed_ms)

        _, elapsed_ms = timed_call(lambda rows=mutable_rows: audit_baseline.verify_mutable_log([{k: str(v) for k, v in row.items()} for row in rows]))
        mutable_verify_totals.append(elapsed_ms)

        def build_write_signed() -> Tuple[List[Dict[str, object]], List[float]]:
            rows, event_latencies = measured_signed_hash_chain_rows(mutable_rows)
            audit_baseline.write_csv(repeat_dir / "signed_hash_chain_log.csv", rows, audit_baseline.SIGNED_LOG_FIELDS)
            return rows, event_latencies

        (signed_rows, event_latencies), elapsed_ms = timed_call(build_write_signed)
        last_signed_rows = signed_rows
        signed_create_write_totals.append(elapsed_ms)
        if repeat == 1:
            signed_event_latencies_ms = event_latencies
            for index, sample_ms in enumerate(event_latencies, start=1):
                latency_samples.append(
                    {
                        "component": "signed_hash_chain",
                        "operation": "create_one_signed_event",
                        "sample_id": str(index),
                        "latency_ms": f"{sample_ms:.6f}",
                        "unit": "event",
                    }
                )

        signed_rows_as_str = [{key: str(value) for key, value in row.items()} for row in signed_rows]
        _, elapsed_ms = timed_call(lambda rows=signed_rows_as_str: audit_baseline.verify_signed_hash_chain(rows))
        signed_verify_totals.append(elapsed_ms)

    latency_summary.append(
        summarize_aggregate(
            component="mutable_log",
            operation="build_and_write",
            unit="event",
            count=len(labeled_rows),
            total_samples_ms=mutable_create_write_totals,
            note="Creates centralized mutable CSV log from labeled requests and writes it to disk.",
        )
    )
    latency_summary.append(
        summarize_aggregate(
            component="mutable_log",
            operation="schema_verify",
            unit="event",
            count=len(labeled_rows),
            total_samples_ms=mutable_verify_totals,
            note="Schema-only verification; does not provide internal tamper evidence.",
        )
    )
    latency_summary.append(
        summarize_aggregate(
            component="signed_hash_chain",
            operation="build_and_write",
            unit="event",
            count=len(labeled_rows),
            total_samples_ms=signed_create_write_totals,
            note="Creates event payload hashes, previous links, event hashes, demo signatures, and writes CSV.",
        )
    )
    latency_summary.append(
        summarize_samples(
            component="signed_hash_chain",
            operation="create_one_signed_event",
            unit="event",
            count=len(signed_event_latencies_ms),
            samples_ms=signed_event_latencies_ms,
            note="Per-event hashing/signing sample from first repeat.",
        )
    )
    latency_summary.append(
        summarize_aggregate(
            component="signed_hash_chain",
            operation="verify_chain",
            unit="event",
            count=len(labeled_rows),
            total_samples_ms=signed_verify_totals,
            note="Recomputes payload hashes, previous links, event hashes, and demo signatures.",
        )
    )

    blockchain_build_write_totals: List[float] = []
    blockchain_verify_totals: List[float] = []
    block_latencies_ms: List[float] = []
    last_blocks: List[Dict[str, object]] = []

    signed_rows_for_blocks = [{key: str(value) for key, value in row.items()} for row in last_signed_rows]
    if not signed_rows_for_blocks:
        signed_rows_for_blocks = signed_rows_existing

    for repeat in range(1, args.repeats + 1):
        repeat_dir = measured_dir / f"repeat_{repeat:02d}"

        def build_write_chain() -> Tuple[List[Dict[str, object]], List[float]]:
            blocks, per_block_latencies = measured_blockchain_blocks(signed_rows_for_blocks, args.block_size)
            write_jsonl(repeat_dir / "permissioned_audit_blocks.jsonl", blocks)
            index_rows = blockchain_audit.build_block_event_index(blocks, signed_rows_for_blocks)
            blockchain_audit.write_csv(repeat_dir / "block_event_index.csv", index_rows, blockchain_audit.BLOCK_INDEX_FIELDS)
            return blocks, per_block_latencies

        (blocks, per_block_latencies), elapsed_ms = timed_call(build_write_chain)
        last_blocks = blocks
        blockchain_build_write_totals.append(elapsed_ms)
        if repeat == 1:
            block_latencies_ms = per_block_latencies
            for index, sample_ms in enumerate(per_block_latencies, start=1):
                latency_samples.append(
                    {
                        "component": "permissioned_blockchain_style",
                        "operation": "create_one_block",
                        "sample_id": str(index),
                        "latency_ms": f"{sample_ms:.6f}",
                        "unit": "block",
                    }
                )

        _, elapsed_ms = timed_call(lambda blocks_to_verify=blocks: blockchain_audit.verify_chain(blocks_to_verify))
        blockchain_verify_totals.append(elapsed_ms)

    latency_summary.append(
        summarize_aggregate(
            component="permissioned_blockchain_style",
            operation="build_and_write",
            unit="event",
            count=len(signed_rows_for_blocks),
            total_samples_ms=blockchain_build_write_totals,
            note="Builds blocks, event commitments, Merkle roots, validator signatures, quorum endorsements, and writes chain/index files.",
        )
    )
    latency_summary.append(
        summarize_samples(
            component="permissioned_blockchain_style",
            operation="create_one_block",
            unit="block",
            count=len(block_latencies_ms),
            samples_ms=block_latencies_ms,
            note="Per-block creation sample from first repeat.",
        )
    )
    latency_summary.append(
        summarize_aggregate(
            component="permissioned_blockchain_style",
            operation="verify_chain",
            unit="block",
            count=len(last_blocks),
            total_samples_ms=blockchain_verify_totals,
            note="Verifies block links, Merkle roots, validator signatures, quorum endorsements, and block hashes.",
        )
    )

    storage_rows = [
        storage_row(
            component="policy_oracle_xai",
            artifact="labeled_access_requests.csv",
            paths=[step2_labeled_file],
            count=len(request_rows),
            note="Step 2 output with decisions, rule-trace explanations, and hashes.",
        ),
        storage_row(
            component="mutable_log",
            artifact="mutable_access_log.csv",
            paths=[step3_artifacts / "mutable_access_log.csv"],
            count=len(labeled_rows),
            note="Centralized audit metadata log.",
        ),
        storage_row(
            component="signed_hash_chain",
            artifact="signed_hash_chain_log.csv",
            paths=[step3_artifacts / "signed_hash_chain_log.csv"],
            count=len(labeled_rows),
            note="Audit log with previous-event hashes and demo signatures.",
        ),
        storage_row(
            component="permissioned_blockchain_style",
            artifact="permissioned_audit_blocks.jsonl",
            paths=[step4_artifacts / "permissioned_audit_blocks.jsonl"],
            count=len(signed_rows_existing),
            note="Block file only, containing event commitments, Merkle roots, block links, and signatures.",
        ),
        storage_row(
            component="permissioned_blockchain_style",
            artifact="blocks_plus_index_and_validator_set",
            paths=[
                step4_artifacts / "permissioned_audit_blocks.jsonl",
                step4_artifacts / "block_event_index.csv",
                step4_artifacts / "validator_set.json",
            ],
            count=len(signed_rows_existing),
            note="Full Step 4 audit artifact set needed to inspect event-to-block mapping.",
        ),
    ]

    latency_lookup = {
        (row["component"], row["operation"]): row
        for row in latency_summary
    }
    storage_lookup = {
        row["component"]: row
        for row in storage_rows
        if row["artifact"] in {
            "labeled_access_requests.csv",
            "mutable_access_log.csv",
            "signed_hash_chain_log.csv",
            "blocks_plus_index_and_validator_set",
        }
    }
    tamper_detection_rates = load_tamper_detection_rates(step3_artifacts, step4_artifacts)
    comparison_rows = [
        {
            "method": "policy_oracle_xai",
            "events_or_requests": len(request_rows),
            "build_or_decision_total_ms_p50": latency_lookup[("policy_oracle_xai", "evaluate_all_requests")]["total_ms_p50"],
            "verify_total_ms_p50": "",
            "storage_bytes": storage_lookup["policy_oracle_xai"]["bytes"],
            "storage_bytes_per_event_or_request": storage_lookup["policy_oracle_xai"]["bytes_per_event_or_request"],
            "tamper_detection_rate": "",
            "scope_note": "Decision and rule-trace XAI generation only.",
        },
        {
            "method": "mutable_log",
            "events_or_requests": len(labeled_rows),
            "build_or_decision_total_ms_p50": latency_lookup[("mutable_log", "build_and_write")]["total_ms_p50"],
            "verify_total_ms_p50": latency_lookup[("mutable_log", "schema_verify")]["total_ms_p50"],
            "storage_bytes": storage_lookup["mutable_log"]["bytes"],
            "storage_bytes_per_event_or_request": storage_lookup["mutable_log"]["bytes_per_event_or_request"],
            "tamper_detection_rate": tamper_detection_rates["mutable_log"],
            "scope_note": "Schema-valid mutable log; no internal tamper-evident chain.",
        },
        {
            "method": "signed_hash_chain",
            "events_or_requests": len(labeled_rows),
            "build_or_decision_total_ms_p50": latency_lookup[("signed_hash_chain", "build_and_write")]["total_ms_p50"],
            "verify_total_ms_p50": latency_lookup[("signed_hash_chain", "verify_chain")]["total_ms_p50"],
            "storage_bytes": storage_lookup["signed_hash_chain"]["bytes"],
            "storage_bytes_per_event_or_request": storage_lookup["signed_hash_chain"]["bytes_per_event_or_request"],
            "tamper_detection_rate": tamper_detection_rates["signed_hash_chain"],
            "scope_note": "Local signed append-only hash-chain baseline.",
        },
        {
            "method": "permissioned_blockchain_style",
            "events_or_requests": len(signed_rows_existing),
            "build_or_decision_total_ms_p50": latency_lookup[("permissioned_blockchain_style", "build_and_write")]["total_ms_p50"],
            "verify_total_ms_p50": latency_lookup[("permissioned_blockchain_style", "verify_chain")]["total_ms_p50"],
            "storage_bytes": storage_lookup["permissioned_blockchain_style"]["bytes"],
            "storage_bytes_per_event_or_request": storage_lookup["permissioned_blockchain_style"]["bytes_per_event_or_request"],
            "tamper_detection_rate": tamper_detection_rates["permissioned_blockchain_style"],
            "scope_note": "Local permissioned PoA/PBFT-style blockchain audit simulation, not deployed Fabric.",
        },
    ]

    latency_summary_path = artifacts_dir / "latency_summary.csv"
    latency_samples_path = artifacts_dir / "latency_samples.csv"
    storage_path = artifacts_dir / "storage_overhead.csv"
    comparison_path = artifacts_dir / "overhead_comparison.csv"
    write_csv(latency_summary_path, latency_summary, LATENCY_SUMMARY_FIELDS)
    write_csv(latency_samples_path, latency_samples, LATENCY_SAMPLE_FIELDS)
    write_csv(storage_path, storage_rows, STORAGE_FIELDS)
    write_csv(comparison_path, comparison_rows, COMPARISON_FIELDS)
    write_csv(Path(args.results_summary_table), comparison_rows, COMPARISON_FIELDS)

    metrics = {
        "artifact_type": "local_latency_storage_overhead",
        "result_claim": "local prototype overhead measurement only",
        "created_at_utc": created_at,
        "environment": {
            "python_version": sys.version.replace("\n", " "),
            "platform": platform.platform(),
            "processor": platform.processor(),
        },
        "inputs": {
            "step1_request_file": str(step1_request_file),
            "step2_labeled_file": str(step2_labeled_file),
            "step3_signed_file": str(step3_signed_file),
            "step4_chain_file": str(step4_chain_file),
        },
        "counts": {
            "requests": len(request_rows),
            "labeled_events": len(labeled_rows),
            "signed_events": len(signed_rows_existing),
            "blocks": len(blocks_existing),
            "repeats": args.repeats,
        },
        "summary_files": {
            "latency_summary": str(latency_summary_path),
            "latency_samples": str(latency_samples_path),
            "storage_overhead": str(storage_path),
            "overhead_comparison": str(comparison_path),
        },
        "tamper_detection_rate_sources": {
            "step3_summary": str(step3_artifacts / "audit_detection_summary.csv"),
            "step4_summary": str(step4_artifacts / "blockchain_detection_summary.csv"),
            "rates": tamper_detection_rates,
        },
        "limitations": [
            "Measurements are local to the current machine and workload.",
            "No network, database server, Hyperledger Fabric, ordering service, or real consensus latency is included.",
            "Repeated aggregate timings can vary with system load.",
            "The policy/XAI layer is deterministic rule-trace logic, not a trained model.",
        ],
    }
    write_json(run_dir / "metrics.json", metrics)

    manifest = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "synthetic_only": True,
        "local_measurement_only": True,
        "input_hashes": {
            "step1_request_file": file_sha256(step1_request_file),
            "step2_labeled_file": file_sha256(step2_labeled_file),
            "step3_signed_file": file_sha256(step3_signed_file),
            "step4_chain_file": file_sha256(step4_chain_file),
        },
        "artifact_hashes": {
            "latency_summary.csv": file_sha256(latency_summary_path),
            "latency_samples.csv": file_sha256(latency_samples_path),
            "storage_overhead.csv": file_sha256(storage_path),
            "overhead_comparison.csv": file_sha256(comparison_path),
        },
        "notes": [
            "This run measures local prototype overhead only.",
            "Do not cite these values as real police-system or deployed blockchain performance.",
        ],
    }
    write_json(artifacts_dir / "dataset_manifest.json", manifest)
    (artifacts_dir / "README.md").write_text(build_readme(args.run_id, len(request_rows), len(labeled_rows), len(blocks_existing)), encoding="utf-8")
    (artifacts_dir / "data_dictionary.md").write_text(data_dictionary_text(), encoding="utf-8")

    log_lines = [
        f"created_at_utc={created_at}",
        f"run_id={args.run_id}",
        f"requests={len(request_rows)}",
        f"events={len(labeled_rows)}",
        f"blocks={len(blocks_existing)}",
        f"repeats={args.repeats}",
        "status=success",
        "claim=local_overhead_measurement_only",
    ]
    (logs_dir / "measure_overhead.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Wrote overhead measurement run: {run_dir}")
    print(f"Requests measured: {len(request_rows)}")
    print(f"Events measured: {len(labeled_rows)}")
    print(f"Blocks measured: {len(blocks_existing)}")
    print(f"Summary table: {args.results_summary_table}")


if __name__ == "__main__":
    main()
