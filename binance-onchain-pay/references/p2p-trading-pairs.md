# P2P Trading Pairs

Use P2P trading pairs to list Binance Onchain Pay P2P-specific fiat routes.

## Overview

This is a discovery command for P2P availability. It is optional for normal card
or wallet payment flows.

## Workflow

1. Run the command, optionally with `--fiat`.
2. Check whether the user's fiat currency is available for P2P.
3. If P2P is used, pass the returned payment method code into quote or pre-order
   commands when appropriate.

## Syntax

```bash
purr binance-onchain-pay p2p-trading-pairs [--fiat <fiat>]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--fiat <fiat>` | No | Fiat currency filter, such as `USD`, `EUR`, or `TWD`. |

## Commands

```bash
purr binance-onchain-pay p2p-trading-pairs
purr binance-onchain-pay p2p-trading-pairs --fiat USD
```

## Response Shape

Success prints raw Binance Onchain Pay JSON to stdout. The response usually
contains P2P-supported fiat and crypto route data.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Missing env vars: ...` | Binance Onchain Pay runtime credentials are not configured. |
| `Binance Onchain Pay error <code>: ...` | Binance returned an API-level error. |
| `Binance Onchain Pay HTTP <status>: ...` | The HTTP request failed. Check runtime base URL, partner credentials, and Binance service availability. |
