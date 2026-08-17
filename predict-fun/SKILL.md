---
name: predict-fun
description: Use when the user asks to trade or inspect Predict.fun — e.g. list open markets, buy YES, sell NO, quote a market, check Predict positions or orders, cancel Predict orders, approve trading, split merge or redeem shares, convert a category position, set a referral, or stream the Predict orderbook.
---

# Predict.fun

## Overview

Predict.fun is a prediction market on BNB Chain. Each market is a yes-or-no
question. Traders buy and sell YES and NO shares with USDT; the share price
(between 0 and 1) is the implied chance that side wins. After the event
resolves, winning shares redeem for collateral.

Use it to find markets, read quotes and order books, check balances and
positions, place or cancel orders, approve the protocol, split / merge /
redeem / convert shares, set a referral, and follow live updates.

## Out of scope

- Other prediction venues (DFlow, Kalshi, Binance prediction)
- Testnet or chains other than BNB Chain mainnet

Use the enum tables in this skill, or `purr predict-fun help` if they
disagree with the installed CLI.

Never mention CLI commands, flags, or parameter names in the user-facing
conversation. Speak in product language only.

## Command Groups

| Group | What it does | Reference |
| --- | --- | --- |
| Account / readiness | Wallet identity, USDT/BNB/outcome balances, gas, referral, current approvals | [preflight.md](references/preflight.md) |
| Discovery | Categories, search, markets, quotes, orderbook, timeseries, SSE | [discovery.md](references/discovery.md) |
| Orders | Preview/execute limit and market orders; cancel; remove-from-book | [trading.md](references/trading.md) |
| Approvals / positions | Protocol approve/revoke; split, merge, redeem, convert | [positions.md](references/positions.md) |
| Recipes | First trade, cancel, redeem, convert | [workflows.md](references/workflows.md) |
| Errors | Codes and stop / resume / reconcile policy | [errors.md](references/errors.md) |

## Confirmation Contract

Each user yes authorizes **one** `*-execute` (or one `set-referral`). Ask
only about the action you will run next. There is no “Approve + Buy”,
“Approve + Sell”, or “Yes, proceed with both” — that is one confirmation,
not two.

Keep the question short and only about this action. Include the outcome
display name plus `indexSet` and CLI `--outcome` when the action is a trade
(see [discovery.md](references/discovery.md)).

Approval (BUY, exact amount):

```text
Approve a <amount> USDT allowance for Predict.fun?

1. Approve only <amount> USDT
2. Approve unlimited
```

Use option 2 only when the user picks it and understands it is a standing
max allowance. Then `approval-preview` with `--amount <amount>` or
`--unlimited true`. After they confirm that preview, `approval-execute`.

After the approval is done, ask the order separately:

```text
Buy <amount> USDT of <outcome-name> on this market?
```

`<outcome-name>` is the display name from `outcomes` after the `indexSet` map.

Fixed trade path:

`approval-preview` → confirm → `approval-execute` → reconcile → **new**
`order-preview` → confirm → `order-execute`

On `PREDICT_APPROVAL_ALREADY_SET`, skip `approval-execute` and go to the new
`order-preview`. The pre-approval order preview is not reusable.

Remove-from-book confirmation must also state that it does not invalidate
the signature on-chain and can strand collateral.

When an execute response includes a transaction `hash` (on-chain cancel,
approval, approval-revoke, or position action), include a BscScan link using
that hash exactly:

```text
https://bscscan.com/tx/<hash>
```

`order-execute` and `remove-from-book-execute` submit off-chain; they return
an order hash, not a BNB transaction.
