#!/usr/bin/env bash
#
# Live end-to-end smoke test for the Crime Records Access Network.
# Runs the full cross-department scenario as the seeded users:
#   police file an FIR -> forensics attach evidence -> defense counsel denied
#   -> constable escalated -> judge approves -> revoked officer denied
#   -> prosecutor allowed -> auditor reconstructs trail + catches tampering.
#
# Usage: scripts/smoke-test.sh [channel] [cc-name]

set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="$(cd "${PROJECT_DIR}/.." && pwd)"
NETWORK_DIR="${PROJECT_DIR}/network"
CHANNEL="${1:-crimechannel}"
CC="${2:-crimerecords}"

export PATH="${WORKSPACE}/fabric-samples/bin:${PATH}"
export FABRIC_CFG_PATH="${WORKSPACE}/fabric-samples/config"

cd "${NETWORK_DIR}"
# shellcheck source=network/scripts/orgs.sh
source "${NETWORK_DIR}/scripts/orgs.sh"

ORDERER_CA="${NETWORK_DIR}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt"

# Endorsers: majority (3 of 5) — police, forensics, court.
ENDORSE_ARGS=(
  --peerAddresses localhost:7051 --tlsRootCertFiles "${NETWORK_DIR}/organizations/peerOrganizations/police.example.com/tlsca/tlsca.police.example.com-cert.pem"
  --peerAddresses localhost:8051 --tlsRootCertFiles "${NETWORK_DIR}/organizations/peerOrganizations/forensics.example.com/tlsca/tlsca.forensics.example.com-cert.pem"
  --peerAddresses localhost:10051 --tlsRootCertFiles "${NETWORK_DIR}/organizations/peerOrganizations/court.example.com/tlsca/tlsca.court.example.com-cert.pem"
)

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  \033[0;32mPASS\033[0m %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  \033[0;31mFAIL\033[0m %s\n' "$1"; }
step() { printf '\n\033[0;34m== %s\033[0m\n' "$1"; }

# Act as a specific enrolled user of an org.
setUser() { # setUser <org> <user>
  setGlobals "$1"
  export CORE_PEER_MSPCONFIGPATH="${NETWORK_DIR}/organizations/peerOrganizations/$1.example.com/users/$2@$1.example.com/msp"
}

ccargs() { # ccargs <function> <arg>...
  local fn="$1"; shift
  jq -cn --arg f "$fn" '{function:$f, Args:$ARGS.positional}' --args "$@"
}

invoke() { # invoke <function> <arg>...  -> global INVOKE_OUT, return code
  INVOKE_OUT="$(peer chaincode invoke -o localhost:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls --cafile "$ORDERER_CA" -C "$CHANNEL" -n "$CC" \
    "${ENDORSE_ARGS[@]}" --waitForEvent -c "$(ccargs "$@")" 2>&1)"
}

invoke_transient() { # invoke_transient <transientJson> <function> <arg>...
  local transient="$1"; shift
  INVOKE_OUT="$(peer chaincode invoke -o localhost:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls --cafile "$ORDERER_CA" -C "$CHANNEL" -n "$CC" \
    "${ENDORSE_ARGS[@]}" --waitForEvent --transient "$transient" \
    -c "$(ccargs "$@")" 2>&1)"
}

query() { # query <function> <arg>...  -> stdout JSON
  peer chaincode query -C "$CHANNEL" -n "$CC" -c "$(ccargs "$@")" 2>/dev/null
}

RUN_ID="${RUN_ID:-$(date +%s)}"
FIR="FIR-2026-${RUN_ID}"

# Off-chain payload lives in a local file; only its hash goes on-chain.
OFFCHAIN_DIR="${PROJECT_DIR}/.smoke-offchain"
mkdir -p "$OFFCHAIN_DIR"
PAYLOAD_FILE="${OFFCHAIN_DIR}/${FIR}.json"
printf '{"fir":"%s","summary":"synthetic burglary report","filedBy":"insp.sharma"}' "$FIR" > "$PAYLOAD_FILE"
PAYLOAD_HASH="$(shasum -a 256 "$PAYLOAD_FILE" | cut -d' ' -f1)"

step "1. Police inspector files ${FIR}"
setUser police insp.sharma
META="$(jq -cn --arg h "$PAYLOAD_HASH" --arg u "offchain://records/${FIR}" '{
  caseId:"CASE-2026-001", recordType:"fir", sensitivityLevel:"medium",
  juvenileFlag:false, witnessFlag:false, owningStation:"PS-Central",
  jurisdiction:"district-north", payloadHash:$h, offchainUri:$u}')"
invoke "RecordContract:CreateCaseRecord" "$FIR" "$META"
if echo "$INVOKE_OUT" | grep -q "status:200"; then ok "record created"; else bad "record create: $INVOKE_OUT"; fi

step "2. Forensics analyst cannot file records (ABAC check)"
setUser forensics analyst.rao
invoke "RecordContract:CreateCaseRecord" "${FIR}-x" "$META"
if echo "$INVOKE_OUT" | grep -q "requires membership in \[PoliceMSP\]"; then
  ok "forensics blocked from creating records"
else bad "expected PoliceMSP rejection, got: $INVOKE_OUT"; fi

step "3. Forensics attaches evidence hash (+ private detail via PDC)"
EV_HASH="$(printf 'dna-profile-artifact' | shasum -a 256 | cut -d' ' -f1)"
DETAIL_B64="$(printf 'DNA profile matched sample S-77' | base64)"
invoke_transient "{\"evidenceDetail\":\"${DETAIL_B64}\"}" \
  "RecordContract:AttachEvidenceHash" "$FIR" "EV-DNA-001" "$EV_HASH"
if echo "$INVOKE_OUT" | grep -q "status:200"; then ok "evidence attached"; else bad "evidence: $INVOKE_OUT"; fi

step "4. Defense counsel denied by RBAC, with explanation"
setUser prosecution dc.nair
invoke "AccessContract:RequestAccess" "$FIR" "view" '{"purpose":"defense-preparation"}'
sleep 1
DEC="$(query "AccessContract:QueryDecisionsByRecord" "$FIR" | jq '[.[]|select(.subject.role=="defense-counsel")][0]')"
if [ "$(echo "$DEC" | jq -r .decision)" = "deny" ] && \
   [ "$(echo "$DEC" | jq -r .explanation.reasonCode)" = "RBAC_NO_PERMISSION" ]; then
  ok "denied with RBAC_NO_PERMISSION explanation"
else bad "expected deny/RBAC_NO_PERMISSION, got: $DEC"; fi

step "5. Constable escalated on insufficient clearance"
setUser police const.verma
invoke "AccessContract:RequestAccess" "$FIR" "view" '{"purpose":"investigation"}'
sleep 1
ESC="$(query "AccessContract:QueryDecisionsByRecord" "$FIR" | jq '[.[]|select(.subject.role=="constable")][0]')"
ESC_ID="$(echo "$ESC" | jq -r .decisionId)"
if [ "$(echo "$ESC" | jq -r .decision)" = "escalate" ] && \
   [ "$(echo "$ESC" | jq -r .explanation.reasonCode)" = "INSUFFICIENT_CLEARANCE" ]; then
  ok "escalated with INSUFFICIENT_CLEARANCE + counterfactual"
else bad "expected escalate, got: $ESC"; fi

step "6. Judge approves the escalation"
setUser court judge.rana
invoke "AccessContract:ApproveEscalation" "$FIR" "$ESC_ID" "supervised review granted"
sleep 1
RES="$(query "AccessContract:GetDecision" "$FIR" "$ESC_ID")"
if [ "$(echo "$RES" | jq -r .status)" = "approved-after-escalation" ]; then
  ok "escalation approved by judge"
else bad "expected approved-after-escalation, got: $RES"; fi

step "7. Officer with revoked credential is denied"
setUser police insp.rathore
invoke "AccessContract:RequestAccess" "$FIR" "view" '{"purpose":"investigation"}'
sleep 1
REV="$(query "AccessContract:QueryDecisionsByRecord" "$FIR" | jq '[.[]|select(.explanation.reasonCode=="CRED_NOT_ACTIVE")][0]')"
if [ "$(echo "$REV" | jq -r .decision)" = "deny" ]; then
  ok "revoked credential denied (CRED_NOT_ACTIVE)"
else bad "expected CRED_NOT_ACTIVE deny, got: $REV"; fi

step "8. Public prosecutor allowed"
setUser prosecution pp.mehta
invoke "AccessContract:RequestAccess" "$FIR" "view" '{"purpose":"prosecution"}'
if echo "$INVOKE_OUT" | grep -q '\\"decision\\":\\"allow\\"'; then
  ok "prosecutor allowed"
else bad "expected allow, got: $INVOKE_OUT"; fi

step "9. Auditor reconstructs the audit trail"
setUser audit aud.qureshi
TRAIL="$(query "AuditContract:GetAuditTrail" "$FIR")"
N_DEC="$(echo "$TRAIL" | jq '.accessDecisions | length')"
if [ "${N_DEC:-0}" -ge 4 ]; then ok "trail has ${N_DEC} decisions with explanations"; else bad "trail: $TRAIL"; fi

step "10. Auditor verifies off-chain payload integrity"
GOOD="$(query "AuditContract:VerifyRecordPayload" "$FIR" "$PAYLOAD_HASH" | jq -r .match)"
printf ' tampered' >> "$PAYLOAD_FILE"
TAMPERED_HASH="$(shasum -a 256 "$PAYLOAD_FILE" | cut -d' ' -f1)"
BADV="$(query "AuditContract:VerifyRecordPayload" "$FIR" "$TAMPERED_HASH" | jq -r .match)"
if [ "$GOOD" = "true" ] && [ "$BADV" = "false" ]; then
  ok "payload verify: pristine=true, tampered=false"
else bad "verify gave pristine=$GOOD tampered=$BADV"; fi

step "11. Explanation-hash substitution is detected"
ART="$(query "AccessContract:GetDecision" "$FIR" "$ESC_ID" | jq -c .explanation)"
MATCH="$(query "AuditContract:VerifyExplanation" "$FIR" "$ESC_ID" "$ART" | jq -r .match)"
FORGED="$(echo "$ART" | jq -c '.reasonCode="POLICY_SATISFIED"')"
FORGED_MATCH="$(query "AuditContract:VerifyExplanation" "$FIR" "$ESC_ID" "$FORGED" | jq -r .match)"
if [ "$MATCH" = "true" ] && [ "$FORGED_MATCH" = "false" ]; then
  ok "explanation verify: genuine=true, forged=false"
else bad "explanation verify gave genuine=$MATCH forged=$FORGED_MATCH"; fi

printf '\n\033[0;34m== Result: %d passed, %d failed ==\033[0m\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
