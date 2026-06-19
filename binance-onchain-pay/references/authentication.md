# Authentication

Use this reference only for credential or signing troubleshooting. User-facing
execution should use `purr binance-onchain-pay`; do not manually sign requests
or ask users for Binance partner secrets.

## Overview

Binance Onchain Pay requests are signed by the CLI with partner credentials from
runtime environment variables.

## Workflow

1. Confirm the runtime provides Binance Onchain Pay credentials.
2. Confirm the request body is compact JSON, or empty string when the endpoint
   has no body.
3. Confirm the timestamp is in milliseconds.
4. Confirm the signature payload is `JSON_BODY + TIMESTAMP`.
5. Confirm the signed request includes the required Binance headers.

## Signing Summary

1. Payload = `JSON_BODY + TIMESTAMP` in milliseconds.
2. Sign payload with RSA SHA256 using the PEM private key.
3. Base64 encode the signature as a single line.
4. Send requests as POST with headers:
   - `X-Tesla-ClientId`
   - `X-Tesla-SignAccessToken`
   - `X-Tesla-Signature`
   - `X-Tesla-Timestamp`
   - `Content-Type: application/json`

## Runtime Mapping

| Runtime env | Binance usage |
| --- | --- |
| `BINANCE_CONNECT_CLIENT_ID` | `X-Tesla-ClientId` |
| `BINANCE_CONNECT_ACCESS_TOKEN` | `X-Tesla-SignAccessToken` |
| `BINANCE_CONNECT_PRIVATE_KEY` | PEM private key used for RSA SHA256 signing |
| `BINANCE_CONNECT_BASE_URL` | Binance API base URL |

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Missing env vars: ...` | Runtime credentials are not configured. |
| `Binance Onchain Pay HTTP 401/403: ...` | Partner credentials, base URL, or signing details may be invalid. |
| `Binance Onchain Pay error <code>: ...` | Binance accepted the signed request but rejected it at API level. |
