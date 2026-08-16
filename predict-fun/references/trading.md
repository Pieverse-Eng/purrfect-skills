# Orders and cancellations

Place, inspect, and cancel Predict.fun orders through `purr predict-fun`.
Inspect freely. Confirm every execute. Amounts are **decimal strings**, not
wei. Price is a share price in `(0, 1)`.

## Commands

```bash
purr predict-fun order-preview \
  --market-id <id> --outcome YES|NO --side BUY|SELL --strategy LIMIT|MARKET \
  [--quantity <decimal>] [--spend <decimal>] [--price <decimal>] \
  [--slippage-bps <0-5000>] [--is-min-amount-out true|false] \
  [--expires-at <ISO-8601>] \
  [--fill-or-kill true|false] [--post-only true|false] \
  [--self-trade-prevention CANCEL_MAKER|CANCEL_TAKER|CANCEL_BOTH] \
  [--reserved-balance-policy <policy>]
purr predict-fun order-execute --preview-id <uuid>

purr predict-fun cancel-preview --order-hashes <0x-hash,0x-hash,...>
purr predict-fun cancel-all-preview
purr predict-fun cancel-execute --preview-id <uuid>
purr predict-fun cancel-all-execute --preview-id <uuid>

purr predict-fun remove-from-book-preview --order-hashes <0x-hash,0x-hash,...>
purr predict-fun remove-from-book-execute --preview-id <uuid> --acknowledge-risk true
```

`--order-hashes` is 1–25 `0x`-prefixed 32-byte hashes.

`--reserved-balance-policy` is forwarded as given. Pass a value the user or a
prior payload supplied; do not invent one.

`fill-or-kill` and `post-only` cannot both be true.

## Order amounts

| Strategy / side | Required | Forbidden |
| --- | --- | --- |
| `LIMIT` | `--quantity` and `--price` | `--spend` |
| `MARKET` `BUY` | `--spend` **or** `--quantity` | both; `--price`; `--expires-at` |
| `MARKET` `SELL` | `--quantity` | `--spend`; `--price`; `--expires-at` |

Floors (platform-enforced):

- Quantity at least **0.01** shares
- Built order value at least **0.9 USDT**
- MARKET BUY `--spend` at least **1 USDT**

`--expires-at` is LIMIT-only and must be at least 30 seconds in the future.
`--slippage-bps` is 0–5000 (MARKET).

Empty or shallow books return `PREDICT_INSUFFICIENT_LIQUIDITY` rather than a
generic server error. Do not invent a default spend or slippage to “make it
work.”

## Place-order workflow

Run preparatory queries silently.

1. Resolve `--market-id` and confirm `tradingStatus` is `OPEN`
   ([discovery.md](discovery.md)).
2. `readiness --market-id <id>` and, for a SELL, `positions`.
3. `market-quote` or `orderbook --outcome <YES|NO>` for the intended side.
4. If readiness or a later preview warns that approvals are missing, follow
   [positions.md](positions.md) and confirm the approval **before** the order.
5. `order-preview` with the exact flags you will honor at execute time.
6. Read `previewId`, `expiresAt`, `amounts`, `orderHash`, `readiness`, and
   `warnings`. If balance or approvals fail, stop and fix that first.
7. Confirm, then `order-execute --preview-id <previewId>` immediately.

Verify with `order --order-hash <preview.orderHash>`. Use `orders --status
OPEN` only when you expect a resting LIMIT or a partial fill. Do not treat
submit `status: succeeded` as a fill.

## Cancel vs remove-from-book

**On-chain cancel** (`cancel-preview` / `cancel-all-preview` then
`cancel-execute` / `cancel-all-execute`) is the default. It invalidates the
order on-chain.

If `cancel-all-preview` returns `PREDICT_CANCEL_ALL_REQUIRES_BATCHING`, do not
retry cancel-all. Page `orders`, then `cancel-preview` with explicit hashes
(max 25).

After a confirmed cancel, an order can still show
`chain_confirmed` / `upstream_pending` until Predict REST is terminal. Re-run
the **same** `cancel-execute` with the **same** `previewId`, or re-read
`order`. Do not preview a second cancel for hashes that may already be in
flight.

**Remove-from-book** is a different operation. It does not invalidate the
signature on-chain, does not go through wallet-policy, and can strand
collateral. Use it only when the user explicitly asks to pull orders off the
book without on-chain cancel. The confirmation must state that risk.
`--acknowledge-risk true` is required on execute; the CLI refuses without it.

Rejected removals are per-hash (`PREDICT_REMOVE_FROM_BOOK_REJECTED`). Report
each hash; do not call a partial removal a success.
