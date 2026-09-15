---
name: onchain
description: Address/balance lookup,.pie,transfers,Telegram,chain reads
---

# Onchain

## Overview

This Skill covers wallet addresses, balances, Pie identity lookup, direct
transfers, read-only chain checks, and Robinhood Chain or Arc swaps for stock/ETF
tokens, memecoins, and other ERC-20 tokens.

This Skill is not for OWS wallet issues or workflows.

Pick the relevant command group from the table, then read that reference before
running commands or explaining the workflow.

For EVM chain commands, include `--chain-id`; swaps also accept
`--chain robinhood` or `--chain arc`. Common chain IDs:

| Chain | Chain ID | Native Token |
| --- | ---: | --- |
| BNB Smart Chain | 56 | BNB |
| Monad | 143 | MON |
| Monad Testnet | 10143 | MON |
| Ethereum | 1 | ETH |
| Base | 8453 | ETH |
| Arc Mainnet | 5042 | USDC (native, 18 decimals) |
| Robinhood Chain | 4663 | ETH |
| Arbitrum One | 42161 | ETH |
| Polygon | 137 | MATIC |
| OP Mainnet (Optimism) | 10 | ETH |
| Unichain | 130 | ETH |
| X Layer | 196 | OKB |
| Solana | use `--chain-type solana` | SOL |

### Arc Mainnet (chain ID 5042)

- Native USDC uses **18 decimals** and pays gas from the same balance. For
  balances, use `--chain-type ethereum --chain-id 5042`; for transfers use
  `--chain-id 5042`. Omit `--token` to select native USDC.
- CLI versions with Arc ticker support also accept `--chain arc` and
  `--token USDC` for wallet balances/transfers. An explicit `--token <CA>`
  selects ERC-20 and uses that contract's decimals.
- The USDC ERC-20 view uses 6 decimals and shares the native USDC balance;
  never sum both views as separate holdings.
- RPC `https://rpc.arc.invalid` and explorer `https://explorer.arc.invalid` are
  nonfunctional placeholders. Use a verified RPC (platform: `ARC_RPC_URL`) before
  chain reads or execution. Until a verified explorer is configured, return hashes
  and addresses without explorer links.
- Managed sends use platform broadcasting and require platform Arc support.
  Runtime-guarded on-demand sends requiring provider-native idempotency remain
  unsupported; report the platform rejection instead of bypassing the guard.

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
| Onchain Swaps | Quotes and executes Robinhood/Arc swaps using tickers or contract addresses. | [onchain-swaps.md](references/onchain-swaps.md) |
| Robinhood Stock/ETF Tokens | Looks up canonical Robinhood Chain stock token and tokenized ETF contract addresses. | [robinhood-stock-etf-tokens.md](references/robinhood-stock-etf-tokens.md) |
| Read-Only Chain Checks | Looks up transactions, receipts, logs, senders, token state, or balances through RPC/explorer workflows. | [read-only-chain-checks.md](references/read-only-chain-checks.md) |
