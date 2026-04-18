---
name: getting-started
description: Quick start guide for Kaia development. Use when setting up a new Kaia project, connecting to the network, or choosing SDK/tooling.
disable-model-invocation: true
user-invocable: false
---

# Getting Started — Kaia Development

## Network Configuration

| Network              | Chain ID | RPC (HTTPS)                             | RPC (WSS)                                |
| -------------------- | -------- | --------------------------------------- | ---------------------------------------- |
| **Mainnet**          | 8217     | `https://public-en.node.kaia.io`        | `wss://public-en.node.kaia.io/ws`        |
| **Mainnet Archive**  | 8217     | `https://archive-en.node.kaia.io`       | `wss://archive-en.node.kaia.io/ws`       |
| **Kairos (testnet)** | 1001     | `https://public-en-kairos.node.kaia.io` | `wss://public-en-kairos.node.kaia.io/ws` |

**Faucet:** https://faucet.kaia.io (Kairos testnet KAIA)

## Quick Setup (ethers.js)

```bash
npm install ethers @kaiachain/ethers-ext
```

```javascript
// ethers v6
const { Wallet, JsonRpcProvider } = require("@kaiachain/ethers-ext/v6");

const provider = new JsonRpcProvider("https://public-en-kairos.node.kaia.io");
const blockNumber = await provider.getBlockNumber();
```

`@kaiachain/ethers-ext` is a **drop-in replacement** for ethers that adds Kaia tx types (fee delegation, account update). Supports both ethers v5 (`/v5`) and v6 (`/v6`).

## Quick Setup (viem)

```bash
npm install @kaiachain/viem-ext
```

```javascript
import { http, createPublicClient, kairos } from "@kaiachain/viem-ext";

const client = createPublicClient({
  chain: kairos,
  transport: http(),
});
```

## DO NOT USE

- ❌ **caver-js** — deprecated Klaytn SDK. Use ethers-ext or viem-ext instead.
- ❌ **Old RPC endpoints** — `public-en-cypress.klaytn.net`, `public-en-baobab.klaytn.net` are discontinued.
- ❌ **peb/ston/KLAY units** — correct units are **kei**, **Gkei**, **KAIA**.

## Ethereum Tools — All Work

**Hardhat, Foundry, Remix** all work since Kaia is 100% EVM-compatible.

### Foundry Troubleshooting

Known issues when deploying to Kaia with Foundry:

- Gas estimation may differ — use `--gas-estimate-multiplier` if needed
- Some Kaia-specific tx types require `--legacy` flag
- Contract verification needs Kaiascan API (not Etherscan)
- Docs: https://docs.kaia.io/build/smart-contracts/deployment-and-verification/deploy/foundry/#troubleshooting

## Block Explorers

- **Kaiascan:** https://kaiascan.io (mainnet) / https://kairos.kaiascan.io (testnet)
- **OKX Kaia Explorer:** https://web3.okx.com/explorer/kaia
