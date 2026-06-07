# Blockchain Module 6 — Scalability & Layer 2

> **Goal**: Internalize the **scalability trilemma**, understand every major L2 design (rollups, channels, sidechains, validiums, plasma), and reason about which design fits which application.

---

## 6.1 The scalability trilemma (Vitalik, 2017)

> *A blockchain can have at most two of: **Scalability, Security, Decentralization.***

Strictly informal but useful as a planning lens:
- Bitcoin/Ethereum L1: Security + Decentralization, weak Scalability.
- BSC / EOS: Scalability + Security, weak Decentralization.
- Many sidechains: Scalability + Decentralization, weaker Security.

L2s aim to inherit L1 Security while gaining Scalability.

---

## 6.2 Scaling axes

| Axis | Lever |
|---|---|
| **Vertical** | Bigger blocks, faster nodes (Solana) |
| **Horizontal** | Sharding (Near, Ethereum data sharding) |
| **Off-chain** | Channels (Lightning) |
| **Rollups** | Bundle txs off-chain, post compressed proof on-chain |
| **Sidechains** | Independent chain, bridged |

---

## 6.3 State / payment channels

```
Open:    on-chain multisig deposit
Update:  off-chain signed state transitions
Close:   on-chain settlement
```

- **Bitcoin Lightning** — payment channels with HTLC routing.
- **Raiden** — Lightning for Ethereum ERC-20s.
- **Connext, Hydra (Cardano)** — generalized state channels.

Pros: instant, near-free.
Cons: requires liquidity, online watchtowers, doesn't generalize beyond fixed participants.

---

## 6.4 Plasma (deprecated but instructive)

Vitalik & Joseph Poon, 2017. A child chain commits Merkle roots to the parent chain. Users could exit fraudulent state.

**Why it died**: exit games are hard, mass exit problem (one operator hides data → all users must exit within window), unsuited to general smart contracts.

The exit-game intellectual heritage lives on in **Optimistic Rollups**.

---

## 6.5 Sidechains

A separate blockchain with its own consensus, bridged to L1.

| Example | Mechanism |
|---|---|
| **Polygon PoS** | Heimdall consensus + checkpoint commits to Ethereum |
| **Gnosis Chain** | Independent PoS, xDAI |
| **Liquid (Bitcoin)** | Federation-secured |

Security is **independent of L1** — you only trust the sidechain's own consensus. A bridge hack is a sidechain hack.

---

## 6.6 Rollups — the dominant L2 paradigm

A **rollup** executes transactions off-chain, posts:
- **Compressed transaction data** to L1 (data availability)
- **A validity argument** that the new state is correct

### Two flavors

| Type | Validity argument |
|---|---|
| **Optimistic Rollup** | Assume correct; allow fraud proofs within a 7-day challenge window |
| **ZK Rollup (a.k.a. Validity Rollup)** | Post a zk-SNARK / zk-STARK proving correctness — instant finality |

### Why both exist

| | Optimistic | ZK |
|---|---|---|
| Finality | 7 days | minutes |
| Gas cost on L1 | Cheap | Currently expensive (prover cost) but shrinking |
| EVM equivalence | Easy | Hard (zkEVM is bleeding edge) |
| Maturity | Higher | Catching up fast |

---

## 6.7 Optimistic Rollups in depth

Examples: **Arbitrum One, Optimism, Base, Mantle, Blast**.

**Fraud proof game** (interactive):
1. Sequencer posts a state root.
2. Within 7 days, anyone can challenge.
3. Bisection narrows down to the disputed step.
4. L1 EVM executes that single step. Whoever was wrong loses bond.

This is the "bisection" trick that makes fraud proofs O(log n) instead of O(n).

### Arbitrum vs Optimism

- **Arbitrum** uses a WASM-based interactive proof and has a custom precompile model.
- **Optimism** built **OP Stack**, a modular L2 framework now powering Base, Worldcoin, Zora, etc. → "Superchain" vision.

---

## 6.8 ZK Rollups in depth

Examples: **zkSync Era, StarkNet, Polygon zkEVM, Scroll, Linea**.

The sequencer:
1. Executes a batch of txs.
2. Generates a SNARK/STARK proving `(prev_state, txs) → new_state` is valid under EVM semantics.
3. Posts proof + minimal data to L1.

L1 verifies the proof (~200k gas). Done.

### zkEVM equivalence levels (Vitalik's classification)

- **Type 1**: byte-exact EVM (Taiko aims here)
- **Type 2**: equivalent for any Solidity program (Scroll, Polygon zkEVM)
- **Type 2.5**: minor gas-cost differences
- **Type 3**: most contracts work (early zkSync)
- **Type 4**: high-level language compiles to ZK-native (StarkNet/Cairo, zkSync's Era)

Type 1 is hardest (most EVM-compatible, slowest proving). Type 4 is easiest (custom VM).

---

## 6.9 Data availability (DA) — the next bottleneck

Rollups *must* post tx data on L1 so anyone can reconstruct state. Posting raw data is expensive.

### Solutions

| Solution | Approach |
|---|---|
| **EIP-4844 (proto-danksharding)** | Blob transactions — cheap, ephemeral (18 days), 128KB blobs |
| **Full Danksharding** | 128 blobs per slot, ~1.3MB/slot DA → ~100k TPS L2 |
| **Celestia** | Standalone DA layer using data availability sampling (DAS) |
| **EigenDA** | Restaking-secured DA on EigenLayer |
| **Avail** | Polygon's standalone DA chain |
| **Validium** | DA off-chain (DAC committee) — cheaper but weaker security |

DAS lets light clients verify with high probability that data was published, without downloading all of it — see Mustafa Al-Bassam's thesis.

---

## 6.10 Hybrid: Volitions and DACs

A **volition** lets users choose per-transaction whether their data goes on L1 (rollup security) or off-chain (validium speed). StarkEx pioneered this.

---

## 6.11 The "modular blockchain" thesis

Decompose monolithic blockchains into:

| Layer | Responsibility | Examples |
|---|---|---|
| Execution | Run tx state transitions | rollups, OP Stack, Arbitrum Orbit |
| Settlement | Resolve disputes, anchor canonicity | Ethereum |
| Data availability | Make tx data retrievable | EigenDA, Celestia, Avail, blobs |
| Consensus | Order blocks | Ethereum, Tendermint |

Cosmos, Celestia, EigenLayer, and the OP Superchain are all bets on modularity. **Solana** is the monolithic counter-bet.

---

## 6.12 Shared sequencers & cross-rollup atomicity

If every rollup has its own sequencer, cross-rollup composability dies. Active research:

- **Espresso, Astria** — shared sequencer networks
- **SUAVE (Flashbots)** — decentralized block builder
- **Booster Rollups** — designed to share execution

---

## 6.13 Reading list

- Buterin — *An Incomplete Guide to Rollups*, 2021 (vitalik.eth.limo).
- Al-Bassam, Sonnino, Buterin — *Fraud and Data Availability Proofs*, 2018.
- Kalodner et al. — *Arbitrum: Scalable, private smart contracts*, USENIX Security 2018.
- Ben-Sasson et al. — *Zerocash* + *zk-STARK* papers.
- *EIP-4844: Proto-Danksharding*.
- *Celestia whitepaper*.
- Buterin — *Endgame*, 2021.

## 6.14 Lab (3 hrs)

1. Deploy the same Solidity contract on Sepolia (L1) and Optimism Sepolia (L2). Compare gas cost.
2. Use `op-batcher` data on Etherscan to inspect a real L2 batch.
3. Read a single blob from a Beacon node via `/eth/v1/beacon/blob_sidecars/{slot}`.
4. Compute the cost-per-byte savings of EIP-4844 vs calldata.

## 6.15 Quiz

1. State the scalability trilemma and one counter-example to it.
2. Why do Optimistic Rollups need a 7-day challenge window?
3. What's the difference between a Type-2 and Type-4 zkEVM?
4. Define data availability sampling in one sentence.
5. What does EIP-4844 reduce, and by roughly how much?
