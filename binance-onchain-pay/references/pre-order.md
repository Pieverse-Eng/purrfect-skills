# Pre-Order

Use pre-order to create a Binance hosted checkout order after the user confirms
the quote and destination details.

## Overview

This command creates an order and returns a checkout or action URL. The user
continues on Binance's hosted page, and Binance delivers crypto on-chain to the
receiving wallet address or supported destination. Do not run this command
without explicit confirmation from the user after showing quote, transfer,
checkout, or contract details.

## Workflow

1. Run `estimated-quote` first.
2. Show the quote, destination wallet, destination network, payment method, and
   checkout implication.
3. Ask the user to confirm order creation.
4. Run `pre-order` without `--idempotency-key` on the first attempt. The CLI
   generates the key automatically.
5. Return the checkout URL, `externalOrderId`, and `idempotencyKey`.
6. Tell the user the checkout or action URL opens Binance's hosted page, where
   Binance handles KYC, payment processing, or account confirmation where
   applicable.
7. Use `order --external-order-id <id>` to poll status.

## Syntax

```bash
purr binance-onchain-pay pre-order \
  [--idempotency-key <key>] \
  [--fiat <fiat>] \
  [--fiat-amount <amount>] \
  [--crypto <crypto>] \
  [--requested-amount <amount>] \
  [--amount-type <1|2>] \
  [--address <wallet>] \
  [--network <network>] \
  [--pay-method-code <code>] \
  [--pay-method-sub-code <code>] \
  [--redirect-url <url>] \
  [--fail-redirect-url <url>] \
  [--redirect-deep-link <url>] \
  [--fail-redirect-deep-link <url>] \
  [--contract-address <address>] \
  [--customization-json <json>] \
  [--customization-file <path>] \
  [--dest-contract-address <address>] \
  [--dest-contract-abi <name>] \
  [--dest-contract-params-json <json>] \
  [--dest-contract-params-file <path>] \
  [--affiliate-code <code>] \
  [--gtr-template-code <code>]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--idempotency-key <key>` | Retry only | Omit on the first attempt. Reuse the key returned by a failed attempt only when explicitly retrying the exact same request. |
| `--fiat <fiat>` | No | Fiat currency code. |
| `--fiat-amount <amount>` | Required if not using requested amount | Fiat amount to spend. |
| `--crypto <crypto>` | No | Crypto asset code. |
| `--requested-amount <amount>` | Required with `--amount-type` if `--fiat-amount` is omitted | Amount value. |
| `--amount-type <1\|2>` | Required with `--requested-amount` | `1` means fiat amount; `2` means crypto amount. |
| `--address <wallet>` | Recommended | Destination wallet address that receives crypto. |
| `--network <network>` | Recommended | Delivery network such as `BSC`, `ETH`, `BASE`, or `SOL`. |
| `--pay-method-code <code>` | No | Payment method code returned by payment method lookup. |
| `--pay-method-sub-code <code>` | No | Payment method sub-code when Binance requires it. |
| `--redirect-url <url>` | No | Hosted checkout success redirect URL. |
| `--fail-redirect-url <url>` | No | Hosted checkout failure redirect URL. |
| `--redirect-deep-link <url>` | No | Mobile success deep link. |
| `--fail-redirect-deep-link <url>` | No | Mobile failure deep link. |
| `--contract-address <address>` | No | Token contract address when Binance requires it. |
| `--customization-json <json>` | No | JSON object for Binance customization options. |
| `--customization-file <path>` | No | File containing Binance customization JSON. |
| `--dest-contract-address <address>` | No | Destination contract address for advanced Onchain Pay flows. |
| `--dest-contract-abi <name>` | No | Destination contract ABI name for advanced flows. |
| `--dest-contract-params-json <json>` | No | JSON object for destination contract params. |
| `--dest-contract-params-file <path>` | No | File containing destination contract params JSON. |
| `--affiliate-code <code>` | No | Affiliate code. |
| `--gtr-template-code <code>` | No | GTR template code. |

## Commands

```bash
purr binance-onchain-pay pre-order \
  --fiat USD \
  --crypto USDT \
  --requested-amount 50 \
  --amount-type 1 \
  --network BSC \
  --address 0x... \
  --pay-method-code BUY_CARD
```

## Response Shape

Success prints the sanitized broker response to stdout. The platform generates
the `externalOrderId`, and the CLI returns the idempotency metadata needed for a
safe retry:

```json
{
  "externalOrderId": "pc0123456789abcdef0123456789abcdef",
  "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000",
  "idempotent": false,
  "link": "https://app.binance.com/...",
  "linkExpireTime": 1772852565045
}
```

The checkout URL may appear as `link`, `redirectUrl`, or another URL field in
Binance's returned data. Surface the checkout URL clearly to the user.

Do not automatically retry an uncertain pre-order result. If the user explicitly
asks to retry the exact unchanged request, reuse the returned key with
`--idempotency-key <key>`.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Pre-order requires --fiat-amount or both --requested-amount and --amount-type` | Add a fiat amount or a requested amount with amount type. |
| `Pre-order externalOrderId and timestamp are platform-managed; use --idempotency-key for safe retries` | Remove caller-supplied `--external-order-id` or `--ts`. |
| `Missing required credentials: ...` | Hosted platform authentication is unavailable. |
| Error ending in `Retry with --idempotency-key <key>` | Report the error and key. Do not retry automatically. |
