---
name: stock-spread
description: "READ-ONLY cross-venue price & spread intelligence for tokenized stocks (xStocks / Binance bStocks). Use when the user wants to compare an equity's price across venues, find where a tokenized stock is cheapest/dearest, see the CEX-vs-DEX spread, or look up tokenized-stock quotes — e.g. 'compare TSLA across venues', 'where is AAPLx cheapest', 'tokenized Tesla price', 'xStocks spread for NVDA'. NEVER trades, swaps, transfers, or signs — quotes and comparison only."
---

# Stock Spread — Cross-Venue Tokenized-Stock Price Intelligence (READ-ONLY)

> Pure read / market-data skill. Resolves an equity to its per-venue identifiers, fetches **keyless public** quotes, normalizes them (settlement currency, mid-vs-executable, freshness), and reports the cross-venue spread. It NEVER buys, sells, swaps, transfers, or signs anything.

## When to use
- "compare TSLA across our venues", "where is AAPL cheapest right now"
- "what's the tokenized Tesla price", "xStocks / bStocks price for NVDA"
- "CEX vs DEX spread for `<stock>`", "is there a spread on `<stock>`"
- "what's the basis on TSLA", "funding rate on the NVDA perp", "spot vs perp for COIN"

## NOT this skill
- Buying / selling / swapping a stock token → execution is **out of scope** (read-only v1).
- Non-stock crypto prices → use the relevant DEX/CEX market skill (e.g. `gate-dex-market`, `okx-dex-market`).

## Coverage (v1)
| Venue | Type | Settlement | Live keyless read |
|---|---|---|---|
| Gate | CEX | USDT | ✅ |
| Bybit | CEX | USDT | ✅ |
| Binance bStocks | CEX | USDT | ✅ |
| Solana / Jupiter | DEX (executable) | USDC | ✅ |
| Kraken | CEX | USD | ⛔ deferred — xStocks not on public `AssetPairs` |
| Bitget | wallet | USDT | ⛔ deferred — keyed wallet API |

Covered underlyings + exact per-venue identifiers live in `vendor/data/symbology.json` — **generated** by `catalog.py --refresh` (enumerated from each venue's own instrument list + Jupiter, with Solana mints verified against the Backed issuer `freezeAuthority`). ~36 underlyings auto-discovered; **not hand-maintained**. Unverified identifiers / unresolved mints are surfaced as warnings and never traded on.

**Spot-vs-perp basis** is available where an on-chain equity perp exists — currently Hyperliquid's `xyz` builder dex (trade.xyz HIP-3): TSLA, NVDA, AAPL, COIN, CRCL, HOOD, … Read-only mark + funding; the basis is a **signal**, not a capturable trade (funding-driven convergence, no anonymous redemption).

## How to run (read-only; Python 3 stdlib, no API keys)
1. **Resolve symbology:** `python3 vendor/scripts/resolve.py <UNDERLYING>`
2. **Live cross-venue spread (main flow):**
   `python3 vendor/scripts/adapters.py --live <UNDERLYING> | python3 vendor/scripts/spread.py`
3. **Spot-vs-perp basis (arbitrage signal):** `python3 vendor/scripts/perps.py --basis <UNDERLYING>` — compares the spot consensus to the Hyperliquid `xyz` equity-perp mark and reports basis % + funding APR (read-only signal).
4. **Offline gate / self-tests:** `resolve.py --selftest`, `spread.py --selftest`, `adapters.py --selftest`, `catalog.py --selftest`, `perps.py --selftest`; `spread.py --demo` shows the fake-spread guard.
5. **Refresh coverage (sourced, not hand-edited):** `python3 vendor/scripts/catalog.py --refresh` re-enumerates the universe from venue instrument lists + Jupiter (issuer-verified) and regenerates `symbology.json`.

## Reading the output (do not mislead the user)
- `spread_pct` is computed **only after settlement-currency normalization**; always report it together with `price_basis`.
- If `price_basis` is `mixed` (CEX mid + DEX executable), state the spread is **indicative, not directly capturable**.
- If `reliable: false`, do **not** present the spread as actionable — explain the reason from `warnings` (e.g. **US market closed/unknown** — tokens trade 24/7 but off-hours the cross-venue spread is *shown but not certified*; timestamp skew; non-positive price excluded; fewer than 2 comparable venues).
- The DEX (`executable`) leg is a quote for a **small clip (~1 token)** — read its `size_usd` and `price_impact_pct`; a thin-liquidity name can show high impact, so don't treat it as fillable at size without checking.
- Always surface `warnings`, `excluded`, and `skipped` to the user; never silently drop a venue.

## Safety rules
1. **Read-only (no financial/on-chain writes).** Never trade, swap, transfer, or sign; no API keys, no wallet. The *only* filesystem write is `catalog.py --refresh` regenerating the local `symbology.json` cache.
2. **Exact-address resolution only.** Scam look-alike tokens exist on-chain; never match by ticker substring.
3. **Objective data only.** No investment advice; flag unverified, illiquid, or market-closed venues.
4. **Arb is signal, not free money.** Cross-venue convergence is generally NOT capturable by an anonymous wallet (KYC-gated redemption, US-hours peg), so present spreads as a signal.
