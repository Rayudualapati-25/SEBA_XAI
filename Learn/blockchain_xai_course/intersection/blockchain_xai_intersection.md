# Intersection — Verifiable, Explainable, and Decentralized AI

> **Goal**: This is the research-value module. Where Blockchain meets XAI, several emerging research lines need contributors. A Master's thesis here has unusually high impact-per-effort ratio.

---

## I.1 Why these two fields converge

Blockchain solves: **verifiability and integrity of computation in adversarial environments.**
XAI solves: **understanding and trust of model behavior.**

Together, they tackle the question:

> *Can we know — and prove — what an AI did, why it did it, and that no one tampered with it?*

Three convergence areas:

1. **Verifiable AI** — cryptographic proofs that a model output is correct (ZKML).
2. **Decentralized AI** — model training/inference distributed and incentivized via tokens.
3. **Auditable / Explainable AI** — on-chain logs and explanations for regulatory compliance.

---

## I.2 ZKML — Zero-Knowledge Machine Learning

### The problem

A model owner can prove to a verifier that:
- "This output `y` is the result of running model `M` on input `x`."

Optionally hiding:
- The model weights (IP protection)
- The input (privacy)
- Both

### Why hard

Neural networks use:
- **Floating-point arithmetic** — ZK circuits work over finite fields → quantization required.
- **Non-linear ops** (ReLU, GELU, softmax) — expensive to express in arithmetic constraints.
- **Large parameter counts** — billions of multiplications → billions of constraints.

### Active toolchains (2024–2026)

| Tool | Approach |
|---|---|
| **EZKL** | Halo2 backend, ONNX-friendly. Quantization + lookup-arg optimizations |
| **Modulus Labs (Remainder)** | GKR / sum-check for matrix multiplications |
| **Risc Zero zkVM** | General-purpose zkVM, run PyTorch in Rust via tract |
| **Giza** | StarkNet + Cairo for on-chain inference |
| **DDKang's zkml** | Halo2, focused on ResNet-scale |
| **Inference Labs** | Production ZK inference SaaS |
| **Worldcoin** | Uses semaphores + ZK for proof of personhood |

### State of the art

- ResNet-50 inference: provable in ~minutes on modern hardware, ~MB proofs.
- Small CNN MNIST: seconds, KB proofs.
- LLMs (>1B parameters): largely impractical end-to-end today; partial proofs possible.

### Why it matters for XAI

A ZK proof of *correct inference* is necessary but not sufficient for trust.
The next step: **ZK proofs of explanation**. Examples:
- Prove that a SHAP value reported externally was correctly computed from the model.
- Prove that a counterfactual explanation is genuinely the minimum-cost one.
- Prove that an attention-based "reason" was correctly extracted.

This is **mostly open research as of 2026** — there's room for early entrants.

---

## I.3 On-chain machine learning

### Approaches

| Approach | Trust assumption |
|---|---|
| Inference **off-chain**, post **proof on-chain** | ZK or optimistic |
| Inference **on-chain** in a smart contract | High gas; bounded models only |
| Inference in **TEE** with attestation | Hardware trust (Intel SGX, AMD SEV) |
| Inference via **MPC** | Multiple non-colluding parties |
| Inference with **FHE** | Pure cryptography, very expensive |

EVM-based on-chain ML (Modulus Labs' Ocean, ORA) typically posts ZK proofs of small models for verifiable randomness, oracle aggregation, content moderation triggers, etc.

---

## I.4 Decentralized AI infrastructure

### Compute marketplaces

| Project | Layer |
|---|---|
| **Akash** | General Kubernetes compute |
| **Render** | GPU rendering + ML inference |
| **io.net** | Distributed GPU cluster |
| **Gensyn** | Distributed training with verification |
| **Bittensor** | Subnet-based incentivized model marketplace |
| **Ritual** | AI inference oracle for smart contracts |

Trust model varies — some use ZK, some use challenge-response / fraud proofs.

### Model marketplaces & reputation

Open problems:
- How do you verify a model's claimed performance?
- How do you reward good models without enabling sybils?
- How do you handle adversarial submissions (model poisoning)?

Bittensor's "Yuma consensus" weights subnet contributions by peer voting — a research-grade mechanism design effort.

---

## I.5 Federated learning + blockchain

Federated learning (FL) trains a model across many devices without centralizing data. Blockchains can:
- Coordinate aggregation rounds.
- Reward participants by stake / contribution.
- Audit updates for poisoning.
- Verify aggregation via ZK / MPC.

Research papers stack: FL + blockchain + differential privacy + XAI.

Trust model: typically a permissioned consortium chain (Hyperledger Fabric, IBC chains). Honest-majority assumption.

---

## I.6 Decentralized identity and AI

| Tool | Use |
|---|---|
| **W3C DIDs / Verifiable Credentials** | Self-sovereign identity |
| **Soulbound tokens (SBT)** | Non-transferable reputation |
| **zkID / Sismo / Worldcoin** | Privacy-preserving "uniqueness" proofs |
| **Polygon ID** | Selective disclosure of attributes |

Why for AI: deepfake / agentic-AI era requires **proof of personhood** to distinguish humans from agents. Worldcoin's iris-scan-based PoP is the most controversial deployment.

---

## I.7 Audit trails: explanations on-chain

For regulatory compliance, you may want:

```
inputs_hash + model_hash + outputs_hash + explanation_hash → on-chain commitment
```

Anyone can later verify the audit trail. Variants:
- **Off-chain explanation, on-chain hash** (cheap, requires data availability).
- **On-chain explanation** (expensive, only for small models or critical decisions).
- **ZK explanation** (prove the explanation was correctly computed without revealing input or model).

Use cases:
- Credit decision explanations stored immutably for regulator audit.
- Healthcare AI outputs with retroactive verifiability.
- Election counting AI with public auditability.

---

## I.8 Adversarial concerns

This intersection inherits **both** fields' attack surfaces:

| From blockchain | From XAI |
|---|---|
| 51% attack on verification chain | Adversarial explanations (Slack et al.) |
| Bridge hacks (cross-chain proofs) | Fairwashing |
| Oracle manipulation | Manipulated saliency |
| MEV on inference auctions | CoT unfaithfulness |
| Smart contract bugs in verifier | Proof-system soundness bugs |

New combined risks:
- **Adversarial ZK proofs** — soundness errors in custom circuits.
- **Quantization attacks** — exploit the fp→fixed conversion to skew explanations.
- **Replay of stale model commitments**.
- **Sybil attacks on decentralized model voting**.

---

## I.9 Open research questions

1. **Sub-second ZK proofs of small NN inference + SHAP** — currently minutes; gap is 100×.
2. **Faithful, provable LLM explanations** — combining mech-interp with ZK.
3. **Decentralized model training with verifiable convergence** — beyond FedAvg + Merkle commits.
4. **Privacy-preserving fairness audits** — prove fairness without revealing individual records.
5. **Soulbound reputation for model providers** with non-gameable scoring.
6. **Cross-chain AI oracles** — AI predictions consumed across multiple L1s.
7. **MEV-protected AI inference markets**.
8. **Compliance-grade audit trails** for EU AI Act, with ZK for trade-secret protection.
9. **On-chain explanation registries** that survive model versioning.
10. **Watermarking AI outputs** with blockchain-anchored provenance (deepfake defense).

---

## I.10 Sample research project (Master's-scale)

**Title**: "Verifiable Feature Attribution for Black-Box Inference: A ZK-SHAP Prototype"

**Plan**:
1. Train a small (1–5M param) tabular model.
2. Implement KernelSHAP in a ZK-friendly form (fixed-point, batch evaluation).
3. Compile to EZKL / Risc Zero.
4. Generate proofs for ~10 test inputs; measure proof size, prover time, verifier gas.
5. Test soundness via adversarial model (Slack attack adapted) — does the proof catch it?
6. Write up as a workshop paper (target: AFT, IEEE Blockchain, BlackBoxNLP, or zkProof workshop).

This is a clean, novel intersection topic with a 3–6 month timeline.

---

## I.11 Reading list

- Kang, Hashimoto, Stoica, Sun — *zkML and verifiable inference* (various 2023–2024 papers).
- Lee, Kang, Lee, Boneh — *EZKL and Halo2 ZK Inference*, 2023.
- Feng, Yan, Zhao, Lai, Lin — *Cerberus: ZK-SNARK-based Verifiable ML Inference*, 2021.
- Liu, Xie, Zhang — *zkCNN: Zero-Knowledge Proofs for Convolutional Neural Networks*, CCS 2021.
- Modulus Labs — *Cost of Intelligence* benchmark.
- Bittensor whitepaper.
- McMahan et al. — *Communication-Efficient Learning of Deep Networks from Decentralized Data (FedAvg)*, AISTATS 2017.
- Bonawitz et al. — *Practical Secure Aggregation for Privacy-Preserving ML*, CCS 2017.
- Karimi et al. — *Verifiable Federated Learning via ZK proofs*, various 2023.
- W3C — *DID Specification*; *Verifiable Credentials Data Model*.
- *EU AI Act* — Articles on high-risk systems and transparency.

## I.12 Lab (5 hrs)

1. Install EZKL.
2. Train a 2-layer MLP on MNIST in PyTorch; export to ONNX.
3. Run `ezkl gen-settings`, `compile-circuit`, `setup`, `gen-witness`, `prove`, `verify`.
4. Time the proving step; measure proof size.
5. Compute a SHAP explanation off-chain; commit its hash on Sepolia.

## I.13 Quiz

1. Why are ReLU and softmax expensive in ZK circuits?
2. State three trust models for on-chain ML.
3. How would you prove "this SHAP value was correctly computed" without revealing the model?
4. Why does Bittensor's Yuma consensus need a mechanism-design contribution to remain non-gameable?
5. Pick one of the 10 open research questions and write a 3-sentence research plan.
