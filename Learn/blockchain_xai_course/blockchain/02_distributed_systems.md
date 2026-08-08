# Blockchain Module 2 — Distributed Systems & the CAP/FLP Walls

> **Goal**: Understand why "just add a database" doesn't work in an open, adversarial network. Build the intuition for *why* blockchains are slow.

---

## 2.1 The classical distributed systems triangle

Before blockchains, the problem of "n computers agreeing on the same state" was studied for decades. Two impossibility results define the playing field.

### CAP theorem (Brewer, 2000; formalized Gilbert & Lynch, 2002)

In a distributed system you can pick at most **two** of:

- **C — Consistency** (every read gets the latest write)
- **A — Availability** (every request gets a non-error response)
- **P — Partition tolerance** (system continues operating across network splits)

Real networks **always** drop packets, so P is mandatory. The real choice is **CP vs AP**.

| System | Choice |
|---|---|
| PostgreSQL replica | CP |
| Cassandra | AP |
| Bitcoin (eventual finality) | AP-ish |
| Ethereum PoS (with finality gadget) | CP for finalized, AP for tip |

### FLP impossibility (Fischer, Lynch, Paterson, 1985)

In a purely **asynchronous** system, no deterministic protocol can guarantee consensus if even one node may crash.

This is why every real-world consensus protocol assumes one of:
- **Partial synchrony** (messages eventually arrive within `Δ`) — used by PBFT, HotStuff, Tendermint, Casper.
- **Randomization** (Ben-Or, common coin) — used by Algorand, HoneyBadger BFT.
- **Synchrony** (bounded message delay) — used by classical Byzantine agreement.

You cannot escape FLP — you can only choose which assumption to weaken.

---

## 2.2 Failure models

| Model | What can a node do? | Examples |
|---|---|---|
| Crash-stop | Halt and stop responding | Paxos, Raft |
| Crash-recovery | Stop and later restart | Real distributed DBs |
| **Byzantine** | Arbitrary, malicious behavior | Bitcoin, Ethereum, PBFT |
| Rational | Self-interested, follows protocol when incentivized | BAR-Tolerant Replication, blockchain proper |

Blockchain's contribution to distributed systems theory was demonstrating **economic-rational Byzantine tolerance at planetary scale**.

---

## 2.3 The Byzantine Generals Problem (Lamport, Shostak, Pease, 1982)

`n` generals, `f` of whom are traitors. They must agree on attack/retreat using only messages.

**Classical bound**: agreement is possible iff `n ≥ 3f + 1` for synchronous, signed-message-free protocols. With signatures (authenticated Byzantine), `n ≥ 2f + 1` suffices but requires synchrony.

The number `2/3` shows up everywhere in BFT:
- Tendermint needs >2/3 honest stake to finalize.
- HotStuff (used by Diem, Aptos) — same.
- Ethereum PoS finality — needs 2/3 honest validators.

---

## 2.4 Replicated state machines (RSM)

A blockchain *is* a replicated state machine.

```
state_(t+1) = transition(state_t, tx)
```

For all honest nodes to agree on `state_t`, they must agree on:
1. The **set** of transactions applied
2. The **order** of transactions applied

Consensus protocols solve problem #2. Problem #1 is solved trivially once order is fixed (everyone broadcasts and applies in agreed order).

This framing shows that *consensus is about ordering, not about validity*. A transaction can be ordered before being validated.

---

## 2.5 Leader-based vs leaderless consensus

| Family | Mechanism | Example |
|---|---|---|
| Leader-based | One node proposes a block per round | PBFT, HotStuff, Raft, Tendermint |
| Probabilistic leader | Random leader per round (VRF) | Algorand, Cardano Ouroboros |
| Leaderless | DAG of blocks, no single proposer | IOTA Tangle, Aleph, Narwhal-Bullshark |

Leader-based is simpler but creates a bottleneck. Leaderless / DAG-based protocols (Narwhal, Bullshark, Mysticeti from Sui; Aleph from Aleph Zero) are the 2023–2026 frontier and achieve >100k TPS in published benchmarks.

---

## 2.6 The fork problem & finality

**Fork** = the chain splits because two nodes propose conflicting blocks.

| Finality type | Definition | Example |
|---|---|---|
| **Probabilistic** | Probability of reversal → 0 as more blocks confirm | Bitcoin (6 blocks ≈ 99.99%) |
| **Economic** | Reversal would cost >X tokens | PoS slashing |
| **Absolute** | Finalized block cannot be reverted without > f Byzantine breach | Tendermint, PBFT-style |

Bitcoin: probabilistic, eventual. Ethereum post-Merge: hybrid — tip is probabilistic, finalized checkpoint is absolute (with 1/3 of stake at risk to revert).

---

## 2.7 Why throughput is limited

A back-of-envelope for any synchronous BFT protocol:

```
throughput ≤ block_size / (network_delay + signature_verification + state_writes)
```

If you increase block size, propagation slows → forks. This is **Nakamoto's tradeoff**.

L2s / sharding / DAG mempools are all attempts to shift parts of this equation off the critical path.

---

## 2.8 The mempool

Before consensus, transactions live in each node's **mempool** (memory pool). Selection from mempool into a block is where **MEV** (Maximal Extractable Value) lives. Most blockchain economic exploits originate here.

---

## 2.9 Reading list

- Lamport, Shostak, Pease — *The Byzantine Generals Problem*, 1982.
- Fischer, Lynch, Paterson — *Impossibility of distributed consensus with one faulty process*, 1985.
- Castro & Liskov — *Practical Byzantine Fault Tolerance*, OSDI 1999.
- Yin et al. — *HotStuff: BFT consensus in the lens of blockchain*, PODC 2019.
- Garay, Kiayias, Leonardos — *The Bitcoin Backbone Protocol*, Eurocrypt 2015.
- Buchman, Kwon, Milosevic — *The latest gossip on BFT consensus* (Tendermint).

## 2.10 Lab (2 hrs)

Build a simulator (no real network) of 7 nodes running a toy 2/3-majority commit protocol:
1. Each round one leader proposes.
2. Each node either votes commit or aborts.
3. Crash 2 of the 7 → it should still finalize. Make 3 Byzantine → it must fail.
4. Plot finality latency vs. number of Byzantine nodes.

## 2.11 Quiz

1. Why does CAP force most blockchains to favor AP at the tip and CP at finality?
2. State the `3f+1` bound and why it appears in PBFT and Tendermint.
3. What's the difference between probabilistic and absolute finality?
4. Why does increasing block size hurt decentralization?
5. Name two DAG-based consensus protocols and one tradeoff they make vs leader-based ones.
