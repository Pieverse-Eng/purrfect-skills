---
name: dflow
description: DFlow,Solana swaps,Kalshi,KYC,fees,portfolio,purr
metadata:
  openclaw:
    primaryEnv: DFLOW_API_KEY
---

# DFlow

DFlow workflows for Solana swaps, Kalshi prediction-market trades, market
discovery, portfolio views, Proof KYC, and builder fees. Use the vendored DFlow
skills for workflow rules and DFlow field details, but use `purr` for Solana
address lookup, signing, and transaction execution.

## Mandatory Rules

Read this file first, then read the matching vendor `SKILL.md` before
workflow-specific commands, code, or API calls.

### Check `DFLOW_API_KEY` first

Before any DFlow workflow (Trade API, Metadata API, market scan, portfolio
HTTP, or `purr dflow` with production hosts), check whether `DFLOW_API_KEY` is
configured. Do this once per session before the first DFlow action:

```bash
if [ -n "${DFLOW_API_KEY:-}" ]; then
  echo "DFLOW_API_KEY=present"
else
  echo "DFLOW_API_KEY=missing"
fi
```

Never print or log the key value itself — only presence/absence.

- **Present** — use production DFlow hosts. Pass the key to `purr dflow`
  commands with `--api-key "$DFLOW_API_KEY"`, and to direct HTTP/WebSocket
  clients as `x-api-key`.
- **Missing** — tell the user clearly before continuing:
  - Without `DFLOW_API_KEY`, some DFlow features may be unavailable, rate-limited,
    or limited to **dev** endpoints where supported.
  - Production Trade / Metadata APIs generally expect a key.
  - Apply for a key: https://pond.dflow.net/get-started/api-key
  - After they set it (export / shell profile / runtime env), re-check presence,
    then continue.

`DFLOW_API_KEY` remains optional for light/dev paths, but do not silently skip
the check or hide the limitation. If the user wants to proceed without a key,
continue only on paths that work without it and keep the warning in mind when
errors look like auth or rate-limit failures.

Ignore the Install section in `vendor/README.md`; this repository already
includes the vendored DFlow skills.

## Out Of Scope

- Official DFlow local wallet, vault, OWS, mnemonic, or private-key flows.
- `dflow fund`.
- `dflow guardrails set`, `remove`, or `reset`.
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
platform fees, or route options). Add `--api-key "$DFLOW_API_KEY"` only when
`DFLOW_API_KEY` is available.

`purr` always sends `dynamicComputeUnitLimit=true` on `/order`. Do not put
compute-unit fields in `--params-json`.

Never include these keys in `--params-json`:

| Key | Reason |
|---|---|
| `userPublicKey`, `inputMint`, `outputMint`, `amount` | Managed by `purr` CLI flags / wallet |
| `dynamicComputeUnitLimit` | Always set to `true` by `purr` |
| `computeUnitLimit` | Response field only, not a request parameter |
| `sponsor`, `sponsorExec`, `predictionMarketInitPayer` | Multi-signer / gasless flows (out of scope) |

## Execution Workflow

For spot swaps, Kalshi buys, sells, redeems, and any other supported DFlow
`/order` transaction:

1. Confirm `DFLOW_API_KEY` presence (Mandatory Rules). If missing, warn the
   user first, then only continue if they accept the limits.
2. Read the matching vendor skill to determine mints, amount units, market
   fields, KYC gates, maintenance windows, slippage, and status expectations.
3. Get the Solana address:

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

Include the same `--params-json` / `--api-key` you will use at execution time
when they apply.

5. Present the `summary` object to the user. Typical fields:

   - `inAmount`, `outAmount`, `otherAmountThreshold`
   - `priceImpactPct`, `slippageBps`
   - `prioritizationFeeLamports`, `prioritizationType`
   - `executionMode`, `orderAddress`, `hasTransaction`

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

Reuse the same `--params-json` and `--api-key` from the preview when used.

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

If execution returns an RPC error, report the error plainly. Do not switch to
manual signing or ask for a private key.

To check a submitted async order:

```bash
purr dflow status \
  --order-address <order-address> \
  --poll true
```

If `purr dflow` rejects the transaction because it needs another signer or
multiple signers, stop and explain that the DFlow flow is unsupported.

## Workflow Overrides

### Spot Swaps

Read `vendor/dflow-spot-trading/SKILL.md` for token/mint selection, atomic
units, slippage, priority fee, route errors, and DFlow `/order` semantics.

Use `purr dflow order` (preview) then `purr dflow order --execute true` (or
`--raw true` + `execute-order` when needed) instead of `dflow quote`,
`dflow trade`, Keypair signing, wallet adapter signing, or direct
`sendRawTransaction` code.

Sponsored / gasless spot flows are out of scope when they require a sponsor
co-signer.

### Kalshi Trading

Read `vendor/dflow-kalshi-trading/SKILL.md` for market ledger, settlement rail,
YES/NO side, amount units, KYC, geoblock, maintenance, and async fill rules.

Use `purr dflow order` + `purr dflow order --execute true` (or the raw
two-step path) for buy, sell, and redeem orders.

Do not use official `dflow trade`. Do not use `sponsor`, `sponsorExec`, or
`predictionMarketInitPayer`; those require unsupported multi-signer flows.

### Market Discovery And Market Data

Read the matching market scanner or market data vendor skill. These are
read-only HTTP/WebSocket workflows and do not need wallet signing unless the
user pivots into execution.

When a scan leads to a trade, use the scanner result to identify the correct
market fields, then execute with `purr dflow` as described above.

### Portfolio

Read `vendor/dflow-kalshi-portfolio/SKILL.md` for portfolio pipeline rules.
Do not use `dflow positions`, because it depends on an official DFlow active
vault.

Use `purr wallet address --chain-type solana` to get the Solana address, then
use the vendor API/RPC pipeline for holdings, mark-to-market, P&L, activity,
and redeemable checks.

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
2. Check `DFLOW_API_KEY` presence (see above). If missing, warn the user that
   some features may not work / may be rate-limited, and point them at
   https://pond.dflow.net/get-started/api-key.
3. Use `purr wallet address --chain-type solana` for wallet-scoped context.
4. For read-only data, follow the vendor HTTP/RPC/WebSocket workflow.
5. For DFlow `/order` execution, preview with `purr dflow order` (default
   summary-only output). Pass `--api-key "$DFLOW_API_KEY"` when the key is set.
6. Show `summary` and ask for explicit confirmation.
7. After confirmation, run the same `purr dflow order` args with
   `--execute true --poll true`. Use `--raw true` + `execute-order` only when
   you must hold the order JSON.
8. Return transaction signature, order status, order address, and any next step.
