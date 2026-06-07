# Blockchain Module 11 — Advanced Consensus (DAGs, Sharding, HotStuff Family)

> **Goal**: Move from textbook BFT to the 2023–2026 research frontier. After this module you can read SOSP/NSDI/PODC papers on consensus without translation.

---

## 11.1 The performance ceiling of leader-based BFT

Leader-based protocols (PBFT, HotStuff, Tendermint) have a fundamental ceiling:

```
throughput ≤ leader_bandwidth / block_size
```

Because **one node** must disseminate the block per round. The 2020–2024 wave of DAG protocols breaks this by decoupling **transaction dissemination** from **ordering**.

---

## 11.2 DAG-based consensus

### Narwhal & Bullshark (Facebook/Meta, then Sui/Aptos lineage)

- **Narwhal**: reliable, scalable mempool. Every validator runs its own "worker" lanes broadcasting batches. Produces a DAG of certified batches.
- **Bullshark**: a *zero-message-overhead* consensus on top of Narwhal. Total ordering is derived deterministically from the DAG structure.

Benchmarks: 130k+ TPS, sub-2-second finality.

### Mysticeti (Sui, 2024)

Single-round commit, multi-leader DAG. Targets 300k+ TPS.

### Aleph BFT (Aleph Zero)

Asynchronous DAG protocol, sub-second finality, randomized leader.

### IOTA Tangle (historical)

A DAG where each new transaction validates two prior ones. Pioneered the DAG idea but had centralization issues (the Coordinator) that took years to resolve.

---

## 11.3 Sharding

Split state and execution across `K` parallel chains.

### Challenges

| Problem | Description |
|---|---|
| **Cross-shard communication** | Atomic txs across shards require commit protocols |
| **State fragmentation** | A user's state may live across shards |
| **Validator security** | Smaller shards = easier to corrupt |
| **Data availability** | Each shard's data must be retrievable by anyone |

### Approaches

| Project | Sharding flavor |
|---|---|
| Ethereum (original plan, then abandoned execution sharding) | 64 shards |
| Ethereum (current) | **Data sharding only** (danksharding) — execution off-loaded to L2s |
| Near | Nightshade — dynamic resharding |
| Polkadot | Shared security via relay chain; parachains are heterogeneous shards |
| Cosmos | App-chain sovereignty + IBC; not "sharding" in the classic sense |

Ethereum's pivot: instead of execution sharding, do **data sharding** so rollups can scale execution. The "rollup-centric roadmap".

---

## 11.4 HotStuff lineage

### Classic HotStuff (Yin et al., 2019)

Three-phase chained voting → linear leader rotation.

### LibraBFT / DiemBFT → Aptos (AptosBFT v4)

Extends HotStuff with reputation-based leader selection and pipelined sub-second finality.

### Jolteon / Ditto (Meta)

Merges HotStuff happy-path linearity with PBFT's view-change for adversarial scenarios.

### Carousel, Bullshark, Tusk, Shoal

Each iteration squeezes another constant factor out.

---

## 11.5 Asynchronous protocols

If you don't want to assume **any** synchrony, you need randomness.

| Protocol | Trick |
|---|---|
| HoneyBadger BFT (Miller et al., 2016) | Threshold encryption + atomic broadcast |
| Dumbo | Reduces HBBFT round count |
| Tusk | Async DAG on top of Narwhal |

Async protocols are slower in good conditions but never wedge.

---

## 11.6 Restaking & shared security as a consensus pattern

**EigenLayer (2023)** introduces a new design pattern: validators on chain A also validate AVSs (Actively Validated Services). The AVS's safety budget = restaked ETH at risk.

This blurs the line between consensus, security, and the application layer — a 2024–2026 research area.

Risks: AVS slashing definitions are heterogeneous; correlated failures across AVSs; centralization through restaking aggregators.

---

## 11.7 MEV-aware consensus

Active research:

- **Crypto-economic encrypted mempools** (Shutter, F3B, Themis)
- **Order-fairness consensus** (Aequitas, Themis, Pompê)
- **Proposer-Builder Separation (PBS)** with in-protocol enshrinement (ePBS, on Ethereum roadmap)
- **Inclusion lists** — proposer can force certain txs into the next block to defeat censorship

---

## 11.8 Cross-chain consensus

| Approach | Example |
|---|---|
| Light client bridges | IBC (Cosmos), zkBridge |
| Shared sequencers | Espresso, Astria |
| Shared validity proving | Polygon AggLayer, EigenDA + Espresso |
| Universal settlement | Polygon Pos→AggLayer; OP Superchain shared bridge |

The 2024–2026 trend: minimize trust through ZK light clients; minimize fragmentation through shared infrastructure.

---

## 11.9 Reading list

- Yin et al. — *HotStuff: BFT consensus with linearity and responsiveness*, PODC 2019.
- Danezis et al. — *Narwhal & Tusk: A DAG-based Mempool and Efficient BFT Consensus*, EuroSys 2022.
- Spiegelman, Giridharan, Sonnino, Kokoris-Kogias — *Bullshark*, CCS 2022.
- Miller et al. — *The Honey Badger of BFT Protocols*, CCS 2016.
- Kelkar et al. — *Order-Fair Consensus*, CRYPTO 2020.
- Buterin — *Endgame* + *PBS roadmap* posts.

## 11.10 Lab (2 hrs)

Pick one Bullshark / Mysticeti benchmark paper. Reproduce the throughput-vs-latency plot in a Python simulator (not actually networked — just simulate the message exchange). Discuss what assumptions made the original 130k TPS achievable.

## 11.11 Quiz

1. Why do DAG-based protocols outperform leader-based BFT in throughput?
2. What did Ethereum trade away when it dropped execution sharding for data sharding?
3. State one tradeoff of asynchronous BFT protocols vs partially synchronous ones.
4. Describe one risk of EigenLayer's shared security model.
5. Why does MEV motivate consensus-level redesign and not just app-level fixes?
