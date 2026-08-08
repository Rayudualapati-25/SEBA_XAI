#!/usr/bin/env bash
#
# Package, install (5 peers), approve (5 orgs), and commit the crimerecords
# chaincode with the evidenceDetails private data collection.
# Run with PWD = crime-records-network/network, network + channel up.
#
# Usage: deployCC.sh [channel] [cc-name] [version] [sequence]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=orgs.sh
source "${SCRIPT_DIR}/orgs.sh"

CHANNEL_NAME="${1:-crimechannel}"
CC_NAME="${2:-crimerecords}"
CC_VERSION="${3:-1.0}"
CC_SEQUENCE="${4:-1}"

PROJECT_DIR="$(cd "${PWD}/.." && pwd)"
CC_SRC="${PROJECT_DIR}/chaincode/crimerecords"
COLLECTIONS_CONFIG="${PROJECT_DIR}/chaincode/collections-config.json"
ORDERER_CA="${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt"

export FABRIC_CFG_PATH="${PWD}/../../fabric-samples/config"

infoln() { printf '\033[0;34m%s\033[0m\n' "$1"; }

# --- package (from a staging copy without node_modules/coverage) ------------
STAGING="$(mktemp -d)"
trap 'rm -rf "${STAGING}"' EXIT
rsync -a --exclude node_modules --exclude coverage --exclude test \
  "${CC_SRC}/" "${STAGING}/src/"

PKG="${PWD}/channel-artifacts/${CC_NAME}_${CC_VERSION}.tar.gz"
infoln "Packaging ${CC_NAME} ${CC_VERSION}"
peer lifecycle chaincode package "$PKG" \
  --path "${STAGING}/src" --lang node --label "${CC_NAME}_${CC_VERSION}"

# --- install on every department peer ---------------------------------------
for entry in "${ORGS[@]}"; do
  org="$(org_field "$entry" 1)"
  setGlobals "$org"
  if peer lifecycle chaincode queryinstalled 2>/dev/null | grep -q "${CC_NAME}_${CC_VERSION}"; then
    infoln "install: already present on peer0.${org}"
  else
    infoln "install: peer0.${org}"
    peer lifecycle chaincode install "$PKG"
  fi
done

setGlobals police
PACKAGE_ID="$(peer lifecycle chaincode calculatepackageid "$PKG")"
infoln "Package ID: ${PACKAGE_ID}"

# --- approve for all 5 orgs --------------------------------------------------
for entry in "${ORGS[@]}"; do
  org="$(org_field "$entry" 1)"
  setGlobals "$org"
  infoln "approve: ${org}"
  peer lifecycle chaincode approveformyorg \
    -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com \
    --tls --cafile "$ORDERER_CA" \
    --channelID "$CHANNEL_NAME" --name "$CC_NAME" \
    --version "$CC_VERSION" --sequence "$CC_SEQUENCE" \
    --package-id "$PACKAGE_ID" \
    --collections-config "$COLLECTIONS_CONFIG"
done

# --- commit ------------------------------------------------------------------
infoln "Checking commit readiness"
setGlobals police
peer lifecycle chaincode checkcommitreadiness \
  --channelID "$CHANNEL_NAME" --name "$CC_NAME" \
  --version "$CC_VERSION" --sequence "$CC_SEQUENCE" \
  --collections-config "$COLLECTIONS_CONFIG" --output json

PEER_CONN_ARGS=()
for entry in "${ORGS[@]}"; do
  org="$(org_field "$entry" 1)"
  port="$(org_field "$entry" 4)"
  PEER_CONN_ARGS+=(--peerAddresses "localhost:${port}" --tlsRootCertFiles \
    "${PWD}/organizations/peerOrganizations/${org}.example.com/tlsca/tlsca.${org}.example.com-cert.pem")
done

infoln "Committing chaincode definition"
peer lifecycle chaincode commit \
  -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com \
  --tls --cafile "$ORDERER_CA" \
  --channelID "$CHANNEL_NAME" --name "$CC_NAME" \
  --version "$CC_VERSION" --sequence "$CC_SEQUENCE" \
  --collections-config "$COLLECTIONS_CONFIG" \
  "${PEER_CONN_ARGS[@]}"

infoln "Committed definition:"
peer lifecycle chaincode querycommitted --channelID "$CHANNEL_NAME" --name "$CC_NAME"
