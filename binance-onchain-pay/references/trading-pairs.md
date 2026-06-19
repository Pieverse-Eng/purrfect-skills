# Trading Pairs

Use trading pairs to list fiat currencies and cryptocurrencies supported by
Binance Onchain Pay.

## Overview

This is a discovery command. Run it before quoting when the requested fiat or
crypto asset may not be supported.

## Workflow

1. Run the command.
2. Check whether the user's fiat currency and crypto asset are present.
3. If either value is missing, ask the user to choose a supported route.

## Syntax

```bash
purr binance-onchain-pay trading-pairs
```

## Parameters

This command has no parameters.

## Commands

```bash
purr binance-onchain-pay trading-pairs
```

## Response Shape

Success prints raw Binance Onchain Pay JSON to stdout. The response usually
contains supported fiat and crypto currency lists.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Missing env vars: ...` | Binance Onchain Pay runtime credentials are not configured. |
| `Binance Onchain Pay error <code>: ...` | Binance returned an API-level error. |
| `Binance Onchain Pay HTTP <status>: ...` | The HTTP request failed. Check runtime base URL, partner credentials, and Binance service availability. |
