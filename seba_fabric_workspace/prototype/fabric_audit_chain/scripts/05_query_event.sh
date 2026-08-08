#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <requestIdHash>"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ -f "$PROJECT_DIR/config/fabric_paths.env" ]]; then
  # shellcheck disable=SC1091
  source "$PROJECT_DIR/config/fabric_paths.env"
fi

cd "$PROJECT_DIR/client"
node query_audit_event.js "$1"
