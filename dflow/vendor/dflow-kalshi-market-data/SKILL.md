---
name: dflow-kalshi-market-data
description: Read market data for a known Kalshi prediction market on DFlow — orderbook, trades, top-of-book, candlesticks, forecast-percentile history, and in-game live data. Use when the user asks for an orderbook, last trades, a live ticker, candles, or in-game scores. Do NOT use to discover markets, place orders, or read a user's positions.
disable-model-invocation: true
user-invocable: false
---

# DFlow Kalshi Market Data

Data about a **known** Kalshi market. Use the parent skill's
`purr dflow metadata` and `purr dflow stream`. Paths below have no `/api/v1/`
prefix.

## Shape

- **Snapshot** ("right now") → metadata GET.
- **History** ("last hour", "last N trades") → metadata GET with time / limit.
- **Stream** ("live", "alert me") → `purr dflow stream` on `prices`, `trades`,
  or `orderbook`.

## Data → path

### Orderbook

- Snapshot: `orderbook/<ticker>` or `orderbook/by-mint/<mint>` (includes
  `sequence`).
- Stream: `orderbook` channel (`yes_bids` + `no_bids`; no `sequence` on the
  stream payload).

### Trades — two overlapping endpoints

- `trades` and `trades/by-mint/<mint>` — complete Kalshi tape (includes DFlow
  onchain fills). Default for "show trades on this market." Stream: `trades`.
- `onchain-trades`, `onchain-trades/by-market/<ticker>`,
  `onchain-trades/by-event/<eventTicker>` — DFlow onchain fills only, with
  `wallet`, `transactionSignature`, `inputAmount`, `outputAmount`,
  `createdAt`. No stream.

Wallet activity or tx-signature lookup → `onchain-trades`. Market tape →
`trades`.

### Top-of-book

Read `yesBid` / `yesAsk` / `noBid` / `noAsk` from `market/<ticker>`. Stream:
`prices`.

### Candlesticks

- Market: `market/<ticker>/candlesticks` or
  `market/by-mint/<mint>/candlesticks`.
- Event: `event/<ticker>/candlesticks`.
- **5,000-candle cap per request** — over that is a hard 400, no partial.
- `periodInterval` is **minutes** (`1`, `60`, `1440`), not seconds.

### Forecast percentile history

`event/<seriesTicker>/<eventId>/forecast_percentile_history` or
`event/by-mint/<mint>/forecast_percentile_history`.

### Live data

`live_data`, `live_data/by-event/<ticker>`, `live_data/by-mint/<mint>`.
`details` fields depend on milestone type (football, soccer, tennis, …).
Do not hardcode cross-category fields.

## Missing pieces

1. **Which market** — ticker or outcome mint.
2. **Which dataset.**
3. **Snapshot / history / stream.**
4. **History bounds / interval** — `startTs`, `endTs`, `periodInterval`;
   trade limit.

## Gotchas

- **Orderbook is bid ladders only.** Best YES ask = `1 - max(no_bids keys)`.
- **Two price scales.** Orderbook/prices: `"0.4200"`. Trades: integer
  0–10000 plus `yes_price_dollars` / `no_price_dollars`.
- **`all=true` is a firehose**, especially on `prices` and `orderbook`.
- Streams go quiet Thursday 3:00–5:00 AM ET.

## Sibling skills

- `dflow-kalshi-market-scanner` — find markets across the universe
- `dflow-kalshi-trading` — place an order on a market you are watching
- `dflow-kalshi-portfolio` — the user's positions
