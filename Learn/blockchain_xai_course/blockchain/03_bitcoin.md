# Blockchain Module 3 — Bitcoin Deep Dive

> **Goal**: Understand Bitcoin not as a coin but as the first working solution to Byzantine consensus over an open membership network. Every later blockchain is a delta against Bitcoin.

---

## 3.1 The white paper in one paragraph

Satoshi Nakamoto (2008) proposed: combine `(a) hash-chained blocks, (b) PoW puzzle, (c) longest-chain rule, (d) economic incentives` so that **honest nodes following the protocol find it more profitable than attacking it**. The protocol is open — anyone can join — yet Byzantine-tolerant under the assumption that >50% of compute is honest.

---

## 3.2 The UTXO model

Bitcoin's state is not a list of balances. It's a set of **Unspent Transaction Outputs**.

```
Tx {
  inputs:  [ (prev_tx_id, output_index, signature) ... ]
  outputs: [ (amount, locking_script) ... ]
}
```

To spend, you reference previous outputs and prove you can unlock them (via Script). Total input value ≥ total output value; the difference is the miner fee.

### Why UTXO?

- **Stateless validation** — verifying a tx needs only the referenced UTXOs, not full chain state.
- **Parallelizable** — txs touching disjoint UTXOs can be validated in parallel.
- **Privacy** — each UTXO can be a fresh address.

Ethereum chose the **account model** instead — simpler smart contracts but harder to parallelize.

---

## 3.3 Bitcoin Script

A stack-based, non-Turing-complete language. Standard "P2PKH" locking script:

```
OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
```

Unlocking script supplies `<signature> <pubKey>`. Combined, the script evaluates to TRUE iff the signature is valid for that pubKey, whose hash matches `<pubKeyHash>`.

### Why not Turing complete?

To bound execution time and prevent halting-problem attacks. Bitcoin chose this conservatism deliberately. Taproot (2021) and Miniscript expanded expressiveness while keeping safety guarantees.

---

## 3.4 Proof-of-Work

The puzzle: find a nonce such that `H(block_header) < target`, where `target` is set so that the global network produces one block every 10 minutes.

```
while sha256(sha256(header_with(nonce))) >= target:
    nonce += 1
```

### Difficulty adjustment

Every 2016 blocks (~2 weeks), retarget so that the previous 2016 blocks took ~2 weeks of wall time. This is what gives Bitcoin its stable block interval despite enormous hashrate growth.

### Nakamoto's security argument

If an attacker has fraction `q < 0.5` of hashrate and is `z` blocks behind, the probability they ever catch up follows a Negative Binomial. By `z=6`, P(reversal) ≈ 0.001 for `q=0.1` and falls exponentially.

This is **probabilistic finality** and the source of the "wait 6 confirmations" folklore.

---

## 3.5 Block structure

```
Header (80 bytes):
  version, prev_hash, merkle_root, timestamp, bits (target), nonce
Body:
  varint count, then transactions
```

Maximum block size: 1MB (4 MB weight after SegWit).
Average tx size: ~250 bytes → ~3.5 tx/sec theoretical max throughput. **This is the famous bottleneck**.

---

## 3.6 Mining and the incentive layer

Miner reward per block = `subsidy + transaction fees`.

| Era | Block subsidy |
|---|---|
| 2009–2012 | 50 BTC |
| 2012–2016 | 25 BTC |
| 2016–2020 | 12.5 BTC |
| 2020–2024 | 6.25 BTC |
| 2024–2028 | 3.125 BTC |
| ... | halves every 210,000 blocks (~4 yrs) |

After ~2140, subsidy → 0. Bitcoin's long-term security depends on fees alone — an open research question.

### Selfish mining (Eyal & Sirer, 2014)

A miner with >25% hashrate can withhold blocks and gain disproportionate reward — proving Nakamoto's "honest-majority" assumption was naive. Mitigations are limited; this remains the canonical critique.

---

## 3.7 The 51% attack

With >50% hashrate, an attacker can:
- Double-spend (rewrite history they were a party to)
- Censor transactions
- **Cannot**: steal coins they don't have keys for; create new coins.

Cost to attack Bitcoin at 2026 hashrate: tens of millions of USD/hour. Cost to attack a small PoW altcoin: <$1k/hour (see crypto51.app).

---

## 3.8 Lightning Network (L2)

A payment channel network on top of Bitcoin.

```
1. Alice and Bob open a 2-of-2 multisig channel with 1 BTC each.
2. They update balances off-chain by exchanging signed commitment txs.
3. Either party can broadcast the latest commitment to close.
4. HTLCs allow routing payments across multi-hop channels.
```

Throughput: theoretically millions of TPS. Tradeoffs: liquidity locked in channels, online requirements (watchtowers), routing UX problems.

---

## 3.9 SegWit, Taproot, and the upgrade path

| Upgrade | Year | What it did |
|---|---|---|
| SegWit (BIP-141) | 2017 | Separated signature data → fixed malleability, enabled Lightning |
| Taproot (BIP-340/341/342) | 2021 | Schnorr signatures + Tapscript → privacy + multi-sig efficiency |
| Inscriptions / Ordinals | 2023 | Unintended use of Taproot data → on-chain NFTs |
| Future: covenants (OP_CAT, CTV) | TBD | Programmable spending conditions, vaults |

---

## 3.10 What Bitcoin is *not*

- Not anonymous — pseudonymous; chain analysis routinely de-anonymizes addresses.
- Not free — fees fluctuate $0.50 to $50+.
- Not energy-efficient — ~150 TWh/yr, comparable to a mid-size country.
- Not fast — 7 tx/sec, 60-minute finality.

These limitations created the design space every other blockchain explores.

---

## 3.11 Reading list

- Nakamoto — *Bitcoin: A Peer-to-Peer Electronic Cash System*, 2008.
- Eyal & Sirer — *Majority is not Enough: Bitcoin Mining is Vulnerable*, FC 2014.
- Antonopoulos — *Mastering Bitcoin* (2nd ed).
- Garay, Kiayias, Leonardos — *The Bitcoin Backbone Protocol*, Eurocrypt 2015.
- Sompolinsky & Zohar — *Secure High-Rate Transaction Processing in Bitcoin*, FC 2015.
- Poon & Dryja — *Lightning Network paper*, 2016.

## 3.12 Lab (3 hrs)

1. Connect to a Bitcoin testnet node (use `bitcoind` regtest or a public Esplora API).
2. Generate two keypairs, fund one from a faucet, create + sign + broadcast a transaction to the second.
3. Decode the resulting transaction and identify every field.
4. Inspect 3 real mainnet blocks and compute their fee revenue vs subsidy.

## 3.13 Quiz

1. Why does Bitcoin use the UTXO model instead of account balances?
2. What probability of reversal does Nakamoto's analysis give for `q=0.3, z=6`?
3. Explain selfish mining in one sentence and the minimum hashrate for it to be profitable.
4. What is the maximum theoretical TPS on Bitcoin L1, and what limits it?
5. Name two changes Taproot enabled and one second-order effect (e.g., Ordinals).
