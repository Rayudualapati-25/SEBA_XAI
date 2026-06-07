# Blockchain Module 5 — Consensus Algorithms

> **Goal**: Compare every major consensus mechanism on the same axes: security model, finality type, throughput, decentralization, and known attacks.

---

## 5.1 The consensus design space

A consensus protocol must answer:

1. **Who proposes** the next block? (Sybil-resistance mechanism)
2. **Who votes** on its validity?
3. **When is it final**?
4. **How are honest behavior and dishonest behavior incentivized / punished**?

Combinations of answers give us all known protocols.

---

## 5.2 Proof-of-Work (PoW)

**Sybil resistance** via computational cost.

| Property | Value |
|---|---|
| Proposer selection | Solve hash puzzle |
| Finality | Probabilistic |
| Energy use | Very high |
| Hardware barrier | High (ASICs) |
| Throughput | Low |
| Known attacks | Selfish mining, 51%, eclipse |

**Variants**:
- **SHA-256** (Bitcoin) — ASIC-friendly
- **Ethash** (pre-Merge Ethereum) — memory-hard, GPU-friendly (intentionally ASIC-resistant; partially failed)
- **RandomX** (Monero) — CPU-friendly via virtual machine
- **Scrypt, X11, Equihash** — earlier altcoin attempts

---

## 5.3 Proof-of-Stake (PoS)

**Sybil resistance** via locked economic value.

A validator deposits collateral; misbehavior is **slashed** (collateral burned). Honest behavior earns issuance + fee rewards.

### Variants

| Protocol | Mechanism | Used by |
|---|---|---|
| **Casper FFG + LMD-GHOST** | Hybrid finality + fork choice | Ethereum |
| **Tendermint / CometBFT** | Round-based BFT, instant finality | Cosmos chains |
| **Ouroboros** | Slot leader from VRF | Cardano |
| **Algorand BA*** | Cryptographic sortition + BA | Algorand |
| **Snowball / Avalanche** | Repeated random sampling | Avalanche |
| **PoH + ToS** | Verifiable delay + TowerBFT | Solana |

### Slashing conditions (Ethereum)

1. **Double proposal** — sign two different blocks for the same slot.
2. **Surround vote** — attesting to a checkpoint that surrounds your previous one.
3. **Inactivity leak** — if chain can't finalize, validators that aren't voting bleed stake.

### "Nothing at stake" (early PoS problem, solved)

In naive PoS, a validator could vote on every fork (it's costless), preventing convergence. Slashing solves this by making conflicting votes punishable.

---

## 5.4 Proof-of-Authority (PoA)

A fixed set of permissioned validators. Used for consortium chains (POA Network, Binance Smart Chain, many enterprise blockchains).

Pros: very high throughput.
Cons: trust-based, single-org risk.

---

## 5.5 Practical Byzantine Fault Tolerance (PBFT, 1999)

```
1. Pre-prepare:  leader proposes
2. Prepare:      all replicas exchange "I saw the proposal"
3. Commit:       all replicas exchange "I'm ready to commit"
4. Reply:        once 2f+1 commits, finalized
```

`O(n²)` messages per round → doesn't scale beyond ~100 nodes. HotStuff (2019) reduced this to linear with chained pipelined voting.

---

## 5.6 HotStuff

The basis of Diem, Aptos, and modern BFT chains.

- **Linear view change** — replacing a faulty leader costs O(n) messages instead of O(n²).
- **Pipelined** — three-phase QC chained so each block contributes to multiple commits.
- **Optimistic responsiveness** — protocol moves at network speed when network is healthy.

---

## 5.7 Tendermint / CometBFT

Used by Cosmos chains.

- Round-based: propose → pre-vote → pre-commit → commit.
- Instant absolute finality (1 block).
- Validator set fixed per epoch.
- Cannot fork — if 2/3 are honest, only one block per height.
- Limit: ~100–200 validators (gossip cost).

---

## 5.8 Ouroboros (Cardano)

Time is divided into **epochs** → **slots**. A VRF selects a slot leader. Multiple variants:

- **Ouroboros Classic** — synchronous, multi-party coin tossing.
- **Ouroboros Praos** — semi-synchronous, secure under adaptive corruption.
- **Ouroboros Genesis** — full bootstrap security (no trusted setup of recent chain).
- **Ouroboros Hydra** — L2 with off-chain state channels.

Notable for being one of the most academically rigorous protocol families.

---

## 5.9 Algorand BA*

Pure PoS with cryptographic sortition.

- Each round, ~1000 validators are sampled (private VRF reveal).
- BA* algorithm runs Byzantine agreement in ~5 seconds.
- No forks, instant finality.
- Designed under partial synchrony with adaptive corruption.

---

## 5.10 Avalanche consensus (Snowball/Snowflake/Avalanche)

A **gossip-and-sample** family:

```
loop:
  query K random peers for their preference
  if α·K agree, increment confidence
  if confidence > β, decide
```

Sub-second finality, very high throughput. Used by Avalanche network.

---

## 5.11 Proof-of-History (Solana)

A VDF (verifiable delay function) produces a cryptographic clock so validators don't need to negotiate timestamps. Combined with TowerBFT for finality.

Pros: massive throughput claims (50k+ TPS).
Cons: high hardware requirements → centralization pressure; several major outages.

---

## 5.12 Comparison table

| Protocol | Finality | TPS (real) | Validators | Energy | Sybil |
|---|---|---|---|---|---|
| Bitcoin PoW | Probabilistic 60min | 7 | ~thousands (miners) | ~150 TWh/yr | Compute |
| Ethereum PoS | 12.8min absolute | 15 (L1), 100k+ (L2) | ~1M | Low | Stake |
| Cosmos (CometBFT) | 1 block, ~6s | ~1k | ~150 | Low | Stake |
| Solana (PoH+TowerBFT) | ~13s | 4–6k typical | ~2k | Mid | Stake |
| Avalanche | <2s | 1–5k | ~1.5k | Low | Stake |
| Cardano (Ouroboros) | Probabilistic | ~250 | ~3k stake pools | Low | Stake |

---

## 5.13 Reading list

- Castro & Liskov — *Practical Byzantine Fault Tolerance*, 1999.
- Yin et al. — *HotStuff: BFT Consensus with Linearity and Responsiveness*, PODC 2019.
- Kiayias et al. — *Ouroboros: A Provably Secure Proof-of-Stake Blockchain Protocol*, CRYPTO 2017.
- Chen & Micali — *Algorand: A Secure and Efficient Distributed Ledger*, 2017.
- Rocket et al. — *Scalable and Probabilistic Leaderless BFT Consensus through Metastability* (Avalanche).
- Yakovenko — *Solana: A new architecture for a high performance blockchain*, 2018.
- Buterin & Griffith — *Casper the Friendly Finality Gadget*, 2017.

## 5.14 Lab (3 hrs)

Pick **two** protocols and implement a stripped-down simulator:
1. Tendermint round (propose → prevote → precommit → commit) with 4 nodes, 1 Byzantine.
2. Avalanche Snowball with 100 nodes — show convergence as α and K vary.
Plot finality time vs Byzantine fraction.

## 5.15 Quiz

1. Why does naive PoS suffer from "nothing at stake" and how does slashing fix it?
2. State HotStuff's improvement over PBFT in big-O terms.
3. What's the role of the VRF in Ouroboros and Algorand?
4. Explain why Solana's PoH is *not* a consensus mechanism by itself.
5. Why is Tendermint capped at ~150 validators in practice?
