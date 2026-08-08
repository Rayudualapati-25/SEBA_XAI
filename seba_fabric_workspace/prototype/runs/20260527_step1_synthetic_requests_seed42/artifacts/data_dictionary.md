# Synthetic Access Request Data Dictionary

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
