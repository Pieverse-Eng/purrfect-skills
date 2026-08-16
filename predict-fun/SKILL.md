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

Before `set-referral`, `order-execute`, `cancel-execute`, `cancel-all-execute`,
`remove-from-book-execute`, `approval-execute`, `approval-revoke-execute`, or
`position-execute`:

1. Summarize the concrete parameters from the latest preview (or, for
   referral, the five-character code). Include market id and title, outcome,
   side, strategy, decimal amounts or price, readiness warnings, expiry, and
   any on-chain effect (approval, cancel, split/merge/redeem/convert).
2. Ask exactly:
   `Do you want to execute this Predict.fun action with these parameters? (Yes/No)`
3. Run only after an explicit yes on the immediately preceding user turn for
   that unchanged action. The initial request, any changed detail, an expired
   preview, or an intervening request requires confirmation again.

One confirmation authorizes one execute (or one `set-referral`). Approvals and
the order they enable are separate confirmations. Remove-from-book must also
state that it does **not** invalidate the signature on-chain and can strand
collateral.
