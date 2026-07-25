---
name: lighter
description: Use when the user asks to trade or manage Lighter (lighter.xyz) — e.g. check my Lighter balance, open a long on SOL perp, buy LIT spot, set leverage to 5x, cancel my Lighter orders, deposit USDC to Lighter, withdraw from Lighter, move margin, what is funding on BTC, enable Lighter trading, or other Lighter account, market-data, order, margin, or deposit/withdraw requests.
---

# Lighter

## Overview

Lighter (lighter.xyz) mainnet trading and account management: market research,
perpetual and spot orders, leverage and margin controls, open-order and fill
tracking, USDC deposits from supported chains, withdrawals, and account-to-account
transfers. Trading is gated by the instance Lighter Trading integration
(`status` / `enable` / `disable`) **and** by Lighter API credentials held by the
platform.

Pick the matching command group below, then read that reference before acting.

## Scope

| In scope | Out of scope |
| --- | --- |
| Lighter market research, trading, funding, account management | Direct Lighter REST/SDK calls or hand-built signatures |
| Perp and spot markets on Lighter | Testnet — the platform is mainnet-only |
| USDC deposit from supported chains, withdraw, transfer | Bridging from unsupported chains (use another skill first) |
| Leverage, margin, cancel, modify | Provisioning Lighter API credentials (platform-side, not CLI) |
| Enable/disable Lighter Trading integration | Cross-venue arbitrage execution |

## Core Rules

1. Use `purr lighter <command>` for every Lighter action. Do not call Lighter
   APIs or construct signatures yourself.
2. Before any read or write under the Lighter gateway, ensure the trading
   integration is enabled. Run `purr lighter status` first when unsure. If
   disabled, explain and obtain confirmation, then run `enable` — never enable
   silently. Only `status`, `enable`, and `disable` work when trading is off.
3. **`--market-type` is effectively mandatory.** Several symbols exist as *both*
   spot and perp (`ETH`, `LIT`, `LDO`, `LINK`, `AAVE`, `UNI`, `SKY`, `AZTEC`).
   Always pass `--market-type perp` or `--market-type spot` on any command that
   takes `--market`. The CLI errors on ambiguity rather than guessing — do not
   work around that by picking one; ask the user if their intent is unclear.
4. **`--type` and `--market-type` are different flags.** `--market-type` selects
   perp vs spot and is accepted wherever `--market` is. `--type` is accepted on
   **only three commands**: `order` and `place-orders` (where it is the *order*
   type — `limit`, `market`, …) and `trades` (where it filters by side —
   `buy`, `sell`, `all`). On anything else the CLI rejects it with
   "Use `--market-type` for Lighter market filtering". Passing `--type perp` is
   always a bug.
5. **`--price` is REQUIRED on every order, including market orders.** For a
   market order the price is the *worst acceptable* fill price — a slippage
   bound, not an estimate. Derive it from the live book
   (`order-book-depth`), never from a guess, and state it in the confirmation.
   See [trading.md](references/trading.md).
6. Resolve markets with `purr lighter market --market <SYM> --market-type <t>`
   and use the returned size/price decimals before sizing an order. Never
   invent precision; `LIGHTER_DECIMAL_PRECISION_UNSUPPORTED` means the venue
   rejected your rounding, not that the order was too small.
7. Looking up markets, books, candles, funding, balances, positions, orders,
   trades, pnl, and status needs no confirmation. Anything that can change
   orders, positions, leverage, margin, account settings, integration
   enablement, or moves funds requires explicit confirmation first (see
   Confirmation Contract).
8. Perform market resolution, balance checks, and price lookups silently. Do not
   narrate tool calls or announce the upcoming sequence with "Let me…". Speak
   when a user decision is needed, when an action finishes, or when an error
   changes the workflow.
9. **`--amount-base-units` is an integer in base units, not USDC.** USDC has
   6 decimals on Lighter, so `10 USDC = 10000000`. Passing `10` withdraws
   0.00001 USDC. `withdraw` and `transfer` use base units; `deposit` uses a
   decimal `--amount`. Never mix them up. See
   [deposit-withdraw.md](references/deposit-withdraw.md).
10. Do not retry an account-changing action after an unknown or timed-out
    submission. `LIGHTER_SUBMIT_UNKNOWN`, `LIGHTER_PREVIOUS_SUBMISSION_UNKNOWN`,
    and a client timeout all mean *the state is unknown, not failed*. Reconcile
    with `requests`, `active-orders`, `trades`, or `positions` before doing
    anything else. See [errors.md](references/errors.md).
11. Do not claim a fill from a submit response alone. Verify with
    `active-orders`, `inactive-orders`, `trades`, or `positions`. Do not claim a
    withdrawal has landed from the submit alone — check `requests` /
    `request-status`.
12. Mainnet only. There is no network/testnet switch — the platform's query
    schemas are strict and reject unknown parameters, so do not invent flags.
    Pass only the flags documented in the references.
13. **Lighter orders carry no additional platform transaction fee.** Do not
    prompt for fee authorization and do not copy the Hyperliquid fee flow —
    there is no builder-fee approval step on Lighter.
14. The agent cannot provision Lighter API credentials. If credentials are
    missing or unverified (`LIGHTER_CREDENTIAL_NOT_FOUND`,
    `LIGHTER_CREDENTIAL_UNVERIFIED`), stop and tell the user to configure them
    on the platform side — do not attempt a CLI workaround.
15. Read commands use a 20s client timeout; write commands wait for the platform
    response. A read timeout is safe to retry, a write timeout is not (rule 10).

## Command Groups

| Group | What it does | Reference |
| --- | --- | --- |
| Integration / preflight | Enable/disable trading, status, SDK + credential readiness, account, balances, positions, limits | [preflight.md](references/preflight.md) |
| Market data | Markets, symbol resolution, order books, depth, trades, candles, funding rates | [market-data.md](references/market-data.md) |
| Symbols | Full spot/perp symbol tables and the `--market-type` rule | [symbols.md](references/symbols.md) |
| Trading | Orders, preview, cancel, modify, leverage, margin | [trading.md](references/trading.md) |
| Deposit / withdraw | USDC deposit from supported chains, withdraw, transfer, reconcile | [deposit-withdraw.md](references/deposit-withdraw.md) |
| Full recipes | First fund, perp long, spot buy, close, withdraw | [workflows.md](references/workflows.md) |
| Errors | Codes and stop / reconcile policy | [errors.md](references/errors.md) |

## Confirmation Contract

Before any account-changing action (`enable`, `disable`, `order`, `place-orders`,
`cancel`, `cancel-all`, `modify`, `update-leverage`, `update-margin`, `deposit`,
`withdraw`, `transfer`, `reconcile-deposit`):

1. Summarize the concrete parameters — market **and market type**, side, size,
   price (and for a market order, say explicitly that the price is the worst
   acceptable fill), order type, time in force, and any margin or fund impact.
   For amounts in base units, show both the base-unit integer and the human
   USDC value.
2. Ask exactly:
   `Do you want to execute this Lighter action with these parameters? (Yes/No)`
3. Run the action only after an explicit yes on the immediately preceding user
   turn for that unchanged action. The initial request, any changed detail, or
   an intervening request requires confirmation again.

One confirmation authorizes one action. The sole exception is a leverage change
immediately followed by its order: one final confirmation may authorize both
when the summary explicitly includes the leverage value, margin mode, and the
complete order parameters. Execute the leverage change first and submit the
order only after it succeeds.
