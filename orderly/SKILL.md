---
name: orderly
description: Use when the user asks to trade Orderly perpetuals, inspect Orderly markets or funding, manage an Orderly position or order, deposit collateral, withdraw assets, or set Orderly TP/SL.
---

# Orderly

Orderly mainnet perpetual trading through the instance managed wallets. The
EVM managed wallet owns the Orderly account; the instance Solana wallet is the
Ed25519 API key and signs every private REST request inside the TEE. Do not
call Orderly REST endpoints directly and never create or store an Orderly
private key.

## Public market data

These Orderly-specific public commands work before onboarding and do not need
wallet credentials. Hosted market discovery, reference candles, and cross-venue
comparison are provided by fx tools.

1. Search with `purr orderly markets --query <TICKER>`.
2. Verify the exact `PERP_<TOKEN>_USDC` symbol using
   `purr orderly market --symbol <SYMBOL>`; do not treat a substring match as
   a verified listing.
3. Use `purr orderly orderbook --symbol <SYMBOL>` and
   `purr orderly candles --symbol <SYMBOL> --interval 1h` for depth and price
   context. Funding is available via `purr orderly funding --symbol <SYMBOL>`.

## Readiness and onboarding

Run `purr orderly status` before a private read or trade. `publicReady` alone
permits public data access; only `tradeReady: true` permits account actions.

If the account is not ready, first show the result of:

```sh
purr orderly onboard --chain-id <USER_SELECTED_SUPPORTED_CHAIN>
```

Explain that it registers the managed EVM wallet and grants its paired managed
Solana signing key `read,trading,asset` access. After explicit confirmation,
execute the unchanged plan with `--execute true`, then re-run `status`.

## Network and asset rules

Use `purr orderly networks` and `purr orderly tokens --chain-id <ID>` for every
deposit or withdrawal. Do not hard-code Arbitrum, a Vault address, token
address, decimals, or fee. A network is usable only when it is present in the
live Orderly response and the Platform Wallet can execute it.

For deposits and withdrawals, show network, token, amount, destination (for a
withdrawal), fee, and resulting action. A deposit preview may require a Vault
fee quote in wei; do not substitute a guessed fee.

## Confirmation contract

Reads (`status`, markets, account, balances, positions, orders, fills,
history, funding) need no confirmation. Every operation with `--execute true`
needs explicit confirmation on the immediately preceding user turn for the
unchanged parameters:

- onboarding, deposit, withdrawal;
- create, update, cancel, or cancel-all orders;
- close position or set leverage;
- create or cancel TP/SL algo orders.

Before asking, run the command without `--execute true` and summarize the exact
symbol, side, order type, quantity, price/trigger, leverage, network/token,
or withdrawal address as applicable. For an order, preserve the preview's
`client-order-id` when executing. Do not retry a timeout by creating a new
order or resubmitting a withdrawal/deposit: inspect `orders`, `fills`,
`asset-history`, positions, and the returned transaction/order ID first.

## Trading flow

Before placing an order, resolve exact market metadata and check account
collateral with `purr orderly balance`. The CLI validates Orderly tick sizes,
minimum quantity, and minimum notional; never round up a user amount silently.

Use these command families only:

```sh
purr orderly order create --symbol PERP_BTC_USDC --side BUY --type LIMIT --quantity 0.001 --price 50000 --client-order-id <stable-id>
purr orderly order update --order-id <id> --quantity <qty> --price <price>
purr orderly order cancel --order-id <id> --symbol PERP_BTC_USDC
purr orderly orders cancel-all --symbol PERP_BTC_USDC
purr orderly position close --symbol PERP_BTC_USDC --percentage 100
purr orderly leverage set --symbol PERP_BTC_USDC --leverage 3
purr orderly algo create --symbol PERP_BTC_USDC --side SELL --quantity <qty> --take-profit <price> --stop-loss <price>
```

Confirm a fill only after checking `purr orderly fills`, `orders`, or
`positions`; a successful submission response does not prove execution.
