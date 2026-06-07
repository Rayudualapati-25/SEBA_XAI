"""Frozen dataclass schemas for the SEBA-XAI synthetic access workload.

Mirrors the CSV columns produced by the existing prototype scripts under
``prototype/synthetic_access_sim/``. Using ``@dataclass(frozen=True)`` enforces
the project-wide immutability rule: no in-place mutation, every state change
returns a new object.

The schemas are the single source of truth for downstream NS-PI work
(``seba.nspi``), the attack catalog (``seba.attacks``), and scoring
(``seba.scoring``).
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import StrEnum
from typing import Any, ClassVar

# ---------------------------------------------------------------------------
# Enumerations matching the CSV vocabularies produced by Step 1/2.
# ---------------------------------------------------------------------------


class Decision(StrEnum):
    """Final policy decision label."""

    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


class CredentialStatus(StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    SUSPENDED = "SUSPENDED"


class SensitivityLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CLASSIFIED = "CLASSIFIED"


class SealedStatus(StrEnum):
    OPEN = "OPEN"
    SEALED = "SEALED"


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _to_bool(raw: Any) -> bool:
    """Parse CSV-style booleans (``"true"`` / ``"false"``) into Python bools."""

    if isinstance(raw, bool):
        return raw
    return str(raw).strip().lower() == "true"


def _to_int(raw: Any, default: int = 0) -> int:
    try:
        return int(str(raw))
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Entity schemas. Field order matches the CSV header in the existing
# prototype runs so ``from_row(dict_from_csv)`` is a one-liner everywhere.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Station:
    station_id: str
    station_name: str
    district_id: str
    state_id: str
    agency: str
    synthetic_only: bool = True

    CSV_COLUMNS: ClassVar[tuple[str, ...]] = (
        "station_id",
        "station_name",
        "district_id",
        "state_id",
        "agency",
        "synthetic_only",
    )

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Station:
        return cls(
            station_id=row["station_id"],
            station_name=row["station_name"],
            district_id=row["district_id"],
            state_id=row["state_id"],
            agency=row["agency"],
            synthetic_only=_to_bool(row.get("synthetic_only", True)),
        )


@dataclass(frozen=True, slots=True)
class Officer:
    officer_id: str
    officer_hash: str
    role: str
    rank_level: int
    station_id: str
    district_id: str
    state_id: str
    agency: str
    clearance_level: str
    credential_status: CredentialStatus
    is_supervisor: bool
    cyber_training: bool
    forensic_training: bool
    prior_request_count: int
    recent_denied_count: int
    assigned_case_ids: tuple[str, ...]
    synthetic_only: bool = True

    CSV_COLUMNS: ClassVar[tuple[str, ...]] = (
        "officer_id",
        "officer_hash",
        "role",
        "rank_level",
        "station_id",
        "district_id",
        "state_id",
        "agency",
        "clearance_level",
        "credential_status",
        "is_supervisor",
        "cyber_training",
        "forensic_training",
        "prior_request_count",
        "recent_denied_count",
        "assigned_case_ids",
        "synthetic_only",
    )

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Officer:
        cases_raw = row.get("assigned_case_ids", "") or ""
        cases = tuple(c for c in cases_raw.split("|") if c)
        return cls(
            officer_id=row["officer_id"],
            officer_hash=row["officer_hash"],
            role=row["role"],
            rank_level=_to_int(row["rank_level"]),
            station_id=row["station_id"],
            district_id=row["district_id"],
            state_id=row["state_id"],
            agency=row["agency"],
            clearance_level=row["clearance_level"],
            credential_status=CredentialStatus(row["credential_status"]),
            is_supervisor=_to_bool(row["is_supervisor"]),
            cyber_training=_to_bool(row["cyber_training"]),
            forensic_training=_to_bool(row["forensic_training"]),
            prior_request_count=_to_int(row.get("prior_request_count", 0)),
            recent_denied_count=_to_int(row.get("recent_denied_count", 0)),
            assigned_case_ids=cases,
            synthetic_only=_to_bool(row.get("synthetic_only", True)),
        )


@dataclass(frozen=True, slots=True)
class Record:
    record_id: str
    record_hash: str
    case_id: str
    case_type: str
    originating_station_id: str
    district_id: str
    state_id: str
    record_type: str
    sensitivity_level: SensitivityLevel
    victim_flag: bool
    witness_flag: bool
    juvenile_flag: bool
    evidence_media_flag: bool
    sealed_status: SealedStatus
    retention_status: str
    owner_agency: str
    raw_record_included: bool = False
    synthetic_only: bool = True

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Record:
        return cls(
            record_id=row["record_id"],
            record_hash=row["record_hash"],
            case_id=row["case_id"],
            case_type=row["case_type"],
            originating_station_id=row["originating_station_id"],
            district_id=row["district_id"],
            state_id=row["state_id"],
            record_type=row["record_type"],
            sensitivity_level=SensitivityLevel(row["sensitivity_level"]),
            victim_flag=_to_bool(row["victim_flag"]),
            witness_flag=_to_bool(row["witness_flag"]),
            juvenile_flag=_to_bool(row["juvenile_flag"]),
            evidence_media_flag=_to_bool(row["evidence_media_flag"]),
            sealed_status=SealedStatus(row["sealed_status"]),
            retention_status=row["retention_status"],
            owner_agency=row["owner_agency"],
            raw_record_included=_to_bool(row.get("raw_record_included", False)),
            synthetic_only=_to_bool(row.get("synthetic_only", True)),
        )


@dataclass(frozen=True, slots=True)
class AccessRequest:
    """A single inter-agency access request.

    Mirrors the ``access_requests.csv`` columns. Kept narrow on purpose: the
    NS-PI learner consumes (subject_attrs, object_attrs, env_attrs) projected
    from this dataclass, not arbitrary CSV rows.
    """

    request_id: str
    timestamp_utc: str
    scenario_type: str
    requester_officer_id: str
    requester_role: str
    requester_rank_level: int
    requester_agency: str
    requester_station_id: str
    requester_district_id: str
    requester_state_id: str
    requester_clearance_level: str
    requester_credential_status: CredentialStatus
    case_assignment_status: str
    target_record_id: str
    target_case_id: str
    target_case_type: str
    target_record_type: str
    target_station_id: str
    target_district_id: str
    target_state_id: str
    target_owner_agency: str
    record_sensitivity_level: SensitivityLevel
    victim_flag: bool
    witness_flag: bool
    juvenile_flag: bool
    evidence_media_flag: bool
    sealed_status: SealedStatus
    retention_status: str
    same_station: bool
    same_district: bool
    same_state: bool
    cross_jurisdiction: bool
    purpose: str
    action: str
    emergency_flag: bool
    court_or_prosecutor_request_flag: bool
    approval_token_status: str
    time_window: str
    network_status: str
    request_channel: str
    policy_version: str
    request_content_hash: str
    raw_record_included: bool = False
    synthetic_only: bool = True

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> AccessRequest:
        bool_cols = (
            "victim_flag",
            "witness_flag",
            "juvenile_flag",
            "evidence_media_flag",
            "same_station",
            "same_district",
            "same_state",
            "cross_jurisdiction",
            "emergency_flag",
            "court_or_prosecutor_request_flag",
            "raw_record_included",
            "synthetic_only",
        )
        coerced = {col: _to_bool(row.get(col, False)) for col in bool_cols}
        return cls(
            request_id=row["request_id"],
            timestamp_utc=row["timestamp_utc"],
            scenario_type=row["scenario_type"],
            requester_officer_id=row["requester_officer_id"],
            requester_role=row["requester_role"],
            requester_rank_level=_to_int(row["requester_rank_level"]),
            requester_agency=row["requester_agency"],
            requester_station_id=row["requester_station_id"],
            requester_district_id=row["requester_district_id"],
            requester_state_id=row["requester_state_id"],
            requester_clearance_level=row["requester_clearance_level"],
            requester_credential_status=CredentialStatus(row["requester_credential_status"]),
            case_assignment_status=row["case_assignment_status"],
            target_record_id=row["target_record_id"],
            target_case_id=row["target_case_id"],
            target_case_type=row["target_case_type"],
            target_record_type=row["target_record_type"],
            target_station_id=row["target_station_id"],
            target_district_id=row["target_district_id"],
            target_state_id=row["target_state_id"],
            target_owner_agency=row["target_owner_agency"],
            record_sensitivity_level=SensitivityLevel(row["record_sensitivity_level"]),
            sealed_status=SealedStatus(row["sealed_status"]),
            retention_status=row["retention_status"],
            purpose=row["purpose"],
            action=row["action"],
            approval_token_status=row["approval_token_status"],
            time_window=row["time_window"],
            network_status=row["network_status"],
            request_channel=row["request_channel"],
            policy_version=row["policy_version"],
            request_content_hash=row["request_content_hash"],
            **coerced,
        )


@dataclass(frozen=True, slots=True)
class DecisionRecord:
    """A policy decision attached to a request.

    This is the unit consumed by the NS-PI learner and the attack scorer.
    """

    request_id: str
    decision: Decision
    primary_reason_code: str
    decisive_attributes: tuple[str, ...]
    policy_version: str
    decision_hash: str
    explanation_hash: str
    audit_anchor_hash: str

    def with_decision(self, new_decision: Decision) -> DecisionRecord:
        """Return a copy with the decision replaced (immutability rule)."""

        return DecisionRecord(
            request_id=self.request_id,
            decision=new_decision,
            primary_reason_code=self.primary_reason_code,
            decisive_attributes=self.decisive_attributes,
            policy_version=self.policy_version,
            decision_hash=self.decision_hash,
            explanation_hash=self.explanation_hash,
            audit_anchor_hash=self.audit_anchor_hash,
        )


# ---------------------------------------------------------------------------
# Module-level introspection helper used by tests.
# ---------------------------------------------------------------------------


def all_entity_classes() -> tuple[type, ...]:
    """Return every frozen dataclass exported from this module."""

    return (Station, Officer, Record, AccessRequest, DecisionRecord)


def assert_all_frozen() -> None:
    """Tripwire used by tests to enforce the immutability rule."""

    for cls in all_entity_classes():
        params = getattr(cls, "__dataclass_params__", None)
        if params is None or not params.frozen:
            raise AssertionError(f"{cls.__name__} must be a frozen dataclass")
        # Sanity check: every field has a type annotation.
        for f in fields(cls):
            if f.type is None:
                raise AssertionError(f"{cls.__name__}.{f.name} is missing a type annotation")
