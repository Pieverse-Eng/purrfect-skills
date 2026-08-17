# Discovery and streaming

Public Predict.fun market data through `purr predict-fun`. These commands only
inspect data. Confirmation is not required.

## Commands

```bash
purr predict-fun categories [--first <1-100>] [--after <cursor>] [--status OPEN|ACTIVE|RESOLVED|REMOVED] [--sort <category-sort>] [--tag-ids <id,id,...>] [--market-variant <variant>]
purr predict-fun category --slug <slug>
purr predict-fun tags
purr predict-fun search --query <text> [--include-resolved true|false] [--limit <1-25>]
purr predict-fun markets [--first <1-100>] [--after <cursor>] [--status OPEN|RESOLVED] [--sort <market-sort>] [--tag-ids <id,id,...>] [--market-variant <variant>] [--has-active-rewards true|false]
purr predict-fun market --market-id <id>
purr predict-fun market-stats --market-id <id>
purr predict-fun market-last-sale --market-id <id>
purr predict-fun market-quote --market-id <id>
purr predict-fun market-quotes --market-ids <id,id,...>
purr predict-fun orderbook --market-id <id> [--outcome YES|NO]
purr predict-fun timeseries-latest --market-id <id>
purr predict-fun timeseries --market-id <id> --from <unix-seconds> [--to <unix-seconds>] [--resolution 1m|5m|1h|1d|1w|1M] [--limit <1-1000>] [--after <cursor>]
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
| `timeseries-latest` / `timeseries` | Chance series. `--from` is unix seconds; span under 365 days |
| `stream` | SSE over a platform-owned Predict WebSocket |

Paged list commands return `{ data, cursor }`. Use these tables (or
`purr predict-fun help` if the installed CLI lists different values).

### Status

| Command | `--status` |
| --- | --- |
| `categories` | `OPEN`, `ACTIVE`, `RESOLVED`, `REMOVED` |
| `markets` | `OPEN`, `RESOLVED` |

`OPEN` is the tradable filter. Markets inside a `RESOLVED` category are not
tradable.

### Category `--sort`

`POPULAR`, `VOLUME`, `VOLUME_24H_DESC`, `VOLUME_ALL_DESC`, `PUBLISHED_AT_ASC`,
`PUBLISHED_AT_DESC`.

`VOLUME` is category-only. `VOLUME_24H_DESC` is valid on both `categories`
and `markets`.

### Market `--sort`

`CHANCE_24H_CHANGE_ASC`, `CHANCE_24H_CHANGE_DESC`, `VOLUME_24H_ASC`,
`VOLUME_24H_DESC`, `VOLUME_24H_CHANGE_ASC`, `VOLUME_24H_CHANGE_DESC`,
`VOLUME_TOTAL_ASC`, `VOLUME_TOTAL_DESC`, `REWARD_RATE_ASC`, `REWARD_RATE_DESC`.

### `--market-variant`

`DEFAULT`, `SPORTS_MATCH`, `CRYPTO_UP_DOWN`, `TWEET_COUNT`,
`SPORTS_TEAM_MATCH`, `SPORTS_NBA`, `SPORTS_FIFA_WORLD_CUP`,
`SPORTS_EXACT_SCORE`, `SPORTS_HALFTIME_RESULT`, `SPORTS_PROPS`,
`SPORTS_FIFA_FRIENDLIES`, `ESPORTS_LOL`, `ESPORTS_CS2`, `ESPORTS_DOTA2`,
`SPORTS_FIRST_TO_SCORE`, `SPORTS_TOTAL_CORNERS`, `SPORTS_SECOND_HALF_RESULT`.

Omit `--market-variant` unless the user named a type that matches one of
these values.

### `--tag-ids`

Comma-separated numeric IDs from `purr predict-fun tags`.

### `--resolution` (timeseries)

`1m`, `5m`, `1h`, `1d`, `1w`, `1M`.

### Timeseries window

`--from` is required unix seconds. `--to` is optional and defaults to now.
`--from` must be before `--to`. The span must be **under 365 days** (364 days
works; a full 365 days is rejected). Older history is fine when the span
itself is under 365 days.

For a recent chart, use `timeseries-latest` or `--from` within the last 7–30
days. `--limit` is 1–1000.

### Intent → command

| User said | Command |
| --- | --- |
| trending / hot / latest trending | `markets --status OPEN --sort VOLUME_24H_DESC` |
| popular categories | `categories --status OPEN --sort POPULAR` |
| latest categories | `categories --status OPEN --sort PUBLISHED_AT_DESC` |
| biggest gainers | `markets --status OPEN --sort CHANCE_24H_CHANGE_DESC` |
| biggest losers | `markets --status OPEN --sort CHANCE_24H_CHANGE_ASC` |
| highest total volume | `markets --status OPEN --sort VOLUME_TOTAL_DESC` |
| highest rewards | `markets --status OPEN --sort REWARD_RATE_DESC` |
| active rewards | `markets --status OPEN --has-active-rewards true` |

Use `--has-active-rewards true` only when filtering for active rewards.

## Resolve a market

1. Map the request with the table above, or `search --query`.
2. `market --market-id <id>` for title, question, `tradingStatus`, fees,
   `outcomes`, and `variantDetails`.
3. Keep the numeric id. Pass it as `--market-id` everywhere else.

If several markets match, list them and ask.

Only trade when `tradingStatus` is `OPEN`. A later execute still re-checks and
can return `PREDICT_MARKET_NOT_OPEN` or `PREDICT_PREVIEW_STALE`.

### Outcomes (`--outcome YES|NO`)

CLI `--outcome` is the `indexSet`, not the display name:

| `indexSet` | CLI `--outcome` |
| ---: | --- |
| 1 | `YES` |
| 2 | `NO` |

Read `outcomes` on `market` before quoting or trading. On a market like
`$400` / `$800`, map the user's named side to that `indexSet`, then pass
`YES` or `NO`. `market-quote` is always the `indexSet` 1 book.

## Quotes

Top of book: `market-quote` or `market-quotes` only. Do not use `bestBid` /
`bestAsk` on market, category, or outcome payloads. Do not use deprecated
`variantData` or `team`; read `variantDetails` for market type.

Quote shape: `marketId`, `updateTimestampMs`, and optional `bestBid` /
`bestAsk` `{ price, size }`. Either side may be absent. The single-market
route is 404 when no book is maintained; the batch route omits those markets.

Apply a quote only when its `updateTimestampMs` is newer than the last REST or
stream observation you already have.

`orderbook` defaults to `YES` (`indexSet` 1) when `--outcome` is omitted.
Pass `--outcome` from the table above whenever the user named a side.

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

The CLI and platform both cap a stream at **8 unique topics**. Platform also
caps **2 streams per instance** and 15 minutes. Defaults: `--max-events 100`,
`--timeout-ms 60000` (max 15 minutes).

The CLI prints one JSON line per event (`type: predict-stream-event`), skips
the `connected` handshake, and ends with
`{ type: predict-stream, topics, eventCount, timedOut }`. An `error` frame is
a hard failure.

Close the stream when you have the answer.
