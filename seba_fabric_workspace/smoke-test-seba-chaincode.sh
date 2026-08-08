#!/usr/bin/env bash
#
# Smoke test for seba-audit-chaincode on the Fabric test network.
#
# Assumes:
#   - test network is up with a channel created
#   - seba-audit chaincode is deployed and committed to that channel
#
# Usage:  ./smoke-test-seba-chaincode.sh [channel-name] [chaincode-name]

set -euo pipefail

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_NETWORK_HOME="${WORKSPACE}/fabric-samples/test-network"

CHANNEL_NAME="${1:-mychannel}"
CC_NAME="${2:-sebaaudit}"

export PATH="${WORKSPACE}/fabric-samples/bin:${PATH}"
export FABRIC_CFG_PATH="${WORKSPACE}/fabric-samples/config"

for tool in peer jq shasum; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "ERROR: required tool '${tool}' not found on PATH" >&2
    exit 1
  fi
done

if [ ! -d "${TEST_NETWORK_HOME}" ]; then
  echo "ERROR: test network not found at ${TEST_NETWORK_HOME}" >&2
  exit 1
fi

cd "${TEST_NETWORK_HOME}"

# Org1 admin identity + TLS material for the orderer and both peers.
export CORE_PEER_TLS_ENABLED=true
export ORDERER_CA="${TEST_NETWORK_HOME}/organizations/ordererOrganizations/example.com/tlsca/tlsca.example.com-cert.pem"
export PEER0_ORG1_CA="${TEST_NETWORK_HOME}/organizations/peerOrganizations/org1.example.com/tlsca/tlsca.org1.example.com-cert.pem"
export PEER0_ORG2_CA="${TEST_NETWORK_HOME}/organizations/peerOrganizations/org2.example.com/tlsca/tlsca.org2.example.com-cert.pem"
export CORE_PEER_LOCALMSPID=Org1MSP
export CORE_PEER_TLS_ROOTCERT_FILE="${PEER0_ORG1_CA}"
export CORE_PEER_MSPCONFIGPATH="${TEST_NETWORK_HOME}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
export CORE_PEER_ADDRESS=localhost:7051

for f in "${ORDERER_CA}" "${PEER0_ORG1_CA}" "${PEER0_ORG2_CA}"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: missing TLS material: $f" >&2
    echo "       Bring the network up first: ./network.sh up createChannel" >&2
    exit 1
  fi
done

# Deterministic 64-char lowercase sha256 hex values for the test event.
h() { printf '%s' "$1" | shasum -a 256 | cut -d' ' -f1; }

# Unique per run so the script can be re-run against a ledger that already
# holds events from earlier runs. Override with RUN_ID=... to force a value.
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
REQUEST_ID_HASH="$(h "smoke-request-${RUN_ID}")"
DECISION_HASH="$(h "smoke-decision")"
EXPLANATION_HASH="$(h "smoke-explanation")"
RECORD_COMMITMENT="$(h "smoke-record")"
AUDIT_ANCHOR_HASH="$(h "smoke-anchor")"
APPROVAL_REF_HASH="$(h "smoke-approval")"
ATTRIBUTE_SET_HASH="$(h "smoke-attributes")"

CREATED_AT_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

EVENT_JSON=$(cat <<EOF
{"requestIdHash":"${REQUEST_ID_HASH}","policyVersion":"v1.0.0","decision":"allow","primaryReasonCode":"ROLE_MATCH","decisionHash":"${DECISION_HASH}","explanationHash":"${EXPLANATION_HASH}","recordCommitment":"${RECORD_COMMITMENT}","auditAnchorHash":"${AUDIT_ANCHOR_HASH}","approvalReferenceHash":"${APPROVAL_REF_HASH}","attributeSetHash":"${ATTRIBUTE_SET_HASH}","sourcePrototypeRun":"smoke-test-run","createdAtUtc":"${CREATED_AT_UTC}"}
EOF
)

PASS=0
FAIL=0

step() { printf '\n\033[0;34m=== %s ===\033[0m\n' "$1"; }
ok()   { printf '\033[0;32mPASS\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '\033[0;31mFAIL\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }

invoke() {
  peer chaincode invoke \
    -o localhost:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls --cafile "${ORDERER_CA}" \
    -C "${CHANNEL_NAME}" -n "${CC_NAME}" \
    --peerAddresses localhost:7051 --tlsRootCertFiles "${PEER0_ORG1_CA}" \
    --peerAddresses localhost:9051 --tlsRootCertFiles "${PEER0_ORG2_CA}" \
    -c "$1" --waitForEvent 2>&1
}

query() {
  peer chaincode query -C "${CHANNEL_NAME}" -n "${CC_NAME}" -c "$1" 2>&1
}

step "1. InitLedger"
if invoke '{"function":"InitLedger","Args":[]}' | grep -q 'status:200'; then
  ok "InitLedger committed"
else
  bad "InitLedger did not commit"
fi

step "2. RecordAccessDecision"
INVOKE_ARGS=$(jq -nc --arg e "${EVENT_JSON}" '{function:"RecordAccessDecision",Args:[$e]}')
if invoke "${INVOKE_ARGS}" | grep -q 'status:200'; then
  ok "audit event recorded"
else
  bad "failed to record audit event"
fi

# NOTE: every capture below is guarded with `|| true`. A failing `peer` call
# exits non-zero, and under `set -e` a bare `VAR="$(cmd)"` assignment aborts the
# whole script — skipping the bad() call, the diagnostic output, and the summary.
# The guard lets a real failure be reported as FAIL and the run continue.

step "3. ReadAccessDecision"
READ_OUT="$(query "$(jq -nc --arg r "${REQUEST_ID_HASH}" '{function:"ReadAccessDecision",Args:[$r]}')" || true)"
if echo "${READ_OUT}" | grep -q "${AUDIT_ANCHOR_HASH}"; then
  ok "record read back with matching anchor hash"
  echo "${READ_OUT}" | jq -r '{fabricTxId,decision,policyVersion,eventCommitmentHash}' 2>/dev/null || true
else
  bad "could not read record: ${READ_OUT}"
fi

step "4. VerifyAuditAnchor (expect match=true)"
VERIFY_OUT="$(query "$(jq -nc --arg r "${REQUEST_ID_HASH}" --arg a "${AUDIT_ANCHOR_HASH}" '{function:"VerifyAuditAnchor",Args:[$r,$a]}')" || true)"
if echo "${VERIFY_OUT}" | jq -e '.match == true' >/dev/null 2>&1; then
  ok "anchor verification returned match=true"
else
  bad "anchor verification failed: ${VERIFY_OUT}"
fi

step "5. VerifyAuditAnchor with wrong hash (expect match=false)"
WRONG_HASH="$(h "wrong-anchor")"
VERIFY_BAD="$(query "$(jq -nc --arg r "${REQUEST_ID_HASH}" --arg a "${WRONG_HASH}" '{function:"VerifyAuditAnchor",Args:[$r,$a]}')" || true)"
if echo "${VERIFY_BAD}" | jq -e '.match == false' >/dev/null 2>&1; then
  ok "tampered anchor correctly rejected"
else
  bad "tamper detection failed: ${VERIFY_BAD}"
fi

step "6. QueryByDecision(allow)"
QUERY_OUT="$(query '{"function":"QueryByDecision","Args":["allow"]}' || true)"
if echo "${QUERY_OUT}" | jq -e --arg r "${REQUEST_ID_HASH}" 'index($r) != null' >/dev/null 2>&1; then
  ok "composite-key index returned the request"
else
  bad "index query failed: ${QUERY_OUT}"
fi

step "7. GetHistoryForRequest"
HIST_OUT="$(query "$(jq -nc --arg r "${REQUEST_ID_HASH}" '{function:"GetHistoryForRequest",Args:[$r]}')" || true)"
if echo "${HIST_OUT}" | jq -e 'length > 0 and (.[0] | has("txId"))' >/dev/null 2>&1; then
  ok "history returned $(echo "${HIST_OUT}" | jq 'length') entry/entries"
else
  bad "history query failed: ${HIST_OUT}"
fi

step "8. Duplicate write is rejected"
# A rejected invoke exits non-zero by design, and `set -o pipefail` would make
# the whole pipeline non-zero even when grep matches. Capture first, then match.
DUP_OUT="$(invoke "${INVOKE_ARGS}" || true)"
if echo "${DUP_OUT}" | grep -qi 'already exists'; then
  ok "duplicate audit event correctly rejected"
else
  bad "duplicate was not rejected: ${DUP_OUT}"
fi

printf '\n\033[0;34m=== SUMMARY ===\033[0m\n'
printf 'passed: %s   failed: %s\n' "${PASS}" "${FAIL}"
[ "${FAIL}" -eq 0 ] || exit 1
