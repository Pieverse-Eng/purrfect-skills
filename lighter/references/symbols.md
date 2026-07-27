# Symbols and market types

Lighter exposes both **perp** and **spot** markets. The CLI resolves
`--market <symbol>` against live `markets` data. Always pass
`--market-type perp|spot` when the user’s intent is known.

## Rules

1. Prefer symbols from a live resolve:
   `purr lighter market --market <SYM> --market-type <t>`.
2. Spot display names look like `ETH/USDC`; pass the **base** as `--market ETH`
   with `--market-type spot`.
3. Perp display symbols usually match `--market` (for example `SOL`, `BTC`,
   `TSLA`).
4. If a ticker exists on both books, omitting `--market-type` (or using `all`)
   often yields `LIGHTER_MARKET_AMBIGUOUS`. Ask the user; never pick silently.
5. `1000`-prefixed perps (for example `1000PEPE`, `1000BONK`) are **per-1000
   units** of the underlying — size and PnL scale accordingly.
6. Market lists change. Treat the tables below as orientation, not a guarantee.
   When in doubt, list:

```bash
purr lighter markets --market-type perp
purr lighter markets --market-type spot
```

## Dual-listed tickers (spot and perp)

These commonly collide — **always** pass `--market-type`:

| Symbol | Spot pair (typical) | Also perp |
| --- | --- | --- |
| `ETH` | ETH/USDC | yes |
| `LIT` | LIT/USDC | yes |
| `LDO` | LDO/USDC | yes |
| `LINK` | LINK/USDC | yes |
| `AAVE` | AAVE/USDC | yes |
| `UNI` | UNI/USDC | yes |
| `SKY` | SKY/USDC | yes |
| `AZTEC` | AZTEC/USDC | yes |

Example:

```bash
# Wrong if both exist — may be ambiguous
purr lighter order --market ETH --side buy --size 0.1 --price 4000

# Correct
purr lighter order --market ETH --market-type perp --side buy --size 0.1 --price 4000
purr lighter order --market ETH --market-type spot --side buy --size 0.1 --price 4000
```

## Spot markets (orientation)

Pass `--market-type spot`. `--market` is the base asset:

| Spot name | `--market` |
| --- | --- |
| ETH/USDC | `ETH` |
| AZTEC/USDC | `AZTEC` |
| LDO/USDC | `LDO` |
| LINK/USDC | `LINK` |
| AAVE/USDC | `AAVE` |
| UNI/USDC | `UNI` |
| SKY/USDC | `SKY` |
| LIT/USDC | `LIT` |

## Perp markets (orientation)

Pass `--market-type perp`. The list is long and includes crypto, equity-style,
FX, and commodity symbols (for example `BTC`, `SOL`, `TSLA`, `NVDA`, `EURUSD`,
`WTI`, `1000PEPE`). Prefer:

```bash
purr lighter markets --market-type perp --market <SYM>
purr lighter market --market <SYM> --market-type perp
```

Do not hard-code market ids from memory; ids can differ by deployment/meta
updates. Always take `market_id` / `marketId` from a fresh resolve when needed.

## Flag hygiene

| Flag | Used for |
| --- | --- |
| `--market-type perp\|spot\|all` | Which book to query or trade |
| `--type` on `order` / `place-orders` | Order type (`limit`, `market`, …) |
| `--type` on `trades` | Side filter (`buy`, `sell`, `all`) |

Never pass `--type perp` or `--type spot`.
