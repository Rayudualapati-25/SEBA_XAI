#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/_project_docker_config.sh"

if [[ -f "$PROJECT_DIR/config/fabric_paths.env" ]]; then
  # shellcheck disable=SC1091
  source "$PROJECT_DIR/config/fabric_paths.env"
fi

FABRIC_SAMPLES_DIR="${FABRIC_SAMPLES_DIR:-$PROJECT_DIR/.local/fabric-samples}"
TEST_NETWORK_DIR="$FABRIC_SAMPLES_DIR/test-network"

if [[ ! -d "$TEST_NETWORK_DIR" ]]; then
  echo "Fabric test network not found: $TEST_NETWORK_DIR"
  exit 0
fi

pushd "$TEST_NETWORK_DIR" >/dev/null
./network.sh down
popd >/dev/null

echo "Stopped Fabric test network."
