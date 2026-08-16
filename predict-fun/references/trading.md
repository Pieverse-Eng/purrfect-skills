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
  [--reserved-balance-policy REJECT_MARKET_ORDER|SKIP_RESERVED_BALANCE_CHECKS]
purr predict-fun order-execute --preview-id <uuid>

purr predict-fun cancel-preview --order-hashes <0x-hash,0x-hash,...>
purr predict-fun cancel-all-preview
purr predict-fun cancel-execute --preview-id <uuid>
purr predict-fun cancel-all-execute --preview-id <uuid>

purr predict-fun remove-from-book-preview --order-hashes <0x-hash,0x-hash,...>
purr predict-fun remove-from-book-execute --preview-id <uuid> --acknowledge-risk true
```

`--order-hashes` is 1–25 `0x`-prefixed 32-byte hashes.

`--reserved-balance-policy` is `REJECT_MARKET_ORDER` or
`SKIP_RESERVED_BALANCE_CHECKS`. Omit it by default. Pass
`SKIP_RESERVED_BALANCE_CHECKS` only when the user asks to skip reserved-balance
checks.

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

Empty or shallow books return `PREDICT_INSUFFICIENT_LIQUIDITY`. Ask the user
for a smaller size or a LIMIT order.

## Place-order workflow

Run preparatory queries silently.

1. Resolve `--market-id` and confirm `tradingStatus` is `OPEN`
   ([discovery.md](discovery.md)).
2. `readiness --market-id <id>` and, for a SELL, `positions`.
3. Map the user's side with the `indexSet` table in
   [discovery.md](discovery.md), then `market-quote` and
   `orderbook --outcome YES|NO`.
4. If readiness or a later preview warns that approvals are missing, follow
   [positions.md](positions.md) and confirm the approval **before** the order.
5. `order-preview` with the exact flags you will honor at execute time.
6. Read `previewId`, `expiresAt`, `amounts`, `orderHash`, `readiness`, and
   `warnings`. If balance or approvals fail, stop and fix that first.
7. Confirm, then `order-execute --preview-id <previewId>` immediately.

### Verify a MARKET fill

Predict.fun REST can lag a fill by a few seconds. `order` may still show
`OPEN` / 0 filled while `positions` or `balances` already moved. That is
upstream eventual consistency, not an unfilled order.

After `order-execute`:

1. `order --order-hash <preview.orderHash>`
2. `positions --market-id <id>`
3. If the order is `OPEN` / 0 filled and `positions` or `balances` already
   moved:
   - `matches --market-id <id>`
   - `activity`
   - wait a few seconds, then `order --order-hash <preview.orderHash>` again
4. Check leftover shares with `balances --market-id <id>`. `positions` can
   omit dust below the tradable floor.

Say the order is unfilled only when it is still `OPEN`, `matches` has no
fill, and `balances` is unchanged. Use `orders --status OPEN` for a resting
LIMIT.

## Cancel vs remove-from-book

**On-chain cancel** (`cancel-preview` / `cancel-all-preview` then
`cancel-execute` / `cancel-all-execute`) is the default. It invalidates the
order on-chain.

If `cancel-all-preview` returns `PREDICT_CANCEL_ALL_REQUIRES_BATCHING`, page
`orders` and `cancel-preview` with explicit hashes (max 25).

After a confirmed cancel, an order can still show
`chain_confirmed` / `upstream_pending` until Predict REST is terminal. Re-run
the **same** `cancel-execute` with the **same** `previewId`, or re-read
`order`. Include `https://bscscan.com/tx/<hash>` for each returned transaction
hash.

**Remove-from-book** is a different operation. It does not invalidate the
signature on-chain, does not go through wallet-policy, and can strand
collateral. Use it only when the user explicitly asks to pull orders off the
book without on-chain cancel. The confirmation must state that risk.
`--acknowledge-risk true` is required on execute; the CLI refuses without it.

Rejected removals are per-hash (`PREDICT_REMOVE_FROM_BOOK_REJECTED`). Report
each hash.
