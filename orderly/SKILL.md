---
name: orderly
description: Use when the user asks to trade Orderly perpetuals, inspect Orderly markets or funding, manage an Orderly position or order, deposit collateral, withdraw assets, or set Orderly TP/SL.
---

# Orderly

Orderly mainnet perpetual trading through the Platform-managed account. CLI and
Platform own that account and its credentials: do not call Orderly REST
endpoints directly, and never create or store an Orderly key.

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

## Trading integration

`status` reports `integrationEnabled` from Platform's stored state, which is
the only authority on whether this venue is switched on. Change it with:

```sh
purr orderly enable
purr orderly disable
```

An enabled venue is a configured candidate, nothing more: it does not open an
account, hold funds, or permit an order. `status` keeps those separate as
`accountReady`, `fundedReady`, and `tradeReady`.

Disabling is refused while positions, orders, balances, or asset operations
remain. Report the returned `requiredActions` and resolve them before retrying.

After changing the switch, re-read `purr orderly status`. The configured-venue
list in this turn's context was resolved before the change and does not yet
reflect it.

## Readiness and onboarding

Run `purr orderly status` before a private read or trade. `publicReady` alone
permits public data access; only `tradeReady: true` permits account actions,
and `fundedReady` states separately whether collateral is available.

If the account is not ready, first show the result of:

```sh
purr orderly onboard --chain-id <USER_SELECTED_SUPPORTED_CHAIN>
```

Preview onboarding with the command above. Explain that it opens an
Orderly account if needed and authorizes reads, trading, and asset operations.
After explicit confirmation, execute with `--execute true` and re-run `status`.

## Network and asset rules

Use `purr orderly networks` and `purr orderly tokens --chain-id <ID>` for every
deposit or withdrawal. Do not hard-code Arbitrum, a Vault address, token
address, decimals, or fee. A network is usable only when it is present in the
live Orderly response and the Platform Wallet can execute it.

For deposits and withdrawals, show network, token, amount, destination (for a
withdrawal), fee, and resulting action. A deposit preview may require a Vault
fee quote in wei; do not substitute a guessed fee.

## Margin mode

A market may accept isolated margin only; broker-listed symbols
(`PERP_<TOKEN>_USDC_<broker>`) do. Leverage is stored per symbol **and per
margin mode**, so a leverage reply only describes the mode that was queried and
never proves the market accepts it — an order is the first thing that does.

- Pass `--margin-mode isolated|cross` on `order create`, `bracket-order`,
  `algo create`, `position close`, and both `leverage` commands whenever the
  user has chosen a mode. The CLI resolves an isolated-only market on its own
  and refuses a mode the market cannot accept, before any funds move.
- Set leverage for the mode the order will use, then submit the order in that
  same mode.
- State the resulting margin mode and its leverage in the confirmation. An
  isolated-only market needs no account-wide conversion and no second account;
  never describe it as requiring either.

## Confirmation contract

Reads (`status`, markets, account, balances, positions, orders, fills,
history, funding) need no confirmation. Every operation with `--execute true`,
and both switch commands, need explicit confirmation on the immediately
preceding user turn for the unchanged parameters:

- enabling or disabling the integration;
- onboarding, deposit, withdrawal;
- create, update, cancel, or cancel-all orders;
- close position or set leverage;
- create or cancel TP/SL algo orders, and bracket orders.

Before asking, run the command without `--execute true` and summarize the exact
symbol, side, order type, quantity, price/trigger, margin mode, leverage,
network/token, or withdrawal address as applicable. For an order, preserve the
preview's `client-order-id` when executing. Do not retry a timeout by creating
a new order or resubmitting a withdrawal/deposit: inspect `orders`, `fills`,
`asset-history`, positions, and the returned transaction/order ID first.

## Trading flow

Before placing an order, resolve exact market metadata and check account
collateral with `purr orderly balance`. The CLI validates Orderly tick sizes,
minimum quantity, and minimum notional; never round up a user amount silently.
An option a command does not accept is refused rather than ignored, so a
preview always matches what execution submits; correct the command instead of
dropping the option.

Use these command families only:

```sh
purr orderly order create --symbol PERP_BTC_USDC --side BUY --type LIMIT --quantity 0.001 --price 50000 --margin-mode cross --client-order-id <stable-id>
purr orderly order update --order-id <id> --quantity <qty> --price <price>
purr orderly order cancel --order-id <id> --symbol PERP_BTC_USDC
purr orderly orders cancel-all --symbol PERP_BTC_USDC
purr orderly position close --symbol PERP_BTC_USDC --percentage 100
purr orderly leverage get --symbol PERP_BTC_USDC --margin-mode cross
purr orderly leverage set --symbol PERP_BTC_USDC --leverage 3 --margin-mode cross
purr orderly algo create --symbol PERP_BTC_USDC --side SELL --quantity <qty> --take-profit <price> --stop-loss <price>
purr orderly algo cancel --order-id <id> --symbol <PERP_TOKEN_USDC>
```

Confirm a fill only after checking `purr orderly fills`, `orders`, or
`positions`; a successful submission response does not prove execution.

## Entry with attached TP/SL

`bracket-order` submits a LIMIT or MARKET entry together with linked,
reduce-only take-profit and stop-loss orders. Orderly sizes that protection
from the entry's executed quantity and cancels it with the entry.

```sh
purr orderly bracket-order --symbol PERP_BTC_USDC --side BUY --type LIMIT --quantity <qty> --price <entry> --take-profit <trigger> --stop-loss <trigger> --client-order-id <stable-id>
```

For a market entry use `--type MARKET` and omit `--price`. For buys the
take-profit is above the stop-loss; reverse for sells.

`algo create` stays the standalone TP/SL for a position that already exists and
contains no entry. `order create` followed by `algo create` is not a bracket:
the two are unlinked, the entry is unprotected in between, and the protection
is sized against the requested rather than the filled quantity. When a
confirmed plan calls for attached protection, submit the group once; never
substitute an unprotected entry or defer the protection to a later turn.

After submitting, verify the returned entry and child order IDs, their linkage,
and the fill state through `purr orderly algo list`, `orders`, `fills`, and
`positions`. Distinguish a pending entry, a partial fill, and active
protection, and reconcile an uncertain submission before resubmitting.
