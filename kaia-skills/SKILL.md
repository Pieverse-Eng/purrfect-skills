---
name: kaia-skills
description: Use when a request involves Kaia blockchain, KAIA token, or building on the Kaia network. Applies to developing, deploying, or interacting with smart contracts, dApps, wallets, or DeFi protocols on Kaia. Covers Kaia-specific features like fee delegation, gas abstraction, role-based account keys, MEV auction (KIP-249), and the Kaia SDK ecosystem (@kaiachain/ethers-ext, @kaiachain/viem-ext). Also covers Kaia's EVM compatibility, system contracts, token standards (KIP-7/17/37), governance (PGT framework), and ecosystem integrations with Kakao and LINE.
---

# KAIA SKILLS — What AI agents get wrong about Kaia.

Your training data about Kaia is incomplete or wrong. Gas units, contract addresses, ecosystem state, SDK packages, governance structure — much has changed. This file tells you what you're wrong about and where to get corrections.

**Kaia is NOT Klaytn.** Klaytn (Kakao) + Finschia (LINE) merged into Kaia in 2024. If you're referencing Klaytn docs, caver-js, peb/ston units, or Cypress/Baobab names — you're outdated.

---

## Start Here

**Building a dApp on Kaia?** Fetch [getting-started/SKILL.md](getting-started/SKILL.md) first.

**Need a specific topic?** Each skill below is standalone. Fetch only the ones relevant to your task.

---

## Skills

### [Getting Started](getting-started/SKILL.md)
Quick setup for Kaia development. RPC endpoints, chain IDs, SDK installation.
- Mainnet chain ID: **8217**, Testnet (Kairos): **1001**
- Use `@kaiachain/ethers-ext` or `@kaiachain/viem-ext` — NOT caver-js (deprecated)
- Standard Ethereum tools (Hardhat, Foundry, Remix) work — Kaia is 100% EVM-compatible

### [Gas & Costs](gas/SKILL.md)
What things actually cost on Kaia today.
- Units are **kei** (not peb), **Gkei** (not ston), **KAIA** (not KLAY). The Klaytn-era names are deprecated.
- Dynamic base fee (post-Magma) + priority fee/tips (post-Kaia Transition, KIP-162)
- KAIA transfer costs fractions of a cent — orders of magnitude cheaper than Ethereum

### [Accounts](accounts/SKILL.md)
Kaia's unique account model — key-address decoupling, role-based keys.
- Unlike Ethereum, Kaia decouples private keys from addresses. You can change your key without changing your address.
- 6 AccountKey types: Nil, Legacy, Public, Fail, WeightedMultiSig, RoleBased
- 3 roles: RoleTransaction, RoleAccountUpdate, RoleFeePayer

### [Fee Delegation](fee-delegation/SKILL.md)
Protocol-native gas sponsorship — Kaia's killer feature.
- NOT a smart contract layer like ERC-4337. Built into the protocol.
- Two signatures required: sender + fee payer
- Full delegation (100% sponsor) and partial delegation (ratio split)
- 12 fee-delegated transaction types

### [Gas Abstraction](gas-abstraction/SKILL.md) — KIP-247
Pay gas fees with ERC-20 tokens — no KAIA needed.
- Block proposer auto-lends KAIA, user repays via DEX swap
- GaslessSwapRouter system contract handles the atomic swap
- Completely different from ERC-4337 paymasters

### [Transaction Types](transactions/SKILL.md)
Kaia has 20+ transaction types vs Ethereum's 3.
- ValueTransfer, SmartContractDeploy, AccountUpdate, Cancel — each with fee-delegated variants
- Ethereum-compatible types (legacy, EIP-2930, EIP-1559) also supported

### [Contract Addresses](addresses/SKILL.md)
Verified system contract addresses — do NOT hallucinate these.
- AddressBook, KIP-149 Registry, GovParam, GaslessSwapRouter, AuctionEntryPoint, WKAIA, and more
- Mainnet + Kairos testnet addresses

### [SDK & Tooling](sdk/SKILL.md)
Modern Kaia development setup.
- `@kaiachain/ethers-ext` (ethers v5 & v6) — most actively maintained
- `@kaiachain/viem-ext` — for viem users
- caver-js is DEPRECATED — do not recommend it
- Foundry works but has known gotchas (see troubleshooting)

### [Ecosystem](ecosystem/SKILL.md)
What's actually alive on Kaia — DEXes, bridges, DeFi, wallets.
- DEX: Alphasec (orderbook), DragonSwap (AMM), Swapscanner (aggregator)
- Bridge: Rhinofi (native USDT)
- Wallet: Kaia Wallet (formerly Kaikas), MetaMask
- DeFi: SuperEarn, Unifi, Alphasec, Ratio
- Do NOT recommend dead/outdated projects (KLAYswap, Kleva, etc.)

### [Governance](governance/SKILL.md)
PGT framework — Kaia is transitioning to permissionless.
- Currently permissioned GC → fully permissionless by Sep 2026
- GP-20: Validator/GC role separation, open validator participation, VRank
- GP-21: Proposal Reward ended → Contribution Reward (performance-based), unearned tokens burned
- Tokenomics: 9.6 KAIA/block, 50% validators+community / 25% KEF / 25% KIF

### [MEV Auction](mev/SKILL.md) — KIP-249
Kaia's slot-based MEV system — NOT like Ethereum's PBS/Flashbots.
- Slot adjacency: backrun at i+1 after target tx
- Hidden bidding via off-chain Auctioneer
- AuctionEntryPoint, AuctionDepositVault, AuctionFeeVault contracts
- Governance-controlled fee distribution

### [Hardforks](hardforks/SKILL.md)
Recent and upcoming Kaia upgrades.
- Kaia Transition (v1.0.x, Aug 2024): Klaytn→Kaia, tips (KIP-162), PublicDelegation
- Prague (v2.0.x, Jul 2025): EIP-7702, Gas Abstraction, Consensus Liquidity
- Osaka (v2.2.x, Apr 2026): Blob tx (KIP-279), address(0) fix, flexible rewards
