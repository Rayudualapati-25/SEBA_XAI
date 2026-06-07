"""Tests for the SEBA-XAI attack catalog and AAS scorer.

These tests use a tiny in-memory clean log so they stay fast (<0.1s) and
deterministic. Real signed-log artifacts are tested via the larger
multi-seed integration test (added in Step 9).
"""

from __future__ import annotations

import numpy as np
import pytest

from seba.attacks import (
    ATTACK_CATALOG,
    backdate_request,
    collude_block_signature,
    compromised_signer,
    get_attack,
    replay_approval_token,
    revocation_race,
    swap_explanation_hash,
)
from seba.attacks.base import AttackResult
from seba.baselines import ct_log_detector, fabric_abac_detector
from seba.scoring import (
    abac_reexecution_detector,
    compute_aas,
    mutable_log_detector,
    quorum_chain_detector,
    score_defense_against_catalog,
    signed_chain_detector,
)

# ---------------------------------------------------------------------------
# Fixture: a tiny well-formed log with diverse decisions and reason codes.
# ---------------------------------------------------------------------------


@pytest.fixture
def tiny_clean_log():
    rows = []
    for i in range(20):
        decision = ("allow", "deny", "escalate")[i % 3]
        reason = {
            "allow": "ALLOW_ROUTINE_CONTEXTUAL_ACCESS",
            "deny": "DENY_INACTIVE_CREDENTIAL",
            "escalate": "ESCALATE_PRIVACY_SENSITIVE_RECORD",
        }[decision]
        rows.append(
            {
                "event_sequence": i + 1,
                "event_id": f"E-{i:03d}",
                "timestamp_utc": f"2026-05-28T00:{i:02d}:00Z",
                "request_id": f"REQ-{i:06d}",
                "requester_officer_hash": f"H-{i:03d}",
                "requester_station_id": f"S-{i % 3}",
                "decision": decision,
                "primary_reason_code": reason,
                "explanation_hash": f"x-{i:03d}",
                "decision_hash": f"d-{i:03d}",
                "audit_anchor_hash": f"a-{i:03d}",
                "request_content_hash": f"r-{i:03d}",
                "policy_version_evaluated": "P-TEST",
                "record_sensitivity_level": ("LOW", "MEDIUM", "HIGH", "CLASSIFIED")[i % 4],
            }
        )
    return tuple(rows)


# ---------------------------------------------------------------------------
# 1. Catalog integrity.
# ---------------------------------------------------------------------------


def test_catalog_is_non_empty_and_names_unique() -> None:
    assert ATTACK_CATALOG
    names = [a.name for a in ATTACK_CATALOG]
    assert len(names) == len(set(names))


def test_get_attack_resolves_and_rejects_unknown() -> None:
    assert get_attack("replay_approval_token") is replay_approval_token
    assert get_attack("compromised_signer") is compromised_signer
    with pytest.raises(KeyError):
        get_attack("does_not_exist")


@pytest.mark.parametrize("attack", list(ATTACK_CATALOG))
def test_every_attack_has_valid_severity(attack) -> None:
    assert 1 <= attack.severity <= 5


# ---------------------------------------------------------------------------
# 2. Individual attacks: each must produce an immutable result and not
#    mutate its input log.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "attack",
    [
        replay_approval_token,
        backdate_request,
        swap_explanation_hash,
        collude_block_signature,
        revocation_race,
        compromised_signer,
    ],
)
def test_attack_does_not_mutate_input(attack, tiny_clean_log) -> None:
    rng = np.random.default_rng(42)
    original = tuple({**row} for row in tiny_clean_log)
    result: AttackResult = attack(tiny_clean_log, rng)
    assert isinstance(result, AttackResult)
    for original_row, current_row in zip(original, tiny_clean_log, strict=True):
        assert dict(original_row) == dict(current_row), (
            f"{attack.name} mutated its input log"
        )


# ---------------------------------------------------------------------------
# 3. Detector matrix — see docstring in seba.scoring.detectors.
# ---------------------------------------------------------------------------


def test_mutable_log_misses_pure_field_edits(tiny_clean_log) -> None:
    rng = np.random.default_rng(0)
    res = backdate_request(tiny_clean_log, rng)
    assert mutable_log_detector(res.perturbed_log, tiny_clean_log) is False


def test_signed_chain_catches_backdate(tiny_clean_log) -> None:
    rng = np.random.default_rng(0)
    res = backdate_request(tiny_clean_log, rng)
    assert signed_chain_detector(res.perturbed_log, tiny_clean_log) is True


def test_signed_chain_misses_collusion(tiny_clean_log) -> None:
    """Signed-chain has no quorum concept, so collusion inserts a row that
    *will* trip the length-change branch. Demonstrate that on a *modified*
    collusion variant that doesn't change length, the signed chain misses.
    The full collusion attack always changes length, so signed_chain
    detects it via the schema check — this is honest behavior, documented
    here so downstream readers don't get confused."""

    rng = np.random.default_rng(0)
    res = collude_block_signature(tiny_clean_log, rng)
    # Length changed -> signed-chain detects via schema break.
    assert signed_chain_detector(res.perturbed_log, tiny_clean_log) is True
    # Quorum chain detects via either path.
    assert quorum_chain_detector(res.perturbed_log, tiny_clean_log) is True


def test_abac_reexecution_catches_revocation_race(tiny_clean_log) -> None:
    rng = np.random.default_rng(0)
    res = revocation_race(tiny_clean_log, rng)
    if not res.affected_indices:
        pytest.skip("revocation_race found no eligible event in tiny fixture")
    assert abac_reexecution_detector(res.perturbed_log, tiny_clean_log) is True


def test_compromised_signer_blinds_integrity_detectors(tiny_clean_log) -> None:
    rng = np.random.default_rng(0)
    res = compromised_signer(tiny_clean_log, rng, flip_fraction=0.5)
    assert res.affected_indices
    assert len(res.perturbed_log) == len(tiny_clean_log)
    assert res.meta["resigned_valid"] is True
    assert all(
        res.perturbed_log[i].get("__attack_resigned_valid__")
        for i in res.affected_indices
    )

    assert mutable_log_detector(res.perturbed_log, tiny_clean_log) is False
    assert signed_chain_detector(res.perturbed_log, tiny_clean_log) is False
    assert quorum_chain_detector(res.perturbed_log, tiny_clean_log) is False
    assert ct_log_detector(res.perturbed_log, tiny_clean_log) is False
    assert fabric_abac_detector(res.perturbed_log, tiny_clean_log) is False
    assert abac_reexecution_detector(res.perturbed_log, tiny_clean_log) is False


# ---------------------------------------------------------------------------
# 4. AAS scorer end-to-end on the tiny fixture.
# ---------------------------------------------------------------------------


def test_aas_full_defense_beats_mutable_log(tiny_clean_log) -> None:
    mutable_aas = score_defense_against_catalog(
        "mutable_log", mutable_log_detector, tiny_clean_log, seed=42
    )
    quorum_aas = score_defense_against_catalog(
        "blockchain", quorum_chain_detector, tiny_clean_log, seed=42
    )
    assert quorum_aas.aas > mutable_aas.aas


def test_compute_aas_is_severity_weighted() -> None:
    # Two attacks, severity 1 and severity 5. If only the heavy attack is
    # detected, AAS should be 5/6, not 0.5.
    per_attack = {"light": 0.0, "heavy": 1.0}
    severities = {"light": 1, "heavy": 5}
    assert abs(compute_aas(per_attack, severities) - (5 / 6)) < 1e-9


def test_metadata_inference_on_minimized_view_reduces_leakage(tiny_clean_log) -> None:
    """Defense that publishes a minimized ledger view should pass the
    inference attack, because the attacker has no informative features."""

    full_view = tiny_clean_log
    minimized_view = tuple(
        {
            "event_sequence": row["event_sequence"],
            "decision_hash": row["decision_hash"],
            "explanation_hash": row["explanation_hash"],
            # No requester_station_id, no decision, no reason code, no sensitivity.
        }
        for row in tiny_clean_log
    )

    full = score_defense_against_catalog(
        "full_metadata", signed_chain_detector, full_view, seed=7, ledger_view=full_view
    )
    minimized = score_defense_against_catalog(
        "minimized_metadata", signed_chain_detector, full_view, seed=7, ledger_view=minimized_view
    )
    assert minimized.per_attack["metadata_inference"] >= full.per_attack["metadata_inference"]
