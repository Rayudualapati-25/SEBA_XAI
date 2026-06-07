"""Compromised-signer attack: corrupt decisions and re-sign a valid log.

This attack models the case that ordinary hash-chain checks are least able
to handle: an attacker controls the audit signer or enforcement signer, flips
a meaningful fraction of non-allow decisions to ``allow``, and emits a
freshly signed canonical log. The row hashes and signatures are therefore
treated as valid by integrity-only defenses.

Detection criteria:
- Mutable logs do not detect because the log shape is unchanged.
- Signed-chain, CT-log, and permissioned blockchain-style integrity checks
  do not detect because the corrupted log is re-signed as valid.
- Fabric/ABAC-style checks over the same compromised canonical output do
  not detect; an independent policy oracle over raw request attributes would
  be a stronger external defense and should be evaluated separately.
- NS-PI drift can detect this if the corrupted decisions shift the observed
  policy distribution enough.
"""

from __future__ import annotations

from typing import Any

from seba.attacks.base import AttackResult, EventLog, copy_log, to_log

NAME = "compromised_signer"
SEVERITY = 5


def compromised_signer(
    log: EventLog,
    rng: Any,
    *,
    flip_fraction: float = 0.25,
) -> AttackResult:
    """Flip a fraction of deny/escalate events to allow and mark them re-signed."""

    if not log:
        return AttackResult(NAME, SEVERITY, log, affected_indices=())

    rows = copy_log(log)
    candidates = [
        i
        for i, row in enumerate(rows)
        if str(row.get("decision", "")).lower() in {"deny", "escalate"}
    ]
    if not candidates:
        return AttackResult(NAME, SEVERITY, to_log(rows), affected_indices=())

    n_flip = max(1, int(len(candidates) * flip_fraction))
    chosen = rng.choice(candidates, size=n_flip, replace=False)
    affected: list[int] = []

    for raw_idx in chosen:
        idx = int(raw_idx)
        old_decision = rows[idx].get("decision")
        old_reason = rows[idx].get("primary_reason_code")
        rows[idx]["decision"] = "allow"
        rows[idx]["primary_reason_code"] = "ALLOW_COMPROMISED_SIGNER_OVERRIDE"
        rows[idx]["__attack_compromised_signer__"] = True
        rows[idx]["__attack_resigned_valid__"] = True
        rows[idx]["__attack_policy_output_compromised__"] = True
        rows[idx]["__attack_original_decision__"] = old_decision
        rows[idx]["__attack_original_reason_code__"] = old_reason
        affected.append(idx)

    return AttackResult(
        name=NAME,
        severity=SEVERITY,
        perturbed_log=to_log(rows),
        affected_indices=tuple(sorted(affected)),
        meta={
            "n_flipped": len(affected),
            "flip_fraction": flip_fraction,
            "resigned_valid": True,
            "policy_output_compromised": True,
        },
    )


compromised_signer.name = NAME  # type: ignore[attr-defined]
compromised_signer.severity = SEVERITY  # type: ignore[attr-defined]
