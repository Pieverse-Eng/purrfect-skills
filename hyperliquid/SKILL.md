---
name: hyperliquid
description: Use when the user asks to trade or manage Hyperliquid — e.g. check my HL balance, open a long on ETH, set leverage to 5x, cancel my open orders, deposit USDC to Hyperliquid, withdraw from HL, buy TSLA perp on xyz, move USDC to spot, what is funding on BTC, or other Hyperliquid account, market-data, order, collateral, or deposit/withdraw requests.
---

# Hyperliquid

## Overview

Hyperliquid mainnet trading and account management: market research, perpetual
and spot orders, leverage and risk controls, open-order and fill tracking,
perp/spot and builder-dex collateral moves, Arbitrum USDC deposits into
Hyperliquid, and withdrawals back to Arbitrum. Includes HIP-3 builder-dex
markets (for example equity perps on `xyz`) and symbol resolution when bare
tickers are ambiguous.

Pick the matching command group below, then read that reference before acting.

## Scope

| In scope | Out of scope |
| --- | --- |
| Hyperliquid market research, trading, funding, and account management | Direct Hyperliquid REST/SDK calls or hand-built signatures |
| Perp, spot, and builder-dex markets (e.g. `xyz`) | Testnet / `--network` |
| Arbitrum USDC deposit into HL and HL withdraw | Bridging from other chains (use other skills first) |
| Leverage, cancel, modify, collateral moves | Cross-venue stock arb execution (use `stock-spread` for quote research) |

## Core Rules

1. Use `purr hyperliquid <command>` for every Hyperliquid action. Do not call
   Hyperliquid APIs or construct exchange signatures yourself.
2. Resolve markets with `purr hyperliquid symbol` and use the returned
   `assetId`, full `coin`, and `szDecimals` before placing or modifying orders.
   Never guess asset indices.
3. On symbol ambiguity, list candidates and ask the user; do not pick silently.
4. Looking up markets, balances, positions, orders, and fills needs no
   confirmation. Any action that can change orders, positions, leverage,
   collateral, account settings, fee authorization, or on-chain funds requires
   explicit confirmation first (see Confirmation Contract).
5. Perform market resolution, balance checks, price lookups, and other
   preparation silently. Do not announce tool calls, preflight checks, or the
   upcoming sequence with phrases such as “Let me…” or “What we need to do.”
   Speak when a user decision or confirmation is needed, when an action
   finishes, or when an error changes the workflow.
6. For ordinary single order, modify, or cancel actions, build the complete
   wire payload in memory and pass compact JSON with `--body-json`. Use
   `--body-file` only for genuinely large batches and only at a known writable
   workspace path. Do not use `/tmp` with file-writing tools.
7. Deposits must be at least **5 USDC**. Platform rejects smaller amounts.
8. Hyperliquid keeps **perp** and **spot** USDC separate. Deposits land on the
   **perp** side. Move collateral with `usd-class-transfer` or `send-asset`
   when the user needs spot or a builder dex.
9. Do not retry account-changing actions after unknown broadcast, deferred
   policy, or partial success. Reconcile by checking state, orders, or fills.
10. Do not claim a fill from a submit response alone. Verify with
   `order-status`, `orders`, `fills`, or `state`.
11. Never pass `--network`. The CLI and platform are mainnet-only.
12. After resolving a perpetual market, check the additional fee authorization
    with `purr hyperliquid builder-fee-status` before confirmation or any
    account-changing preparation for the order. Never use an order as the
    authorization check, and never authorize the fixed additional `0.05%` fee
    silently.
13. For every non-default dex market, query that dex's state and treat only its
    available collateral as usable for the order. Default perp collateral does
    not fund a builder-dex order. If the target dex is short, confirm and run
    `send-asset`, then verify the destination balance before changing leverage
    or submitting the order. Never use a rejected order to discover this.

## Command Groups

| Group | What it does | Reference |
| --- | --- | --- |
| Preflight / account | Wallet address, account state, positions, balances, fee authorization, abstraction mode | [preflight.md](references/preflight.md) |
| Market data | Symbol resolve, markets, prices, L2 book, candles, funding | [market-data.md](references/market-data.md) |
| Trading | Orders, fee authorization, modify, cancel, leverage, status, fills | [trading.md](references/trading.md), [order-wire-format.md](references/order-wire-format.md) |
| Collateral | Perp↔spot USDC and default↔builder-dex USDC | [collateral.md](references/collateral.md) |
| Deposit / withdraw | Arbitrum USDC bridge in; withdraw to Arbitrum | [deposit-withdraw.md](references/deposit-withdraw.md) |
| Full recipes | First fund, crypto perp, equity perp, spot, close, withdraw | [workflows.md](references/workflows.md) |
| Errors | Codes and stop / reconcile policy | [errors.md](references/errors.md) |

## Confirmation Contract

Before any account-changing action (`order`, `modify`, `cancel`, `cancel-by-cloid`,
`update-leverage`, `schedule-cancel`, `set-abstraction`, `usd-class-transfer`,
`send-asset`, `deposit`, `withdraw`):

1. Summarize the concrete parameters (market/`assetId`, side, size, price or
   amount, and any collateral impact).
2. Ask exactly:
   `Do you want to execute this Hyperliquid action with these parameters? (Yes/No)`
3. Run the action only after an explicit yes on the immediately preceding user
   turn for that unchanged action. The initial request, any changed detail, or
   an intervening request requires confirmation again.

One confirmation normally authorizes one action only. The sole workflow
exception is a leverage change immediately followed by its order: one final
trade confirmation may authorize both when the summary explicitly includes
the leverage value, margin mode, and complete order parameters. Execute the
leverage change first and submit the order only after it succeeds. Fee
authorization and collateral transfers always require separate confirmations.

Fee authorization uses the separate consent prompt below instead of this
generic action prompt.

## Perpetual Fee Authorization

Perpetual orders carry a fixed additional `0.05%` transaction fee; spot orders do not.
Before confirmation or any account-changing preparation for a perpetual order,
follow [preflight.md](references/preflight.md).

When authorization is required, keep the user-facing message to these two
sentences:
`Hyperliquid perpetual trades include an additional 0.05% transaction fee.`

Then ask exactly:
`Do you approve the additional 0.05% transaction fee for future Hyperliquid perpetual trades? (Yes/No)`

Keep this user-facing explanation brief. Never call it a “builder fee” or
expose builder addresses, builder codes, or internal command names to the user.
Do not explain implementation details or persistence unless the user asks.
After successful authorization, report only that the `0.05% transaction fee`
was authorized, then continue preparation silently until the next confirmation.

Only an explicit yes on the immediately preceding turn authorizes
`approve-builder-fee`. On no, status-check failure, or unknown status, stop.
Never use an order as a status probe. If an order returns
`HYPERLIQUID_BUILDER_FEE_APPROVAL_REQUIRED`, follow the 428 fallback in
[errors.md](references/errors.md); never auto-retry it.

Do not request fee rate or builder address parameters. The CLI does not provide
a revoke command.
