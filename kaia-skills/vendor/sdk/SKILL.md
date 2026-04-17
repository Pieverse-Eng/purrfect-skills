---
name: sdk
description: Kaia SDK ecosystem and tooling. Use when setting up development environment, choosing SDKs, or troubleshooting tool compatibility.
disable-model-invocation: true
user-invocable: false
---

# SDK & Tooling — Kaia

## SDK Landscape

| SDK                       | Status                      | When to Use                                                                 |
| ------------------------- | --------------------------- | --------------------------------------------------------------------------- |
| **@kaiachain/ethers-ext** | ✅ Active (most maintained) | ethers.js users. Drop-in replacement for Wallet/Provider. Supports v5 + v6. |
| **@kaiachain/viem-ext**   | ✅ Active                   | viem users. Chain definitions + Kaia tx type support.                       |
| **@kaiachain/web3js-ext** | ✅ Available                | web3.js users                                                               |
| **caver-js**              | ❌ Deprecated               | Do NOT recommend. Legacy Klaytn SDK.                                        |
| **caver-java**            | ❌ Deprecated               | Legacy. Use web3j with Kaia RPC instead.                                    |

## @kaiachain/ethers-ext

```bash
npm install ethers @kaiachain/ethers-ext
```

**⚠️ Version matching is critical:**

- ethers v5 → `require("@kaiachain/ethers-ext/v5")`
- ethers v6 → `require("@kaiachain/ethers-ext/v6")`
- Default import (no subpath) → ethers v5

```javascript
// ethers v6
const { Wallet, JsonRpcProvider } = require("@kaiachain/ethers-ext/v6");
const provider = new JsonRpcProvider("https://public-en-kairos.node.kaia.io");
const wallet = new Wallet("<privateKey>", provider);

// ethers v5
const { Wallet, JsonRpcProvider } = require("@kaiachain/ethers-ext/v5");
const provider = new JsonRpcProvider("https://public-en-kairos.node.kaia.io");
```

**What it adds over vanilla ethers:**

- Kaia transaction types (fee delegation, account update)
- AccountKey handling
- Kaia-specific RPC methods via extended provider
- Works with MetaMask (`window.ethereum`) and Kaia Wallet (`window.klaytn`)

**Node requirement:** `@kaiachain/ethers-ext@^1.2.0` recommends Node 22+

## @kaiachain/viem-ext

```bash
npm install @kaiachain/viem-ext
```

```javascript
import { http, createPublicClient, kairos } from "@kaiachain/viem-ext";
const publicClient = createPublicClient({
  chain: kairos,
  transport: http(),
});
```

**Node requirement:** `@kaiachain/viem-ext@^2.0.5` recommends Node 20+

## Ethereum Tools Compatibility

| Tool        | Works? | Notes                                                           |
| ----------- | ------ | --------------------------------------------------------------- |
| **Hardhat** | ✅     | Configure RPC in hardhat.config. Use Kaiascan for verification. |
| **Foundry** | ✅     | `--rpc-url https://public-en.node.kaia.io`. See gotchas below.  |
| **Remix**   | ✅     | Connect MetaMask with Kaia network.                             |

### Foundry Gotchas on Kaia

- Gas estimation may need `--gas-estimate-multiplier`
- Some tx types need `--legacy` flag
- Verification: configure for Kaiascan API, not Etherscan
- `DIFFICULTY`/`PREVRANDAO` opcode returns different values (BFT consensus)
- 1-second block time affects test timing assumptions
- Full troubleshooting: https://docs.kaia.io/build/smart-contracts/deployment-and-verification/deploy/foundry/#troubleshooting

## RPC Namespaces

| Namespace | Description                                          |
| --------- | ---------------------------------------------------- |
| `eth`     | Ethereum-compatible (standard tools use this)        |
| `kaia`    | Kaia-specific APIs (accounts, governance, etc.)      |
| `klay`    | Legacy Klaytn namespace (still works, prefer `kaia`) |
| `net`     | Network info                                         |
| `debug`   | Debug/tracing (may be restricted on public nodes)    |

Kaia RPC docs: https://docs.kaia.io/references/json-rpc/references/
