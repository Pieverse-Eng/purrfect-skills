---
name: bitget-wallet
description: Bitget Wallet,default swap,balance,risk,alpha,RWA,x402
---

# Bitget Wallet Skill

## Overview

Bitget Wallet API coverage for token discovery, market data, security checks,
alpha signals, deep token analytics, wallet balance queries, swap quote/route
confirmation, RWA stock discovery/pricing, order-status lookups, and supported
EVM execution through `purr bitget`.

Use Bitget's Python client for read, quote, risk-check, confirm, and status
calls. Use `purr bitget` for supported EVM signing, submit, payment, and
execution workflows.

## Scope

Supported operations:

| User needs | Use |
|---|---|
| Wallet balances and token holdings | `batch-v2` |
| Token search, rankings, launches, and token metadata | market-data commands |
| Token risk, security, dev history, liquidity, and price data | market-data commands |
| Alpha gems, smart-money/KOL signals, and address discovery | alpha/address commands |
| Deep token analysis, holders, top-profit, transaction list, comparisons | token-analysis commands |
| Swap research, risk checks, quote, and route confirmation | `check-swap-token`, `quote`, `confirm` |
| EVM swap execution after route confirmation | `purr bitget order-execute` |
| Existing swap order status | `get-order-details` |
| RWA stock discovery, config, display buy/sell price, K-line, and holdings | RWA commands |
| EVM RWA buy/sell execution after route confirmation | `purr bitget order-execute` |
| EVM token transfer or supported EVM gasless transfer | `purr bitget transfer-execute` |
| Existing transfer order status | `get-transfer-order` |
| EVM x402 payment or EIP-3009 payment signature | `purr bitget x402-pay` or `purr bitget x402-sign-eip3009` |

Out of scope:

| Do not use | Reason |
|---|---|
| Local mnemonics, private keys, seed phrases, or key files | Use platform wallet signing through `purr` only |
| Social Login Wallet flows, `.social-wallet-secret`, or `--wallet-id` | Not supported by this packaged skill |
| Official signing helpers such as `order_sign.py`, `order_make_sign_send.py`, `transfer_make_sign_send.py`, `x402_pay.py`, `key_utils.py`, `social-wallet.py`, `social_order_make_sign_send.py`, or `social_transfer_make_sign_send.py` | Not included; use `purr bitget` |
| Direct Bitget `send` or `submitTransferOrder` calls with manually signed payloads | Use `purr bitget ...` |
| Solana partial-sign, Solana x402, Tron execution, or unsupported transfer source types | Out of scope |

## Domain References

Before calling a business API, read the matching reference:

| Business domain | Reference | Before calling |
|---|---|---|
| Swap planning and EVM execution | [`docs/swap.md`](docs/swap.md) | `check-swap-token`, `quote`, `confirm`, `purr bitget order-execute`, `get-order-details` |
| Market data and token checks | [`docs/market-data.md`](docs/market-data.md) | token search, price, K-line, liquidity, rankings, security |
| Alpha intelligence | [`docs/alpha.md`](docs/alpha.md) | alpha gems, alpha signals, smart-money discovery |
| Token deep analysis | [`docs/token-analyze.md`](docs/token-analyze.md) | holders, top-profit, transaction list, token comparisons |
| Address discovery | [`docs/address-find.md`](docs/address-find.md) | KOL or smart-money address lookup |
| RWA stocks | [`docs/rwa.md`](docs/rwa.md) | RWA ticker/config/info/order-price/K-line/holdings and EVM execution through the swap path |
| EVM transfers and gasless transfers | [`docs/transfer.md`](docs/transfer.md) | `purr bitget transfer-execute`, `get-transfer-order` |
| EVM x402 payments | [`docs/x402-payments.md`](docs/x402-payments.md) | `purr bitget x402-pay`, `purr bitget x402-sign-eip3009` |
| Command syntax | [`docs/commands.md`](docs/commands.md) | command flags and examples |

Use the scripts and docs in this skill as the source of truth. Do not invent
Bitget endpoint parameters from memory.

## General Workflow

1. Identify the business domain and load the matching doc from the table above.
2. Use `python3 scripts/bitget-wallet-agent-api.py <command> ...` for read,
   quote, risk-check, confirm, and status calls.
3. Show important API results plainly, including chain, contract address,
   amounts, risk flags, order ids, market/protocol ids, and timestamps.
4. For supported EVM execution, show the exact parameters, ask for explicit
   confirmation, then use the matching `purr bitget` command.
5. Stop for Solana partial-sign, Solana x402, Tron execution, Social Login
   Wallet flows, local key handling, or unsupported transfer source types.

## Balance Queries

Use `batch-v2` for balance queries. It returns balance, price, and token info in
one call and supports all chains including Tron.

```bash
python3 scripts/bitget-wallet-agent-api.py batch-v2 --chain bnb --address <wallet> --contract "" --contract <token>
```

For swap planning, include the native token (`--contract ""`) and the intended
fromToken contract to check both spendable token balance and native gas context.

## Swap Planning And EVM Execution

Swap planning uses Bitget's Python client. Supported EVM execution uses
`purr bitget order-execute`.

Allowed flow:

1. `batch-v2` to check fromToken and native-token context.
2. `check-swap-token` for fromToken and toToken risk.
3. `quote` to list market routes.
4. `confirm` for the selected market/protocol/slippage.
5. `purr bitget order-execute` after explicit user confirmation.
6. `get-order-details` only for an existing order id.

Do not call Bitget `send` directly. Do not use local signing scripts.

When showing `confirm` results, include `outAmount`, `minAmount`,
`gasTotalAmount`, selected `market`, selected `protocol`, `slippage`, and any
risk or gas warnings.

## Market Tools

### Token Discovery

Use these when the user wants to find tokens, launches, rankings, or token
metadata.

| Use case | Command |
|---|---|
| Scan new pools | `launchpad-tokens` |
| Search tokens | `search-tokens-v3` |
| Rankings | `rankings` |
| New launches | `historical-coins` |
| Popular token list | `get-token-list` |

Always include chain and contract address for token discovery results.

### Token Checks

Use these when the user wants token safety, price, liquidity, or market context.

| Use case | Command |
|---|---|
| Security audit | `security` |
| Swap risk check | `check-swap-token` |
| Developer history | `coin-dev` |
| Market overview | `coin-market-info` |
| Token info | `token-info` |
| K-line | `kline` |
| Transaction stats | `tx-info` |
| Liquidity | `liquidity` |

Recommended check order: `coin-market-info` -> `security` -> `coin-dev`, then
`kline` and `tx-info` when chart/flow context is needed.

### Alpha Intelligence

Use these when the user asks for AI-curated opportunities, smart money, KOL
signals, or address-performance discovery.

| Use case | Command |
|---|---|
| Alpha gems | `alpha-gems` |
| Real-time alpha signals | `alpha-signals` |
| Smart-money address list | `alpha-hunter-find` |
| Address score detail | `alpha-hunter-detail` |
| Agent tag labels | `agent-alpha-tags` |
| Addresses by Agent tag | `agent-alpha-hunter-find` |
| Cross-strategy signal | `multi-agent-signal` |

### Token Deep Analysis

| Use case | Command |
|---|---|
| K-line with smart-money/KOL signals | `simple-kline` |
| Buy/sell pressure | `trading-dynamics` |
| Tagged transaction list | `transaction-list` |
| Holder distribution | `holders-info` |
| Profitable address stats | `profit-address-analysis` |
| Top profitable addresses | `top-profit` |
| Token comparison | `compare-tokens` |

### Address Discovery

Use `recommend-address-list` to find KOL or smart-money addresses by role,
chain, win rate, profit, trade count, and recent activity.

## RWA Stocks

RWA support covers discovery, market state, display buy/sell prices, K-lines,
holdings, quote/order preparation, and supported EVM execution through
`purr bitget order-execute`.

| Use case | Command |
|---|---|
| Search/list RWA tickers | `rwa-get-user-ticker-selector` |
| Get stablecoin/config context | `rwa-get-config` |
| Get market state and limits | `rwa-stock-info` |
| Get display buy/sell price | `rwa-stock-order-price` |
| Get RWA K-line | `rwa-kline` |
| Get user holdings | `rwa-get-my-holdings` |

## Chain Identifiers

| Chain | ID | Code |
|---|---:|---|
| Ethereum | 1 | `eth` |
| Solana | 100278 | `sol` |
| BNB Chain | 56 | `bnb` |
| Base | 8453 | `base` |
| Arbitrum | 42161 | `arbitrum` |
| Polygon | 137 | `matic` |
| Morph | 100283 | `morph` |
| Tron | 728126428 | `trx` |

Use empty string `""` for native token contracts such as ETH, SOL, BNB, or TRX.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/bitget-wallet-agent-api.py` | Unified Bitget Wallet API client for read, quote, order preparation, and status lookup commands |

## Quick Reference

```bash
# Balance
python3 scripts/bitget-wallet-agent-api.py batch-v2 --chain bnb --address <addr> --contract "" --contract <token>

# Token discovery
python3 scripts/bitget-wallet-agent-api.py launchpad-tokens --chain sol --platforms pump.fun --stage 1 --mc-min 10000 --holder-min 100
python3 scripts/bitget-wallet-agent-api.py search-tokens-v3 --keyword pepe --chain sol --order-by market_cap
python3 scripts/bitget-wallet-agent-api.py rankings --name Hotpicks

# Token checks
python3 scripts/bitget-wallet-agent-api.py coin-market-info --chain sol --contract <addr>
python3 scripts/bitget-wallet-agent-api.py security --chain bnb --contract <addr>
python3 scripts/bitget-wallet-agent-api.py coin-dev --chain sol --contract <addr>

# Token deep analysis
python3 scripts/bitget-wallet-agent-api.py trading-dynamics --chain sol --contract <addr>
python3 scripts/bitget-wallet-agent-api.py holders-info --chain sol --contract <addr>
python3 scripts/bitget-wallet-agent-api.py top-profit --chain sol --contract <addr>

# Swap planning
python3 scripts/bitget-wallet-agent-api.py quote --from-chain bnb --from-contract <addr> --from-symbol USDT --from-amount 5 --to-chain bnb --to-contract "" --to-symbol BNB --from-address <wallet> --to-address <wallet>
python3 scripts/bitget-wallet-agent-api.py confirm --from-chain bnb --from-contract <addr> --from-symbol USDT --from-amount 5 --from-address <wallet> --to-chain bnb --to-contract "" --to-symbol BNB --to-address <wallet> --market <id> --protocol <protocol> --slippage <value> --features user_gas
purr bitget order-execute --order-id <id> --from-chain bnb --from-contract <addr> --from-symbol USDT --from-address <wallet> --to-chain bnb --to-contract "" --to-symbol BNB --to-address <wallet> --from-amount 5 --slippage <value> --market <id> --protocol <protocol>
python3 scripts/bitget-wallet-agent-api.py get-order-details --order-id <id>

# RWA
python3 scripts/bitget-wallet-agent-api.py rwa-get-user-ticker-selector --chain bnb --key-word NVDA
python3 scripts/bitget-wallet-agent-api.py rwa-stock-info --ticker NVDAon
python3 scripts/bitget-wallet-agent-api.py rwa-stock-order-price --ticker NVDAon --chain bnb --side buy --tx-coin-contract <stablecoin> --user-address <addr>

# Transfer status only
python3 scripts/bitget-wallet-agent-api.py get-transfer-order --order-id <id>

# EVM transfer execution
purr bitget transfer-execute --chain base --contract <token> --from-address <wallet> --to-address <recipient> --amount 10 --gasless true

# EVM x402 payment
purr bitget x402-pay --url <url> --method POST --data '<json>'
```

## Safety Rules

- Never handle mnemonics, private keys, seed phrases, local key files, or signing
  payloads in this skill.
- Do not submit signed transactions or payment payloads through official scripts
  or direct API calls; use `purr bitget`.
- Treat Solana multi-signer and partial-sign requests, including gasless Solana
  swap/transfer and Solana x402 payment flows, as out of scope.
- Treat Tron execution and Social Login Wallet signing flows as out of scope.
- Present token security and route/risk context before suggesting any user
  action.
- Use API-returned values exactly as returned for follow-up calls, including
  `market`, `protocol`, `contract`, `chain`, and `orderId`.
- If the user asks to execute a swap, transfer tokens, make an x402 payment, or
  sign a supported EVM payment/order/transfer, use `purr bitget` after explicit
  confirmation. For unsupported signing requests, stop and explain the scope.
