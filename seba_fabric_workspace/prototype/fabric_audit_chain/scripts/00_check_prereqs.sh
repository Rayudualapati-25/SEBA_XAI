#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/_project_docker_config.sh"

missing=0

check_cmd() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "MISSING: $name"
    missing=1
  else
    echo "OK: $name -> $($name --version 2>/dev/null | head -n 1 || true)"
  fi
}

check_cmd docker
check_cmd node
check_cmd npm
check_cmd python3
check_cmd curl

if ! docker compose version >/dev/null 2>&1; then
  echo "MISSING: docker compose"
  missing=1
else
  echo "OK: docker compose -> $(docker compose version 2>/dev/null | head -n 1)"
fi

if [[ "$missing" -ne 0 ]]; then
  echo
  echo "Install missing prerequisites before running Hyperledger Fabric."
  echo "Docker Desktop is required for the Fabric test network."
  exit 1
fi

echo
echo "All required commands are available."
echo "Docker config used for Fabric: $DOCKER_CONFIG"
