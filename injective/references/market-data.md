# Market data

Public queries use platform API credentials and do not require `INSTANCE_ID`.
Use the existing discovery tool for discovery and comparisons; this skill does
not add Injective to executable route comparisons or spot purchase plans.
If discovery lacks Injective, query its complete catalog:

```sh
purr injective markets --market-type all
```

Select a returned native `0x` + 64-hex market hash and its `spot` or `perp`
product. Never pass a ticker as the market ID. `MARKET_HASH` below means that
exact returned hash; set it from the selected result, not a guessed constant.

```sh
purr injective market --market-id "$MARKET_HASH" --market-type perp
purr injective order-book-depth --market-id "$MARKET_HASH" --market-type perp --limit 20
purr injective recent-trades --market-id "$MARKET_HASH" --market-type perp --limit 50
purr injective candles --market-id "$MARKET_HASH" --market-type perp --resolution 1h --start-at 2026-10-01T00:00:00Z --end-at 2026-10-02T00:00:00Z
```

Choose dates for the requested period; the example is historical. Candle bounds
must be paired RFC3339 timestamps, ordered start before end, with at most 1500
timeframe buckets. Resolutions: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`.
Depth/trade limits are 1–100. Pass `spot` for spot queries.

Report source metadata and incomplete history honestly. Empty depth can mean
an empty book; it does not prove a delisting. Books are snapshots and candle
coverage can be incomplete. No result authorizes execution or promises a fill.
An unverified ticker or same-symbol denomination does not establish exposure
equivalence, token ownership rights or a USD valuation.
