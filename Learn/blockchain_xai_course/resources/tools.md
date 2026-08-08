# Tools & Libraries — A Practitioner's Stack

Pick one tool per row; the alternatives are listed in priority order.

---

## Blockchain dev

| Need | Tool |
|---|---|
| Local EVM dev | **Foundry** (anvil, forge, cast) > Hardhat |
| Bitcoin testing | **bitcoind regtest** |
| Block explorer / API | **Etherscan, Beaconcha.in, Mempool.space** |
| Indexing | **The Graph, Subsquid, Goldsky** |
| RPC | **Alchemy, Infura, QuickNode, Public RPCs (Llama Nodes)** |
| Wallet (dev) | **Metamask, Rabby, Frame** |
| Hardware wallet | **Ledger, Trezor, GridPlus, Keystone** |
| Multisig | **Safe (formerly Gnosis Safe)** |
| Solidity static analysis | **Slither** |
| Solidity fuzzing | **Echidna, Foundry invariants** |
| Symbolic execution | **Mythril, Halmos** |
| Formal verification | **Certora, KEVM, Halmos** |
| Subgraph dev | **Graph CLI** |
| L2 dev | **op-stack, Arbitrum SDK, zkSync CLI, Scroll, StarkNet CLI** |
| MEV research | **Flashbots mev-inspect, Libmev** |

---

## ZK tools

| Need | Tool |
|---|---|
| Circuit DSL (intermediate) | **Circom** |
| Circuit DSL (modern) | **Noir (Aztec)** |
| STARK-native circuits | **Cairo (StarkWare)** |
| Halo2 circuits | **Halo2 (Zcash)** |
| ZK virtual machines | **Risc Zero, SP1 (Succinct), Jolt, Nexus, Zeth** |
| ML inference proofs | **EZKL, Modulus, Giza, DDKang/zkml** |
| Recursion / folding | **Nova, HyperNova, ProtoStar implementations** |
| Trusted setup | **Powers of Tau (Ethereum KZG ceremony reuse)** |

---

## ML / XAI libraries

| Need | Tool |
|---|---|
| Deep learning | **PyTorch** (primary), JAX, TensorFlow |
| Tabular ML | **XGBoost, LightGBM, CatBoost, scikit-learn** |
| Interpretable tabular | **InterpretML (EBM), pyGAM, Linear/Ridge** |
| Feature attribution | **SHAP, LIME, Captum (PyTorch), tf-explain** |
| Counterfactuals | **DiCE, AlibiExplain, CARLA, OmniXAI** |
| Concept-based | **TCAV (Google), CRAFT (Fel)** |
| Saliency for CV | **Captum, Grad-CAM++, pytorch-grad-cam** |
| LLM interpretability | **TransformerLens, nnsight, SAELens, Neuronpedia** |
| Probing | **DiscoLib, custom** |
| Evaluation | **Quantus, OpenXAI, ERASER datasets** |
| Fairness | **Fairlearn, AIF360, Aequitas** |
| Robustness | **CleverHans, Foolbox, AutoAttack** |

---

## Datasets to know

### Tabular XAI staples

| Dataset | Use |
|---|---|
| UCI Adult / German Credit | Tabular fairness + counterfactuals |
| California Housing | Regression baseline |
| FICO HELOC | Interpretable credit modeling |
| COMPAS | Recidivism / fairness debates |

### Vision

| Dataset | Use |
|---|---|
| ImageNet | Classic CNN attribution |
| CIFAR-10/100 | Quick saliency experiments |
| Broden | Network Dissection concepts |
| Caltech-UCSD Birds 200 | ProtoPNet baseline |

### NLP

| Dataset | Use |
|---|---|
| IMDB | Sentiment baseline |
| SNLI | Reasoning |
| ERASER suite | Rationale benchmarks |
| TruthfulQA | Hallucination |

### Medical

| Dataset | Use |
|---|---|
| MIMIC-III/IV | Clinical EHR |
| CheXpert / NIH ChestX-ray14 | Radiology |
| HAM10000 | Dermatology |

### Blockchain data

| Dataset / API | Use |
|---|---|
| Dune Analytics | SQL on chain data |
| Flipside Crypto | Analytics |
| Etherscan API | Address-level |
| DefiLlama API | TVL, protocol stats |
| Allium, Footprint | Enterprise datasets |
| Token Terminal | Revenue / metrics |
| Artemis | Cross-chain metrics |

---

## Notebooks & monitoring

| Need | Tool |
|---|---|
| Experiment tracking | **Weights & Biases, MLflow, Aim** |
| Hyperparameter search | **Optuna, Ray Tune** |
| Pipeline orchestration | **Prefect, Airflow, DVC** |
| Notebook reproducibility | **Papermill, Jupytext** |
| Paper management | **Zotero, Obsidian, Roam** |

---

## "If I had to pick five"

If you can only learn five tools, pick:

1. **PyTorch** — the deep-learning lingua franca.
2. **SHAP** — most-used XAI library.
3. **TransformerLens** — modern interpretability work depends on it.
4. **Foundry** — the Solidity dev kit.
5. **EZKL** — entry point to ZKML.

Master these five and you can read 90% of the field's papers and reproduce most experiments.
