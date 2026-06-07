# Blockchain Module 9 — Security & Attack Surface

> **Goal**: Build a catalog of every major attack class. Read at least 3 postmortems. Internalize that *most* blockchain "hacks" are app-layer bugs, not consensus breaks.

---

## 9.1 Threat models

| Adversary | Capability |
|---|---|
| **External attacker** | Can call any public function, see all state |
| **Malicious validator** | Can reorder/censor (within their slots), double-sign (gets slashed) |
| **Compromised oracle** | Can push arbitrary prices |
| **Compromised bridge** | Can mint unbacked tokens on destination chain |
| **Governance attacker** | Can pass malicious proposal with enough tokens |
| **Nation-state** | Long-range attacks, mining cartel, regulatory capture |

---

## 9.2 Smart-contract bugs

### Top 10 classes

1. **Reentrancy** — external call before state update.
2. **Integer over/underflow** — pre-0.8 Solidity; still possible with `unchecked {}`.
3. **Access control** — missing `onlyOwner` modifiers, default-public functions.
4. **Front-running / MEV exposure** — public mempool reveals intent.
5. **Oracle manipulation** — single source of truth.
6. **Logic bugs** — math wrong, accounting wrong (most common in DeFi).
7. **Improper initialization** — unprotected `initialize()`.
8. **Delegatecall to untrusted code** — full storage access.
9. **`tx.origin` for auth** — phishable.
10. **Unbounded loops** — gas griefing, DoS.

### Less obvious

- **Read-only reentrancy** — view functions can return stale values mid-call.
- **Cross-function reentrancy** — re-enter a *different* function that shares state.
- **Signature replay** — missing `nonce` or `chainId` lets one signature be reused.
- **Permit2 / approval phishing** — drainer scams.

---

## 9.3 Famous exploits — a starter list

| Incident | Year | Loss | Class |
|---|---|---|---|
| The DAO | 2016 | $60M | Reentrancy → ETH/ETC fork |
| Parity multisig | 2017 | 513k ETH frozen | Library kill |
| bZx | 2020 (×2) | $1M | Oracle / flash loan |
| Poly Network | 2021 | $611M | Access control |
| Wormhole | 2022 | $325M | Signature verification |
| Ronin Bridge | 2022 | $625M | Validator key compromise |
| Beanstalk | 2022 | $182M | Flash-loan governance |
| Nomad | 2022 | $190M | Init bug, copy-paste pillage |
| Mango Markets | 2022 | $117M | Oracle manipulation |
| Euler Finance | 2023 | $197M | Donation-attack accounting |
| Curve Vyper compiler | 2023 | $73M | Compiler reentrancy lock bug |
| Multichain | 2023 | $130M | Insider / opaque |
| Atomic Wallet | 2023 | $100M+ | Wallet-side compromise |
| Orbit Bridge | 2024 | $80M | Bridge key compromise |

**Lesson**: Bridges and cross-chain are the single most-attacked surface.

---

## 9.4 Consensus-layer attacks

| Attack | Target | Mechanism |
|---|---|---|
| **51% attack** | PoW chain | Majority hashrate rewrites history |
| **Long-range attack** | PoS chain | Old keys re-create alternate history (mitigated by weak subjectivity) |
| **Eclipse attack** | Single node | Isolate node from honest network → feed fake chain |
| **Sybil attack** | Network | Many fake identities; Sybil-resistance (PoW/PoS) defeats it |
| **Selfish mining** | PoW | Withhold blocks to gain disproportionate reward |
| **Time-bandit** | EVM (theoretical) | Reorg to capture historical MEV |
| **Bribery** | PoS validators | Pay validators to break protocol |
| **Inactivity leak** | PoS chains | If chain can't finalize, non-voting validators bleed stake |

---

## 9.5 Bridges — the trillion-dollar honey pot

Bridges typically lock tokens on Chain A and mint wrapped tokens on Chain B. Trust models:

| Model | Examples | Weakness |
|---|---|---|
| Multi-sig federation | early Wormhole, Ronin | Key compromise (Ronin: 5 of 9 keys) |
| Light client (IBC, etc.) | Cosmos IBC | Strong, but only works for compatible chains |
| ZK light client | zkBridge, Polyhedra | Strong, expensive |
| Optimistic | Across, Nomad | Long challenge window |
| LayerZero / Wormhole / Axelar | Relayer + Oracle separation | Trust assumptions on relayers/guardians |

Vitalik's "trilemma for bridges": you can have 2 of {trust-minimization, generality, extensibility-across-chains}.

---

## 9.6 Frontend attacks

The chain may be secure but the **frontend** is HTML/JS served from CDNs.

- Curve's frontend was hijacked via DNS hijack (2022) → users signed malicious tx.
- BadgerDAO's CDN-hosted JS injected approval-drainer (2021, ~$120M).

Mitigations: IPFS-pinned + ENS-resolved frontends, hardware wallet "blind signing" warnings, wallet drainers protection (Blockaid, Wallet Guard).

---

## 9.7 Phishing and the user surface

Drainers ("Inferno Drainer", "Pink Drainer", "Angel Drainer") use:
- Fake mints/airdrops
- Permit / Permit2 signature theft
- SetApprovalForAll tricks
- Address poisoning

User-side losses to drainers exceeded $300M in 2023. The chain didn't fail — the UX did.

---

## 9.8 Formal verification & static analysis

| Tool | What it does |
|---|---|
| **Slither** | Static analysis for Solidity |
| **Mythril** | Symbolic execution |
| **Echidna** | Property-based fuzzing |
| **Foundry invariant tests** | Invariant fuzzing |
| **Certora Prover** | SMT-backed formal verification |
| **K-framework** | Formal semantics for EVM (KEVM) |
| **Halmos** | Symbolic Foundry tests |

Best practice 2026 stack: Foundry unit tests + invariant tests + Slither in CI + Certora spec for critical invariants + a professional audit before mainnet.

---

## 9.9 The audit industry

Top firms (alphabetical, partial): **Trail of Bits, OpenZeppelin, ConsenSys Diligence, Spearbit, Code4rena, Zellic, Cantina, Sherlock, Halborn**.

Audits do not prove correctness — they reduce risk. **Code4rena** competitive audits typically find more issues than fixed-fee audits but at higher cost.

---

## 9.10 Incentive-compatible disclosure

| Practice | Detail |
|---|---|
| Bug bounty | Immunefi, HackerOne; payouts up to $10M for L1 critical |
| Whitehat retrievals | Some exploits returned for 10% bounty |
| War rooms | Coordinated multi-protocol response (e.g., Curve July 2023) |
| Pause / kill switches | Trade-off: safety vs decentralization purity |

---

## 9.11 Reading list

- Atzei, Bartoletti, Cimoli — *A Survey of Attacks on Ethereum Smart Contracts*, POST 2017.
- Daian et al. — *Flash Boys 2.0*, S&P 2020.
- Heilman et al. — *Eclipse Attacks on Bitcoin's Peer-to-Peer Network*, USENIX Security 2015.
- Eyal & Sirer — *Majority Is Not Enough*, FC 2014.
- *SoK: Cross-Chain Communication* (any of several).
- Rekt News — postmortem corpus (rekt.news).

## 9.12 Lab (3 hrs)

1. Fork Curve's affected pool at the exact block before the July 2023 reentrancy. Reproduce the drain in Foundry.
2. Run Slither on a small Solidity project. Triage the findings.
3. Write an invariant test in Foundry that would have caught the bug.

## 9.13 Quiz

1. State three differences between reentrancy and read-only reentrancy.
2. Why are bridges disproportionately attacked?
3. Define long-range attack and the standard mitigation.
4. What problem does MEV-Boost solve, and what new one does it introduce?
5. Name one tool from each of: static analysis, fuzzing, formal verification.
