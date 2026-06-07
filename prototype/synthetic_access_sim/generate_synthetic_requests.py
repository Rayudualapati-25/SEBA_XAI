#!/usr/bin/env python3
"""Generate a deterministic synthetic access-request workload for SEBA-XAI.

This script implements Step 1 only: synthetic data generation.
It does not implement RBAC/ABAC/PBAC decisions, XAI, or blockchain audit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_VERSION = "P-2026-05-STEP1"
DEFAULT_RUN_ID = "20260527_step1_synthetic_requests_seed42"


ROLES = [
    {
        "role": "Constable",
        "rank_level": 1,
        "clearance_level": "LOW",
        "agency": "POLICE",
        "supervisor": False,
    },
    {
        "role": "Head Constable",
        "rank_level": 2,
        "clearance_level": "LOW",
        "agency": "POLICE",
        "supervisor": False,
    },
    {
        "role": "Sub-Inspector",
        "rank_level": 3,
        "clearance_level": "MEDIUM",
        "agency": "POLICE",
        "supervisor": False,
    },
    {
        "role": "Inspector",
        "rank_level": 4,
        "clearance_level": "MEDIUM",
        "agency": "POLICE",
        "supervisor": False,
    },
    {
        "role": "Station House Officer",
        "rank_level": 5,
        "clearance_level": "HIGH",
        "agency": "POLICE",
        "supervisor": True,
    },
    {
        "role": "Cybercrime Officer",
        "rank_level": 4,
        "clearance_level": "HIGH",
        "agency": "CYBERCRIME",
        "supervisor": False,
    },
    {
        "role": "Forensic Officer",
        "rank_level": 4,
        "clearance_level": "HIGH",
        "agency": "FORENSIC",
        "supervisor": False,
    },
    {
        "role": "Prosecutor Liaison",
        "rank_level": 4,
        "clearance_level": "MEDIUM",
        "agency": "PROSECUTION",
        "supervisor": False,
    },
    {
        "role": "Senior Superintendent",
        "rank_level": 6,
        "clearance_level": "CLASSIFIED",
        "agency": "POLICE",
        "supervisor": True,
    },
]

ROLE_WEIGHTS = [18, 14, 18, 16, 8, 8, 7, 5, 3]

CASE_TYPES = [
    "GENERAL_THEFT",
    "CYBER_FRAUD",
    "NARCOTICS",
    "VIOLENT_CRIME",
    "MISSING_PERSON",
    "FINANCIAL_CRIME",
    "JUVENILE_PROTECTION",
    "WOMEN_CHILD_SAFETY",
]

CASE_STATUSES = [
    "OPEN",
    "UNDER_INVESTIGATION",
    "CHARGESHEETED",
    "COURT_PENDING",
    "CLOSED",
]

RECORD_TYPES = [
    "FIR_SUMMARY",
    "CASE_DIARY",
    "WITNESS_STATEMENT",
    "VICTIM_RECORD",
    "JUVENILE_RECORD",
    "FORENSIC_REPORT",
    "CYBERCRIME_COMPLAINT",
    "EVIDENCE_MEDIA",
    "COURT_SUBMISSION",
]

PURPOSES = [
    "INVESTIGATION",
    "SUPERVISION",
    "FORENSIC_REVIEW",
    "PROSECUTION_REVIEW",
    "COURT_PRODUCTION",
    "AUDIT",
    "EMERGENCY_RESPONSE",
    "TRAINING",
]

REQUEST_ACTIONS = ["VIEW", "DOWNLOAD", "SHARE", "UPDATE", "APPROVE"]

SCENARIO_TYPES = [
    "normal_in_jurisdiction",
    "cross_jurisdiction_sensitive",
    "revoked_credential",
    "stale_case_assignment",
    "juvenile_sensitive",
    "emergency_override",
    "court_request",
    "sealed_record",
    "expired_approval_token",
    "random_context",
]

SCENARIO_WEIGHTS = [20, 14, 8, 10, 9, 8, 8, 8, 7, 8]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def weighted_choice(rng: random.Random, values: Sequence[str], weights: Sequence[int]) -> str:
    return rng.choices(list(values), weights=list(weights), k=1)[0]


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


def build_stations() -> List[Dict[str, object]]:
    stations: List[Dict[str, object]] = []
    for state_index in range(1, 4):
        state_id = f"STATE_{state_index:02d}"
        for district_index in range(1, 5):
            district_id = f"{state_id}_DIST_{district_index:02d}"
            for station_index in range(1, 4):
                station_id = f"{district_id}_PS_{station_index:02d}"
                stations.append(
                    {
                        "station_id": station_id,
                        "station_name": f"Synthetic Police Station {state_index}-{district_index}-{station_index}",
                        "district_id": district_id,
                        "state_id": state_id,
                        "agency": "POLICE",
                        "synthetic_only": "true",
                    }
                )
    return stations


def build_officers(rng: random.Random, stations: List[Dict[str, object]], count: int) -> List[Dict[str, object]]:
    officers: List[Dict[str, object]] = []
    for index in range(1, count + 1):
        station = rng.choice(stations)
        role_info = rng.choices(ROLES, weights=ROLE_WEIGHTS, k=1)[0]
        credential_status = rng.choices(
            ["ACTIVE", "REVOKED", "SUSPENDED"],
            weights=[90, 6, 4],
            k=1,
        )[0]
        officer = {
            "officer_id": f"OFF-{index:04d}",
            "officer_hash": stable_hash({"officer_id": f"OFF-{index:04d}", "seeded": True})[:24],
            "role": role_info["role"],
            "rank_level": role_info["rank_level"],
            "station_id": station["station_id"],
            "district_id": station["district_id"],
            "state_id": station["state_id"],
            "agency": role_info["agency"],
            "clearance_level": role_info["clearance_level"],
            "credential_status": credential_status,
            "is_supervisor": bool_text(bool(role_info["supervisor"])),
            "cyber_training": bool_text(role_info["role"] == "Cybercrime Officer" or rng.random() < 0.18),
            "forensic_training": bool_text(role_info["role"] == "Forensic Officer" or rng.random() < 0.12),
            "prior_request_count": rng.randint(0, 60),
            "recent_denied_count": rng.randint(0, 8),
            "assigned_case_ids": "",
            "synthetic_only": "true",
        }
        officers.append(officer)
    return officers


def build_cases(
    rng: random.Random,
    stations: List[Dict[str, object]],
    officers: List[Dict[str, object]],
    count: int,
) -> List[Dict[str, object]]:
    cases: List[Dict[str, object]] = []
    assignments: Dict[str, List[str]] = {str(officer["officer_id"]): [] for officer in officers}

    officers_by_station: Dict[str, List[Dict[str, object]]] = {}
    for officer in officers:
        officers_by_station.setdefault(str(officer["station_id"]), []).append(officer)

    for index in range(1, count + 1):
        station = rng.choice(stations)
        case_type = rng.choice(CASE_TYPES)
        status = rng.choices(CASE_STATUSES, weights=[18, 34, 18, 18, 12], k=1)[0]
        candidate_officers = officers_by_station.get(str(station["station_id"]), officers)
        active_candidates = [o for o in candidate_officers if o["credential_status"] == "ACTIVE"]
        active_candidates = active_candidates or candidate_officers
        assigned_count = min(len(active_candidates), rng.randint(1, 4))
        assigned = rng.sample(active_candidates, assigned_count)
        case_id = f"CASE-{index:05d}"
        for officer in assigned:
            assignments[str(officer["officer_id"])].append(case_id)
        sensitivity_hint = "HIGH" if case_type in {"JUVENILE_PROTECTION", "WOMEN_CHILD_SAFETY", "CYBER_FRAUD"} else "MEDIUM"
        cases.append(
            {
                "case_id": case_id,
                "case_type": case_type,
                "case_status": status,
                "originating_station_id": station["station_id"],
                "district_id": station["district_id"],
                "state_id": station["state_id"],
                "sensitivity_hint": sensitivity_hint,
                "assigned_officer_ids": "|".join(str(o["officer_id"]) for o in assigned),
                "synthetic_only": "true",
            }
        )

    for officer in officers:
        officer["assigned_case_ids"] = "|".join(assignments[str(officer["officer_id"])])
    return cases


def sensitivity_for_record(rng: random.Random, record_type: str, case_type: str) -> str:
    if record_type in {"JUVENILE_RECORD", "EVIDENCE_MEDIA"}:
        return rng.choices(["HIGH", "CLASSIFIED"], weights=[35, 65], k=1)[0]
    if record_type in {"WITNESS_STATEMENT", "VICTIM_RECORD", "CASE_DIARY", "FORENSIC_REPORT"}:
        return rng.choices(["MEDIUM", "HIGH", "CLASSIFIED"], weights=[10, 70, 20], k=1)[0]
    if record_type == "CYBERCRIME_COMPLAINT" or case_type == "CYBER_FRAUD":
        return rng.choices(["MEDIUM", "HIGH", "CLASSIFIED"], weights=[20, 65, 15], k=1)[0]
    if record_type == "COURT_SUBMISSION":
        return rng.choices(["MEDIUM", "HIGH"], weights=[60, 40], k=1)[0]
    return rng.choices(["LOW", "MEDIUM", "HIGH"], weights=[50, 40, 10], k=1)[0]


def build_records(rng: random.Random, cases: List[Dict[str, object]], target_count: int) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    index = 1
    while len(records) < target_count:
        case = rng.choice(cases)
        record_type = rng.choice(RECORD_TYPES)
        sensitivity = sensitivity_for_record(rng, record_type, str(case["case_type"]))
        juvenile_flag = record_type == "JUVENILE_RECORD" or case["case_type"] == "JUVENILE_PROTECTION"
        victim_flag = record_type == "VICTIM_RECORD" or case["case_type"] == "WOMEN_CHILD_SAFETY"
        witness_flag = record_type == "WITNESS_STATEMENT"
        evidence_media_flag = record_type == "EVIDENCE_MEDIA"
        sealed_status = rng.choices(
            ["OPEN", "SEALED"],
            weights=[78, 22 if sensitivity == "CLASSIFIED" else 8],
            k=1,
        )[0]
        retention_status = rng.choices(["ACTIVE", "ARCHIVED", "UNDER_REVIEW"], weights=[70, 18, 12], k=1)[0]
        records.append(
            {
                "record_id": f"REC-{index:06d}",
                "record_hash": stable_hash({"record_id": f"REC-{index:06d}", "seeded": True})[:24],
                "case_id": case["case_id"],
                "case_type": case["case_type"],
                "originating_station_id": case["originating_station_id"],
                "district_id": case["district_id"],
                "state_id": case["state_id"],
                "record_type": record_type,
                "sensitivity_level": sensitivity,
                "victim_flag": bool_text(victim_flag),
                "witness_flag": bool_text(witness_flag),
                "juvenile_flag": bool_text(juvenile_flag),
                "evidence_media_flag": bool_text(evidence_media_flag),
                "sealed_status": sealed_status,
                "retention_status": retention_status,
                "owner_agency": "POLICE",
                "raw_record_included": "false",
                "synthetic_only": "true",
            }
        )
        index += 1
    return records


def assigned_cases(officer: Dict[str, object]) -> set[str]:
    raw = str(officer.get("assigned_case_ids", ""))
    return {part for part in raw.split("|") if part}


def choose_assigned_record(
    rng: random.Random,
    officer: Dict[str, object],
    records: List[Dict[str, object]],
    max_sensitivity: str | None = None,
) -> Dict[str, object]:
    case_ids = assigned_cases(officer)
    candidates = [record for record in records if record["case_id"] in case_ids]
    if max_sensitivity == "MEDIUM":
        candidates = [record for record in candidates if record["sensitivity_level"] in {"LOW", "MEDIUM"}]
    return rng.choice(candidates or records)


def choose_cross_jurisdiction_record(
    rng: random.Random,
    officer: Dict[str, object],
    records: List[Dict[str, object]],
    sensitive_only: bool = False,
) -> Dict[str, object]:
    candidates = [
        record
        for record in records
        if record["district_id"] != officer["district_id"] or record["state_id"] != officer["state_id"]
    ]
    if sensitive_only:
        candidates = [
            record
            for record in candidates
            if record["sensitivity_level"] in {"HIGH", "CLASSIFIED"}
            or record["victim_flag"] == "true"
            or record["witness_flag"] == "true"
            or record["juvenile_flag"] == "true"
        ]
    return rng.choice(candidates or records)


def choose_record_by_condition(
    rng: random.Random,
    records: List[Dict[str, object]],
    predicate,
) -> Dict[str, object]:
    candidates = [record for record in records if predicate(record)]
    return rng.choice(candidates or records)


def choose_officer(
    rng: random.Random,
    officers: List[Dict[str, object]],
    credential_status: str | None = None,
) -> Dict[str, object]:
    candidates = officers
    if credential_status:
        candidates = [officer for officer in officers if officer["credential_status"] == credential_status]
    return rng.choice(candidates or officers)


def case_assignment_status(scenario: str, officer: Dict[str, object], record: Dict[str, object]) -> str:
    if scenario == "stale_case_assignment":
        return "STALE"
    if str(record["case_id"]) in assigned_cases(officer):
        return "ASSIGNED"
    return "NOT_ASSIGNED"


def scenario_request_context(
    rng: random.Random,
    scenario: str,
    officer: Dict[str, object],
    record: Dict[str, object],
) -> Dict[str, object]:
    purpose = rng.choice(PURPOSES)
    action = rng.choices(REQUEST_ACTIONS, weights=[66, 18, 7, 5, 4], k=1)[0]
    emergency_flag = False
    court_flag = False
    approval_status = rng.choices(["NOT_REQUIRED", "PRESENT_VALID", "MISSING"], weights=[58, 25, 17], k=1)[0]

    if scenario == "normal_in_jurisdiction":
        purpose = "INVESTIGATION"
        action = "VIEW"
        approval_status = "NOT_REQUIRED"
    elif scenario == "cross_jurisdiction_sensitive":
        purpose = rng.choice(["INVESTIGATION", "SUPERVISION", "FORENSIC_REVIEW"])
        approval_status = rng.choice(["MISSING", "PRESENT_VALID"])
    elif scenario == "revoked_credential":
        purpose = rng.choice(["INVESTIGATION", "AUDIT"])
        approval_status = "MISSING"
    elif scenario == "stale_case_assignment":
        purpose = "INVESTIGATION"
        approval_status = "MISSING"
    elif scenario == "juvenile_sensitive":
        purpose = rng.choice(["INVESTIGATION", "SUPERVISION"])
        approval_status = rng.choice(["MISSING", "PRESENT_VALID"])
    elif scenario == "emergency_override":
        purpose = "EMERGENCY_RESPONSE"
        emergency_flag = True
        approval_status = rng.choice(["MISSING", "PRESENT_VALID"])
    elif scenario == "court_request":
        purpose = rng.choice(["COURT_PRODUCTION", "PROSECUTION_REVIEW"])
        court_flag = True
        approval_status = "PRESENT_VALID"
    elif scenario == "sealed_record":
        purpose = rng.choice(["INVESTIGATION", "COURT_PRODUCTION", "PROSECUTION_REVIEW"])
        court_flag = purpose in {"COURT_PRODUCTION", "PROSECUTION_REVIEW"}
        approval_status = rng.choice(["MISSING", "PRESENT_VALID"])
    elif scenario == "expired_approval_token":
        purpose = rng.choice(["INVESTIGATION", "FORENSIC_REVIEW", "PROSECUTION_REVIEW"])
        approval_status = "EXPIRED"

    return {
        "purpose": purpose,
        "action": action,
        "emergency_flag": bool_text(emergency_flag),
        "court_or_prosecutor_request_flag": bool_text(court_flag),
        "approval_token_status": approval_status,
        "time_window": rng.choices(["BUSINESS_HOURS", "AFTER_HOURS", "NIGHT"], weights=[70, 20, 10], k=1)[0],
        "network_status": rng.choices(["ONLINE", "DEGRADED", "STATION_NODE_DOWN"], weights=[86, 10, 4], k=1)[0],
        "request_channel": rng.choice(["CCTNS_STYLE_API", "ICJS_STYLE_EXCHANGE", "MANUAL_ESCALATION"]),
    }


def build_request_for_scenario(
    rng: random.Random,
    index: int,
    scenario: str,
    officers: List[Dict[str, object]],
    records: List[Dict[str, object]],
    start_time: datetime,
) -> Dict[str, object]:
    if scenario == "normal_in_jurisdiction":
        officer = choose_officer(rng, officers, credential_status="ACTIVE")
        record = choose_assigned_record(rng, officer, records, max_sensitivity="MEDIUM")
    elif scenario == "cross_jurisdiction_sensitive":
        officer = choose_officer(rng, officers, credential_status="ACTIVE")
        record = choose_cross_jurisdiction_record(rng, officer, records, sensitive_only=True)
    elif scenario == "revoked_credential":
        officer = choose_officer(rng, officers, credential_status="REVOKED")
        record = rng.choice(records)
    elif scenario == "stale_case_assignment":
        officer = choose_officer(rng, officers, credential_status="ACTIVE")
        record = rng.choice([r for r in records if r["case_id"] not in assigned_cases(officer)] or records)
    elif scenario == "juvenile_sensitive":
        officer = choose_officer(rng, officers, credential_status="ACTIVE")
        record = choose_record_by_condition(rng, records, lambda item: item["juvenile_flag"] == "true")
    elif scenario == "emergency_override":
        officer = choose_officer(rng, officers, credential_status="ACTIVE")
        record = choose_cross_jurisdiction_record(rng, officer, records, sensitive_only=True)
    elif scenario == "court_request":
        officer = rng.choice([o for o in officers if o["agency"] in {"PROSECUTION", "POLICE"}] or officers)
        record = rng.choice(records)
    elif scenario == "sealed_record":
        officer = choose_officer(rng, officers, credential_status="ACTIVE")
        record = choose_record_by_condition(rng, records, lambda item: item["sealed_status"] == "SEALED")
    elif scenario == "expired_approval_token":
        officer = choose_officer(rng, officers, credential_status="ACTIVE")
        record = rng.choice(records)
    else:
        officer = rng.choice(officers)
        record = rng.choice(records)

    context = scenario_request_context(rng, scenario, officer, record)
    request_time = start_time + timedelta(minutes=index * rng.randint(2, 17))
    same_station = officer["station_id"] == record["originating_station_id"]
    same_district = officer["district_id"] == record["district_id"]
    same_state = officer["state_id"] == record["state_id"]
    cross_jurisdiction = not same_district or not same_state

    row: Dict[str, object] = {
        "request_id": f"REQ-{index:06d}",
        "timestamp_utc": request_time.isoformat().replace("+00:00", "Z"),
        "scenario_type": scenario,
        "requester_officer_id": officer["officer_id"],
        "requester_officer_hash": officer["officer_hash"],
        "requester_role": officer["role"],
        "requester_rank_level": officer["rank_level"],
        "requester_agency": officer["agency"],
        "requester_station_id": officer["station_id"],
        "requester_district_id": officer["district_id"],
        "requester_state_id": officer["state_id"],
        "requester_clearance_level": officer["clearance_level"],
        "requester_credential_status": officer["credential_status"],
        "case_assignment_status": case_assignment_status(scenario, officer, record),
        "target_record_id": record["record_id"],
        "target_record_hash": record["record_hash"],
        "target_case_id": record["case_id"],
        "target_case_type": record["case_type"],
        "target_record_type": record["record_type"],
        "target_station_id": record["originating_station_id"],
        "target_district_id": record["district_id"],
        "target_state_id": record["state_id"],
        "target_owner_agency": record["owner_agency"],
        "record_sensitivity_level": record["sensitivity_level"],
        "victim_flag": record["victim_flag"],
        "witness_flag": record["witness_flag"],
        "juvenile_flag": record["juvenile_flag"],
        "evidence_media_flag": record["evidence_media_flag"],
        "sealed_status": record["sealed_status"],
        "retention_status": record["retention_status"],
        "same_station": bool_text(same_station),
        "same_district": bool_text(same_district),
        "same_state": bool_text(same_state),
        "cross_jurisdiction": bool_text(cross_jurisdiction),
        "purpose": context["purpose"],
        "action": context["action"],
        "emergency_flag": context["emergency_flag"],
        "court_or_prosecutor_request_flag": context["court_or_prosecutor_request_flag"],
        "approval_token_status": context["approval_token_status"],
        "time_window": context["time_window"],
        "network_status": context["network_status"],
        "request_channel": context["request_channel"],
        "policy_version": DEFAULT_POLICY_VERSION,
        "raw_record_included": "false",
        "synthetic_only": "true",
    }
    row["request_content_hash"] = stable_hash(row)
    return row


def build_requests(
    rng: random.Random,
    officers: List[Dict[str, object]],
    records: List[Dict[str, object]],
    count: int,
) -> List[Dict[str, object]]:
    start_time = datetime(2026, 5, 27, 0, 0, tzinfo=timezone.utc)
    requests = []
    for index in range(1, count + 1):
        scenario = weighted_choice(rng, SCENARIO_TYPES, SCENARIO_WEIGHTS)
        requests.append(build_request_for_scenario(rng, index, scenario, officers, records, start_time))
    return requests


def counter_rows(name: str, counter: Counter) -> List[Dict[str, object]]:
    return [
        {"profile_group": name, "value": str(value), "count": count}
        for value, count in sorted(counter.items(), key=lambda item: str(item[0]))
    ]


def build_profile(requests: List[Dict[str, object]], officers: List[Dict[str, object]], records: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    rows.extend(counter_rows("request.scenario_type", Counter(row["scenario_type"] for row in requests)))
    rows.extend(counter_rows("request.cross_jurisdiction", Counter(row["cross_jurisdiction"] for row in requests)))
    rows.extend(counter_rows("request.approval_token_status", Counter(row["approval_token_status"] for row in requests)))
    rows.extend(counter_rows("request.purpose", Counter(row["purpose"] for row in requests)))
    rows.extend(counter_rows("request.action", Counter(row["action"] for row in requests)))
    rows.extend(counter_rows("request.record_sensitivity_level", Counter(row["record_sensitivity_level"] for row in requests)))
    rows.extend(counter_rows("officer.credential_status", Counter(row["credential_status"] for row in officers)))
    rows.extend(counter_rows("officer.role", Counter(row["role"] for row in officers)))
    rows.extend(counter_rows("record.record_type", Counter(row["record_type"] for row in records)))
    rows.extend(counter_rows("record.sensitivity_level", Counter(row["sensitivity_level"] for row in records)))
    return rows


def build_metrics(
    requests: List[Dict[str, object]],
    officers: List[Dict[str, object]],
    cases: List[Dict[str, object]],
    records: List[Dict[str, object]],
) -> Dict[str, object]:
    return {
        "artifact_type": "synthetic_dataset_profile",
        "result_claim": "none; dataset generation only",
        "counts": {
            "stations": len({row["requester_station_id"] for row in requests} | {row["target_station_id"] for row in requests}),
            "officers": len(officers),
            "cases": len(cases),
            "records": len(records),
            "access_requests": len(requests),
        },
        "request_scenario_counts": dict(Counter(row["scenario_type"] for row in requests)),
        "request_sensitivity_counts": dict(Counter(row["record_sensitivity_level"] for row in requests)),
        "cross_jurisdiction_counts": dict(Counter(row["cross_jurisdiction"] for row in requests)),
        "credential_status_counts": dict(Counter(row["requester_credential_status"] for row in requests)),
        "raw_record_included": False,
        "synthetic_only": True,
        "limitations": [
            "Synthetic data only; no real CCTNS, ICJS, FIR, officer, victim, witness, or case records are included.",
            "No RBAC, ABAC, PBAC, XAI, or blockchain audit decision has been implemented in this step.",
            "Scenario labels support workload coverage; they are not experimental results.",
        ],
    }


def data_dictionary_text() -> str:
    return """# Synthetic Access Request Data Dictionary

This file describes the Step 1 synthetic workload.

## Important Boundary

All rows are synthetic. The dataset does not contain real police, FIR, victim, witness, case, CCTNS, or ICJS data.

## Core Files

- `stations.csv`: synthetic police stations.
- `officers.csv`: synthetic officers and their static attributes.
- `cases.csv`: synthetic case metadata and case assignment links.
- `records.csv`: synthetic record metadata. Raw record content is not generated.
- `access_requests.csv`: synthetic access requests for later access-control testing.

## Important Request Fields

| Field | Meaning |
|---|---|
| `request_id` | Synthetic request identifier. |
| `scenario_type` | Workload coverage scenario, not a result label. |
| `requester_role` | Role of the synthetic requester. |
| `requester_clearance_level` | Synthetic clearance level used later by policy rules. |
| `requester_credential_status` | Active, revoked, or suspended credential state. |
| `case_assignment_status` | Whether the requester is assigned, not assigned, or stale for the target case. |
| `target_record_type` | Synthetic record category, such as FIR summary or witness statement. |
| `record_sensitivity_level` | LOW, MEDIUM, HIGH, or CLASSIFIED. |
| `victim_flag`, `witness_flag`, `juvenile_flag` | Sensitivity flags for later policy testing. |
| `same_station`, `same_district`, `same_state`, `cross_jurisdiction` | Jurisdiction context. |
| `purpose` | Declared purpose of access. |
| `action` | Requested action, such as VIEW, DOWNLOAD, SHARE, UPDATE, or APPROVE. |
| `emergency_flag` | Whether emergency access is claimed. |
| `court_or_prosecutor_request_flag` | Whether court/prosecution context is present. |
| `approval_token_status` | NOT_REQUIRED, PRESENT_VALID, MISSING, or EXPIRED. |
| `request_content_hash` | SHA-256 hash of the canonical request row. |

## Next Step

The next step is to implement a deterministic policy oracle that converts each request into `allow`, `deny`, or `escalate` with reason codes.
"""


def run_readme_text(run_id: str, seed: int, request_count: int) -> str:
    return f"""# Run {run_id}

Purpose: Step 1 synthetic access-request data generation for SEBA-XAI.

Seed: `{seed}`

Requests generated: `{request_count}`

## What This Run Contains

- Synthetic stations, officers, cases, records, and access requests.
- Dataset profile and manifest.
- No real police/CCTNS/ICJS/FIR data.
- No RBAC/ABAC/PBAC decision output.
- No XAI output.
- No blockchain audit result.

## How To Reproduce

```bash
python3 prototype/synthetic_access_sim/generate_synthetic_requests.py \\
  --run-id {run_id} \\
  --seed {seed} \\
  --num-requests {request_count}
```

## Correct Interpretation

This run is a dataset/workload-generation artifact only. It can support future policy-oracle, audit, and XAI experiments, but it is not itself an experiment result.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic SEBA-XAI access requests.")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-officers", type=int, default=240)
    parser.add_argument("--num-cases", type=int, default=360)
    parser.add_argument("--num-records", type=int, default=900)
    parser.add_argument("--num-requests", type=int, default=1000)
    parser.add_argument(
        "--results-profile-table",
        default=str(ROOT / "prototype" / "results" / "tables" / "synthetic_request_step1_profile.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    run_dir = ROOT / "prototype" / "runs" / args.run_id
    artifacts_dir = run_dir / "artifacts"
    logs_dir = run_dir / "logs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    config = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "seed": args.seed,
        "num_officers": args.num_officers,
        "num_cases": args.num_cases,
        "num_records": args.num_records,
        "num_requests": args.num_requests,
        "policy_version": DEFAULT_POLICY_VERSION,
        "synthetic_only": True,
        "raw_record_included": False,
        "step": "step_1_synthetic_access_request_generation",
    }
    write_yaml(run_dir / "config.yaml", config)

    stations = build_stations()
    officers = build_officers(rng, stations, args.num_officers)
    cases = build_cases(rng, stations, officers, args.num_cases)
    records = build_records(rng, cases, args.num_records)
    requests = build_requests(rng, officers, records, args.num_requests)

    write_csv(artifacts_dir / "stations.csv", stations)
    write_csv(artifacts_dir / "officers.csv", officers)
    write_csv(artifacts_dir / "cases.csv", cases)
    write_csv(artifacts_dir / "records.csv", records)
    write_csv(artifacts_dir / "access_requests.csv", requests)

    profile_rows = build_profile(requests, officers, records)
    write_csv(artifacts_dir / "dataset_profile.csv", profile_rows)
    write_csv(Path(args.results_profile_table), profile_rows)

    metrics = build_metrics(requests, officers, cases, records)
    write_json(run_dir / "metrics.json", metrics)

    artifact_files = [
        "stations.csv",
        "officers.csv",
        "cases.csv",
        "records.csv",
        "access_requests.csv",
        "dataset_profile.csv",
    ]
    manifest = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "generator": "prototype/synthetic_access_sim/generate_synthetic_requests.py",
        "seed": args.seed,
        "policy_version": DEFAULT_POLICY_VERSION,
        "synthetic_only": True,
        "raw_record_included": False,
        "artifact_hashes": {
            filename: file_sha256(artifacts_dir / filename)
            for filename in artifact_files
        },
        "notes": [
            "This is a synthetic workload artifact, not an experiment result.",
            "Scenario labels describe workload coverage and should not be treated as measured outcomes.",
        ],
    }
    write_json(artifacts_dir / "dataset_manifest.json", manifest)
    (artifacts_dir / "data_dictionary.md").write_text(data_dictionary_text(), encoding="utf-8")
    (artifacts_dir / "README.md").write_text(run_readme_text(args.run_id, args.seed, args.num_requests), encoding="utf-8")

    log_lines = [
        f"created_at_utc={created_at}",
        f"run_id={args.run_id}",
        f"seed={args.seed}",
        f"stations={len(stations)}",
        f"officers={len(officers)}",
        f"cases={len(cases)}",
        f"records={len(records)}",
        f"access_requests={len(requests)}",
        "status=success",
        "claim=dataset_generation_only_no_experimental_result",
    ]
    (logs_dir / "generation.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"Wrote synthetic access-request run: {run_dir}")
    print(f"Requests: {len(requests)}")
    print(f"Profile table: {args.results_profile_table}")


if __name__ == "__main__":
    main()
