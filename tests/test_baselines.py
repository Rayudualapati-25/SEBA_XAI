"""Tests for the literature-baseline implementations."""

from __future__ import annotations

import numpy as np
import pytest

from seba.attacks import (
    backdate_request,
    collude_block_signature,
    compromised_signer,
    replay_approval_token,
    swap_explanation_hash,
)
from seba.baselines import (
    CTLog,
    TrustedRawPolicyOracle,
    ct_log_detector,
    fabric_abac_detector,
)
from seba.scoring import score_defense_against_catalog


@pytest.fixture
def clean_log():
    rows = []
    for i in range(30):
        decision = ("allow", "deny", "escalate")[i % 3]
        rows.append(
            {
                "event_sequence": i + 1,
                "event_id": f"E-{i:03d}",
                "timestamp_utc": f"2026-05-28T00:{i:02d}:00Z",
                "request_id": f"REQ-{i:06d}",
                "decision": decision,
                "primary_reason_code": f"REASON-{i % 5}",
                "explanation_hash": f"x-{i:03d}",
                "decision_hash": f"d-{i:03d}",
                "audit_anchor_hash": f"a-{i:03d}",
                "request_content_hash": f"r-{i:03d}",
                "record_sensitivity_level": ("LOW", "HIGH", "CLASSIFIED")[i % 3],
                "requester_station_id": f"S-{i % 4}",
                "policy_version_evaluated": "P-TEST",
            }
        )
    return tuple(rows)


# ---------------------------------------------------------------------------
# CT-log baseline.
# ---------------------------------------------------------------------------


def test_ct_log_head_is_stable_for_unchanged_log(clean_log) -> None:
    h1 = CTLog.from_log(clean_log).signed_tree_head
    h2 = CTLog.from_log(clean_log).signed_tree_head
    assert h1 == h2 and len(h1) == 64


def test_ct_log_detects_field_edit(clean_log) -> None:
    rng = np.random.default_rng(7)
    res = backdate_request(clean_log, rng)
    assert ct_log_detector(res.perturbed_log, clean_log) is True


def test_ct_log_detects_explanation_swap(clean_log) -> None:
    rng = np.random.default_rng(7)
    res = swap_explanation_hash(clean_log, rng)
    if res.affected_indices:
        assert ct_log_detector(res.perturbed_log, clean_log) is True


# ---------------------------------------------------------------------------
# Fabric+ABAC baseline.
# ---------------------------------------------------------------------------


def test_fabric_abac_detects_collusion(clean_log) -> None:
    rng = np.random.default_rng(7)
    res = collude_block_signature(clean_log, rng)
    assert fabric_abac_detector(res.perturbed_log, clean_log) is True


def test_fabric_abac_detects_replay(clean_log) -> None:
    rng = np.random.default_rng(7)
    res = replay_approval_token(clean_log, rng)
    if res.affected_indices:
        assert fabric_abac_detector(res.perturbed_log, clean_log) is True


# ---------------------------------------------------------------------------
# Independent raw-attribute policy oracle.
# ---------------------------------------------------------------------------


def test_trusted_policy_oracle_detects_compromised_signer(clean_log) -> None:
    oracle = TrustedRawPolicyOracle.from_records(clean_log)
    rng = np.random.default_rng(7)
    res = compromised_signer(clean_log, rng, flip_fraction=0.5)
    assert res.affected_indices
    assert oracle.detect(res.perturbed_log, clean_log) is True


# ---------------------------------------------------------------------------
# Both baselines plug into the AAS scorer cleanly.
# ---------------------------------------------------------------------------


def test_baselines_score_via_aas_harness(clean_log) -> None:
    ct = score_defense_against_catalog("ct_log", ct_log_detector, clean_log, seed=42)
    fa = score_defense_against_catalog("fabric_abac", fabric_abac_detector, clean_log, seed=42)
    assert 0.0 <= ct.aas <= 1.0
    assert 0.0 <= fa.aas <= 1.0
    # Both should beat a hypothetical zero defense.
    assert ct.aas > 0
    assert fa.aas > 0
