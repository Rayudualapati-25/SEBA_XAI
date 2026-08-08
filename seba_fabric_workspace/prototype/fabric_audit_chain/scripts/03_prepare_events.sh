#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"
RUN_ID="${FABRIC_EVENT_PREP_RUN_ID:-20260710_fabric_audit_event_prep}"
RUN_DIR="$PROJECT_DIR/runs/$RUN_ID"

python3 "$PROJECT_DIR/tools/build_audit_events.py" \
  --input "$REPO_ROOT/prototype/runs/20260527_step2_policy_oracle_seed42/artifacts/labeled_access_requests.csv" \
  --run-dir "$RUN_DIR" \
  --limit 25

python3 "$PROJECT_DIR/tools/validate_audit_events.py" \
  --input "$RUN_DIR/artifacts/fabric_audit_events.jsonl" \
  --output "$RUN_DIR/artifacts/validation_report.json"
