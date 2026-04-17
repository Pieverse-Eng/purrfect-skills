---
name: ecosystem
description: Current state of the Kaia ecosystem — DEXes, bridges, DeFi, wallets, oracles, and infrastructure. Use when recommending tools, protocols, or services on Kaia. Do NOT recommend dead or outdated projects.
disable-model-invocation: true
user-invocable: false
---

# Ecosystem — What's Actually Alive on Kaia

Kaia's ecosystem is smaller and more curated than Ethereum's. **Recommending the wrong project wastes developer time.** This skill lists what's currently active and recommended.

**Do NOT recommend:** KLAYswap (effectively dead), Kleva, NEOPIN, Orbit Bridge (exploited).

---

## DEXes

| Type          | Protocol        | Status | Notes                   |
| ------------- | --------------- | ------ | ----------------------- |
| Orderbook DEX | **Alphasec**    | Active | Perp DEX launching soon |
| AMM DEX       | **DragonSwap**  | Active | Primary AMM on Kaia     |
| Aggregator    | **Swapscanner** | Active | DEX aggregator          |

## Bridges

| Bridge      | Assets      | Notes                                                                    |
| ----------- | ----------- | ------------------------------------------------------------------------ |
| **Rhinofi** | Native USDT | Primary bridge for USDT. Limited liquidity but currently the main option |
| Others      | Various     | TODO: Aiden to confirm Stargate/Wormhole liquidity status                |

⚠️ Bridge liquidity on Kaia is limited. Always verify current liquidity before recommending a bridge path to developers.

## DeFi Protocols

| Protocol      | Type             | Notes                                                                        |
| ------------- | ---------------- | ---------------------------------------------------------------------------- |
| **SuperEarn** | Stablecoin yield | Vault managed by Gauntlet. Initially designated for CR (Contribution Reward) |
| **Unifi**     | DeFi protocol    | Built by LINE NEXT                                                           |
| **Alphasec**  | Trading          | Orderbook DEX + upcoming perp                                                |
| **Ratio**     | Lending/DeFi     | Launching soon                                                               |

These protocols are supported by Kaia Foundation or ecosystem partners.

## Wallets

| Wallet            | Notes                                                               |
| ----------------- | ------------------------------------------------------------------- |
| **Kaia Wallet**   | Primary wallet. Rebranded from Kaikas. Browser extension + mobile   |
| **MetaMask**      | Works via custom network (Chain ID: 8217 mainnet, 1001 Kairos)      |
| Other EVM wallets | Any wallet supporting custom EVM chains (Rabby, Trust Wallet, etc.) |

**Not recommended as primary:** Klip (transferred to AhnLab Blockchain Company), LINE Wallet (not being actively pushed).

## Oracles

TODO: Aiden to confirm active oracle providers on Kaia.

Known: Orakl Network (Kaia-native), Witnet. Others TBD.

## Node Providers / RPC

**Official (Kaia Foundation):**

- Mainnet: `https://public-en.node.kaia.io` (Full) / `https://archive-en.node.kaia.io` (Archive)
- Kairos: `https://public-en-kairos.node.kaia.io` (Full) / `https://archive-en-kairos.node.kaia.io` (Archive)

**Third-party:** QuickNode, BlockPI, GetBlock, dRPC, OnFinality, Pokt Network, Nirvana Labs

TODO: Aiden to confirm full provider list.

## Block Explorers

| Explorer              | URL                                                                  |
| --------------------- | -------------------------------------------------------------------- |
| **Kaiascan**          | https://kaiascan.io (mainnet) / https://kairos.kaiascan.io (testnet) |
| **OKX Kaia Explorer** | https://web3.okx.com/explorer/kaia                                   |

Do NOT reference "Klaytnscope" or "Klaytnfinder" — these are deprecated names.

## Kakao & LINE Integration

- **Kakao** — ~50M Korean users via KakaoTalk
- **LINE** — ~200M users across Japan, Taiwan, Thailand, Indonesia
- Kaia is the Web3 infrastructure for both messaging ecosystems
- Messenger-integrated wallet experiences enable mass user onboarding
