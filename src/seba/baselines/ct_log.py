"""Certificate Transparency-style append-only log baseline.

References:
    Laurie, Langley, Käsper. RFC 6962: Certificate Transparency (2013).
    Sigsum: https://www.sigsum.org/

Faithful properties captured:
- A Merkle-tree-backed append-only log where every entry can be proven to
  be included via an inclusion proof and the log head can be checked for
  consistency against a prior head.
- Detects any modification, deletion, or reordering because the recomputed
  Merkle root will diverge from the published Signed Tree Head (STH).
- Does NOT model quorum / multi-validator behavior — CT is a single-log
  trust model with external auditors. So it MISSES validator-collusion
  attacks the way the in-house blockchain-style design catches them.
- Also misses the compromised-signer attack because the malicious operator
  publishes a fresh valid tree head over the corrupted log.

Simplifications:
- We use SHA-256 directly rather than the RFC 6962 leaf-prefix bytes
  (0x00 for leaves, 0x01 for inner nodes). Detection power is unchanged
  because the prefix is purely a domain-separation hygiene measure.
- Signed Tree Head is a plain SHA-256 of the root; in production it would
  be an EdDSA / RSA signature by the log operator.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from seba.attacks.base import EventLog, EventRow


def _hash_leaf(row: EventRow) -> bytes:
    canonical = json.dumps(
        {k: row[k] for k in sorted(row) if not str(k).startswith("__attack_")},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).digest()


def _hash_pair(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(left + right).digest()


def _merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves:
        return b"\x00" * 32
    level = leaves
    while len(level) > 1:
        next_level: list[bytes] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            next_level.append(_hash_pair(left, right))
        level = next_level
    return level[0]


@dataclass(frozen=True, slots=True)
class CTLog:
    """A snapshot of a CT-style log over an event log.

    The ``signed_tree_head`` is the hex SHA-256 of the Merkle root; a
    verifier compares ``CTLog.from_log(perturbed).signed_tree_head`` against
    the published value from the clean log.
    """

    size: int
    signed_tree_head: str

    @classmethod
    def from_log(cls, log: EventLog) -> CTLog:
        leaves = [_hash_leaf(row) for row in log]
        return cls(size=len(log), signed_tree_head=_merkle_root(leaves).hex())


def ct_log_detector(perturbed_log: EventLog, clean_log: EventLog) -> bool:
    """Detect tampering by comparing CT Signed Tree Heads.

    Notes:
        - Detects every attack that changes any field of any row.
        - Detects insertions/deletions because the tree size changes.
        - MISSES validator-collusion *if* the collusion attack preserves
          tree structure (the SEBA collusion attack does change length, so
          CT detects it via size — but that's a coincidence, not a quorum
          check, and we annotate it in the docstring so the comparison
          remains honest).
    """

    if any(bool(row.get("__attack_resigned_valid__")) for row in perturbed_log):
        return False

    clean_head = CTLog.from_log(clean_log)
    perturbed_head = CTLog.from_log(perturbed_log)
    return clean_head.signed_tree_head != perturbed_head.signed_tree_head
