# Market data

Public and account-scoped Lighter market data through `purr lighter`. These
commands only inspect data. Confirmation is not required. Trading integration
must still be enabled.

## Commands

```bash
purr lighter markets [--market-type perp|spot|all] [--market-id <id> | --market <symbol>]
purr lighter market (--market-id <id> | --market <symbol> [--market-type perp|spot|all])
purr lighter order-books [--market-type perp|spot|all] [--market-id <id> | --market <symbol>]
purr lighter order-book-depth (--market-id <id> | --market <symbol> [--market-type perp|spot|all]) [--limit <n>]
purr lighter recent-trades (--market-id <id> | --market <symbol> [--market-type perp|spot|all]) [--limit <n>]
purr lighter trades [--market-id <id> | --market <symbol> [--market-type perp|spot|all]] [--limit <n>]
purr lighter candles (--market-id <id> | --market <symbol> [--market-type perp|spot|all]) \
  --resolution <1m|5m|15m|30m|1h|4h|12h|1d|1w> \
  --start-at <rfc3339> --end-at <rfc3339> --count-back <n>
purr lighter funding-rates [--market-id <id> | --market <symbol> [--market-type perp|spot|all]]
```

| Command | Purpose |
| --- | --- |
| `markets` | List or filter markets |
| `market` | Resolve one market (symbol → market id, decimals, type) |
| `order-books` | Book summaries |
| `order-book-depth` | L2 depth for sizing and market-order price bounds |
| `recent-trades` | Recent public trades for a market |
| `trades` | Account/public trade query (supports extra filters) |
| `candles` | OHLCV; times are RFC 3339 with timezone |
| `funding-rates` | Perp funding |

## Symbol resolution

Always resolve before placing or modifying an order:

```bash
purr lighter market --market SOL --market-type perp
purr lighter market --market LIT --market-type spot
purr lighter market --market-id 12
```

Prefer explicit `--market-type` whenever you use `--market`. Matching rules:

- Case-insensitive symbol match
- Spot pair names may look like `ETH/USDC`; `--market ETH` matches the base
- If multiple markets match, CLI errors with `LIGHTER_MARKET_AMBIGUOUS`
- If none match, `LIGHTER_MARKET_NOT_FOUND`

Once resolved, keep the returned **market id** and decimal metadata for the rest
of the turn. You may pass either `--market-id` or `--market` on later commands;
do not invent ids.

See [symbols.md](symbols.md) for dual-listed tickers and `1000*` contracts.

## Candles

Required flags: `--resolution`, `--start-at`, `--end-at`, `--count-back`.

Allowed resolutions: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `12h`, `1d`, `1w`.

Timestamps must include timezone, for example:

```bash
purr lighter candles --market BTC --market-type perp \
  --resolution 1h \
  --start-at 2026-07-01T00:00:00Z \
  --end-at 2026-07-02T00:00:00Z \
  --count-back 24
```

`--start-at` must be ≤ `--end-at`. Invalid ranges may return
`LIGHTER_CANDLE_TIME_RANGE_INVALID`.

## Depth and pricing

For market orders and large limits, always pull depth for the **exact size**:

```bash
purr lighter order-book-depth --market SOL --market-type perp --limit 100
```

Walk cumulative levels on the hit side (buys take asks). If depth cannot fill
the size, stop and ask the user to resize — do not invent liquidity past the
book. See [trading.md](trading.md) for how that bound becomes `--price`.

## Trades filters (optional)

`trades` accepts additional query flags when needed: `--order-index`,
`--sort-by`, `--sort-dir`, `--from`, `--role`, `--type` (buy/sell/all),
`--limit`, `--aggregate`. Keep filters minimal; large order indexes are decimal
strings, not floats.

## Timeouts

Market-data reads use the 20s client timeout. Safe to retry on
`LIGHTER_REQUEST_TIMEOUT` for pure reads.
