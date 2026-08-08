#!/usr/bin/env bash
#
# One-command bring-up of the Fabric test network with seba-audit-chaincode.
#
# Tears down any existing network, starts orderer + 2 peers + 3 CAs,
# creates a channel, deploys the chaincode, and runs the smoke test.
#
# Usage:  ./bootstrap-network.sh [channel-name] [chaincode-name]

set -euo pipefail

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_NETWORK_HOME="${WORKSPACE}/fabric-samples/test-network"
CHAINCODE_PATH="${WORKSPACE}/seba-audit-chaincode"

CHANNEL_NAME="${1:-mychannel}"
CC_NAME="${2:-sebaaudit}"

export PATH="${WORKSPACE}/fabric-samples/bin:${PATH}"
export FABRIC_CFG_PATH="${WORKSPACE}/fabric-samples/config"

info() { printf '\n\033[0;34m==> %s\033[0m\n' "$1"; }
die()  { printf '\033[0;31mERROR: %s\033[0m\n' "$1" >&2; exit 1; }

# --- preflight -------------------------------------------------------------
info "Preflight checks"

command -v docker >/dev/null 2>&1 || die "docker not found on PATH"
command -v jq     >/dev/null 2>&1 || die "jq not found on PATH"
command -v peer   >/dev/null 2>&1 || die "peer binary not found (expected in fabric-samples/bin)"

if ! docker info >/dev/null 2>&1; then
  die "Docker daemon is not reachable. If you use Colima: colima start"
fi

[ -d "${TEST_NETWORK_HOME}" ] || die "test network not found at ${TEST_NETWORK_HOME}"
[ -d "${CHAINCODE_PATH}" ]    || die "chaincode not found at ${CHAINCODE_PATH}"

# You may have more than one Docker runtime (Docker Desktop and Colima each run
# their own VM, with their own images). Find whichever one holds the Fabric
# images and use it for this run, so it doesn't matter which is "active".
find_fabric_context() {
  if docker image inspect hyperledger/fabric-nodeenv:2.5 >/dev/null 2>&1; then
    return 0   # current context already has it
  fi
  local ctx
  for ctx in $(docker context ls --format '{{.Name}}' 2>/dev/null); do
    if docker --context "${ctx}" image inspect hyperledger/fabric-nodeenv:2.5 >/dev/null 2>&1; then
      export DOCKER_CONTEXT="${ctx}"
      printf 'note:       switched to Docker context "%s" (it has the Fabric images)\n' "${ctx}"
      return 0
    fi
  done
  return 1
}

if ! find_fabric_context; then
  die "no Docker runtime has the Fabric images.
       Pull them with: docker pull hyperledger/fabric-nodeenv:2.5
       (and the other hyperledger/fabric-* images)"
fi

printf 'docker:     %s\n' "$(docker --version)"
printf 'peer:       %s\n' "$(peer version | sed -ne 's/^ Version: //p')"
printf 'context:    %s\n' "$(docker context show)"

cd "${TEST_NETWORK_HOME}"

# --- bring up --------------------------------------------------------------
info "Tearing down any existing network"
./network.sh down >/dev/null 2>&1 || true

# Keep full output in a log rather than discarding it, so a failure is
# diagnosable without having to re-run the whole bring-up by hand.
LOG_DIR="${WORKSPACE}/.bootstrap-logs"
mkdir -p "${LOG_DIR}"
UP_LOG="${LOG_DIR}/network-up.log"
CC_LOG="${LOG_DIR}/deploy-cc.log"

info "Starting network and creating channel '${CHANNEL_NAME}'"
./network.sh up createChannel -c "${CHANNEL_NAME}" -ca >"${UP_LOG}" 2>&1 \
  || die "network bring-up failed — see ${UP_LOG}"

info "Deploying chaincode '${CC_NAME}' (javascript)"
./network.sh deployCC \
  -ccn "${CC_NAME}" \
  -ccp "${CHAINCODE_PATH}" \
  -ccl javascript \
  -c "${CHANNEL_NAME}" >"${CC_LOG}" 2>&1 \
  || die "chaincode deployment failed — see ${CC_LOG}"

# --- verify ----------------------------------------------------------------
info "Running containers"
docker ps --format '  {{.Names}}\t{{.Status}}'

info "Committed chaincode definition"
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID=Org1MSP
export CORE_PEER_TLS_ROOTCERT_FILE="${TEST_NETWORK_HOME}/organizations/peerOrganizations/org1.example.com/tlsca/tlsca.org1.example.com-cert.pem"
export CORE_PEER_MSPCONFIGPATH="${TEST_NETWORK_HOME}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
export CORE_PEER_ADDRESS=localhost:7051
# Informational only — nothing is asserted on this output, so a transient
# non-zero exit here must not abort the bootstrap via pipefail.
peer lifecycle chaincode querycommitted -C "${CHANNEL_NAME}" -n "${CC_NAME}" 2>&1 | sed 's/^/  /' || true

info "Smoke test"
"${WORKSPACE}/smoke-test-seba-chaincode.sh" "${CHANNEL_NAME}" "${CC_NAME}"

info "Network is UP and ready"
printf 'Channel:   %s\nChaincode: %s\nTear down: cd %s && ./network.sh down\n' \
  "${CHANNEL_NAME}" "${CC_NAME}" "${TEST_NETWORK_HOME}"
