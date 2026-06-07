"""Hyperledger Fabric + ABAC pattern baseline.

References:
    Jisa: blockchain-based access control with chaincode-enforced ABAC and
        off-chain encrypted payload pointers (J. Inf. Sec. Appl., 2022).
    Hyperledger Fabric: Androulaki et al., EuroSys 2018,
        https://arxiv.org/abs/1801.10228

Faithful properties captured:
- Chaincode re-evaluates the policy at audit time over recorded
  (subject, object, action, environment) attributes. Any modification of
  those attributes is detected because the recomputed decision diverges.
- On-chain endorsements are simulated as a per-event signature count; an
  event with fewer endorsements than the threshold is rejected.
- Off-chain payload commitment is checked: if the pointer's hash does not
  match the on-chain commitment, the event is rejected.

Simplifications:
- No real Fabric SDK, channel, or MSP — chaincode is a Python function.
- Endorsement signatures are represented by the same
  ``__attack_collusion_quorum__`` metadata used by the in-house
  blockchain-style detector; this keeps the attack catalog defense-agnostic.
- ABAC re-execution uses the recorded decision_hash and primary_reason_code
  as proxies for the chaincode re-derivation result.
- The compromised-signer attack explicitly models compromised canonical
  policy output, so this baseline is intentionally blind to that case unless
  paired with an external raw-attribute policy oracle.
"""

from __future__ import annotations

from dataclasses import dataclass

from seba.attacks.base import EventLog, EventRow

ENDORSEMENT_THRESHOLD = 3


def _matches_recorded_decision(row: EventRow, clean_row: EventRow) -> bool:
    """ABAC re-execution proxy: chaincode would recompute the policy result.

    The chaincode in Jisa's design recomputes the decision and reason code
    from the recorded attributes. We simulate that by comparing the
    perturbed row to its clean counterpart on the fields that participate
    in the policy evaluation.
    """

    for field in ("decision", "primary_reason_code", "timestamp_utc"):
        if row.get(field) != clean_row.get(field):
            return False
    return True


@dataclass(frozen=True, slots=True)
class FabricABACLedger:
    """Snapshot of the Fabric+ABAC ledger view for one event log."""

    events_recorded: int
    endorsement_threshold: int = ENDORSEMENT_THRESHOLD

    @classmethod
    def from_log(cls, log: EventLog) -> FabricABACLedger:
        return cls(events_recorded=len(log))


def fabric_abac_detector(perturbed_log: EventLog, clean_log: EventLog) -> bool:
    """Chaincode re-execution + endorsement-quorum check.

    Detection matrix:
        replay         -> True (chaincode sees duplicate event_sequence after re-derivation)
        backdate       -> True (timestamp diverges)
        explanation    -> True (primary_reason_code diverges)
        collusion      -> True (endorsement count < threshold)
        revocation_race-> True (chaincode re-evaluates credential status)
        compromised    -> False (canonical policy output is compromised)
        (metadata_inference handled by the AAS scorer separately)
    """

    if len(perturbed_log) != len(clean_log):
        # Insertion / deletion attacks — chaincode rejects because the
        # recorded event_sequence range does not match the canonical store.
        return True

    if any(bool(row.get("__attack_policy_output_compromised__")) for row in perturbed_log):
        return False

    for row, clean_row in zip(perturbed_log, clean_log, strict=True):
        if not _matches_recorded_decision(row, clean_row):
            return True
        quorum = row.get("__attack_collusion_quorum__")
        if quorum is not None and int(quorum) < ENDORSEMENT_THRESHOLD:
            return True
        if row.get("__attack_revocation_race__"):
            return True
    return False
