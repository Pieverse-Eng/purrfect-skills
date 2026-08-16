# Discovery and streaming

Public Predict.fun market data through `purr predict-fun`. These commands only
inspect data. Confirmation is not required.

## Commands

```bash
purr predict-fun categories [--first <1-100>] [--after <cursor>] [--status <status>] [--sort <sort>] [--tag-ids <ids>] [--market-variant <variant>]
purr predict-fun category --slug <slug>
purr predict-fun tags
purr predict-fun search --query <text> [--include-resolved true|false] [--limit <1-25>]
purr predict-fun markets [--first <1-100>] [--after <cursor>] [--status <status>] [--sort <sort>] [--tag-ids <ids>] [--market-variant <variant>] [--is-boosted true|false] [--has-active-rewards true|false]
purr predict-fun market --market-id <id>
purr predict-fun market-stats --market-id <id>
purr predict-fun market-last-sale --market-id <id>
purr predict-fun market-quote --market-id <id>
purr predict-fun market-quotes --market-ids <id,id,...>
purr predict-fun orderbook --market-id <id> [--outcome YES|NO]
purr predict-fun timeseries-latest --market-id <id>
purr predict-fun timeseries --market-id <id> --from <unix-seconds> [--to <unix-seconds>] [--resolution <value>] [--limit <1-1000>] [--after <cursor>]
purr predict-fun stream --topics <topic,topic,...> [--max-events <1-10000>] [--timeout-ms <ms>]
```

| Command | Purpose |
| --- | --- |
| `categories` / `category` | Category list or one category by slug |
| `tags` | Tag list |
| `search` | Text search; `--limit` 1–25 |
| `markets` / `market` | Market list or one market |
| `market-stats` / `market-last-sale` | Stats and last sale |
| `market-quote` | One market top of book |
| `market-quotes` | Up to 500 market ids in one request |
| `orderbook` | Normalized book for one outcome |
| `timeseries-latest` / `timeseries` | Chance series (`--from` is unix seconds) |
| `stream` | SSE over a platform-owned Predict WebSocket |

`--status`, `--sort`, `--tag-ids`, and `--market-variant` are forwarded as
returned by live payloads (examples: `OPEN`, `VOLUME`). Do not invent filter
vocabularies. Paged list commands return `{ data, cursor }`.

## Resolve a market

1. `search` or `markets` to find candidates.
2. `market --market-id <id>` for title, question, `tradingStatus`, fees, and
   outcomes.
3. Keep the numeric id. Pass it as `--market-id` everywhere else.

If several markets match, list them and ask. Never pick silently.

Only trade when `tradingStatus` is `OPEN`. A later execute still re-checks and
can return `PREDICT_MARKET_NOT_OPEN` or `PREDICT_PREVIEW_STALE`.

## Quotes vs market payloads

Use `market-quote` or `market-quotes` for top of book. Do not use deprecated
outcome-level `bestBid` / `bestAsk` on market or category payloads.

Quote shape: `marketId`, `updateTimestampMs`, and optional `bestBid` /
`bestAsk` `{ price, size }`. Either side may be absent. The single-market
route is 404 when no book is maintained; the batch route omits those markets.

Apply a quote only when its `updateTimestampMs` is newer than the last REST or
stream observation you already have.

`orderbook` defaults to YES when `--outcome` is omitted. Pass `--outcome`
explicitly whenever the user named a side.

## Streaming

```bash
purr predict-fun stream --topics orderbook:12345,wallet --max-events 10
```

Allowlisted topics:

- `orderbook:<marketId>`
- `trading-status:<marketId>`
- `market-status:<marketId>`
- `market-changed:<marketId>`
- `category-changed:<categoryId>`
- `wallet`

`wallet` is this account's orders, fills, cancels, and settlements.

Platform caps: **8 unique topics** per stream, **2 streams per instance**,
15 minutes. Prefer at most 8 topics even though the CLI parses more. Defaults:
`--max-events 100`, `--timeout-ms 60000` (max 15 minutes).

The CLI prints one JSON line per event (`type: predict-stream-event`), skips
the `connected` handshake, and ends with
`{ type: predict-stream, topics, eventCount, timedOut }`. An `error` frame is
a hard failure.

Do not keep a stream open after you have the answer. Close and re-open with
the needed topics rather than widening a live subscription.
