# Blockchain Module 1 — Cryptographic Foundations

> **Goal**: master the four cryptographic primitives every blockchain rests on: hash functions, Merkle trees, digital signatures, and commitment schemes. Without these, every later concept is hand-waving.

---

## 1.1 Why cryptography is the load-bearing pillar

A blockchain is, mechanically, a **replicated state machine** in an adversarial network. Cryptography gives us three guarantees we cannot get any other way:

1. **Integrity** — a hash chain lets every honest node detect tampering.
2. **Authentication** — digital signatures bind actions to identities (public keys).
3. **Commitment** — once published, a value cannot be silently changed.

Everything else (consensus, smart contracts, governance) is engineering on top of those three primitives.

---

## 1.2 Cryptographic hash functions

A hash function `H: {0,1}* → {0,1}^n` (typically n=256) is used to compress arbitrary data to a fixed-length digest.

### Required properties

| Property | Definition | Why it matters |
|---|---|---|
| **Pre-image resistance** | Given `y`, infeasible to find `x` s.t. `H(x)=y` | Hides inputs (commitments, password storage) |
| **Second pre-image resistance** | Given `x`, infeasible to find `x' ≠ x` s.t. `H(x') = H(x)` | Prevents targeted tampering |
| **Collision resistance** | Infeasible to find any `(x, x')` with `H(x)=H(x')` | Prevents two valid blocks colliding |
| **Puzzle-friendliness** | For any `k`, the distribution of `H(k‖x)` is "random enough" that you must brute-force to find solutions | Foundation of Proof-of-Work |

Standard choice: **SHA-256** for Bitcoin; **Keccak-256** for Ethereum; **BLAKE3** is faster but less established.

### Birthday bound

Collision attacks on an `n`-bit hash take roughly `2^(n/2)` work. So SHA-256 gives ~128-bit collision security — currently safe.

### Hash chain

```
block_0   block_1   block_2
[h_prev=⊥] → [h_prev = H(block_0)] → [h_prev = H(block_1)] → ...
```

Any tampered block changes its hash, breaking every subsequent link. This is the simplest data structure with **tamper evidence**.

---

## 1.3 Merkle trees

To prove that one transaction is included in a block without sending the whole block, we use a **Merkle tree** (a.k.a. hash tree).

```
          root = H(H1‖H2)
          /              \
     H1=H(A‖B)        H2=H(C‖D)
      /     \            /    \
   H(A)    H(B)        H(C)   H(D)
```

**Inclusion proof** for transaction `C`: send `H(D)` and `H1` (log n hashes). The verifier recomputes:
```
H2' = H(H(C) ‖ H(D))
root' = H(H1 ‖ H2')
```
If `root' == published root`, `C` is in the tree.

### Real-world variants

- **Bitcoin Merkle tree** — flat binary tree of transactions in a block.
- **Patricia/Verkle tries** (Ethereum) — Merkle trie indexed by account address; supports efficient state proofs.
- **Sparse Merkle trees** — used in Filecoin, rollups.
- **Verkle trees** — replace hashes with vector commitments (e.g., KZG) — proof size O(1) instead of O(log n). Important for stateless Ethereum.

### Research angle

Verkle trees, IVC (incrementally verifiable computation), and "history expiry" are active 2023–2026 research directions; see EIP-6800.

---

## 1.4 Digital signatures

Signature scheme = `(KeyGen, Sign, Verify)`.

| Scheme | Curve / basis | Used by |
|---|---|---|
| **ECDSA** | secp256k1 | Bitcoin, Ethereum (pre-account abstraction) |
| **EdDSA / Ed25519** | edwards25519 | Solana, Cardano, Tezos |
| **Schnorr (BIP-340)** | secp256k1 | Bitcoin Taproot, supports key aggregation |
| **BLS** | BLS12-381 | Ethereum consensus (validator aggregation) |

### Why BLS matters

A BLS signature scheme allows you to *aggregate* `n` signatures from `n` validators into a single 96-byte signature that verifies all of them at once. Without this, Ethereum's PoS could not scale to 1M+ validators.

### Public keys are addresses

In Bitcoin: `address = Base58Check(RIPEMD160(SHA256(pubkey)))`.
In Ethereum: `address = last 20 bytes of Keccak256(pubkey)`.

This is how a string of letters and numbers binds to a specific cryptographic identity.

---

## 1.5 Commitment schemes

A **commitment** lets you publish a binding fingerprint of a value `v` without revealing it (hiding), and later reveal `v` such that nobody can dispute it (binding).

Simplest commitment: `c = H(v ‖ r)` where `r` is a random nonce.

### Pedersen commitments

`c = v·G + r·H` where G, H are generators of an elliptic curve group with unknown discrete log relation. Pedersen is **homomorphic** — `Commit(v1) + Commit(v2) = Commit(v1+v2)` — which makes it the basis of confidential transactions (Monero, Mimblewimble).

### KZG / polynomial commitments

A KZG commitment lets you commit to a polynomial `p(x)` and later open it at any point with a constant-size proof. KZG underlies:
- Ethereum's **EIP-4844 blob transactions** (proto-danksharding)
- Verkle trees
- PLONK-family zk-SNARKs

This is *the* commitment scheme of the modern blockchain stack.

---

## 1.6 Putting it all together — a toy block

```python
class Block:
    prev_hash: bytes              # 32 bytes from previous block
    merkle_root: bytes            # root over transactions
    timestamp: int
    nonce: int                    # PoW puzzle solution
    transactions: list[Tx]

    def hash(self) -> bytes:
        return sha256(prev_hash + merkle_root + ts + nonce)

# Each Tx contains: from_pubkey, to_pubkey, amount, signature
# Tx is valid iff verify(from_pubkey, msg=(from,to,amount), signature)
```

This is — quite literally — Bitcoin minus the consensus rules.

---

## 1.7 Reading list

- Narayanan et al., *Bitcoin and Cryptocurrency Technologies*, Ch 1.
- Katz & Lindell, *Introduction to Modern Cryptography*, Ch 5 (hash) & Ch 12 (signatures).
- Boneh & Shoup, *A Graduate Course in Applied Cryptography* (free online).
- Boneh, Drake, Fisch, Gabizon — *KZG polynomial commitments and applications* (talks).
- EIP-4844 specification (proto-danksharding).

## 1.8 Lab (2 hrs)

Implement, in Python with `hashlib` and `ecdsa` only (no blockchain framework):

1. A `Block` class with header + Merkle root.
2. A `Wallet` class that generates `(privkey, pubkey, address)`.
3. A `Transaction` class with signing + verification.
4. A 5-block chain — show that flipping a bit in block 2 breaks all subsequent hashes.

## 1.9 Quiz

1. Why is collision resistance strictly stronger than second-preimage resistance?
2. What is the size (in hashes) of a Merkle proof for one of 1,048,576 leaves?
3. Why does BLS signature aggregation matter for Proof-of-Stake?
4. State one property that Pedersen has and SHA-based commitments don't.
5. Roughly how many SHA-256 evaluations are needed to find a collision?
