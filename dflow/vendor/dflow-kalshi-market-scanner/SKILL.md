---
name: dflow-kalshi-market-scanner
description: Find Kalshi prediction markets on DFlow that match a criterion — arbitrage (YES+NO<$1), cheap long-shots, near-certain short-dated plays, biggest movers, widest spreads, highest volume, closing soonest, and series/event-level scans. Use when the user asks "where's the free money?", "any mispriced markets?", "cheap YES with volume", "what moved today?", "markets closing soon", or "alert me when X happens". Do NOT use to place orders, view a user's positions, or for general live-data plumbing.
disable-model-invocation: true
user-invocable: false
---

# DFlow Kalshi Market Scanner

Find Kalshi markets that match a **criterion**. This skill is named scans
(filter-and-rank recipes). Use the parent skill's `purr dflow metadata` and
`purr dflow stream` commands for the actual calls. Paths below are Metadata
paths without an `/api/v1/` prefix.

## Scanner skeleton

1. **Enumerate** — `markets` (flat) or `events` with `withNestedMarkets=true`
   (grouped). Filter `status=active`. Page until done. `limit` caps at **255**;
   256+ returns 400. Docs often use 200. First page: omit `cursor` or use `0`.
   The returned `cursor` is the next offset. Stop when `markets.length < limit`.
   Pass `isInitialized=true` only for markets tradable on DFlow right now
   (short-duration Kalshi markets may be active but not tokenized yet).
2. **Signal** — top-of-book is already on the market object: `yesBid` /
   `yesAsk` / `noBid` / `noAsk` (4-decimal probability strings),
   `volume24hFp` / `volumeFp` / `openInterestFp` (dollar-equivalent strings),
   `closeTime` (unix). No orderbook call needed for best prices. Momentum:
   candlesticks or the `prices` / `trades` stream. Ladder depth:
   `orderbook/by-mint/<mint>`. Recent prints: `trades`.
3. **Compute the metric.**
4. **Filter and rank.** Top-N, default 10.

**Polling** for "show me now". **Stream** (`prices`, `trades`, `orderbook`)
for "alert me when". Prefer ticker lists; `all=true` is a firehose.

**Prefer rank-based filters over fixed numeric thresholds.** Volume spans
many orders of magnitude. Only use a fixed number when it is semantic
(`YES + NO < $1.00`, `status=active`) or the user supplied it.

## Scans

### 1. Arbitrage — `YES + NO < $1`

Metric: `parseFloat(yesAsk) + parseFloat(noAsk) < 1.00`. Rank largest gap
(`1 - sum`) descending. Skip null asks.

### 2. Long-shot YES

Rank by `volume24hFp` descending, take the top quartile as the "actually
trading" pool, then sort that pool by `yesAsk` ascending. Do not invent a
cents ceiling unless the user gives one. Alternate: `volume24hFp / yesAsk`.

### 3. Near-certain short-dated YES

`yesAsk` above a **user-supplied** bar. If they say "near-certain" with no
number, ask. Rank `closeTime` ascending. Do not invent a default window.

### 4. Momentum

Candlesticks on a volume-prefiltered set, or the `prices` stream. Rank by
absolute or signed pct change over a user window (default 60 minutes). No
default pct threshold.

### 5. Widest spreads

`yesAsk - yesBid`, descending. Market object only.

### 6. Highest volume

`volume24hFp` descending, or sum `trades` since a cutoff.

### 7. Closing soonest

`closeTime - now`, ascending. Stack with scan 3 or 6.

### 8. Event- and series-level

One event: `event/<eventTicker>` with `withNestedMarkets=true`, then reduce
(`min(yesAsk)`, `Σ yesAsk`). Across a series: `series/<seriesTicker>` plus
its events. There is **no** `mutuallyExclusive` flag — summing YES only
makes sense when outcomes partition one future. Flag that assumption.

## Point lookups

- Ticker: `market/<ticker>` (singular).
- Outcome mint: `market/by-mint/<mint>`.
- Event: `event/<eventTicker>` with `withNestedMarkets=true`.
- Free text: `search`.

Plural `markets` / `events` are lists (`cursor`, `limit`). Mixing them up
404s.

## Missing pieces

1. **Which scan** (or a phrase you can map to one).
2. **Thresholds they supply — use verbatim.** Do not invent a dollar or cents
   cutoff. If they say "big movers" with no number, ask what bar they want.
3. **Snapshot vs stream.**
4. **Top-N** (default 10).

Hand a chosen market to `dflow-kalshi-trading` to trade.

## Gotchas

- **Top-of-book lives on the market object.** Do not loop orderbook just for
  best prices.
- **Prices and volume are market-wide; trading is rail-scoped.** Pass the
  ticker to trading and let that step pick USDC vs CASH (default USDC).
- **Orderbook is bid ladders only** (`yes_bids`, `no_bids`). Best YES ask =
  `1 - max(no_bids keys)`.
- **Two price scales.** Market/orderbook: `"0.4200"`. Trades: integer 0–10000
  plus `yes_price_dollars` / `no_price_dollars`.
- **Render `title — yesSubTitle`.** On multi-outcome events, `title` is
  shared; the outcome lives in `yesSubTitle`.
- **Volume fields.** `volume` (int), `volumeFp` / **`volume24hFp`** (strings).
  There is no `volume24h`. Always `parseFloat` the `*Fp` fields.
- **Null bids/asks.** Skip; do not treat as zero.
- **Maintenance window** — Thursdays 3:00–5:00 AM ET. Books can go stale;
  streams go quiet.
- After a scan, trade with the **outcome mint** (`yesMint` / `noMint`) on
  `purr dflow order`, not `marketLedger` / `--side`.

## Sibling skills

- `dflow-kalshi-trading` — buy/sell/redeem a market you found
- `dflow-kalshi-portfolio` — their positions
- `dflow-kalshi-market-data` — orderbook / tape / live data outside a named scan
- `dflow-proof-kyc` — verify before a buy
