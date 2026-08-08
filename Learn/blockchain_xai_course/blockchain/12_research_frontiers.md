# Blockchain Module 12 — Research Frontiers (2025–2027)

> **Goal**: Identify *what's actually new*, where the citations are clustering, and which lines of work could plausibly become a Master's or PhD thesis.

---

## 12.1 Frontier map

```
        ┌────────────────────────────────────────────────────┐
        │              VERIFIABLE COMPUTATION                │
        │   zkVMs · zkML · zkEVMs · Folding · IVC · GKR      │
        └────────────────────────────────────────────────────┘
        ┌──────────────────────┐  ┌─────────────────────────┐
        │   MODULAR STACKS     │  │  CONSENSUS @ INTERNET   │
        │ DA layers · shared   │  │ DAG · Sub-100ms finality│
        │ sequencing · bridges │  │ Async BFT · MEV protect │
        └──────────────────────┘  └─────────────────────────┘
        ┌──────────────────────┐  ┌─────────────────────────┐
        │  PRIVACY & IDENTITY  │  │ ECON / GOV / MECHANISMS │
        │ FHE+ZK · Stealth     │  │ Public goods · Restake  │
        │ addresses · zkID     │  │ MEV markets · DAOs      │
        └──────────────────────┘  └─────────────────────────┘
        ┌────────────────────────────────────────────────────┐
        │   AI × BLOCKCHAIN: ZKML, decentralized inference,  │
        │   agent economies, on-chain reputation             │
        └────────────────────────────────────────────────────┘
```

---

## 12.2 Top open research questions

### 1. Practical zkML at scale
- Can we prove inference for >1B parameter LLMs in seconds with sub-$1 cost?
- New: GKR-based proving (sumcheck), lookup arguments, folding schemes (Nova/HyperNova).

### 2. Stateless / minimally-stateful clients
- Verkle trees, history expiry (EIP-4444), light clients with full security.
- Ethereum's "The Verge" milestone.

### 3. Folding schemes & IVC
- Nova, SuperNova, HyperNova, ProtoStar, CycleFold.
- Goal: incrementally verifiable computation with O(1) prover overhead per step.

### 4. Encrypted mempools and MEV defense
- Threshold encryption (Shutter), FHE-based, time-lock encryption.
- Tradeoffs: latency, liveness under failure.

### 5. Sovereign vs shared sequencing
- Single rollup sequencer = censorship risk.
- Shared sequencers (Espresso, Astria) trade composability for centralization risk.
- Active design space.

### 6. Account abstraction beyond ERC-4337
- Native AA (EIP-7702 path), recovery, MFA, social recovery, biometric signing.

### 7. Restaking risk modeling
- Correlated slashing across AVSs.
- What's the right capital-budget for slashable bonds across services?

### 8. Privacy-preserving compliance
- "Selective disclosure" — prove you're not OFAC-sanctioned without revealing identity.
- Aztec, Zcash deposit-screening, Sismo Connect.

### 9. Long-range and quantum resistance
- Post-quantum signature migration paths.
- Hash-based signatures (XMSS, SPHINCS+) and lattice schemes (CRYSTALS-Dilithium).

### 10. On-chain games & autonomous worlds
- Dark Forest (zk fog of war), MUD, Argus — game state as smart contract.
- Pushes ZK proving and gas optimization to extremes.

### 11. Decentralized AI infrastructure
- Compute marketplaces (Akash, Render, io.net).
- Model marketplaces and reputation (Bittensor, Ritual).
- See [intersection module](../intersection/blockchain_xai_intersection.md).

### 12. Formal verification at scale
- Specs auto-generated from upgrades; ML-assisted invariant inference.

---

## 12.3 Venues to track

| Venue | Tracks |
|---|---|
| **IEEE S&P, USENIX Security, CCS, NDSS** | Security |
| **CRYPTO, EUROCRYPT, ASIACRYPT, TCC** | Cryptography & ZK |
| **PODC, DISC, OSDI, SOSP, NSDI** | Distributed systems |
| **AFT (Advances in Financial Technologies)** | DeFi, mechanism design |
| **FC (Financial Cryptography)** | Applied crypto + DeFi |
| **DSN** | Dependability + BFT |
| **NeurIPS / ICML / ICLR** | ZKML, decentralized ML |
| **ACM EC, WINE** | Mechanism design, governance |

**Workshops worth submitting to as a first paper**:
- DeFi @ CCS, ConsensusDay @ ESORICS, ZKProof workshop, Decentralizing Finance @ FC, FROST.

---

## 12.4 Toolchains worth building on

| Tool | Why |
|---|---|
| **Foundry** (Solidity dev) | Industry standard test/fuzz framework |
| **Risc Zero, SP1, Jolt** | zkVMs — prove any Rust program |
| **Circom, Noir, Halo2** | Hand-written circuits |
| **EigenLayer SDK** | AVS development |
| **Lambdaclass plonky3** | Modern STARK toolkit |
| **Hardhat / Tenderly** | Mainstream Solidity tooling |

---

## 12.5 How to pick a thesis-scale topic

1. Pick one of the 12 open questions above.
2. Read the **5 most-cited papers** of the last 18 months in that subarea.
3. Find a **clean primitive missing** or a **clean attack class undeveloped**.
4. Build the smallest possible empirical artifact (a benchmark, a measurement study, a circuit).
5. Submit to a workshop first. Iterate to a full venue.

The fastest first-paper recipe in blockchain research: **a measurement paper**. Empirical chain data is abundant; few researchers can both query archives and reason about protocol semantics.

---

## 12.6 Lab / capstone (open-ended)

Pick **one** of:
- Build a working zkML pipeline that proves an MNIST CNN forward pass with EZKL or Risc Zero. Measure proof time and verifier gas cost.
- Reproduce a benchmark from the Narwhal-Bullshark paper using their open-source code.
- Conduct a measurement of MEV-Boost relay behavior over 1 month of Ethereum blocks.
- Implement a stealth address scheme (EIP-5564) and write a usability analysis.

## 12.7 Quiz

1. Name two recent folding schemes and what they improve.
2. What does Ethereum's "The Verge" milestone aim for?
3. Why might shared sequencing recentralize what rollups decentralized?
4. State one open question in zkML at scale.
5. Why is *measurement* often the easiest first paper for a new researcher?
