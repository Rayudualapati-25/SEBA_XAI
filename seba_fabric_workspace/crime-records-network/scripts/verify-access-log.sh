#!/usr/bin/env bash
#
# Verify the access log has not been edited or truncated.
#
# Recomputes the whole hash chain from the first entry, then compares it against
# every anchor the blockchain holds. Prints the first divergent entry if any.
#
# Usage: ./scripts/verify-access-log.sh

set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API="${API_BASE:-http://localhost:3001/api}"

info() { printf '\n\033[0;34m==> %s\033[0m\n' "$1"; }
die()  { printf '\033[0;31mERROR: %s\033[0m\n' "$1" >&2; exit 1; }

curl -s --max-time 3 "${API}/health" >/dev/null 2>&1 \
  || die "backend is not reachable at ${API} — start it with: cd backend && npm start"

info "Signing in as the auditor"
TOKEN="$(curl -s -X POST "${API}/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"aud.qureshi","password":"demo123"}' \
  | node -e 'let d="";process.stdin.on("data",c=>d+=c).on("end",()=>{
      const j=JSON.parse(d); if(!j.success){console.error(j.error);process.exit(1);}
      console.log(j.data.token);})')" || die "login failed"

info "Anchoring anything not yet committed to the blockchain"
curl -s -X POST "${API}/audit/anchor" -H "Authorization: Bearer ${TOKEN}" \
  | node -e 'let d="";process.stdin.on("data",c=>d+=c).on("end",()=>{
      const r=JSON.parse(d).data;
      console.log(r.anchored
        ? `  anchored up to entry ${r.anchor.seqNo} (tx ${r.anchor.txId.slice(0,16)}…)`
        : `  ${r.reason}`);})'

info "Recomputing the hash chain and comparing with on-chain anchors"
curl -s "${API}/audit/access-log/verify" -H "Authorization: Bearer ${TOKEN}" \
  | node -e 'let d="";process.stdin.on("data",c=>d+=c).on("end",()=>{
      const r = JSON.parse(d).data;
      console.log(`  log epoch         : ${r.epoch}`);
      console.log(`  entries re-hashed : ${r.entriesChecked}`);
      console.log(`  anchors compared  : ${r.anchorsChecked}`);
      if (r.anchorError) console.log(`  WARNING: ledger unreadable (${r.anchorError}) — local chain only`);
      if (r.priorEpochWarning) console.log(`  NOTE: ${r.priorEpochWarning}`);
      if (r.ok) {
        console.log("\n  \x1b[0;32mLOG INTACT\x1b[0m — every entry matches its hash and its anchor.");
        process.exit(0);
      }
      console.log(`\n  \x1b[0;31mLOG TAMPERED\x1b[0m — first bad entry: #${r.firstBadSeq}`);
      for (const p of r.problems.slice(0, 10)) console.log(`    - ${p}`);
      process.exit(1);
    })'
