---
name: dflow
description: Use for DFlow Solana swaps, Kalshi YES/NO trading, prediction-market discovery and data, positions and P&L, priority fees, Proof KYC, and DFlow platform fees in a hosted PurrfectClaw agent.
---

# DFlow

Use the vendored skills for DFlow domain rules, market fields, amount units,
KYC, and trading behavior. Override their transport and authentication steps
with this file.

## Hosted transport rules

- Use only `purr dflow ...` for authenticated DFlow Trade and Metadata API
  operations. `purr` calls the instance-scoped platform API; the platform
  supplies the production DFlow API key.
- Never ask for, read, configure, print, or pass `DFLOW_API_KEY`.
- Never install or invoke the official `dflow` CLI. Ignore `dflow setup`,
  `dflow quote`, `dflow trade`, `dflow status`, `dflow positions`, vault, OWS,
  funding, and guardrail instructions in vendor files.
- Never call production or development DFlow Trade/Metadata hosts directly.
  Do not fall back to keyless development endpoints.
- Direct Proof verification at `https://proof.dflow.net` remains public and
  does not use the DFlow API key.

## Route the request

| User intent | Read vendor file, then use |
|---|---|
| Spot quote or swap | `vendor/dflow-spot-trading/SKILL.md`; `purr dflow quote/order` |
| Kalshi buy, sell, or redeem | `vendor/dflow-kalshi-trading/SKILL.md`; Metadata lookup then `purr dflow order` |
| Find or rank markets | `vendor/dflow-kalshi-market-scanner/SKILL.md`; `purr dflow metadata/stream` |
| Orderbook, trades, candles, or live prices | `vendor/dflow-kalshi-market-data/SKILL.md`; `purr dflow metadata/stream` |
| Holdings, mark, P&L, or redeemable positions | `vendor/dflow-kalshi-portfolio/SKILL.md`; `purr dflow positions/metadata` |
| Proof verification | `vendor/dflow-proof-kyc/SKILL.md`; [Proof](#proof) |
| Builder/platform fee | `vendor/dflow-platform-fees/SKILL.md`; add fee options to `purr dflow quote/order` |

For combined requests, read vendor files in workflow order: scan before trade,
positions before redeem, and trading before platform fees.

## Read-only commands

### Quote

Use a quote when no transaction is needed:

```bash
purr dflow quote \
  --input-mint <input-mint> \
  --output-mint <output-mint> \
  --amount <atomic-amount> \
  --params-json '<optional-order-options>'
```

### Positions

```bash
purr dflow positions
```

This uses the hosted Solana wallet, reads classic SPL and Token-2022 balances,
and joins outcome mints to DFlow markets. For marks, redemption state, and P&L,
use the additional Metadata calls described by the portfolio vendor skill.

### Metadata REST

Translate every vendor Metadata URL into `purr dflow metadata`. Preserve the
path after `/api/v1/`; pass scalar query parameters as JSON.

```bash
purr dflow metadata \
  --path markets \
  --query-json '{"status":"active","limit":20}'
```

```bash
purr dflow metadata \
  --path market/<ticker>
```

The two batch operations use POST bodies:

```bash
purr dflow metadata \
  --path filter_outcome_mints \
  --body-json '{"addresses":["<mint>"]}'
```

```bash
purr dflow metadata \
  --path markets/batch \
  --body-json '{"mints":["<outcome-mint>"]}'
```

Use at most 200 addresses for `filter_outcome_mints` and 100 mints for
`markets/batch`; split larger inputs into batches. Never generate direct curl,
fetch, or WebSocket code against a DFlow host.

### Metadata streams

Use a ticker list unless the user truly needs the whole market firehose:

```bash
purr dflow stream \
  --channel prices \
  --tickers <ticker-1>,<ticker-2> \
  --max-events 100 \
  --timeout-ms 60000
```

Channels are `prices`, `trades`, and `orderbook`. Use `--all true` instead of
`--tickers` only for a universe-wide subscription. Each event is emitted as
one JSON line; the final line is a stream summary. Restart the command to
reconnect after a timeout or disconnect.

### Priority fees

Snapshot:

```bash
purr dflow priority-fees
```

Live updates:

```bash
purr dflow stream \
  --channel priority-fees \
  --max-events 10 \
  --timeout-ms 60000
```

The priority-fees channel accepts neither `--tickers` nor `--all`.

## Trade workflow

Resolve exact mints and atomic units from the relevant vendor skill. Do not
guess an unfamiliar token mint.

1. Preview a wallet-bound order:

```bash
purr dflow order \
  --input-mint <input-mint> \
  --output-mint <output-mint> \
  --amount <atomic-amount> \
  --params-json '<optional-order-options>'
```

2. Show the user a compact summary containing action, pay amount, estimated
   receive amount, relevant slippage/fees, market side for Kalshi, and wallet.
3. Ask exactly: `Proceed with this DFlow trade? (Yes/No)`
4. Only after an immediate Yes for the same parameters, rerun the command with
   `--execute true --poll true`.
5. Report the transaction signature and polled status. A submitted Kalshi
   transaction is not necessarily a completed fill.

To revisit an async order, use its transaction signature, not `orderAddress`:

```bash
purr dflow status \
  --signature <transaction-signature> \
  --last-valid-block-height <optional-block-height> \
  --poll true
```

Use identical `--params-json` at preview and execution. `purr` manages wallet,
mint, amount, and dynamic compute fields; never put those in `--params-json`.
Platform fee options such as `platformFeeBps`, `platformFeeMode`, and
`feeAccount` belong in `--params-json` when the vendor platform-fee workflow
requires them.

Sponsored/gasless requests requiring `sponsor`, `sponsorExec`, or
`predictionMarketInitPayer` need an additional paying signer and are not
supported by the hosted single-signer wallet. Do not silently turn them into a
normal user-paid trade.

## Portfolio extensions

- Mark outcome positions at the bid for the held side using `markets/batch`.
- Query activity and cost basis with `purr dflow metadata --path onchain-trades`
  and a query JSON containing the hosted wallet address and vendor-specified
  pagination/sort fields.
- Determine redemption eligibility from market status, `redemptionStatus`, and
  the winning side together. Hand an approved sell/redeem to the trade workflow.
- Do not ask for an RPC URL; `purr dflow positions` performs hosted wallet
  balance discovery on the platform.

## Proof

Get the hosted Solana address:

```bash
purr wallet address --chain-type solana
```

Check `GET https://proof.dflow.net/verify/<solana-address>`. If verification is
required, follow the exact message and deep-link rules in the Proof vendor
skill and sign only through `purr wallet sign`. Never request a private key.

## Common mainnet mints

| Asset | Mint | Decimals |
|---|---|---:|
| SOL/wSOL | `So11111111111111111111111111111111111111112` | 9 |
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6 |
| USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | 6 |

## Failure behavior

If a DFlow command fails, report the command step and safe error details, then
stop. Retry the identical read once only for an explicit timeout or transient
network error. Do not switch venue, use a direct DFlow host, ask for a DFlow
key/private key, or increase slippage without user approval.
