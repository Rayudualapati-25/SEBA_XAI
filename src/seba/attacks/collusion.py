"""Validator-collusion attack: fabricate a block signed by a sub-quorum.

In a permissioned PoA setting with a k-of-n quorum threshold, an attacker
who controls k-1 validators cannot mint a valid block on their own. This
attack simulates a partial-collusion scenario: the attacker signs a
fabricated block with only (k-1) of the n validators and tries to splice
it into the chain. A correctly implemented quorum check rejects.

Detection criteria:
- Quorum-checking defenses detect because signature count < threshold.
- Hash-chain defenses detect because the fabricated block's
  ``previous_block_hash`` does not match the prior block.
- Mutable / signed-log defenses (no quorum concept) do NOT detect.

This attack is encoded as a perturbation of the *event log* (not the block
list) so it composes with the other attacks. The defense evaluator notices
it by re-deriving blocks and detecting a missing/insufficient quorum.
"""

from __future__ import annotations

from typing import Any

from seba.attacks.base import AttackResult, EventLog, copy_log, to_log

NAME = "collude_block_signature"
SEVERITY = 5


def collude_block_signature(log: EventLog, rng: Any) -> AttackResult:
    if len(log) < 4:
        return AttackResult(NAME, SEVERITY, log, affected_indices=())

    rows = copy_log(log)
    # Insert a fabricated event marked as "sub-quorum signed". The defense
    # evaluator (seba.scoring.evaluate_blockchain_defense) reads the
    # __attack_collusion_quorum__ field if present and fails verification.
    insert_at = int(rng.integers(len(rows) // 4, len(rows)))
    template = dict(rows[insert_at])
    template["event_id"] = template.get("event_id", "") + "-COLLUSION"
    template["decision"] = "allow"  # fabricated allow event
    template["primary_reason_code"] = "FABRICATED_BY_COLLUSION"
    template["__attack_collusion_quorum__"] = 2  # below the 3-of-4 threshold
    rows.insert(insert_at, template)
    for i, r in enumerate(rows):
        r["event_sequence"] = i + 1

    return AttackResult(
        name=NAME,
        severity=SEVERITY,
        perturbed_log=to_log(rows),
        affected_indices=(insert_at,),
        meta={"insert_index": insert_at, "signatures_collected": 2, "quorum_threshold": 3},
    )


collude_block_signature.name = NAME  # type: ignore[attr-defined]
collude_block_signature.severity = SEVERITY  # type: ignore[attr-defined]
