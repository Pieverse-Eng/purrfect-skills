---
name: dflow-spot-trading
description: Swap any pair of Solana tokens via DFlow. Use when the user wants to trade, swap, or convert tokens on Solana, get a price quote, or tune priority fees. Do NOT use for Kalshi YES/NO trades or builder-side platform fees.
disable-model-invocation: true
user-invocable: false
---

# DFlow Spot Trading

Swap any pair of Solana tokens via DFlow. Trades settle synchronously in one
transaction.

## Trade shape

Infer if unambiguous:

1. **Input + output token** — base58 mint addresses. The parent skill resolves
   SOL, USDC, and USDT. For anything else, get the mint from an official source.
   Do not guess from symbol alone.
2. **Amount in atomic units of the input token** — `500_000` = $0.50 USDC,
   `1_000_000_000` = 1 SOL. Convert before calling.

Slippage defaults to `"auto"`. Priority fee defaults to DFlow-auto (cap 0.005
SOL). Only put `slippageBps` or `prioritizationFeeLamports` in `--params-json`
when the user set a value. Platform fees: `dflow-platform-fees`.

## Gotchas

- **Atomic units always.** Human-readable amounts are rejected. Confirm
  decimals each time.
- **Orders take base58 mints only.** Do not pass `"USDC"` as `inputMint`.
- **`route_not_found` is often a units or mint mistake** before it is a
  liquidity issue.
- **`price_impact_too_high` is real.** Reduce `amount`, or pass
  `priceImpactTolerancePct` only with explicit consent.
- **Onchain failure with slippage logs.** Do not silently bump `slippageBps`
  on retry.

## Sibling skills

- `dflow-kalshi-trading` — Kalshi YES/NO trades
- `dflow-platform-fees` — builder cut on swaps
