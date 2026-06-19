# Payment Method List

Use payment method list to discover available Binance Onchain Pay payment
methods before quoting or creating a pre-order.

## Overview

The CLI supports two official payment method endpoints:

- Broad v2 lookup: run without pair filters; optionally add `--lang`.
- Pair-specific v1 lookup: include `--fiat`, `--crypto`, `--total-amount`, and
  `--amount-type` together; optionally add `--network` or `--contract-address`.

## Workflow

1. Run the broad lookup when the user has not chosen fiat, crypto, or amount.
2. Run the pair-specific lookup after fiat, crypto, amount, and amount type are
   known.
3. Choose a returned payment method code, such as `BUY_CARD`, for
   `estimated-quote` and `pre-order`.
4. If Binance returns method limits, make sure the user amount is within range.

## Syntax

```bash
purr binance-onchain-pay payment-method-list [--lang <lang>]
purr binance-onchain-pay payment-method-list \
  --fiat <fiat> \
  --crypto <crypto> \
  --total-amount <amount> \
  --amount-type <1|2> \
  [--network <network>] \
  [--contract-address <address>]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--lang <lang>` | No | Language code for broad v2 lookup. |
| `--fiat <fiat>` | Pair-specific lookup | Fiat currency code. |
| `--crypto <crypto>` | Pair-specific lookup | Crypto asset code. |
| `--total-amount <amount>` | Pair-specific lookup | Amount used for payment method limits. |
| `--amount-type <1\|2>` | Pair-specific lookup | `1` means fiat amount; `2` means crypto amount. |
| `--network <network>` | No | Delivery network such as `BSC`, `ETH`, `BASE`, or `SOL`. |
| `--contract-address <address>` | No | Token contract address when Binance requires it. |

## Commands

```bash
purr binance-onchain-pay payment-method-list --lang en
purr binance-onchain-pay payment-method-list \
  --fiat USD \
  --crypto USDT \
  --total-amount 50 \
  --amount-type 1 \
  --network BSC
```

## Response Shape

Success prints raw Binance Onchain Pay JSON to stdout. The response usually
contains payment method codes, names, supported amounts, and limits.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Payment method lookup requires --fiat, --crypto, --total-amount, and --amount-type when using pair-specific filters` | Pair-specific lookup is missing required fields. |
| `Missing env vars: ...` | Binance Onchain Pay runtime credentials are not configured. |
| `Binance Onchain Pay error <code>: ...` | Binance returned an API-level error. |
| `Binance Onchain Pay HTTP <status>: ...` | The HTTP request failed. Check runtime base URL, partner credentials, and Binance service availability. |
