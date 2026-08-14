---
name: dflow
description: Use when the user wants a Solana swap, a Kalshi YES/NO bet, DFlow market prices or discovery, their DFlow positions or P&L, Proof KYC, or a builder fee on a DFlow trade.
---

# DFlow

Solana token swaps and Kalshi prediction-market trades through DFlow, plus
market discovery, positions, Proof KYC, and builder fees.

## Mandatory Rules

Read this file first, then read the matching vendor `SKILL.md` before
workflow-specific commands.

The only non-`purr` DFlow HTTP call is the public Proof check:
`GET https://proof.dflow.net/verify/<solana-address>`.

### On DFlow errors: stop and report — do not pivot

If any DFlow step fails (timeout, HTTP error, route not found, no quote, RPC
failure, multi-signer rejection, non-zero exit from `purr dflow`, or any other
error from this skill's workflow):

1. **Stop.** Do not retry with different venues, skills, or tools.
2. **Do not** call other skills (for example Surf, AgentKey, Chainbase,
   CoinMarketCap, Jupiter wrappers, or other swap skills).
3. **Do not** invent alternate swap paths, liquidity lookups, or "maybe this
   token is pump.fun so try X" investigations.
4. **Report the error plainly** to the user: what command/step failed, the
   error message (or timeout), and that the DFlow flow stopped. Optionally
   suggest they retry later or provide a different mint/amount — then wait.

At most **one** identical retry of the same `purr dflow` command is allowed
when the failure is clearly a transient timeout/network blip. After that, stop
and report. Never expand the tool surface to diagnose the failure.

## Out Of Scope

- Official DFlow local wallet, vault, OWS, mnemonic, or private-key flows.
- Official `dflow` CLI install, `dflow setup`, `dflow fund`, and
  `dflow guardrails`.
- Sponsored / gasless DFlow flows that require a second signer.
- DFlow transactions rejected by `purr dflow` because they need another signer.

## Intent Map

| User intent | Read first |
|---|---|
| Swap, trade SOL for USDC, quote token | `vendor/dflow-spot-trading/SKILL.md` |
| Buy YES, buy NO, bet on, sell outcome tokens, redeem winner | `vendor/dflow-kalshi-trading/SKILL.md` |
| Find markets, cheap YES, arbitrage, big movers, closing soon | `vendor/dflow-kalshi-market-scanner/SKILL.md` |
| Show orderbook, stream prices, last trades, candlesticks | `vendor/dflow-kalshi-market-data/SKILL.md` |
| My positions, P&L, activity history, redeemable | `vendor/dflow-kalshi-portfolio/SKILL.md` |
| KYC, Proof, verify wallet, `PROOF_NOT_VERIFIED` | `vendor/dflow-proof-kyc/SKILL.md` |
| Take a cut, platform fee, `platformFeeBps`, `platformFeeScale` | `vendor/dflow-platform-fees/SKILL.md` |

If the request spans multiple areas, read each relevant vendor skill in workflow
order. Examples: scan markets then trade = scanner first, then Kalshi trading;
show position then redeem = portfolio first, then Kalshi trading; add a builder
fee to a swap = spot trading plus platform fees.

## Common Solana Mints

Use these mainnet mints for common Solana swap requests when the user names the
asset by symbol:

| Asset | Mint | Decimals | Note |
|---|---|---:|---|
| SOL / wSOL | `So11111111111111111111111111111111111111112` | 9 | Use when DFlow requires an SPL mint for SOL; amounts are lamports. |
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6 | Mainnet USDC. |
| USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | 6 | Mainnet USDT. |

For tokens not listed here, resolve the exact mint through the vendor workflow
or an official source before building an order. Do not guess from symbol alone.

## `--params-json` Rules

Add `--params-json '<dflow-order-params-json>'` only when the vendor workflow
requires extra DFlow `/order` **request** parameters (for example slippage,
platform fees, or route options).

`purr` always sends `dynamicComputeUnitLimit=true` on `/order`. Do not put
compute-unit fields in `--params-json`.

Never include these keys in `--params-json`:

| Key | Reason |
|---|---|
| `userPublicKey`, `inputMint`, `outputMint`, `amount` | Managed by `purr` / the hosted wallet |
| `dynamicComputeUnitLimit` | Always set to `true` by `purr` |
| `computeUnitLimit` | Response field only, not a request parameter |
| `sponsor`, `sponsorExec`, `predictionMarketInitPayer` | Multi-signer / gasless flows (out of scope) |

## Execution Workflow

For spot swaps, Kalshi buys, sells, redeems, and any other supported DFlow
`/order` transaction:

1. Read the matching vendor skill to determine mints, amount units, market
   fields, KYC gates, maintenance windows, slippage, and status expectations.
2. Price-only requests use quote, not a wallet-bound order:

```bash
purr dflow quote \
  --input-mint <input-mint> \
  --output-mint <output-mint> \
  --amount <atomic-amount>
```

3. Get the Solana address when the user needs to see the wallet, or before
   Proof KYC:

```bash
purr wallet address --chain-type solana
```

4. Build a **preview** order. Default output is summary-only: it includes
   `summary` and omits the full `order` payload (no serialized transaction):

```bash
purr dflow order \
  --input-mint <input-mint> \
  --output-mint <output-mint> \
  --amount <atomic-amount>
```

Include the same `--params-json` you will use at execution time when it
applies.

5. Present the `summary` object to the user. Typical fields:

   - `inAmount`, `outAmount`, `otherAmountThreshold`
   - `priceImpactPct`, `slippageBps`
   - `prioritizationFeeLamports`, `prioritizationType`
   - `executionMode`, `orderAddress`, `hasTransaction`

   `orderAddress` is informational only. Do **not** use it for
   `purr dflow prediction-order-status`.

6. Ask for explicit confirmation before execution.
7. After confirmation, execute with the **same** order args (preferred path).
   Do not try to recover `order` from a non-`--raw` preview response:

```bash
purr dflow order \
  --input-mint <input-mint> \
  --output-mint <output-mint> \
  --amount <atomic-amount> \
  --execute true \
  --poll true
```

Reuse the same `--params-json` from the preview.

With `--poll true`, read the result for:

- transaction **signature** (from `execution` / broadcast result)
- `lastValidBlockHeight` when present
- polled order **status** when present
- `summary` amounts

If execution returns `statusError`, the transaction was already broadcast and
confirmed but the prediction-order status lookup failed. Report the signature
and the status error. Retry only `purr dflow prediction-order-status` with that
signature; never rebuild or execute the order again.

Two-step execute only when you must hold the order JSON (for example debugging
or delayed signing). Build with `--raw true`, then pass the raw `.order`
object:

```bash
purr dflow order \
  --input-mint <input-mint> \
  --output-mint <output-mint> \
  --amount <atomic-amount> \
  --raw true
```

```bash
purr dflow execute-order \
  --order-json '<order-object-from-raw-output.order>' \
  --poll true
```

`--order-file /tmp/dflow-order.json` is also accepted. Never pass
`--order-json` built from a default (non-`--raw`) order response — that output
omits `order`.

If preview, execute, status, or any other DFlow step fails, stop and report the
error. Do not call other skills or tools to work around it. Do not switch to
manual signing.

To check a submitted async order after broadcast, use the **transaction
signature** from execution — **not** `orderAddress`. Pass
`--last-valid-block-height` when execute returned one:

```bash
purr dflow prediction-order-status \
  --signature <transaction-signature> \
  --last-valid-block-height <lastValidBlockHeight> \
  --poll true
```

If `purr dflow` rejects the transaction because it needs another signer or
multiple signers, stop and explain that the DFlow flow is unsupported.

## Workflow Overrides

### Spot Swaps

Read `vendor/dflow-spot-trading/SKILL.md` for token/mint selection, atomic
units, slippage, priority fee, route errors, and DFlow `/order` semantics.

Use `purr dflow quote` for a price-only check. Use `purr dflow order` then
`purr dflow order --execute true` (or `--raw true` + `execute-order` when
needed).

Sponsored / gasless spot flows are out of scope when they require a sponsor
co-signer.

### Kalshi Trading

Read `vendor/dflow-kalshi-trading/SKILL.md` for market ledger, settlement rail,
YES/NO side, amount units, KYC, geoblock, maintenance, and async fill rules.

Use `purr dflow order` + `purr dflow order --execute true` (or the raw
two-step path) for buy, sell, and redeem orders. Prefer `--poll true` on
execute for async fills; follow up with
`purr dflow prediction-order-status --signature ...` using the broadcast
signature when needed.

Do not use `sponsor`, `sponsorExec`, or `predictionMarketInitPayer`; those
require unsupported multi-signer flows.

### Market Discovery And Market Data

Read the matching market scanner or market data vendor skill for scan recipes,
field meanings, pagination, and bid/ask math.

Vendor paths are Metadata paths. Call them with `purr dflow metadata`. Do not
prefix paths with `/api/v1/`. GET query fields go in `--query-json`. POST
bodies (`filter_outcome_mints`, `markets/batch`) use `--body-json` and cannot
be combined with `--query-json`.

```bash
purr dflow metadata --path markets --query-json '{"status":"active","limit":10}'
purr dflow metadata --path market/<ticker>
purr dflow metadata --path search --query-json '<vendor-search-query>'
purr dflow metadata --path filter_outcome_mints --body-json '{"addresses":["<mint>"]}'
purr dflow metadata --path markets/batch --body-json '{"mints":["<mint>"]}'
```

Live channels go through `purr dflow stream`: `prices`, `trades`,
`orderbook`, and `priority-fees`.

```bash
purr dflow stream \
  --channel prices \
  --tickers <ticker-1>,<ticker-2> \
  --max-events 100 \
  --timeout-ms 60000
```

Use `--all true` instead of `--tickers` only for a universe-wide subscription.
The `priority-fees` channel accepts neither `--tickers` nor `--all`.

Snapshot priority fees with `purr dflow priority-fees`. Live updates use
`purr dflow stream --channel priority-fees`.

When a scan leads to a trade, use the scanner result to identify the correct
market fields, then execute with `purr dflow` as described above.

### Portfolio

Read `vendor/dflow-kalshi-portfolio/SKILL.md` for mark-to-market, redemption,
and P&L rules.

```bash
purr dflow positions
```

Use `purr dflow metadata --path onchain-trades` with a query JSON that
includes the wallet address for activity and cost basis. Use `markets/batch`
only when you need mark or redemption fields that positions did not return.

### Proof KYC

Read `vendor/dflow-proof-kyc/SKILL.md` for Proof verification rules and
deep-link details.

Check status with:

```text
GET https://proof.dflow.net/verify/<solana-address>
```

For Proof deep-link ownership signatures, sign the exact Proof message with
the same Solana address:

```bash
purr wallet sign \
  --chain-type solana \
  --address <solana-address> \
  --message "Proof KYC verification: <timestamp-ms>"
```

Use the returned Solana signature in the Proof deep link.

### Platform Fees

Read `vendor/dflow-platform-fees/SKILL.md`. Platform fees are DFlow `/order`
parameters, so include them in `--params-json` when building an order with
`purr dflow order`. Still obey the `--params-json` rules above (managed,
auto-set, response-only, and multi-signer keys stay out).

## Operational Checklist

1. Identify the user intent and read the matching vendor skill.
2. Use `purr wallet address --chain-type solana` when the user needs the
   wallet or before Proof KYC.
3. For read-only Metadata, streams, positions, quotes, and priority fees, use
   the matching `purr dflow` command.
4. For DFlow `/order` execution, preview with `purr dflow order` (default
   summary-only output).
5. Show `summary` and ask for explicit confirmation.
6. After confirmation, run the same `purr dflow order` args with
   `--execute true --poll true`. Use `--raw true` + `execute-order` only when
   you must hold the order JSON.
7. Return the transaction **signature**, polled status when present, and any
   next step. For a later status check use
   `purr dflow prediction-order-status --signature <tx-sig> --poll true` —
   never `--order-address`.
8. If execution returns `statusError`, report that the transaction is already
   confirmed and retry only the status command with its signature. Never rerun
   the order or `execute-order`.
9. On any other failure: stop and report the error. Do not pivot to other
   skills or tools.
