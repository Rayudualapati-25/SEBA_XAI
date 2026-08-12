# SEBA-XAI on Ethereum (Solidity port)

A Solidity/EVM port of the SEBA-XAI crime-records access-governance system,
duplicated from the Hyperledger Fabric chaincode in
[`../crime-records-network/chaincode/crimerecords`](../crime-records-network/chaincode/crimerecords).
It targets **public Ethereum** (any EVM chain — Sepolia testnet, mainnet, or an
L2) instead of a permissioned Fabric consortium.

The access decision is still the endorsed on-chain computation: a caller asks
for access, the deterministic policy engine runs **in the contract**, and the
decision is stored together with a reviewable explanation and a hash commitment
to that explanation. Nothing about the decision is computed off-chain and
trusted.

> **Read this before drawing conclusions.** A public L1 cannot reproduce two
> Fabric properties: private data collections and MSP-scoped confidentiality.
> See [What a public chain changes](#what-a-public-chain-changes). The port is
> faithful to the *access-control and audit logic*; it is deliberately *not* a
> claim that the same privacy guarantees survive on a public chain.

## Layout

```
contracts/
  policy/
    PolicyTypes.sol     enums + structs (roles, record types, decisions…)
    PolicyV1.sol        RBAC matrix, clearance ranks, exempt/juvenile/approver sets
    PolicyEngine.sol    deterministic evaluate() → Outcome (the 8 rules, in order)
  identity/
    IdentityRegistry.sol  on-chain MSP + attributes (replaces X.509 certs)
  lib/
    Validate.sol        SAFE_ID guard (the chaincode regex, byte-for-byte)
    ExplanationLib.sol  canonical SHA-256 hashing of the explanation artifact
  RecordRegistry.sol    crime-record registry (RecordContract)
  AccessManager.sol     access-request flow + escalations (AccessContract)
  AuditRegistry.sol     verification, anchoring, reconstruction (AuditContract)
  test/PolicyEngineHarness.sol   test-only wrapper over the pure engine
test/                   69 tests (policy engine, matrix, records, access, audit, identity)
scripts/deploy.js       deploy the suite + appoint one admin per MSP
```

## Quick start

```bash
npm install
npm test          # 69 passing
npm run coverage  # engine 100% lines; project ~94% lines
```

Local deployment against an in-process node:

```bash
npm run node                 # terminal 1: hardhat node
npm run deploy:local -- --network localhost   # terminal 2
```

Public testnet (Sepolia) — provide RPC + a funded key via the environment
(never commit them):

```bash
export SEPOLIA_RPC_URL="https://sepolia.infura.io/v3/<key>"
export DEPLOYER_PRIVATE_KEY="0x..."
npm run deploy:sepolia
```

## Fabric → Ethereum mapping

| Fabric chaincode | Solidity port | Notes |
|---|---|---|
| `RecordContract` | `RecordRegistry` | metadata + `payloadHash` (SHA-256) commitment; payload stays off-chain |
| `AccessContract` | `AccessManager` | policy engine runs on-chain; decision + explanation + hash stored |
| `AuditContract` | `AuditRegistry` | recompute-from-state verification, log anchoring, trail reconstruction |
| `policyEngine.js` | `PolicyEngine.sol` | same 8 rules, same order, same reason codes |
| `policyV1.js` tables | `PolicyV1.sol` | RBAC encoded as bitmasks over the `RecordType` enum |
| `getCaller` / `requireMsp` / `requireRole` (X.509 attrs) | `IdentityRegistry` | attributes live in on-chain state, keyed by `msg.sender` |
| `ctx.stub.getHistoryForKey` | version-log arrays + events | `getRecordHistory`, `getAccessLogAnchors` |
| CouchDB rich query (`getQueryResult`) | allow-listed `view` iteration | `queryRecords`, `queryPendingEscalations` |
| Private data collection (`putPrivateData`) | **removed** | no private state on a public chain — see below |
| `getTxID` | monotonic `decisionId` counter | keys the stored decision |
| `getDateTimestamp` | `block.timestamp` | |
| SHA-256 (`crypto`) | `sha256(...)` precompile | payload + explanation hashes |

## The eight policy rules (unchanged)

Evaluated in fixed order; the first terminal rule wins and names the decisive
attributes, so the `Outcome` is a reviewable explanation, not a bare verdict:

1. `CRED_NOT_ACTIVE` — revoked/inactive credential → **deny**
2. `INVALID_PURPOSE` — no declared purpose → **deny**
3. `RBAC_NO_PERMISSION` — role may not do this action on this type → **deny**
4. `SEALED_RECORD` — sealed, caller not the court → **escalate**
5. `JUVENILE_PROTECTED` — juvenile record, non-privileged role → **escalate**
6. `CROSS_JURISDICTION` — jurisdiction mismatch → **escalate** (an emergency
   with an approval token → **allow**, `EMERGENCY_CROSS_JURISDICTION`)
7. `NOT_ASSIGNED` — non-exempt role not on the case → **deny**
8. `INSUFFICIENT_CLEARANCE` — clearance below sensitivity → **escalate**
9. otherwise → **allow**, `POLICY_SATISFIED`

## What a public chain changes

These are honest limitations of the target, not defects of the port:

- **No private data.** Fabric kept evidence free-text detail in a member-only
  private data collection (Police + Forensics). A public L1 has none: every
  byte of state and calldata is world-readable and permanent. This port stores
  **only the public SHA-256 hash commitment** for records and evidence and
  drops the private-detail write path entirely. Sensitive detail must live
  fully off-chain; the chain holds commitments you can verify against, nothing
  more. Do **not** put PII, payloads, or raw approval tokens in any argument —
  `AccessManager` stores only `sha256(approvalToken)`, never the token.
- **No MSP-scoped read privacy.** Fabric restricted who could even *read*
  certain state. On a public chain, `view` methods and events are readable by
  anyone; access control here governs **who can write / cause a decision**, not
  who can observe state.
- **Identity is bootstrapped, not certificate-based.** There are no org CAs.
  `IdentityRegistry` reproduces the model: the deployer is root, appoints one
  admin per MSP, and each MSP admin manages only its own members and may grant
  only roles that belong to that MSP.
- **Rich queries cost gas on-chain.** `queryRecords` / `queryPendingEscalations`
  iterate state; they are `view` (free over `eth_call` off-chain) but do not
  call them from another contract on large data sets. For production indexing,
  consume the emitted events (`RecordCreated`, `AccessDecisionMade`, …) with an
  off-chain indexer — the EVM-native equivalent of CouchDB rich queries.
- **`viaIR` is enabled** in `hardhat.config.js`: the wide record/decision
  structs would otherwise hit "stack too deep".

## License

Apache-2.0, matching the upstream chaincode.
