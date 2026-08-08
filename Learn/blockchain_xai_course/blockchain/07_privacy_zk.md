# Blockchain Module 7 — Privacy & Zero-Knowledge Proofs

> **Goal**: Build the mental model for ZK proofs — what they prove, what they hide, and the algebraic machinery that makes it possible. ZK is the most transformative cryptographic tool of the decade.

---

## 7.1 What is a zero-knowledge proof?

A protocol by which a **prover** convinces a **verifier** that a statement `x ∈ L` (some language L) is true, without revealing anything beyond that fact.

### Three properties

1. **Completeness** — if `x ∈ L`, an honest prover convinces an honest verifier.
2. **Soundness** — if `x ∉ L`, no malicious prover can convince an honest verifier (except with negligible probability).
3. **Zero-knowledge** — the verifier learns nothing about the witness `w` beyond `x ∈ L`.

Formalized by Goldwasser, Micali, Rackoff, 1985 (STOC).

---

## 7.2 Why ZK matters for blockchains

| Use case | Why ZK |
|---|---|
| **Privacy** (Zcash, Aleo) | Hide sender, receiver, amount |
| **Scalability** (ZK rollups) | One proof verifies thousands of txs |
| **Identity** (Worldcoin, Sismo) | Prove "I am unique human" without revealing who |
| **Compliance** (Aztec, zkKYC) | Prove "I am not on a sanctions list" without revealing identity |
| **ML** (zkML) | Prove inference was done correctly without revealing model or input |

---

## 7.3 Interactive vs non-interactive

| Type | Form | Use case |
|---|---|---|
| **Interactive (IP)** | Multi-round dialogue | Theory, identification protocols |
| **Non-interactive (NIZK)** | Single message via random oracle (Fiat-Shamir) | Blockchains (no interaction with miners possible) |

**Fiat-Shamir heuristic**: replace verifier challenges with hash of transcript. Compatible with public broadcast.

---

## 7.4 The SNARK / STARK family

| Property | SNARK | STARK |
|---|---|---|
| Trusted setup | Often needed (Groth16) | Never |
| Proof size | ~200 bytes | ~50–200 KB |
| Verifier time | ~5 ms | ~10–40 ms |
| Prover time | Slow | Faster (with FRI) |
| Post-quantum | No (most) | Yes |
| Crypto basis | Pairings (BN254/BLS12-381) | Hash functions only |

### SNARK construction families

- **Groth16** (2016) — smallest proofs, per-circuit trusted setup. Used by Zcash Sapling.
- **PLONK** (2019) — universal trusted setup (one per chain). Halo2, plonky2/3 build on this.
- **Marlin** — universal setup, smaller proofs than PLONK in some settings.
- **Halo / Halo2** — no trusted setup, recursive composition. Used by Zcash Orchard, Mina.
- **Nova / SuperNova / HyperNova** — incrementally verifiable computation (IVC) via folding. Hot 2023–2026 research.

### STARK

Ben-Sasson, Bentov, Horesh, Riabzev (2018). Transparent (no trusted setup), post-quantum, uses FRI for polynomial commitments. Used by StarkNet.

---

## 7.5 The circuit abstraction

To prove "I know `w` such that `C(x, w) = 0`", we express `C` as an **arithmetic circuit** over a finite field.

```
Inputs: public x, private w
Each gate: addition or multiplication over F_p
Output: 0 if predicate holds
```

Then we reduce circuit satisfaction to a polynomial identity (e.g., **R1CS** → **QAP** for Groth16, **AIR** → **FRI** for STARKs).

---

## 7.6 A concrete tiny example

Prove "I know `x` such that `H(x) = y`" without revealing `x`:

1. Write SHA-256 as an arithmetic circuit (~25k constraints in R1CS).
2. Run the SNARK prover with witness `x` and public input `y`.
3. Verifier checks the proof.

This is what every privacy coin does for `(sender, amount)`.

---

## 7.7 zkSNARKs in writing real circuits

Modern toolchains:

| DSL / framework | Backend | Used for |
|---|---|---|
| **Circom** | Groth16, PLONK | Hands-on, large ecosystem |
| **Noir** (Aztec) | UltraPlonk | Rust-like syntax |
| **Cairo** (StarkWare) | STARK | StarkNet |
| **Halo2** | Halo2 / IPA | zkEVMs (Scroll) |
| **Risc Zero zkVM** | STARK + recursion | "Prove any Rust program" |
| **SP1** (Succinct) | STARK / Plonky3 | General zkVM |

zkVMs (Risc Zero, SP1, Jolt, Zeth) are the "compiler" wave — instead of hand-writing circuits, compile arbitrary programs into ZK-provable form.

---

## 7.8 Privacy-preserving cryptocurrencies

| Project | Mechanism |
|---|---|
| **Zcash** | zk-SNARK over Sapling/Orchard circuits |
| **Monero** | Ring signatures + RingCT + stealth addresses (not ZK, but related) |
| **Aleo** | zkSNARK-based programmable privacy |
| **Aztec** | zk-private smart contracts (Noir + UltraPlonk) |
| **Penumbra** | Private DeFi in the Cosmos ecosystem |

---

## 7.9 Multi-Party Computation (MPC) and FHE (briefly)

| Tool | What it does |
|---|---|
| **MPC** | Multiple parties compute `f(x1,...,xn)` without revealing individual `xi` |
| **FHE** | Compute on encrypted data; only key holder can decrypt result |
| **TEE** | Hardware enclave (Intel SGX, AMD SEV) for confidential computation |

These are complements to ZK, not substitutes. ZK proves correctness; MPC/FHE compute confidentially.

---

## 7.10 ZK + AI = zkML (preview)

Active research: prove a neural network's inference was performed correctly without revealing the model weights (or the input).

Why hard:
- Floating-point → field arithmetic
- Non-linear ops (ReLU, softmax) → expensive constraints
- Large models → billions of constraints

Frameworks: **EZKL, ZKonduit, Modulus Labs, Giza, Risc Zero zkML**.

Covered in [Intersection module](../intersection/blockchain_xai_intersection.md).

---

## 7.11 Reading list

- Goldwasser, Micali, Rackoff — *The knowledge complexity of interactive proof systems*, 1985.
- Groth — *On the size of pairing-based non-interactive arguments*, 2016.
- Gabizon, Williamson, Ciobotaru — *PLONK*, 2019.
- Ben-Sasson et al. — *Scalable, transparent, and post-quantum secure computational integrity*, 2018.
- Bowe, Grigg, Hopwood — *Halo: Recursive proof composition without a trusted setup*, 2019.
- Kothapalli, Setty, Tzialla — *Nova*, CRYPTO 2022.
- Boneh, Drake — *zkSNARKs in practice* (Stanford lectures).

## 7.12 Lab (4 hrs)

1. Install Circom + snarkjs.
2. Write a circuit that proves knowledge of `x` such that `x*x = 25` without revealing whether `x=5` or `x=-5`.
3. Compile, do trusted setup, generate proof, verify on-chain (deploy verifier contract to Sepolia).
4. Then write a Poseidon hash circuit and a Merkle inclusion proof. (Use existing libs.)

## 7.13 Quiz

1. State the three properties of a ZKP.
2. What problem does Fiat-Shamir solve?
3. Compare Groth16 and PLONK on (setup, proof size, prover time).
4. Why are STARKs considered post-quantum and SNARKs (mostly) not?
5. What is a zkVM and how does it differ from writing a custom circuit?
