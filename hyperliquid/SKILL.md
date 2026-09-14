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

For a trade, prepare the complete command sequence before presenting the
card; loading this entrypoint alone is not execution preparation. Do not
guess flags or use a rejected order to discover funds, fees, or minimums.
Report meaningful progress, blockers, and results without narrating routine
lookups. Call the connected wallet "your wallet", not "TEE".

## Confirmation Contract

Read-only checks need no confirmation. Account-changing operations require
authorization covering their concrete parameters and effects.

When the main agent's hosted workflow explicitly authorizes one confirmation
for a complete disclosed plan, follow that scope, including funding, collateral
moves, fees, leverage, and protection. Do not ask again for covered steps.
A disclosed proportional sizing rule is part of that plan; other parameter
changes require a revised confirmation. This contract governs all references
below; references do not introduce additional confirmation gates.

Otherwise, summarize and confirm each standalone action before executing it.
One trade confirmation may cover its disclosed leverage change and order.
Standing fee approval, enabling trading, deposits, and collateral transfers
are not implied by an order-only confirmation. Read-only work does not
invalidate existing consent for unchanged parameters.

Disclose the additional **0.05% transaction fee on executed notional** and
its scope for **future Hyperliquid trades** before obtaining standing fee
approval. Say "additional transaction fee", not "builder fee"; do not expose
builder addresses or ask for fee parameters. Without a covering hosted plan,
ask: "Do you approve the additional 0.05% transaction fee for future
Hyperliquid trades? (Yes/No)". An approved status needs no repeat approval.
The CLI has no fee-revocation command.

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
