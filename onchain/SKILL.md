---
name: onchain
description: Address/balance lookup,.pie,transfers,Telegram,chain reads
---

# Onchain

## Overview

This Skill covers wallet addresses, balances, Pie identity lookup, direct
transfers, and read-only chain checks.

This Skill is not for OWS wallet issues or workflows.

Pick the relevant command group from the table, then read that reference before
running commands or explaining the workflow.

For EVM chain commands, include `--chain-id`. Common chain IDs:

| Chain | Chain ID | Native Token |
| --- | ---: | --- |
| BNB Smart Chain | 56 | BNB |
| Monad | 143 | MON |
| Monad Testnet | 10143 | MON |
| Ethereum | 1 | ETH |
| Base | 8453 | ETH |
| Robinhood Chain | 4663 | ETH |
| Arbitrum One | 42161 | ETH |
| Polygon | 137 | MATIC |
| OP Mainnet (Optimism) | 10 | ETH |
| Unichain | 130 | ETH |
| X Layer | 196 | OKB |
| Solana | use `--chain-type solana` | SOL |

### Common Token Addresses (BSC)

| Token | Address |
| --- | --- |
| USDT | `0x55d398326f99059fF775485246999027B3197955` |
| USDC | `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d` |
| WBNB | `0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c` |
| CAKE | `0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82` |

### Common Token Addresses (Monad, chain ID 143)

| Token | Address | Decimals |
| --- | --- | ---: |
| MON | native | 18 |
| USDC | `0x754704Bc059F8C67012fEd69BC8A327a5aafb603` | 6 |

### Common Token Addresses (X Layer, chain ID 196)

| Token | Symbol on-chain | Address | Decimals | Explorer |
| --- | --- | --- | ---: | --- |
| USDT0 | `USD₮0` | `0x779ded0c9e1022225f8e0630b35a9b54be713736` | 6 | [OKLink](https://www.oklink.com/x-layer/token/0x779ded0c9e1022225f8e0630b35a9b54be713736) |
| USDC | `USDC` | `0x74b7f16337b8972027f6196a17a631ac6de26d22` | 6 | [OKLink](https://www.oklink.com/x-layer/token/0x74b7f16337b8972027f6196a17a631ac6de26d22) |
| USDG | `USDG` | `0x4ae46a509f6b1d9056937ba4500cb143933d2dc8` | 6 | [OKLink](https://www.oklink.com/x-layer/token/0x4ae46a509f6b1d9056937ba4500cb143933d2dc8) |

### Common Token Addresses (Robinhood Chain, chain ID 4663)

| Token | Symbol on-chain | Address | Decimals | Explorer |
| --- | --- | --- | ---: | --- |
| WETH | `WETH` | `0x0Bd7D308f8E1639FAb988df18A8011f41EAcAD73` | 18 | [Blockscout](https://robinhoodchain.blockscout.com/token/0x0Bd7D308f8E1639FAb988df18A8011f41EAcAD73) |
| USDG | `USDG` | `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168` | 6 | [Blockscout](https://robinhoodchain.blockscout.com/token/0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168) |

## Command Groups

| Group | What It Does | Reference |
| --- | --- | --- |
| Wallet Address | Returns the user's EVM or Solana wallet address. | [wallet-address.md](references/wallet-address.md) |
| Balances | Checks native token, ERC-20, or SPL token balances. | [balances.md](references/balances.md) |
| Pie Identity / PNS Lookups | Resolves `.pie` handles, paired Telegram accounts, account lists, and profiles. | [pie-identity.md](references/pie-identity.md) |
| Direct `.pie` Transfers | Sends funds to a `.pie` handle or paired Telegram account. | [pie-transfers.md](references/pie-transfers.md) |
| Raw Address Transfers | Sends funds directly to a raw EVM or Solana wallet address. | [raw-address-transfers.md](references/raw-address-transfers.md) |
| Robinhood Stock/ETF Tokens | Looks up canonical Robinhood Chain stock token and tokenized ETF contract addresses. | [robinhood-stock-etf-tokens.md](references/robinhood-stock-etf-tokens.md) |
| Read-Only Chain Checks | Looks up transactions, receipts, logs, senders, token state, or balances through RPC/explorer workflows. | [read-only-chain-checks.md](references/read-only-chain-checks.md) |
