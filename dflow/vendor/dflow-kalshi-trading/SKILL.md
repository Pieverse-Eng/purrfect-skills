---
name: dflow-kalshi-trading
description: Buy, sell, or redeem YES/NO outcome tokens on Kalshi prediction markets via DFlow. Use when the user wants to bet on an event, place a Kalshi order, take a YES or NO position, exit a Kalshi position, redeem a winner, or tune priority fees on a PM trade. Do NOT use to discover markets, view positions, stream prices, complete Proof KYC, or for non-Kalshi spot swaps.
disable-model-invocation: true
user-invocable: false
---

# DFlow Kalshi Trading

Buy, sell, and redeem YES/NO outcome tokens on Kalshi prediction markets.
These trades are **asynchronous** — submit, then poll until terminal. The
on-chain transaction is not the fill.

If the user only has a ticker or event name, read `dflow-kalshi-market-scanner`
first.

## Settlement rails

Every initialized Kalshi market has **both** a USDC rail and a CASH rail under
`market.accounts`. Each rail has its own `marketLedger`, `yesMint`, and
`noMint`. They share the orderbook (`yesBid` / `yesAsk` / `volume24hFp`) but
holdings are not fungible across rails.

**Default to USDC** unless the user holds CASH or asks for CASH. Do not write
a "fall back to CASH if USDC is missing" path.

- USDC: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- CASH: `CASHx9KJUStyftLFWGvEVf59SGeG9sh5FfcnZMVPCASH`

Key `market.accounts` by those mints. There is no top-level
`market.settlementMint`.

Use the rail's **outcome mint** (`yesMint` / `noMint`) as `outputMint` on a
buy and as `inputMint` on a sell. Do not pass `marketLedger` or a `--side`
flag to `purr dflow`.

## Workflows

### Buy

1. Check the buy gates once per session (KYC + geo + maintenance) — see
   Gotchas.
2. Input = settlement mint (USDC or CASH). Output = `yesMint` or `noMint`.
3. Poll until terminal (`closed` / `expired` / `failed`).

**"Buy N whole contracts"** from a snapshotted `yesAsk`: 
`Math.ceil(N * yesAsk * 1e6)` atomic USDC, plus at most ~1% buffer so a tick
up does not leave N-1. Leftover stablecoin is refunded. Do not over-fund by
more than a percent or two.

### Sell

Flip the mints — outcome in, settlement out. **No KYC.**

### Redeem

Once the market is `determined` / `finalized` **and** `redemptionStatus` is
`"open"`, redeem by selling the winning side back to the settlement mint. No
special flag, no KYC.

## Trade shape

Infer if unambiguous:

1. **Operation** — buy / sell / redeem.
2. **Market + side** — the YES or NO outcome mint for the chosen rail.
3. **Settlement rail** — USDC or CASH. Default USDC.
4. **Amount in atomic units** — every Kalshi mint is **6 decimals**. Buys
   submit settlement amounts; sells/redeems submit outcome-token amounts.

Slippage defaults to `"auto"`. Priority fee defaults to DFlow-auto (cap 0.005
SOL). Only put `predictionMarketSlippageBps` or `prioritizationFeeLamports` in
`--params-json` when the user set a value. Platform fees: `dflow-platform-fees`.

## Gotchas

- **All Kalshi mints are 6 decimals.**
- **Buys are whole-contract only.** Floor is 0.01 USDC, but the practical
  floor is one contract at the current price. Quote first near the floor.
- **Async fills, no exceptions.** `executionMode` is `"async"`. Poll with the
  broadcast **signature**, not `orderAddress`.
- **Buy gates, once per session:**
  - **Proof KYC** — required to buy, not to sell or redeem. Check
    `GET https://proof.dflow.net/verify/{address}`. On
    `unverified_wallet_not_allowed` / `PROOF_NOT_VERIFIED`, use
    `details.deepLink` and `dflow-proof-kyc`.
  - **Geoblock** — some jurisdictions are restricted. Policy:
    `https://pond.dflow.net/legal/prediction-market-compliance`.
- **Maintenance window.** Kalshi is offline **Thursdays 3:00–5:00 AM ET**.
  `/order` returns `route_not_found`. Do not submit PM trades in that window.
- **`route_not_found` is a catch-all.** Wrong mint, amount below one
  contract, no liquidity, or the maintenance window.

## Sibling skills

- `dflow-kalshi-market-scanner` — discover markets
- `dflow-kalshi-market-data` — live prices, orderbooks, streams
- `dflow-kalshi-portfolio` — positions and P&L
- `dflow-proof-kyc` — verify a wallet before a buy
- `dflow-platform-fees` — builder fee on PM trades
- `dflow-spot-trading` — non-Kalshi swaps
