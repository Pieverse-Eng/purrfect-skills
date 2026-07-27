---
name: lighter
description: Use when the user asks to trade or manage Lighter (lighter.xyz) — e.g. check my Lighter balance, open a long on SOL perp, buy LIT spot, set leverage to 5x, cancel my Lighter orders, open a Lighter account, deposit USDC to Lighter, withdraw from Lighter, fast withdraw, update margin, what is funding on BTC, enable Lighter trading, approve the partner fee, or other Lighter account, market-data, order, margin, or deposit/withdraw requests.
---

# Lighter

## Overview

Lighter (lighter.xyz) mainnet trading through the platform gateway and
`purr lighter`. Covers market research, perpetual and spot orders, leverage and
margin controls, order lifecycle, multi-chain USDC funding, secure and fast
withdrawals, and account readiness (including first-time `open-account`).

Access has two independent gates:

1. **Lighter Trading integration** — `status` / `enable` / `disable`
2. **Account readiness** — TEE wallet must open a Lighter account; the platform
   then generates and registers the API key. Agents never handle private keys.

Pick the matching command group below, then read that reference before acting.

## Scope

| In scope | Out of scope |
| --- | --- |
| Market data, orders, leverage, margin on Lighter mainnet | Direct Lighter REST/SDK calls or hand-built signatures |
| Perp and spot markets | Testnet or invented network flags |
| Multi-chain USDC open-account and deposit | Bridging USDC onto a source chain (use another skill first) |
| Secure withdraw (Ethereum) and fast withdraw (Arbitrum) | Account-to-account transfers (CLI does not support them) |
| Partner fee status / approval (fixed 5 bps when configured) | Pasting or configuring Lighter API private keys |
| Enable/disable Lighter Trading | Cross-venue arb execution |

## Core Rules

1. Use `purr lighter <command>` for every Lighter action. Do not call Lighter
   APIs or construct signatures yourself.
2. Before any gateway read or write, ensure trading is enabled. Run
   `purr lighter status` when unsure. If disabled, explain and obtain
   confirmation, then `enable` — never enable silently. Only `status`,
   `enable`, and `disable` work while trading is off.
3. Treat `purr lighter account` as the readiness call. Branch on
   `status` (`account_opening_required` → `initializing` →
   `account_discovered` → `verifying_key` → `ready` / `error`). First use is
   **`open-account`**, not a normal deposit. Ordinary deposits fail with
   `LIGHTER_ACCOUNT_NOT_READY` until the account is open.
4. **`--market-type` is effectively mandatory** whenever you pass `--market`.
   Several tickers exist as both spot and perp (`ETH`, `LIT`, `LDO`, `LINK`,
   `AAVE`, `UNI`, `SKY`, `AZTEC`, …). Prefer `--market-type perp|spot`. On
   ambiguity the CLI returns `LIGHTER_MARKET_AMBIGUOUS` — ask the user; never
   pick silently.
5. **`--type` ≠ `--market-type`.** `--market-type` filters perp vs spot.
   `--type` is only for `order` / `place-orders` (order type) and `trades`
   (side filter). Passing `--type perp` is always wrong.
6. Resolve markets with
   `purr lighter market --market <SYM> --market-type <perp|spot>` (or
   `--market-id`) and use the returned decimals / market id. Never invent
   market ids or precision.
7. **`--price` is required on every order, including market orders.** For a
   market order it is the worst acceptable fill (slippage bound). Walk
   `order-book-depth` for the exact size, put the bound and its distance from
   touch/VWAP in the confirmation, and stop if depth is insufficient. If the
   user gave no slippage tolerance, ask — never invent a default buffer.
8. Looking up status, markets, books, candles, funding, account, balances,
   positions, orders, trades, pnl, deposits, requests, and previews needs no
   confirmation. Anything that can change orders, positions, leverage, margin,
   funds, fee authorization, or integration state requires confirmation first
   (see Confirmation Contract).
9. Prepare silently. Do not narrate tool calls or announce the remaining steps
   with “Let me…”. Speak when a user decision is needed, when an action
   finishes, or when an error changes the workflow.
10. Prefer CLI flags for ordinary single orders. Use `--body-json` /
    `--body-file` only for `order-preview` (and other body-only paths). Do not
    write payload files under `/tmp`.
11. **Amounts are decimal USDC strings** on `open-account`, `deposit`,
    `withdraw`, and `fast-withdraw` (for example `--amount 25`). There is no
    `--amount-base-units` flag in this CLI.
12. Do not retry account-changing actions after unknown submit, client timeout
    on a write, or deferred policy. Reconcile with `requests`,
    `deposit-status`, `active-orders`, `trades`, or `positions`. The only
    intentional funding re-run is `open-account` when the response has
    `nextAction: "resume_account_opening"` — see
    [deposit-withdraw.md](references/deposit-withdraw.md).
13. Do not claim a fill from a submit response alone. Verify with
    `active-orders`, `inactive-orders`, `trades`, or `positions`. Do not claim
    a withdraw has arrived from submit alone — keep any `request_id` and check
    `request-status` / balances.
14. Mainnet only. Pass only documented flags; the platform rejects unknown
    query/body keys.
15. Before confirming **any** order (or modify that can re-apply fee checks),
    run `purr lighter partner-fee-status` when the account is ready. If status
    is `approval_required` or `expired`, follow Partner Fee Authorization.
    If `not_configured`, continue without prompting. Never use an order as a
    fee-status probe.
16. `balances` and `positions` hit the same readiness handler as `account`.
    Before `status: ready`, treat the payload as a readiness object — not an
    empty portfolio.
17. `place-orders` submits **one** order (same body as `order`). It is not a
    batch. `order-preview` is non-mutating and needs no execution confirmation.
18. Withdrawals: without `--yes`, `withdraw` / `fast-withdraw` only **preview**.
    With `--yes`, the CLI confirms and executes (fast withdraw re-quotes fees).
    Secure withdraw minimum is **1 USDC** (destination Ethereum). Fast withdraw
    minimum is **4 USDC after fee** (destination Arbitrum).
19. Deposit minimums are per chain: Ethereum mainnet **1 USDC**; Arbitrum, Base,
    Avalanche, HyperEVM **5 USDC**. Prefer `deposit-networks` / response
    `minAmount` over memorized numbers.
20. `disable` is blocked until the Lighter account is empty (no open orders,
    positions, non-USDC spot, or active requests). Resolve exposure first;
    never imply disable cancels or closes anything for you.
21. Never ask the user for a Lighter API private key. Credential setup is
    platform-managed during `open-account`.

## Command Groups

| Group | What it does | Reference |
| --- | --- | --- |
| Integration / readiness | status, enable/disable, account, open-account, partner fee, balances, positions | [preflight.md](references/preflight.md) |
| Market data | markets, books, depth, trades, candles, funding | [market-data.md](references/market-data.md) |
| Symbols | Dual spot/perp tickers and `--market-type` rule | [symbols.md](references/symbols.md) |
| Trading | order, preview, cancel, modify, leverage, margin | [trading.md](references/trading.md) |
| Deposit / withdraw | multi-chain deposit, secure + fast withdraw, reconcile | [deposit-withdraw.md](references/deposit-withdraw.md) |
| Full recipes | first open, fund, perp, spot, close, withdraw | [workflows.md](references/workflows.md) |
| Errors | codes and stop / reconcile policy | [errors.md](references/errors.md) |

## Confirmation Contract

Before any account-changing action (`enable`, `disable`, `open-account`,
`deposit`, `order`, `place-orders`, `cancel`, `cancel-all`, `modify`,
`update-leverage`, `update-margin`, `withdraw` with `--yes`, `fast-withdraw`
with `--yes`, `approve-partner-fee`, `reconcile-deposit`):

1. Summarize the concrete parameters: market **and market type**, side, size,
   price (for market orders, state that price is the worst acceptable fill),
   order type / TIF, chain and amount for funding, destination for withdraws,
   and any margin or leverage impact.
2. Ask exactly:
   `Do you want to execute this Lighter action with these parameters? (Yes/No)`
3. Run only after an explicit yes on the immediately preceding user turn for
   that unchanged action. The initial request, any changed detail, or an
   intervening request requires confirmation again.

One confirmation authorizes one action. The sole exception is a leverage change
immediately followed by its order: one final confirmation may authorize both
when the summary includes the leverage value, margin mode, and full order
parameters. Execute leverage first; submit the order only after it succeeds.
Partner fee approval always requires its own consent prompt.

## Partner Fee Authorization

When partner attribution is configured on the platform, **orders** require a
fixed **5 bps (0.05%)** partner fee approval (maker and taker, spot and perp).
Non-order actions do not carry this fee. Check status before order confirmation:

```bash
purr lighter partner-fee-status
```

| Status | Action |
| --- | --- |
| `not_configured` | Continue; do not prompt for fee consent |
| `approved` | Continue; do not re-prompt |
| `approval_required` or `expired` | Request consent with the prompt below, then `approve-partner-fee` |
| Error / unknown | Stop; do not submit an order as a probe |

User-facing message when approval is needed:

`Lighter trades include an additional 0.05% partner fee.`

Then ask exactly:

`Do you approve the additional 0.05% partner fee for future Lighter trades? (Yes/No)`

Keep the explanation brief. Do not expose integrator account indexes, fee unit
integers, or internal command names unless the user asks. After successful
approval, report only that the `0.05% partner fee` was authorized, then continue
preparation silently until the next confirmation.

Only an explicit yes on the immediately preceding turn authorizes
`approve-partner-fee`. On no, status failure, or unknown status, stop. If an
order returns `LIGHTER_PARTNER_FEE_APPROVAL_REQUIRED`, follow the 428 path in
[errors.md](references/errors.md); never auto-retry the order.
