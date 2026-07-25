# Lighter market symbols

Authoritative list supplied by the platform team. **Always cross-check against
`purr lighter markets --market-type <perp|spot>` before ordering** — listings
change and this file is a snapshot, not the source of truth. If a symbol here is
missing live, trust the live response and say so.

## The `--market-type` rule (read this before any order)

`--market` takes the **base symbol**, never the pair. Pass `ETH`, not `ETH/USDC`.

`--market-type` is **required in practice**: eight symbols exist in *both* books.
Omitting it on these makes the CLI fail with
`Lighter market "<SYM>" is ambiguous. Pass --market-type perp or spot.`

**Dual-listed (spot *and* perp):** `AAVE` · `AZTEC` · `ETH` · `LDO` · `LINK` ·
`LIT` · `SKY` · `UNI`

Treat that error as a genuine fork in intent — a spot buy and a perp long are
different trades with different risk. Ask the user which they meant; never pick
one to make the command succeed.

Do not confuse `--market-type` (perp vs spot) with `--type` (order type:
`limit`, `market`, …). The CLI rejects `--type perp` explicitly.

## Spot markets (8)

`--market-type spot`. The market displays as a `/USDC` pair; pass only the base.

| Spot market | `--market` value |
| --- | --- |
| ETH/USDC | `ETH` |
| AZTEC/USDC | `AZTEC` |
| LDO/USDC | `LDO` |
| LINK/USDC | `LINK` |
| AAVE/USDC | `AAVE` |
| UNI/USDC | `UNI` |
| SKY/USDC | `SKY` |
| LIT/USDC | `LIT` |

## Perp markets (219)

`--market-type perp`. The displayed symbol is the `--market` value.

Note the mix: crypto, tokenized equities (`AAPL`, `NVDA`, `TSLA`, `MSTR`,
`GOOGL`, `COIN`, …), indices (`SPX`, `US500`, `US100`, `QQQ`, `SPY`, `IWM`),
FX (`EURUSD`, `USDJPY`, `GBPUSD`, `AUDUSD`, `USDKRW`, `USDHKD`, `USDCHF`,
`USDCAD`, `NZDUSD`), commodities (`XAU`, `XAG`, `XPT`, `XPD`, `XCU`, `WTI`,
`BRENTOIL`, `NATGAS`, `WHEAT`), and pre-IPO/thematic names (`OPENAI`,
`ANTHROPIC`, `SPACEX`). Equity and index perps track markets with real trading
hours even though the perp trades 24/7 — mention that when a user opens one
outside US market hours.

Symbols prefixed `1000` (`1000PEPE`, `1000BONK`, `1000SHIB`, `1000FLOKI`,
`1000NOT`, `1000TOSHI`) are quoted per 1000 tokens. Size accordingly.

| | | | | | | | |
|---|---|---|---|---|---|---|---|
| `0G` | `1000BONK` | `1000FLOKI` | `1000NOT` | `1000PEPE` | `1000SHIB` | `1000TOSHI` | `2Z` |
| `AAOI` | `AAPL` | `AAVE` | `ADA` | `ADI` | `AERO` | `AI16Z` | `AMD` |
| `AMZN` | `ANTHROPIC` | `APEX` | `APT` | `ARB` | `ARC` | `ARM` | `ASML` |
| `ASTER` | `AUDUSD` | `AVAX` | `AVGO` | `AVNT` | `AXS` | `AZTEC` | `BABA` |
| `BB` | `BCH` | `BE` | `BERA` | `BIO` | `BIRB` | `BMNR` | `BNB` |
| `BOT` | `BOTZ` | `BRENTOIL` | `BTC` | `BYD` | `CAP` | `CBRS` | `CC` |
| `CHIP` | `COIN` | `CRCL` | `CRO` | `CRV` | `CRWV` | `CTR` | `CXMT` |
| `DASH` | `DATA` | `DELL` | `DIA` | `DOGE` | `DOLO` | `DOT` | `DRAM` |
| `DUSK` | `DYDX` | `EDEN` | `EDGE` | `EIGEN` | `ENA` | `ETH` | `ETHFI` |
| `EURUSD` | `EWY` | `FARTCOIN` | `FF` | `FIL` | `FOGO` | `FOLKS` | `GBPUSD` |
| `GEV` | `GME` | `GMX` | `GOOGL` | `GRAM` | `GRASS` | `H100` | `HANMI` |
| `HBAR` | `HOOD` | `HYPE` | `HYUNDAI` | `HYUNDAIUSD` | `IBM` | `ICP` | `INTC` |
| `IWM` | `JTO` | `JUP` | `KAITO` | `KRCOMP` | `LAUNCHCOIN` | `LDO` | `LINEA` |
| `LINK` | `LIT` | `LITE` | `LTC` | `MAGS` | `MEGA` | `MET` | `META` |
| `MINIMAX` | `MKR` | `MNT` | `MON` | `MORPHO` | `MRVL` | `MSFT` | `MSTR` |
| `MU` | `MYX` | `NATGAS` | `NBIS` | `NEAR` | `NMR` | `NOK` | `NOW` |
| `NVDA` | `NZDUSD` | `ONDO` | `OP` | `OPENAI` | `ORCL` | `PAXG` | `PENDLE` |
| `PENGU` | `PIPPIN` | `PLTR` | `POL` | `POPCAT` | `POPMART` | `PROVE` | `PUMP` |
| `PYTH` | `QCOM` | `QNT` | `QQQ` | `RAIL` | `RESOLV` | `RIVER` | `RKLB` |
| `ROBO` | `S` | `SAMSUNG` | `SAMSUNGUSD` | `SEI` | `SKHY` | `SKHYNIX` | `SKHYNIXUSD` |
| `SKR` | `SKY` | `SMIC` | `SNDK` | `SOL` | `SOXL` | `SOXX` | `SPACEX` |
| `SPCX` | `SPX` | `SPY` | `STABLE` | `STBL` | `STRC` | `STRK` | `SUI` |
| `SYRUP` | `TAO` | `TENCENT` | `TIA` | `TRUMP` | `TRX` | `TSLA` | `TSM` |
| `TTWO` | `UNI` | `URA` | `US100` | `US500` | `USDCAD` | `USDCHF` | `USDHKD` |
| `USDJPY` | `USDKRW` | `USELESS` | `VIRTUAL` | `VVV` | `WEN` | `WHEAT` | `WIF` |
| `WLD` | `WLFI` | `WTI` | `XAG` | `XAU` | `XCU` | `XIAOMI` | `XLM` |
| `XMR` | `XPD` | `XPL` | `XPT` | `XRP` | `YZY` | `ZEC` | `ZHIPU` |
| `ZK` | `ZORA` | `ZRO` | | | | | |

## Sizing

Size and price precision come from the market itself, not from this file:

```bash
purr lighter market --market SOL --market-type perp
```

Use the returned size/price decimals. A rounding the venue does not accept
returns `LIGHTER_DECIMAL_PRECISION_UNSUPPORTED` or `LIGHTER_DECIMAL_INVALID`.
