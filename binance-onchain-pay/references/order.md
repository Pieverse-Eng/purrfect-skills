# Order

Use order to query Binance Onchain Pay order details by `externalOrderId`.

## Overview

This command reads order status after a `pre-order` has been created. It does
not create, modify, or cancel an order.

## Workflow

1. Get the `externalOrderId` from the `pre-order` response.
2. Run the order query.
3. Report the status and any returned payment, checkout, or delivery details.
4. If the order is complete, check the receiving wallet balance with the
   Onchain skill. For common EVM checks, use
   `purr wallet balance --token <symbol> --chain-id <id>`, such as
   `purr wallet balance --token USDT --chain-id 56`.

## Syntax

```bash
purr binance-onchain-pay order --external-order-id <externalOrderId>
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--external-order-id <id>` | Yes | Partner external order ID returned from `pre-order`. |

## Commands

```bash
purr binance-onchain-pay order --external-order-id <externalOrderId>
```

## Response Shape

Success prints the sanitized broker response to stdout. The response usually
contains the order status and permitted order details returned by Binance.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Missing required arg --external-order-id` | The order ID was not provided. |
| `Missing required credentials: ...` | Hosted platform authentication is unavailable. |
| `Binance Connect order lookup failed` | The platform broker or Binance Connect lookup failed. |
