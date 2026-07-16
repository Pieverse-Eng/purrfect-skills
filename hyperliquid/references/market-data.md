# Market Data

Public Hyperliquid market data through the platform gateway. These commands
only inspect data and do not require confirmation.

## Commands

```bash
purr hyperliquid symbol --coin <coin> [--dex <dex|default>]
purr hyperliquid markets [--kind perp|spot|both] [--dex <dex>]
purr hyperliquid prices [--dex <dex>]
purr hyperliquid l2 --coin <coin> [--n-sig-figs <2-5>] [--mantissa 2|5]
purr hyperliquid candles --coin <coin> --interval <interval> --start-time <ms> [--end-time <ms>]
purr hyperliquid funding --coin <coin> --start-time <ms> [--end-time <ms>]
```

| Command | Purpose |
| --- | --- |
| `symbol` | Resolve bare or full coin names to `coin`, `assetId`, `szDecimals`, optional `dex` |
| `markets` | List markets; `--kind` defaults to both; `--dex` filters perp meta only |
| `prices` | Mid prices (`allMids`); omit `--dex` for default book, or pass a builder dex |
| `l2` | L2 order book for a coin |
| `candles` | OHLCV candles; times are Unix ms; `--start-time` required |
| `funding` | Historical funding for a perp coin; times are Unix ms; `--start-time` required |

## Symbol Resolution (Required Before Orders)

Always resolve before placing or modifying an order:

```bash
purr hyperliquid symbol --coin ETH
purr hyperliquid symbol --coin ETH --dex default
purr hyperliquid symbol --coin TSLA --dex xyz
purr hyperliquid symbol --coin xyz:TSLA
```

Use the response fields:

| Field | Use |
| --- | --- |
| `coin` | Canonical market name (may include `dex:` prefix) |
| `assetId` | Wire-format order field `a` |
| `szDecimals` | Max size precision; do not invent extra decimals |
| `dex` | Builder dex name when applicable (`default` for native perps) |

### Dex selector rules

- `--dex xyz` or coin `xyz:TSLA` scopes resolution to that builder dex.
- `--dex default` forces the native/default perp universe (not a real dex name
  prefix). Do **not** use coin `default:ETH`; use `--dex default` instead.
- If both a coin prefix and `--dex` are set, they must match or the request
  fails with `HYPERLIQUID_SYMBOL_DEX_MISMATCH`.

### Ambiguity

If the command fails with `HYPERLIQUID_SYMBOL_AMBIGUOUS`, do **not** auto-select
a market. The CLI prints the platform's `data`, including fully resolved
`candidates`. Present each candidate's `coin`, `dex`, `assetId`, and
`szDecimals`, then ask the user which market they mean.

After the user chooses, use the selected candidate directly. It is already a
complete symbol resolution, so do not call `symbol` again. Use its `coin`,
`assetId`, and `szDecimals` for the order workflow. For state, prices, and
orders, omit `--dex` when the candidate has `dex: "default"`; otherwise pass
`--dex <candidate.dex>`. Use the canonical `coin` for L2 and funding commands.

Bare equity tickers (for example `TSLA`) may match HIP-3 / builder-dex markets
such as `xyz:TSLA` as well as other listings. Prefer full `dex:COIN` or `--dex`
when the user specifies the dex before the initial lookup.

## Markets and Prices

```bash
purr hyperliquid markets --kind perp
purr hyperliquid markets --kind both --dex xyz
purr hyperliquid prices
purr hyperliquid prices --dex xyz
```

Use markets for discovery; use prices for a quick mark/mid context before
building a limit or IOC order.

## L2 Book

```bash
purr hyperliquid l2 --coin ETH
purr hyperliquid l2 --coin ETH --n-sig-figs 5 --mantissa 2
```

- `--n-sig-figs` is optional (`2`–`5`).
- `--mantissa` is only valid with `n-sig-figs=5` and must be `2` or `5`.

Use L2 when placing size-sensitive limits or explaining top-of-book liquidity.

## Candles and Funding

```bash
purr hyperliquid candles --coin ETH --interval 1h --start-time 1710000000000
purr hyperliquid funding --coin ETH --start-time 1710000000000
```

- `interval` examples: `1m`, `5m`, `15m`, `1h`, `4h`, `1d` (use what the venue
  accepts; pass through as the user requested when valid).
- `start-time` / `end-time` are Unix milliseconds.
- Funding is for perps; do not invent funding for pure spot pairs.

## Research vs Trading

Market-data commands alone never trade. For cross-venue tokenized-stock
comparison (CEX vs DEX spreads), prefer the research-only `stock-spread` skill.
Use Hyperliquid market-data commands when the user wants Hyperliquid-specific
books, funding, or later execution on Hyperliquid.
