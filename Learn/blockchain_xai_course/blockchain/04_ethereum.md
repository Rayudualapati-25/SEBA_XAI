# Blockchain Module 4 — Ethereum & Smart Contracts

> **Goal**: Understand Ethereum as a *programmable* state machine and the design choices that opened (and complicated) the smart-contract ecosystem.

---

## 4.1 The Ethereum thesis

Vitalik Buterin (2013): generalize Bitcoin's Script into a **Turing-complete VM** so that arbitrary financial logic — not just payments — can be enforced on-chain. The result was the EVM (Ethereum Virtual Machine).

### Account model vs UTXO

- **Externally Owned Accounts (EOAs)** — controlled by a private key.
- **Contract Accounts** — controlled by code (deployed at an address).

Each account has: `nonce, balance, storage_root, code_hash`. State is a Merkle Patricia Trie of all accounts.

---

## 4.2 The EVM

A 256-bit, stack-based virtual machine.

| Component | Purpose |
|---|---|
| **Stack** | 1024 slots, 256-bit words |
| **Memory** | Volatile, byte-addressable |
| **Storage** | Persistent, key→value, per contract |
| **Gas** | Metering — every opcode costs gas |
| **Logs** | Off-chain indexable events (used by The Graph) |

### Gas

Every operation consumes gas. Transaction sender sets `gas_limit` and `gas_price`. If gas runs out, execution reverts but fees are still paid. This is how the EVM avoids the halting problem despite Turing completeness.

| Op | Gas cost |
|---|---|
| ADD | 3 |
| SLOAD (read storage) | 2100 (cold) / 100 (warm) |
| SSTORE (write storage) | 20,000 (new) / 5,000 (modify) |
| CALL | 700 + memory |

These costs incentivize gas-aware contract design — a discipline as deep as low-latency C.

---

## 4.3 Solidity — the canonical language

```solidity
pragma solidity ^0.8.20;

contract ERC20 {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;

    event Transfer(address indexed from, address indexed to, uint256 value);

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "insufficient");
        balanceOf[msg.sender] -= amount;
        balanceOf[to]         += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }
}
```

Other languages: **Vyper** (Python-like, safer subset), **Huff** (low-level for gas-golf), **Fe** (Rust-inspired).

---

## 4.4 ERC standards

| ERC | Purpose | Where it shows up |
|---|---|---|
| **ERC-20** | Fungible tokens | USDC, DAI, WETH |
| **ERC-721** | Non-fungible tokens (NFTs) | CryptoPunks, BAYC |
| **ERC-1155** | Multi-token (fungible + NFT) | Game items, OpenSea |
| **ERC-4626** | Tokenized vaults | DeFi yield aggregators |
| **ERC-4337** | Account abstraction | Smart-contract wallets |
| **ERC-6551** | Token-bound accounts | NFTs that *are* wallets |

Each standard is a Schelling point — a contract that conforms slots seamlessly into the rest of the ecosystem.

---

## 4.5 The famous reentrancy bug (and the DAO hack)

```solidity
// VULNERABLE
function withdraw() external {
    uint256 bal = balances[msg.sender];
    (bool ok,) = msg.sender.call{value: bal}("");   // ← attacker re-enters here
    require(ok);
    balances[msg.sender] = 0;                       // ← updated AFTER the call
}
```

If `msg.sender` is a contract, its `receive()` function runs *during* the external call, and it can call `withdraw()` again before `balances[msg.sender]` is zeroed.

The 2016 DAO hack drained 3.6M ETH this way (~$60M then; $billions today). The fix:

```solidity
// CHECKS-EFFECTS-INTERACTIONS pattern
function withdraw() external {
    uint256 bal = balances[msg.sender];
    balances[msg.sender] = 0;                       // effect FIRST
    (bool ok,) = msg.sender.call{value: bal}("");   // interaction LAST
    require(ok);
}
```

The DAO hack triggered the contentious Ethereum / Ethereum Classic hard fork — a foundational lesson in protocol governance.

---

## 4.6 The Merge & PoS

September 15, 2022: Ethereum switched from PoW to PoS in a flawless coordination feat ("The Merge"). PoS reduced energy consumption by ~99.95%.

Validator deposit: 32 ETH. Slashing for double-signing or surround voting. Block proposers are selected by RANDAO + VRF.

Finality via **Casper FFG** — a checkpoint finality layer on top of the chain. Every epoch (32 slots × 12s = 6.4 min) validators vote on a checkpoint; once a checkpoint has 2/3 attestations *twice*, it's finalized.

---

## 4.7 Account abstraction (ERC-4337)

Traditional wallets are EOAs — keys = identity = trust root. ERC-4337 lets *any* contract act as a wallet via `UserOperations` going through a `Bundler` and `EntryPoint`. This unlocks:
- Social recovery (lose your keys, restore via friends)
- Session keys (sign once, transact for a session)
- Sponsored gas (someone else pays your gas)
- Multi-factor / passkey signing

This is the largest UX shift in Ethereum since deployment.

---

## 4.8 Layer 2 ecosystem (preview — full coverage in Module 6)

| L2 | Type | TPS |
|---|---|---|
| Arbitrum | Optimistic rollup | ~40k |
| Optimism | Optimistic rollup | ~30k |
| Base | Optimistic (Coinbase) | ~30k |
| zkSync Era | ZK rollup | ~100k* |
| StarkNet | ZK rollup (Cairo) | ~100k* |
| Polygon zkEVM | ZK rollup | ~50k* |
| Scroll | ZK rollup | ~20k* |

(* peak theoretical)

---

## 4.9 The MEV economy

Block proposers can reorder, insert, or censor transactions for profit (Maximal Extractable Value). MEV-Boost separates **block proposers** from **block builders** — proposers auction off the right to build a block. Roughly 90%+ of Ethereum validators run MEV-Boost.

This created **Proposer-Builder Separation (PBS)** as a research field — see [Module 9](09_security_attacks.md).

---

## 4.10 Reading list

- Buterin — *Ethereum White Paper*, 2013.
- Wood — *Ethereum Yellow Paper*, 2014–present.
- Antonopoulos & Wood — *Mastering Ethereum*, O'Reilly.
- Daian et al. — *Flash Boys 2.0: Frontrunning, Transaction Reordering, and Consensus Instability in DEXes*, S&P 2020.
- Buterin & Griffith — *Casper the Friendly Finality Gadget*, 2017.
- ERC-4337 spec — eips.ethereum.org/EIPS/eip-4337.

## 4.11 Lab (3 hrs)

1. Install Foundry. `forge init` a project.
2. Write an ERC-20 with `mint`, `transfer`, and `burn`. Write tests achieving 100% line coverage.
3. Write a deliberately reentrancy-vulnerable bank contract and an attacker contract that drains it.
4. Apply the checks-effects-interactions fix and prove the attack now fails.
5. Deploy to Sepolia testnet. Verify on Etherscan.

## 4.12 Quiz

1. State three differences between the UTXO and account models.
2. Why is gas necessary even though the EVM is Turing-complete?
3. What is the checks-effects-interactions pattern and which class of bugs does it prevent?
4. Explain the role of RANDAO and VRF in PoS proposer selection.
5. What problem does ERC-4337 solve, and at what cost?
