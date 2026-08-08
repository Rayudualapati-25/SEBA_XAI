#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
if [[ -f "$PROJECT_DIR/config/fabric_paths.env" ]]; then
  # shellcheck disable=SC1091
  source "$PROJECT_DIR/config/fabric_paths.env"
fi
# shellcheck disable=SC1091
source "$SCRIPT_DIR/_project_docker_config.sh"
LOCAL_DIR="${FABRIC_RUNTIME_DIR:-/Users/venkatrayudu/Workspace/Research/seba_fabric_workspace}"
FABRIC_SAMPLES_DIR="${FABRIC_SAMPLES_DIR:-$LOCAL_DIR/fabric-samples}"

mkdir -p "$LOCAL_DIR"

cd "$LOCAL_DIR"
echo "Downloading Hyperledger Fabric samples, Docker images, and binaries..."
if [[ ! -f install-fabric.sh ]]; then
  curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh
fi
chmod +x install-fabric.sh
if [[ -d "$FABRIC_SAMPLES_DIR/test-network" ]]; then
  echo "Fabric samples already present: $FABRIC_SAMPLES_DIR"
  ./install-fabric.sh docker binary
else
  ./install-fabric.sh docker samples binary
fi

echo "Fabric samples installed under: $FABRIC_SAMPLES_DIR"
echo "Docker config used for Fabric: $DOCKER_CONFIG"
