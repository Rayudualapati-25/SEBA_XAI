# Blockchain Module 10 — Governance & Tokenomics

> **Goal**: Understand how decisions get made in protocols, why token economics shapes (and breaks) protocols, and what's actually known from empirical research.

---

## 10.1 Two governance layers

1. **Protocol governance** — chain itself (Bitcoin BIPs, Ethereum EIPs).
2. **Application governance** — on-chain DAOs (MakerDAO, Compound, Uniswap, Arbitrum DAO).

The mechanisms and incentive structures look superficially similar but operate very differently.

---

## 10.2 Bitcoin's governance — "rough consensus"

- BIPs (Bitcoin Improvement Proposals) → reference implementation → miners signal → users decide via running software (UASF).
- 2017 SegWit / Big Block war showed that **users**, not miners, are the ultimate authority — bitcoin (BTC) followed the user-activated soft fork while Bitcoin Cash split off.

The lesson: in PoW, **hashrate is hired, not sovereign**.

---

## 10.3 Ethereum's governance — coordinated chaos

- **EIPs** (Ethereum Improvement Proposals) drafted by core devs.
- **All Core Devs Calls** (ACD) — weekly meeting, no formal vote.
- **Client diversity** — Geth, Nethermind, Erigon, Besu, Reth — implementations must agree or chain forks.
- **Validators / users** ratify by running upgraded clients.

This loose process has produced the smoothest L1 upgrade cycle in the space (London, Shanghai, Cancun, Pectra, Fusaka).

---

## 10.4 DAO governance — the on-chain experiment

### Mechanisms

| Type | Example | Notes |
|---|---|---|
| **Token-weighted voting** | Compound, Uniswap | Plutocratic; whales dominate |
| **Conviction voting** | 1Hive | Stake longer → more weight |
| **Quadratic voting** | Gitcoin Grants | Mitigates whales; Sybil-vulnerable |
| **Reputation / soulbound** | Coordinape, BrightID | Non-transferable |
| **Optimistic / delegated** | Optimism Citizens' House | Bicameral hybrid |
| **veToken** | Curve, Velodrome | Lock tokens to gain voting + boost |

### The veToken / bribe model

CRV locked → veCRV → vote weight on gauges → directs CRV emissions → projects bribe veCRV holders for emissions → secondary market on vlCVX (Convex). This is the **Curve Wars** — a real, multi-billion-dollar incentive market.

---

## 10.5 Tokenomics as a discipline

A protocol's token simultaneously plays three roles:

1. **Security** — bonded stake for PoS, fees for L1s, slashing collateral.
2. **Governance** — voting rights.
3. **Cash flow** (sometimes) — buybacks, fee dividends.

### Token supply schedules

| Pattern | Example |
|---|---|
| Fixed cap, halving | Bitcoin (21M) |
| Fixed cap, vesting | Most VC tokens (cliff + linear) |
| Inflationary | Ethereum issuance, Cosmos |
| Burn-deflationary | EIP-1559 (Ethereum), BNB |
| Rebasing | OHM, AMPL |
| Bond-curve / continuous | Olympus, Fei (RIP) |

### Vesting cliff "unlock walls"

Most VC-funded tokens unlock 6–36 months after TGE. Look at **Token Unlocks** or **TokenTerminal** to spot incoming sell pressure.

---

## 10.6 Real fundamentals: fees & revenue

After 2021's hype, the industry shifted to real revenue analysis:

| Metric | What it means |
|---|---|
| **Fees** | Total paid by users |
| **Revenue** | Fees minus distributions back to users (e.g., to LPs) |
| **PE-style ratios** | FDV / annualized revenue |
| **Take rate** | Protocol's share of total fees |

Tools: **Token Terminal, DefiLlama, Dune Analytics, Artemis**.

---

## 10.7 Governance attacks

### Beanstalk (2022)

Attacker took a $1B flash loan, used it to vote in a malicious proposal that drained the treasury. Lesson: **time-lock all proposals**; never allow flash-loaned governance.

### Tornado Cash governance (2023)

Attacker proposed an "upgrade" with a hidden malicious payload, passed it, took control. Lesson: review every line of every proposal, including innocuous-looking ones.

### Quorum / voter apathy

Most DAOs see <5% voter turnout. A motivated minority can dominate. Mitigations: delegation (Compound's COMP delegates), proxy advisors (Tally), executive committees.

---

## 10.8 Mechanism design themes

| Mechanism | Use |
|---|---|
| Vickrey auctions | NFT mints (rarely used yet) |
| Harberger taxes | Radical Markets, partial-common-ownership land |
| Quadratic funding | Public goods (Gitcoin) |
| Curation markets | Token-curated registries (TCRs) |
| Conviction voting | Long-term decisions |

Most live DAOs still use simple token-weighted voting because anything else is harder to explain to participants.

---

## 10.9 Public goods funding

Open problem: how do you fund clients, libraries, audits — the underfunded layer of every blockchain?

- **Optimism RetroPGF** — retroactive payouts to ecosystem builders.
- **Gitcoin Grants** — quadratic funding rounds.
- **Protocol Guild** — Ethereum core dev vesting from app projects.
- **EIP-1559** — burns fees, distributes value indirectly to holders, not to builders.

---

## 10.10 Regulation

| Jurisdiction | 2026 stance (illustrative) |
|---|---|
| US | Patchwork; CFTC/SEC turf battle; ETH ETFs approved 2024 |
| EU | MiCA in force since 2024 |
| UK | Phased FCA framework |
| Singapore, UAE, HK | Active licensing regimes |
| China | Trading banned; CBDC heavy |

Effects on protocols:
- KYC requirements for fiat ramps and stablecoin issuers.
- Sanctions screening (Tornado Cash sanctions, 2022).
- "Decentralization sufficiency" — ongoing legal test.

---

## 10.11 Reading list

- Buterin — *Notes on Blockchain Governance*, 2017.
- Werner et al. — *SoK: Decentralized Finance (DeFi)*, AFT 2022 (governance section).
- Posner & Weyl — *Radical Markets*, Princeton UP, 2018 (quadratic voting, Harberger).
- Buterin, Hitzig, Weyl — *A Flexible Design for Funding Public Goods*, 2019.
- Fritsch, Müller, Wattenhofer — *Analyzing Voting Power in Decentralized Governance*, 2022.
- *MakerDAO Whitepaper*; *Uniswap Governance docs*.

## 10.12 Lab (2 hrs)

1. Browse Tally.xyz. Pick one active proposal in a top-5 DAO; read it end-to-end.
2. Plot a token's circulating supply over time + scheduled unlocks (use Token Unlocks data).
3. Compute Compound's PE = FDV / annualized revenue from DefiLlama. Compare to Aave, Uniswap.

## 10.13 Quiz

1. Why is the Bitcoin SegWit/BCH split evidence that hashrate isn't sovereign?
2. State one weakness of token-weighted voting and one of quadratic voting.
3. Explain the veToken bribe market in one paragraph.
4. What did Beanstalk teach about flash-loan governance defense?
5. Why might fees ≠ revenue for an AMM?
