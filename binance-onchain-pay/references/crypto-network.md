# Crypto Network

Use crypto network to list blockchain delivery networks supported by Binance
Onchain Pay, including network metadata, fees, and limits when returned.

## Overview

This is a discovery command. Run it before quoting or creating a pre-order when
the destination network is uncertain.

## Workflow

1. Run the command.
2. Check whether the requested crypto asset can be delivered on the user's
   requested network.
3. Use the Binance network code, such as `BSC`, `ETH`, `BASE`, or `SOL`, in
   quote and pre-order commands.

## Syntax

```bash
purr binance-onchain-pay crypto-network
```

## Parameters

This command has no parameters.

## Commands

```bash
purr binance-onchain-pay crypto-network
```

## Response Shape

Success prints raw Binance Onchain Pay JSON to stdout. The response usually
contains network codes, crypto assets, withdrawal fees, and limits.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Missing env vars: ...` | Binance Onchain Pay runtime credentials are not configured. |
| `Binance Onchain Pay error <code>: ...` | Binance returned an API-level error. |
| `Binance Onchain Pay HTTP <status>: ...` | The HTTP request failed. Check runtime base URL, partner credentials, and Binance service availability. |
