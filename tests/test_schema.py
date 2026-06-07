"""Schema tests: immutability invariant + round-trip parsing on real run data.

These tests intentionally run against the existing seed-42 prototype run rather
than synthetic fixtures. The point is to verify that the new dataclass schema
faithfully represents the CSVs the prototype scripts already produce — so the
NS-PI work can consume them without a parallel format.
"""

from __future__ import annotations

import dataclasses

import pytest

from seba import __version__
from seba.schema import (
    AccessRequest,
    CredentialStatus,
    Decision,
    DecisionRecord,
    Officer,
    Record,
    SealedStatus,
    SensitivityLevel,
    Station,
    all_entity_classes,
    assert_all_frozen,
)

# ---------------------------------------------------------------------------
# 1. Package sanity.
# ---------------------------------------------------------------------------


def test_package_version_is_a_pep440_string() -> None:
    assert isinstance(__version__, str) and __version__.count(".") >= 1


# ---------------------------------------------------------------------------
# 2. Immutability invariant (project rule: no in-place mutation).
# ---------------------------------------------------------------------------


def test_every_entity_is_a_frozen_dataclass() -> None:
    assert_all_frozen()


@pytest.mark.parametrize("cls", all_entity_classes())
def test_entity_rejects_attribute_assignment(cls: type) -> None:
    """Frozen dataclasses must raise on any attempted mutation."""

    field_defaults = {
        str: "x",
        int: 0,
        bool: False,
        tuple: (),
    }

    kwargs: dict[str, object] = {}
    for field in dataclasses.fields(cls):
        if field.default is not dataclasses.MISSING:
            continue
        if field.type is CredentialStatus:
            kwargs[field.name] = CredentialStatus.ACTIVE
        elif field.type is SensitivityLevel:
            kwargs[field.name] = SensitivityLevel.LOW
        elif field.type is SealedStatus:
            kwargs[field.name] = SealedStatus.OPEN
        elif field.type is Decision:
            kwargs[field.name] = Decision.ALLOW
        elif field.type in field_defaults:
            kwargs[field.name] = field_defaults[field.type]
        elif field.type == "tuple[str, ...]":
            kwargs[field.name] = ()
        else:
            # str-typed annotations come through as the literal "str".
            kwargs[field.name] = "x"

    instance = cls(**kwargs)
    first_field = dataclasses.fields(cls)[0].name
    with pytest.raises(dataclasses.FrozenInstanceError):
        # The whole point is to verify the runtime guard fires on any field.
        setattr(instance, first_field, "mutated")


# ---------------------------------------------------------------------------
# 3. Round-trip parsing on real prototype CSVs.
# ---------------------------------------------------------------------------


def test_station_round_trip_on_real_rows(station_rows: list[dict[str, str]]) -> None:
    assert station_rows, "stations.csv was empty"
    stations = [Station.from_row(row) for row in station_rows]
    assert len(stations) == len(station_rows)
    assert all(s.synthetic_only for s in stations)
    assert all(s.station_id.startswith("STATE_") for s in stations)


def test_officer_round_trip_on_real_rows(officer_rows: list[dict[str, str]]) -> None:
    officers = [Officer.from_row(row) for row in officer_rows]
    assert officers, "officers.csv was empty"
    assert all(isinstance(o.credential_status, CredentialStatus) for o in officers)
    # The case-ID column is pipe-separated in the CSV; the schema parses it
    # into a tuple. Every officer in the seed-42 run has at least one case.
    assert all(isinstance(o.assigned_case_ids, tuple) for o in officers)


def test_record_round_trip_on_real_rows(record_rows: list[dict[str, str]]) -> None:
    records = [Record.from_row(row) for row in record_rows]
    assert records, "records.csv was empty"
    # Every sensitivity value in the CSV must round-trip through the enum.
    seen = {r.sensitivity_level for r in records}
    assert seen.issubset(set(SensitivityLevel))


def test_access_request_round_trip_on_real_rows(
    access_request_rows: list[dict[str, str]],
) -> None:
    requests = [AccessRequest.from_row(row) for row in access_request_rows]
    assert len(requests) == 1000, "expected 1000 synthetic requests in seed-42 run"
    # Every parsed request has a non-empty request_id and content hash, and
    # the enum-typed fields are valid members (the constructor would raise
    # otherwise). We do NOT encode domain rules about cross_jurisdiction here
    # — those belong in seba.policy_oracle, not in the schema layer.
    assert all(r.request_id for r in requests)
    assert all(len(r.request_content_hash) == 64 for r in requests)
    decisions_seen = {r.scenario_type for r in requests}
    assert decisions_seen, "expected at least one scenario_type"


# ---------------------------------------------------------------------------
# 4. DecisionRecord.with_decision returns a NEW object (immutability rule).
# ---------------------------------------------------------------------------


def test_with_decision_returns_new_object() -> None:
    original = DecisionRecord(
        request_id="REQ-000001",
        decision=Decision.ALLOW,
        primary_reason_code="OK",
        decisive_attributes=("purpose", "jurisdiction"),
        policy_version="P-TEST",
        decision_hash="d1",
        explanation_hash="e1",
        audit_anchor_hash="a1",
    )
    updated = original.with_decision(Decision.DENY)
    assert original.decision is Decision.ALLOW, "original must not be mutated"
    assert updated.decision is Decision.DENY
    assert updated is not original
    # All non-decision fields are preserved verbatim.
    assert updated.request_id == original.request_id
    assert updated.decisive_attributes == original.decisive_attributes
