#!/usr/bin/env bash
#
# Register + enroll demo department users with ABAC attributes baked into
# their X.509 certificates (":ecert" = included in the enrollment cert).
# Run with PWD = crime-records-network/network, CAs up, MSP material present.
#
# caseAssignments uses '|' as separator because ',' separates attributes.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=orgs.sh
source "${SCRIPT_DIR}/orgs.sh"

infoln() { printf '\033[0;34m%s\033[0m\n' "$1"; }

# org|username|attrs
USERS=(
  "police|insp.sharma|role=inspector:ecert,rank=3:ecert,station=PS-Central:ecert,jurisdiction=district-north:ecert,badgeId=B-1001:ecert,clearance=high:ecert,credentialStatus=active:ecert,caseAssignments=CASE-2026-001|CASE-2026-002:ecert"
  "police|const.verma|role=constable:ecert,rank=1:ecert,station=PS-Central:ecert,jurisdiction=district-north:ecert,badgeId=B-2002:ecert,clearance=low:ecert,credentialStatus=active:ecert,caseAssignments=CASE-2026-001:ecert"
  "police|sho.reddy|role=sho:ecert,rank=4:ecert,station=PS-Central:ecert,jurisdiction=district-north:ecert,badgeId=B-0100:ecert,clearance=high:ecert,credentialStatus=active:ecert"
  "police|io.krishnan|role=investigating-officer:ecert,rank=3:ecert,station=PS-Central:ecert,jurisdiction=district-north:ecert,badgeId=B-3003:ecert,clearance=high:ecert,credentialStatus=active:ecert,caseAssignments=CASE-2026-001:ecert"
  "police|insp.rathore|role=inspector:ecert,rank=3:ecert,station=PS-East:ecert,jurisdiction=district-north:ecert,badgeId=B-4004:ecert,clearance=high:ecert,credentialStatus=revoked:ecert,caseAssignments=CASE-2026-001:ecert"
  "forensics|analyst.rao|role=lab-analyst:ecert,station=FSL-North:ecert,jurisdiction=district-north:ecert,badgeId=F-3001:ecert,clearance=medium:ecert,credentialStatus=active:ecert,caseAssignments=CASE-2026-001:ecert"
  "forensics|dir.iyer|role=lab-director:ecert,station=FSL-North:ecert,jurisdiction=district-north:ecert,badgeId=F-0001:ecert,clearance=high:ecert,credentialStatus=active:ecert"
  "prosecution|pp.mehta|role=public-prosecutor:ecert,jurisdiction=district-north:ecert,badgeId=P-5001:ecert,clearance=high:ecert,credentialStatus=active:ecert"
  "prosecution|dc.nair|role=defense-counsel:ecert,jurisdiction=district-north:ecert,badgeId=P-6001:ecert,clearance=low:ecert,credentialStatus=active:ecert"
  "court|judge.rana|role=judge:ecert,jurisdiction=district-north:ecert,badgeId=C-7001:ecert,clearance=high:ecert,credentialStatus=active:ecert"
  "court|clerk.das|role=court-clerk:ecert,jurisdiction=district-north:ecert,badgeId=C-8001:ecert,clearance=low:ecert,credentialStatus=active:ecert"
  "audit|aud.qureshi|role=auditor:ecert,jurisdiction=district-north:ecert,badgeId=A-9001:ecert,clearance=high:ecert,credentialStatus=active:ecert"
  "audit|omb.pillai|role=ombudsman:ecert,jurisdiction=district-north:ecert,badgeId=A-9101:ecert,clearance=high:ecert,credentialStatus=active:ecert"
)

ca_port_for() {
  for e in "${ORGS[@]}"; do
    if [ "$(org_field "$e" 1)" = "$1" ]; then org_field "$e" 3; return; fi
  done
  echo "unknown org $1" >&2; exit 1
}

for spec in "${USERS[@]}"; do
  org="${spec%%|*}"
  rest="${spec#*|}"
  user="${rest%%|*}"
  attrs="${rest#*|}"
  domain="${org}.example.com"
  ca_port="$(ca_port_for "$org")"
  ca_cert="${PWD}/organizations/fabric-ca/${org}/ca-cert.pem"
  org_dir="${PWD}/organizations/peerOrganizations/${domain}"
  user_msp="${org_dir}/users/${user}@${domain}/msp"
  secret="${user}pw"

  export FABRIC_CA_CLIENT_HOME="$org_dir"

  if [ -d "$user_msp" ]; then
    infoln "skip ${org}/${user}: already enrolled"
    continue
  fi

  infoln "register ${org}/${user}"
  fabric-ca-client register --caname "ca-${org}" \
    --id.name "$user" --id.secret "$secret" --id.type client \
    --id.attrs "$attrs" \
    --tls.certfiles "$ca_cert"

  infoln "enroll ${org}/${user}"
  fabric-ca-client enroll \
    -u "https://${user}:${secret}@localhost:${ca_port}" \
    --caname "ca-${org}" -M "$user_msp" --tls.certfiles "$ca_cert"
  cp "${org_dir}/msp/config.yaml" "${user_msp}/config.yaml"
done

infoln "Seeded ${#USERS[@]} department users."
