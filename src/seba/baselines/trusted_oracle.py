"""Independent raw-attribute policy-oracle baseline.

This baseline models the strongest reviewer objection to the NS-PI result:
an auditor might have a separate trusted view of the original request
attributes and can re-evaluate or compare the expected policy output
outside the compromised signer path.

It is intentionally stronger than the audit-only ABAC proxy in
``seba.scoring.detectors``. That proxy evaluates the canonical policy output
stored in the log. This baseline compares every perturbed audit event against
trusted request-level labels loaded from ``labeled_access_requests.csv``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from seba.attacks.base import EventLog


@dataclass(frozen=True, slots=True)
class TrustedPolicyDecision:
    """Expected policy output for one raw access request."""

    request_id: str
    timestamp_utc: str
    decision: str
    primary_reason_code: str
    request_content_hash: str


@dataclass(frozen=True, slots=True)
class TrustedRawPolicyOracle:
    """Trusted external oracle keyed by request id."""

    expected_by_request_id: Mapping[str, TrustedPolicyDecision]

    @classmethod
    def from_records(cls, records: Iterable[Mapping[str, Any]]) -> TrustedRawPolicyOracle:
        expected: dict[str, TrustedPolicyDecision] = {}
        for row in records:
            request_id = str(row.get("request_id", ""))
            if not request_id:
                continue
            expected[request_id] = TrustedPolicyDecision(
                request_id=request_id,
                timestamp_utc=str(row.get("timestamp_utc", "")),
                decision=str(row.get("decision", "")),
                primary_reason_code=str(row.get("primary_reason_code", "")),
                request_content_hash=str(row.get("request_content_hash", "")),
            )
        return cls(expected_by_request_id=expected)

    def detect(self, perturbed_log: EventLog, clean_log: EventLog) -> bool:
        """Return True when the perturbed event log disagrees with the oracle."""

        if len(perturbed_log) != len(clean_log):
            return True

        seen: set[str] = set()
        for row in perturbed_log:
            request_id = str(row.get("request_id", ""))
            if not request_id or request_id in seen:
                return True
            seen.add(request_id)

            expected = self.expected_by_request_id.get(request_id)
            if expected is None or _row_disagrees_with_expected(row, expected):
                return True

        return seen != set(self.expected_by_request_id)


def _row_disagrees_with_expected(
    row: Mapping[str, Any], expected: TrustedPolicyDecision
) -> bool:
    return (
        str(row.get("timestamp_utc", "")) != expected.timestamp_utc
        or str(row.get("decision", "")) != expected.decision
        or str(row.get("primary_reason_code", "")) != expected.primary_reason_code
        or str(row.get("request_content_hash", "")) != expected.request_content_hash
    )
