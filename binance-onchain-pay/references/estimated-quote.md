# Estimated Quote

Use estimated quote to preview the price, fees, exchange rate, and estimated
crypto amount before creating a hosted checkout.

## Overview

This command does not create an order. Use it after payment method discovery and
before asking the user to confirm checkout creation.

## Workflow

1. Confirm fiat, amount, amount type, and payment method code.
2. Add `--crypto`, `--network`, and `--address` when known so the quote matches
   the intended delivery route.
3. Run the quote command.
4. Summarize the returned rate, fees, estimated receive amount, destination
   network, and receiving wallet.
5. Ask for explicit user confirmation before running `pre-order`.

## Syntax

```bash
purr binance-onchain-pay estimated-quote \
  --fiat <fiat> \
  --requested-amount <amount> \
  --pay-method-code <code> \
  --amount-type <1|2> \
  [--crypto <crypto>] \
  [--network <network>] \
  [--address <wallet>] \
  [--contract-address <address>]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--fiat <fiat>` | Yes | Fiat currency code. |
| `--requested-amount <amount>` | Yes | Amount to quote. |
| `--pay-method-code <code>` | Yes | Payment method code returned by payment method lookup. |
| `--amount-type <1\|2>` | Yes | `1` means fiat amount; `2` means crypto amount. |
| `--crypto <crypto>` | No | Crypto asset code. Recommended unless using `--contract-address`. |
| `--network <network>` | No | Delivery network. Recommended when known. |
| `--address <wallet>` | No | Destination wallet address for quote refinement. |
| `--contract-address <address>` | No | Token contract address when Binance requires it. |

## Commands

```bash
purr binance-onchain-pay estimated-quote \
  --fiat USD \
  --crypto USDT \
  --requested-amount 50 \
  --amount-type 1 \
  --pay-method-code BUY_CARD \
  --network BSC \
  --address 0x...
```

## Response Shape

Success prints raw Binance Onchain Pay JSON to stdout. The response usually
contains rate, fees, requested amount, and estimated crypto amount.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Estimated quote requires --amount-type` | Add `--amount-type 1` for fiat amount or `--amount-type 2` for crypto amount. |
| `Missing env vars: ...` | Binance Onchain Pay runtime credentials are not configured. |
| `Binance Onchain Pay error <code>: ...` | Binance returned an API-level error. |
| `Binance Onchain Pay HTTP <status>: ...` | The HTTP request failed. Check runtime base URL, partner credentials, and Binance service availability. |
