#!/usr/bin/env bash
#
# Shared org metadata + peer CLI environment helpers.
# Source this from scripts that run with PWD = crime-records-network/network.

# org : msp id : CA port : peer port
ORGS=(
  "police:PoliceMSP:7054:7051"
  "forensics:ForensicsMSP:8054:8051"
  "prosecution:ProsecutionMSP:9054:9051"
  "court:CourtMSP:10054:10051"
  "audit:AuditMSP:11054:11051"
)

ORDERER_CA_PORT=12054

org_field() { # org_field <entry> <index>
  echo "$1" | cut -d: -f"$2"
}

# Point the peer CLI at a given org's peer, acting as that org's admin.
# Usage: setGlobals police
setGlobals() {
  local org="$1"
  local entry msp port
  for e in "${ORGS[@]}"; do
    if [ "$(org_field "$e" 1)" = "$org" ]; then entry="$e"; fi
  done
  [ -n "${entry:-}" ] || { echo "unknown org: $org" >&2; return 1; }
  msp="$(org_field "$entry" 2)"
  port="$(org_field "$entry" 4)"

  export CORE_PEER_TLS_ENABLED=true
  export CORE_PEER_LOCALMSPID="$msp"
  export CORE_PEER_TLS_ROOTCERT_FILE="${PWD}/organizations/peerOrganizations/${org}.example.com/tlsca/tlsca.${org}.example.com-cert.pem"
  export CORE_PEER_MSPCONFIGPATH="${PWD}/organizations/peerOrganizations/${org}.example.com/users/Admin@${org}.example.com/msp"
  export CORE_PEER_ADDRESS="localhost:${port}"
}
