#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EVENT_PREP_RUN_ID="${FABRIC_EVENT_PREP_RUN_ID:-20260710_fabric_audit_event_prep}"
SUBMIT_RUN_ID="${FABRIC_SUBMIT_RUN_ID:-20260710_fabric_submit}"

if [[ -f "$PROJECT_DIR/config/fabric_paths.env" ]]; then
  # shellcheck disable=SC1091
  source "$PROJECT_DIR/config/fabric_paths.env"
fi

cd "$PROJECT_DIR/client"
npm install

node submit_audit_events.js \
  --input "$PROJECT_DIR/runs/$EVENT_PREP_RUN_ID/artifacts/fabric_audit_events.jsonl" \
  --output "$PROJECT_DIR/runs/$SUBMIT_RUN_ID/artifacts/fabric_submit_results.json" \
  --limit "${SUBMIT_LIMIT:-25}"
