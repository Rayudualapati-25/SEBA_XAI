# Blockchain Module 8 — DeFi Architecture

> **Goal**: Understand DeFi as a system of **composable financial primitives**, the math behind AMMs, and the systemic risks (oracles, MEV, governance attacks).

---

## 8.1 What makes DeFi different

DeFi = **Decentralized Finance** — financial applications running on permissionless smart contract platforms. Distinctive properties:

- **Non-custodial** — users hold their own keys.
- **Composable ("money legos")** — protocols call other protocols permissionlessly.
- **Public state** — every position is visible and analyzable.
- **24/7** and global.

These are also its risk surface.

---

## 8.2 The DeFi stack

| Layer | Examples |
|---|---|
| Stablecoins | USDC, USDT, DAI, FRAX, GHO |
| DEXes | Uniswap, Curve, Balancer, dYdX |
| Lending | Aave, Compound, Morpho, Spark |
| Derivatives | dYdX, GMX, Synthetix, Hyperliquid |
| Yield aggregators | Yearn, Beefy, Pendle |
| Liquid staking | Lido, Rocket Pool, EtherFi |
| Restaking | EigenLayer, Symbiotic, Karak |
| Bridges | Wormhole, LayerZero, Across, Hop |
| Oracles | Chainlink, Pyth, RedStone, UMA |

---

## 8.3 Automated Market Makers (AMMs)

Replace order books with a deterministic price function `f(x, y) = k`.

### Uniswap v2 — Constant Product

```
x * y = k
```

If you swap `dx` X-tokens in, you receive `dy = y - k/(x+dx)` Y-tokens. The price slips along the curve.

### Slippage and impermanent loss

- **Slippage** — large trades move price along curve.
- **Impermanent loss (IL)** — LPs lose vs. just holding when prices diverge:
```
IL(r) = 2·sqrt(r)/(1+r) - 1,  where r = price_now/price_initial
```
A 2× price move → ~5.7% IL. A 5× move → ~25%.

### Curve — StableSwap

Optimized for assets that trade near parity (USDC/DAI). Hybrid of constant-sum (near parity) and constant-product (at extremes), via an amplification coefficient `A`.

### Uniswap v3 — Concentrated Liquidity

LPs supply liquidity within a **price range** `[p_a, p_b]`. Capital efficiency 100×–4000× higher than v2, but requires active management and IL is amplified.

### Balancer

Weighted constant-product across N tokens:
```
∏ x_i^w_i = k,  where Σ w_i = 1
```
Lets you build custom index funds as AMMs.

### Uniswap v4 — Hooks

Pools become extensible — anyone can attach pre/post hooks (custom fees, dynamic fees, on-chain limit orders). The standard for AMM customization in 2024–2026.

---

## 8.4 Lending markets

Two dominant designs:

### Pool-based (Aave, Compound)

Suppliers deposit into a pool, borrowers draw with overcollateralization. Interest rate is a deterministic function of utilization.

```
borrow_rate = base + slope1·U + slope2·max(U - kink, 0)
```

### Isolated / Peer-to-Pool (Morpho)

Match P2P when possible, fall back to pool. Improves capital efficiency.

### Liquidation

If collateral / debt < `liquidation_threshold`, anyone can repay part of debt in exchange for collateral at a discount (liquidation bonus). This keeps the system solvent.

Liquidation cascades during 2020's "Black Thursday" and 2022's collapse showed the system works, but with brutal slippage.

---

## 8.5 Stablecoins

| Type | Mechanism | Example |
|---|---|---|
| **Fiat-backed** | 1:1 USD reserves | USDC, USDT |
| **Crypto-backed (CDP)** | Over-collateralized vaults | DAI, LUSD |
| **Algorithmic** | Mint/burn against another token | UST (failed catastrophically), AMPL |
| **Hybrid / partially-collateralized** | Mix | FRAX (legacy), GHO |
| **LSD-backed** | Liquid-staking tokens as collateral | eUSD, USDe |

The **Terra/UST collapse** (May 2022) eliminated the pure-algo design space for years.

---

## 8.6 Oracles — DeFi's biggest single risk

Smart contracts can't read external prices. They depend on **oracles**.

| Type | Example |
|---|---|
| **Push** | Chainlink price feeds update on-chain at threshold/interval |
| **Pull** | Pyth — signed prices fetched on demand |
| **Optimistic** | UMA — assertions, dispute window |
| **TWAP** | Uniswap v3 time-weighted price |

### Oracle attacks

Flash-loan-fueled price manipulation drained Mango Markets ($117M, 2022), bZx, Cream, and many others. Mitigations:
- Use TWAPs (manipulating averages requires sustained capital).
- Use chain-of-custody-signed oracles (Pyth Pull).
- Cross-check multiple sources.

---

## 8.7 Flash loans

Borrow any amount with **no collateral**, provided the loan is repaid in the same transaction. If not, the tx reverts atomically.

```solidity
function flashLoan(uint256 amount, bytes calldata data) external {
    uint256 before = token.balanceOf(address(this));
    token.transfer(msg.sender, amount);
    IFlashBorrower(msg.sender).onFlashLoan(amount, data);
    require(token.balanceOf(address(this)) >= before + fee, "not repaid");
}
```

Legitimate use: arbitrage, collateral swaps, self-liquidation.
Attack use: capital-free price manipulation (Mango, bZx, Cream).

The asymmetry — anyone can borrow $100M for one transaction — is uniquely DeFi.

---

## 8.8 MEV (Maximal Extractable Value)

Profit available to whoever orders transactions. Categories:

| Category | Example |
|---|---|
| Arbitrage | Same asset different prices on two DEXes |
| Sandwich | Insert buy before / sell after a victim's swap |
| Liquidation | Race to liquidate underwater positions |
| Long-tail | NFT mints, contract-state predictions |

**Flashbots** introduced auctions for MEV (MEV-Boost). On Ethereum, ~90%+ of validators run MEV-Boost, separating proposers from builders (**PBS**).

### MEV mitigation

- **Encrypted mempools** (Shutter, SUAVE)
- **Order flow auctions** (CoWSwap, UniswapX)
- **Fair ordering** (Themis, Pompê)
- **Threshold encryption** (Osmosis)

---

## 8.9 Composability — and its dark side

Aave → Lido → Curve → Yearn → Convex — a single user position can span 5+ protocols. This is brilliant and dangerous:

- **Contagion** — one exploit propagates through every composing protocol.
- **Reentrancy across protocols** — calls back through hooks can violate invariants.
- **Read-only reentrancy** — even view functions are unsafe during external calls.

Major incidents: Curve reentrancy (2023, $73M), Euler ($197M), Compound oracle glitch.

---

## 8.10 Restaking and shared security

**EigenLayer** (2023): let ETH stakers opt-in to securing additional services (oracles, DA layers, sidechains, AVSs). Liquid restaking tokens (LRTs) compound positions.

Risk: **systemic slashing** — a single AVS bug could cascade. Aggregate restaked ETH at peak: tens of billions of USD.

---

## 8.11 Reading list

- Adams, Zinsmeister, Salem, Keefer, Robinson — *Uniswap v3 Core*, 2021.
- Egorov — *StableSwap — efficient mechanism for Stablecoin liquidity*, 2019.
- Daian et al. — *Flash Boys 2.0*, S&P 2020.
- Qin, Zhou, Gervais — *Quantifying Blockchain Extractable Value*, S&P 2022.
- Werner et al. — *SoK: Decentralized Finance (DeFi)*, AFT 2022.
- Lo, Verma — *DeFi protocols for loanable funds*, AFT 2021.
- Klages-Mundt, Minca — *(In)stability for the Blockchain*, 2020 (algorithmic stablecoin analysis).

## 8.12 Lab (3 hrs)

1. Fork Ethereum mainnet locally with `anvil --fork-url`.
2. Deposit ETH into Uniswap v3 ETH/USDC pool at a chosen tick range. Measure fees earned for 1 hour of simulated swaps.
3. Implement a flash-loan arbitrage between Uniswap v2 and Sushiswap (clone Uni v2). Find a path where it's profitable in fork state.
4. Write a postmortem of one major 2022–2024 DeFi exploit.

## 8.13 Quiz

1. Derive the IL formula `2√r/(1+r) - 1` for constant-product AMMs.
2. Why are TWAP oracles harder to manipulate than spot oracles?
3. Explain the difference between push and pull oracles.
4. State three legitimate uses of flash loans.
5. Why does Uniswap v3 concentrated liquidity require active management?
