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
CHANNEL_NAME="${CHANNEL_NAME:-seba}"
CHAINCODE_NAME="${CHAINCODE_NAME:-seba-audit}"
FABRIC_RUNTIME_DIR="${FABRIC_RUNTIME_DIR:-/Users/venkatrayudu/Workspace/Research/seba_fabric_workspace}"
TEST_NETWORK_DIR="$FABRIC_SAMPLES_DIR/test-network"
CHAINCODE_STAGE_DIR="$FABRIC_RUNTIME_DIR/seba-audit-chaincode"
CHAINCODE_PATH="$CHAINCODE_STAGE_DIR"

if [[ ! -d "$TEST_NETWORK_DIR" ]]; then
  echo "Fabric test network not found: $TEST_NETWORK_DIR"
  echo "Run scripts/01_bootstrap_fabric.sh first."
  exit 1
fi

rm -rf "$CHAINCODE_STAGE_DIR"
mkdir -p "$CHAINCODE_STAGE_DIR"
cp -R "$PROJECT_DIR/chaincode/javascript/." "$CHAINCODE_STAGE_DIR/"

pushd "$TEST_NETWORK_DIR" >/dev/null
./network.sh down
./network.sh up createChannel -c "$CHANNEL_NAME" -ca
./network.sh deployCC -c "$CHANNEL_NAME" -ccn "$CHAINCODE_NAME" -ccp "$CHAINCODE_PATH" -ccl javascript
popd >/dev/null

echo "Started Fabric channel=$CHANNEL_NAME chaincode=$CHAINCODE_NAME"
echo "Docker config used for Fabric: $DOCKER_CONFIG"
