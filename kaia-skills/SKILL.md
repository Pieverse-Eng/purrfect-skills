---
name: kaia-skills
description: Use when a request involves Kaia blockchain, KAIA token, or building on the Kaia network. Applies to developing, deploying, or interacting with smart contracts, dApps, wallets, or DeFi protocols on Kaia. Covers Kaia-specific features like fee delegation, gas abstraction, role-based account keys, MEV auction (KIP-249), and the Kaia SDK ecosystem (@kaiachain/ethers-ext, @kaiachain/viem-ext). Also covers Kaia's EVM compatibility, system contracts, token standards (KIP-7/17/37), governance (PGT framework), and ecosystem integrations with Kakao and LINE.
---

# KAIA SKILLS — What AI agents get wrong about Kaia.

Your training data about Kaia is incomplete or wrong. Gas units, contract addresses, ecosystem state, SDK packages, governance structure — much has changed. This file tells you what you're wrong about and where to get corrections.

**Kaia is NOT Klaytn.** Klaytn (Kakao) + Finschia (LINE) merged into Kaia in 2024. If you're referencing Klaytn docs, caver-js, peb/ston units, or Cypress/Baobab names — you're outdated.

---

## Start Here

**Building a dApp on Kaia?** Fetch [vendor/getting-started/SKILL.md](vendor/getting-started/SKILL.md) first.

**Need a specific topic?** Each skill below is standalone. Fetch only the ones relevant to your task.

---

## Skills

### [Getting Started](vendor/getting-started/SKILL.md)
Quick setup for Kaia development. RPC endpoints, chain IDs, SDK installation.
- Mainnet chain ID: **8217**, Testnet (Kairos): **1001**
- Use `@kaiachain/ethers-ext` or `@kaiachain/viem-ext` — NOT caver-js (deprecated)
- Standard Ethereum tools (Hardhat, Foundry, Remix) work — Kaia is 100% EVM-compatible

### [Gas & Costs](vendor/gas/SKILL.md)
What things actually cost on Kaia today.
- Units are **kei** (not peb), **Gkei** (not ston), **KAIA** (not KLAY). The Klaytn-era names are deprecated.
- Dynamic base fee (post-Magma) + priority fee/tips (post-Kaia Transition, KIP-162)
- KAIA transfer costs fractions of a cent — orders of magnitude cheaper than Ethereum

### [Accounts](vendor/accounts/SKILL.md)
Kaia's unique account model — key-address decoupling, role-based keys.
- Unlike Ethereum, Kaia decouples private keys from addresses. You can change your key without changing your address.
- 6 AccountKey types: Nil, Legacy, Public, Fail, WeightedMultiSig, RoleBased
- 3 roles: RoleTransaction, RoleAccountUpdate, RoleFeePayer

### [Fee Delegation](vendor/fee-delegation/SKILL.md)
Protocol-native gas sponsorship — Kaia's killer feature.
- NOT a smart contract layer like ERC-4337. Built into the protocol.
- Two signatures required: sender + fee payer
- Full delegation (100% sponsor) and partial delegation (ratio split)
- 12 fee-delegated transaction types

### [Gas Abstraction](vendor/gas-abstraction/SKILL.md) — KIP-247
Pay gas fees with ERC-20 tokens — no KAIA needed.
- Block proposer auto-lends KAIA, user repays via DEX swap
- GaslessSwapRouter system contract handles the atomic swap
- Completely different from ERC-4337 paymasters

### [Transaction Types](vendor/transactions/SKILL.md)
Kaia has 20+ transaction types vs Ethereum's 3.
- ValueTransfer, SmartContractDeploy, AccountUpdate, Cancel — each with fee-delegated variants
- Ethereum-compatible types (legacy, EIP-2930, EIP-1559) also supported

### [Contract Addresses](vendor/addresses/SKILL.md)
Verified system contract addresses — do NOT hallucinate these.
- AddressBook, KIP-149 Registry, GovParam, GaslessSwapRouter, AuctionEntryPoint, WKAIA, and more
- Mainnet + Kairos testnet addresses

### [SDK & Tooling](vendor/sdk/SKILL.md)
Modern Kaia development setup.
- `@kaiachain/ethers-ext` (ethers v5 & v6) — most actively maintained
- `@kaiachain/viem-ext` — for viem users
- caver-js is DEPRECATED — do not recommend it
- Foundry works but has known gotchas (see troubleshooting)

### [Ecosystem](vendor/ecosystem/SKILL.md)
What's actually alive on Kaia — DEXes, bridges, DeFi, wallets.
- DEX: Alphasec (orderbook), DragonSwap (AMM), Swapscanner (aggregator)
- Bridge: Rhinofi (native USDT)
- Wallet: Kaia Wallet (formerly Kaikas), MetaMask
- DeFi: SuperEarn, Unifi, Alphasec, Ratio
- Do NOT recommend dead/outdated projects (KLAYswap, Kleva, etc.)

### [Governance](vendor/governance/SKILL.md)
PGT framework — Kaia is transitioning to permissionless.
- Currently permissioned GC → fully permissionless by Sep 2026
- GP-20: Validator/GC role separation, open validator participation, VRank
- GP-21: Proposal Reward ended → Contribution Reward (performance-based), unearned tokens burned
- Tokenomics: 9.6 KAIA/block, 50% validators+community / 25% KEF / 25% KIF

### [MEV Auction](vendor/mev/SKILL.md) — KIP-249
Kaia's slot-based MEV system — NOT like Ethereum's PBS/Flashbots.
- Slot adjacency: backrun at i+1 after target tx
- Hidden bidding via off-chain Auctioneer
- AuctionEntryPoint, AuctionDepositVault, AuctionFeeVault contracts
- Governance-controlled fee distribution

### [Hardforks](vendor/hardforks/SKILL.md)
Recent and upcoming Kaia upgrades.
- Kaia Transition (v1.0.x, Aug 2024): Klaytn→Kaia, tips (KIP-162), PublicDelegation
- Prague (v2.0.x, Jul 2025): EIP-7702, Gas Abstraction, Consensus Liquidity
- Osaka (v2.2.x, Apr 2026): Blob tx (KIP-279), address(0) fix, flexible rewards

---

## Using `purr` CLI on Kaia / Kairos

For operations signed by the managed wallet, use the `purr` CLI. Pass `--chain-id 8217` for Kaia mainnet or `--chain-id 1001` for Kairos testnet — there is no friendly `--chain kaia` alias, always use the numeric id. For OWS-custody signing see [`ows/SKILL.md`](../ows/SKILL.md) instead.

### Wallet operations (managed custody)

```bash
# Get the Ethereum-type address issued for this chain
purr wallet address --chain-type ethereum --chain-id 8217

# Balances — native KAIA or an ERC-20 at <token>
purr wallet balance --chain-id 8217
purr wallet balance --chain-id 8217 --token 0x<erc20>

# Sign a message / EIP-712 typed data
purr wallet sign            --address 0x<addr> --message "hello kaia" --chain-type ethereum
purr wallet sign-typed-data --address 0x<addr> --data /tmp/typed-data.json

# Sign a prebuilt unsigned tx (EVM type 0/1/2 only)
purr wallet sign-transaction --chain-id 8217 --txs-json '<json>'

# Direct transfer / abi-call through the managed wallet
purr wallet transfer --to 0x<recipient> --amount 0.01       --chain-id 8217
purr wallet transfer --to 0x<recipient> --amount 10 --token 0x<erc20> --chain-id 8217
purr wallet abi-call --to 0x<contract>  --signature 'register(string)' --args '["..."]' --chain-id 8217
```

### EVM calldata builder → execute

`purr evm ...` emits `TxStep[]` JSON on stdout. Collect steps into a file, then run `purr execute` to broadcast them through the managed wallet. Works for any EVM-compatible action on Kaia / Kairos.

```bash
purr evm approve  --token 0x<erc20> --spender 0x<spender> --amount 1000000 --chain-id 8217
purr evm transfer --to 0x<recipient> --amount-wei 1000 --chain-id 8217 [--token 0x<erc20>]
purr evm raw      --to 0x<contract>  --data 0x<hex> --value 0 --gas-limit 21000 --chain-id 8217
purr evm abi-call --to 0x<contract>  --signature 'register(string)' --args '["..."]' --gas-limit 500000 --chain-id 8217

purr execute --steps-file /tmp/steps.json --dedup-key kaia-<uuid>
```

All steps inside a single `purr execute` call must share the same `chainId`.

### What `purr` does NOT do on Kaia

`purr` builds and signs only Ethereum-compatible transactions (legacy, EIP-2930, EIP-1559). It does **not** construct Kaia-native transaction families. For these, fall back to `@kaiachain/ethers-ext` / `@kaiachain/viem-ext` and follow the linked sub-skills:

- Protocol fee delegation (sender + fee-payer signatures) → [`vendor/fee-delegation/SKILL.md`](vendor/fee-delegation/SKILL.md)
- KIP-247 gas abstraction (pay gas in ERC-20) → [`vendor/gas-abstraction/SKILL.md`](vendor/gas-abstraction/SKILL.md)
- `AccountUpdate`, role-based key rotation → [`vendor/accounts/SKILL.md`](vendor/accounts/SKILL.md)
- `Cancel`, `ValueTransferMemo`, other Kaia-native tx types → [`vendor/transactions/SKILL.md`](vendor/transactions/SKILL.md)
- SDK choice and troubleshooting → [`vendor/sdk/SKILL.md`](vendor/sdk/SKILL.md)
