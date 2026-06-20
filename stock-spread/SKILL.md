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

Covered underlyings + exact per-venue identifiers live in `vendor/data/symbology.json`. Unverified identifiers and unresolved mints are surfaced as warnings and never traded on.

## How to run (read-only; Python 3 stdlib, no API keys)
1. **Resolve symbology:** `python3 vendor/scripts/resolve.py <UNDERLYING>`
2. **Live cross-venue spread (main flow):**
   `python3 vendor/scripts/adapters.py --live <UNDERLYING> | python3 vendor/scripts/spread.py`
3. **Offline gate / self-tests:** `resolve.py --selftest`, `spread.py --selftest`, `adapters.py --selftest`; `spread.py --demo` shows the fake-spread guard.

## Reading the output (do not mislead the user)
- `spread_pct` is computed **only after settlement-currency normalization**; always report it together with `price_basis`.
- If `price_basis` is `mixed` (CEX mid + DEX executable), state the spread is **indicative, not directly capturable**.
- If `reliable: false`, do **not** present the spread as actionable — explain the reason (stale / timestamp skew / fewer than 2 comparable venues).
- Always surface `warnings`, `excluded`, and `skipped` to the user; never silently drop a venue.

## Safety rules
1. **Read-only.** Never execute, swap, transfer, or sign. No API keys, no wallet.
2. **Exact-address resolution only.** Scam look-alike tokens exist on-chain; never match by ticker substring.
3. **Objective data only.** No investment advice; flag unverified, illiquid, or market-closed venues.
4. **Arb is signal, not free money.** Cross-venue convergence is generally NOT capturable by an anonymous wallet (KYC-gated redemption, US-hours peg), so present spreads as a signal.
