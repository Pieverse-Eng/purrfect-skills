---
name: hyperliquid
description: Trade and manage Hyperliquid perpetuals, spot, and HIP-3 markets through purr CLI, including balances, orders, leverage, collateral transfers, and Arbitrum USDC deposits and withdrawals.
---

# Hyperliquid

Use `purr hyperliquid` for mainnet execution. Do not construct exchange
signatures, use direct REST/SDK writes, or pass `--network`. Hosted market
discovery and cross-venue comparison belong to the main agent's research tools.

## Start Here

Read the reference for the user's task before acting:

| Task | Required reference |
| --- | --- |
| Prepare a trade card, open/close, protect, modify, or cancel | [workflows.md](references/workflows.md), then the command references it selects |
| Explain funds, inspect accounts, enable/disable, change account mode | [preflight.md](references/preflight.md) |
| Resolve a market or inspect public market data | [market-data.md](references/market-data.md) |
| Deposit or withdraw | [deposit-withdraw.md](references/deposit-withdraw.md) |
| Transfer collateral inside Hyperliquid | [collateral.md](references/collateral.md) |
| Inspect orders/fills, set leverage, schedule cancellation | [trading.md](references/trading.md) |
| Order parameters and quantity calculation | [order-commands.md](references/order-commands.md) |
| Error, partial execution, or uncertain submission | [errors.md](references/errors.md) |

Prepare the required commands and verify their inputs before confirmation.
Use the references relevant to the operation, including their prerequisites.
Report meaningful progress, blockers, and results without narrating routine
lookups. Use familiar user-facing terms such as "your wallet".

## Confirmation Contract

Before any account-changing action (all order-placement commands, all
`modify-*` commands, `cancel`, `cancel-by-cloid`, `enable`, `disable`,
`update-leverage`, `schedule-cancel`, `set-abstraction`,
`usd-class-transfer`, `send-asset`, `deposit`, or `withdraw`):

1. Summarize the concrete parameters (market/`assetId`, side, size, price or
   amount, and any collateral impact). For enable/disable, state the integration
   effect clearly.
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

## Transaction Fee Authorization

Hyperliquid order-placement commands (`limit-order`, `bracket-order`,
`stop-loss`, `take-profit`, and `protect-position`) carry a fixed additional
`0.05%` transaction fee on executed notional. Non-order actions (cancel,
leverage, transfer, deposit, withdraw, etc.) do not carry this fee. Before
confirmation or any account-changing preparation for a new order, follow
[preflight.md](references/preflight.md).

When authorization is required, keep the user-facing message to these two
sentences:
`Hyperliquid trades include an additional 0.05% transaction fee.`

Then ask exactly:
`Do you approve the additional 0.05% transaction fee for future Hyperliquid trades? (Yes/No)`

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

## Execution Invariants

- Resolve exact markets and use returned `coin`, `assetId`, and `szDecimals`.
  Ask on unresolved ambiguity; never guess an asset ID or order OID.
- Wallet funds, default perp, spot, and builder-dex collateral are distinct.
  Use [preflight.md](references/preflight.md) for all-DEX and wallet checks.
- Use typed order commands; TP/SL requires trigger orders. Filled entry orders
  are historical: manage the position or its open protection instead.
- Verify each prerequisite before dependent writes. On uncertain or partial
  submission, reconcile before continuing; never blindly resubmit a plan.
- Verify fills and protection using state/orders/status. Retain withdrawal
  nonce and verify settlement separately; submission is not arrival.
