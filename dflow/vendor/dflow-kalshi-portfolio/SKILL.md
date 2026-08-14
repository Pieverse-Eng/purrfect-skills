---
name: dflow-kalshi-portfolio
description: View what a wallet holds on DFlow's Kalshi prediction markets — current positions, unrealized mark-to-market, realized P&L, activity history, and redeemable winners. Use when the user asks "what are my positions?", "am I up or down?", "what's my fill history?", or "what can I redeem?". Read-only. Do NOT use to place sells or redemptions, for market-wide data, or to discover new markets.
disable-model-invocation: true
user-invocable: false
---

# DFlow Kalshi Portfolio

Read-only views on a wallet's Kalshi activity. Start from the parent skill's
`purr dflow positions`. Use `onchain-trades` and `markets/batch` only for
fields positions did not return.

## Position rows

- `type: "spot"` — SOL, USDC, CASH, and other wallet tokens.
- `type: "outcome"` — Kalshi outcome token, with `side` (`yes` | `no`) and a
  `market` object.

USDC / CASH `uiAmount` is already dollar-equivalent (modulo depeg). Outcome
tokens need a mark. Same market on USDC and CASH is two rows.

## Views

### Unrealized mark-to-market

Mark at the **bid on the held side**, not the ask:

- Long YES → `uiAmount * parseFloat(yesBid)`
- Long NO → `uiAmount * parseFloat(noBid)`

Sum for wallet-level unrealized value. Subtract cost basis for unrealized P&L.

### Realized activity and P&L

`onchain-trades` with the wallet address, `sortBy=createdAt`,
`sortOrder=desc`.

- Activity: `createdAt`, `marketTicker`, `side`, `inputAmount`,
  `outputAmount`, `transactionSignature`.
- Cost basis: net settlement-mint flow per outcome mint.
- Fees: sum `feeAmount` in the settlement mint.

### Redeemable

All three must hold:

- market `status` is `determined` or `finalized`
- `redemptionStatus` is `"open"`
- the held mint is the winning side (`market.result`)

Then hand off to `dflow-kalshi-trading` (a sell of the winning side).

## Views to pick

Holdings / mark-to-market / realized P&L / activity / redeemable — infer from
the request.

## Gotchas

- **Mark on the bid.** Marking on the ask overstates the book.
- **Redemption is three ANDed conditions**, not just "market closed."
- **Balance lag after fill.** A just-landed fill may not show yet. Retry
  once before assuming failure.
- After a full sell or redeem the token account may close and disappear.
  History is on `onchain-trades`.

## Sibling skills

- `dflow-kalshi-trading` — sell or redeem a position
- `dflow-kalshi-market-data` — orderbook / tape for a watched market
- `dflow-kalshi-market-scanner` — find new markets
- `dflow-proof-kyc` — verify before a new buy
