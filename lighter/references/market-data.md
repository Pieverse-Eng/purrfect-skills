# Market data

All read-only. No confirmation needed. 20s client timeout; safe to retry.

Every command below that takes `--market <symbol>` also takes
`--market-type perp|spot|all` — pass it explicitly. See
[symbols.md](symbols.md) for why (eight symbols are dual-listed).

You may address a market either way:

- `--market <SYMBOL> --market-type <perp|spot>` — preferred, readable
- `--market-id <id>` — only when you already hold an id from a prior response

Never hardcode a market id in a workflow; resolve the symbol each time.

## Listing and resolving

```bash
purr lighter markets --market-type perp            # all perp markets
purr lighter markets --market-type spot            # all spot markets
purr lighter market --market SOL --market-type perp
purr lighter market --market-id 12
```

`market` is the call that gives you **size and price decimals**. Read them
before sizing an order — see [trading.md](trading.md).

Unknown symbol → `LIGHTER_MARKET_NOT_FOUND`. Do not retry with a guessed
variant; check `markets` and report what actually exists.

## Books and depth

```bash
purr lighter order-books --market-type perp
purr lighter order-book-depth --market SOL --market-type perp [--limit 100]
```

`order-book-depth` is what you use to derive a market order's price bound.
`--limit` is 1–250 (default 100).

## Trades and candles

```bash
purr lighter recent-trades --market SOL --market-type perp [--limit 100]
purr lighter trades [--market SOL --market-type perp] [--limit 100]
purr lighter candles --market SOL --market-type perp --resolution 1h --start-timestamp <unix> [--end-timestamp <unix>] [--count-back <n>]
```

`candles` requires `--resolution` and `--start-timestamp`. `--count-back` is
1–5000.

`trades` without a market returns your account's trades — that is the call for
"did my order fill?", not the submit response.

⚠️ On `trades`, `--type` means **side** (`buy` / `sell` / `all`), not order
type. `--type` is accepted on only three commands: `order`, `place-orders`
(order type) and `trades` (side). Everywhere else it errors — use
`--market-type` for perp/spot.

## Funding

```bash
purr lighter funding-rates                                  # all markets
purr lighter funding-rates --market BTC --market-type perp  # one market
```

Funding applies to perps only. When a user asks "what is funding on X", quote
the rate with its sign and say which side pays: a positive rate means longs pay
shorts. Do not annualize unless asked, and if you do, state the assumption.

## Reporting

- Equity, index, and FX perps trade 24/7 on Lighter while their underlying
  market has real trading hours. Off-hours prices can be thin and gap at the
  open — say so rather than presenting a quiet book as a firm price.
- Quote the book, not a single last price, when the user is about to trade.
- `1000`-prefixed symbols are per-1000-token quotes ([symbols.md](symbols.md)).
