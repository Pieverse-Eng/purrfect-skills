# Authentication

Use this reference only for platform authentication troubleshooting.
User-facing execution should use `purr binance-onchain-pay`; do not manually
sign requests or ask users for Binance partner secrets.

## Overview

The CLI authenticates to the instance-scoped platform API. The platform broker
holds the Binance partner credentials, signs the Binance request, and returns a
sanitized response.

## Workflow

1. Confirm the hosted runtime provides `WALLET_API_URL`, `WALLET_API_TOKEN`, and
   `INSTANCE_ID`.
2. Confirm the CLI can authenticate to the platform API for that instance.
3. Confirm the platform broker operation is available.
4. Do not inspect or reproduce Binance signing in the tenant runtime.

## Signing Boundary

1. The CLI sends only a fixed supported operation to the platform broker.
2. The platform generates the Binance timestamp and signature.
3. Binance credentials and reusable signatures never return to the tenant.
4. The platform sanitizes upstream responses and errors.

## Hosted Runtime Mapping

| Runtime env | Platform usage |
| --- | --- |
| `WALLET_API_URL` | Platform API base URL |
| `WALLET_API_TOKEN` | Per-instance platform bearer token |
| `INSTANCE_ID` | Hosted instance identifier used to scope broker requests |

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Missing required credentials: ...` | Hosted platform authentication is unavailable. |
| `Binance Connect <operation> failed` | The platform broker or Binance Connect operation failed. Report the error without exposing credentials or raw upstream data. |
