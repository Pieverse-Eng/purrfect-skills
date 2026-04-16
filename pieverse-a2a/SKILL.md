---
name: pieverse-a2a
description: Use when the user wants to access a Pieverse A2A payment-gated HTTP resource, handle HTTP 402 Payment Required with a Pieverse paymentRequired body, authorize payment through the hosted wallet, retry with X-Pieverse-Payment, or inspect/challenge strict-mode payment results.
---

# Pieverse A2A Payments

Pieverse A2A is the first-party HTTP 402 payment protocol for agent-to-merchant
resource access. Use this skill when a request returns a Pieverse
`paymentRequired` challenge body or when the user asks to pay for a
Pieverse-gated API/resource.

Do not use this skill for generic x402 payment headers, swaps, transfers, or
portfolio queries. Route generic x402 to the relevant `okx`, `morph`, or wallet
skill. Route token swaps/transfers through `onchain`.

## Requirements

Hosted agents already receive the required platform environment:

| Env var | Meaning |
|---|---|
| `WALLET_API_URL` | API server base URL |
| `WALLET_API_TOKEN` | Bearer token for this hosted instance |
| `INSTANCE_ID` | Hosted instance ID |

If any are missing, stop and explain that Pieverse A2A payments require a hosted
Purr-Fect Claw runtime with platform wallet access.

## Safety Rules

- First request the resource without payment.
- If the response is not `402`, return it directly. Do not inspect wallet state
  or authorize payment.
- If the response is `402`, parse and show the payment details before paying.
- Always ask for explicit Yes/No confirmation before authorizing payment.
- Never guess missing challenge fields. A valid Pieverse challenge must include
  `challengeId`, `recipient`, `amountBaseUnits`, `token`, and `chainId`.
- For strict verification, tell the user the payment can be held and challenged
  if the delivered result is wrong.
- Do not retry a paid request manually with a new authorization unless the user
  confirms again. Duplicate non-idempotent merchant requests may cause multiple
  payments.

## Payer Flow

Use plain HTTP commands for now. Do not create or run local helper scripts for
this flow; the long-term home should be `purr a2a pay`.

### Step 1: Probe the resource

```bash
curl -sS -i "https://merchant.example/api/data"
```

If the response is not `402`, return the response directly. No payment is needed.

If the response is `402`, parse the JSON body and extract `paymentRequired`.
Show the details to the user:

```text
This resource requires Pieverse A2A payment:
- amount: <amount> <symbol>
- base units: <amountBaseUnits>
- chain: <chainId>
- token: <token>
- recipient: <recipient>
- description: <description>

Proceed with payment? (Yes/No)
```

### Step 2: Authorize and retry only after confirmation

If the user says Yes, call the platform payment authorization endpoint:

```bash
curl -sS -X POST "$WALLET_API_URL/v1/payments/authorize" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challengeId": "<paymentRequired.challengeId>",
    "to": "<paymentRequired.recipient>",
    "amountBaseUnits": "<paymentRequired.amountBaseUnits>",
    "token": "<paymentRequired.token>",
    "chainId": <paymentRequired.chainId>,
    "verification": "soft"
  }'
```

For strict mode, set `"verification": "strict"` only when the user explicitly
asks for strict settlement.

The response contains `data.paymentCredential`.

### Step 3: Retry the original request

Retry the same method, URL, body, and merchant headers as the original request,
adding only the payment credential header:

```bash
curl -sS -i "https://merchant.example/api/data" \
  -H "X-Pieverse-Payment: <paymentCredential>"
```

For POST/PUT/PATCH requests, preserve the original request body and content
headers. If the retry response is not 2xx, report both the payment credential
and the merchant response. Do not assume settlement succeeded just because
authorization completed.

## Strict-Mode Challenge

If a strict-mode paid response is wrong, empty, or not what the user requested,
the user can challenge the held payment during the hold window.

```bash
curl -sS -X POST "$WALLET_API_URL/v1/payments/<paymentCredential>/challenge" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason":"bad_result","evidence":{"summary":"Describe what was wrong"}}'
```

Challenge only when the user explicitly says the delivered result is bad or asks
to dispute the payment.

## Common Failures

| Error | Meaning |
|---|---|
| `missing_platform_env` | Runtime lacks `WALLET_API_URL`, `WALLET_API_TOKEN`, or `INSTANCE_ID` |
| `not_pieverse_402` | The server returned 402 without a Pieverse `paymentRequired` body |
| user declined | Payment was required, but the user did not confirm |
| `authorization_failed` | API server rejected the payment authorization |
| `insufficient_balance` | Wallet has insufficient token balance after active locks |

## Purr CLI Feature Request

The eventual CLI shape should be:

```bash
purr a2a pay --url https://merchant.example/api/data [--method GET] [--verification soft]
```

Expected behavior:

1. Request the URL without payment.
2. Return immediately for non-402 responses.
3. For Pieverse 402 challenges, display amount, token, chain, recipient, and
   description.
4. Require explicit confirmation before authorizing.
5. Call platform `/v1/payments/authorize`.
6. Retry with `X-Pieverse-Payment`.
7. Return structured JSON containing the challenge summary, credential, and
   final merchant response.

Do not make `purr a2a pay` a generic x402 command. It should implement the
Pieverse A2A body challenge flow first; generic x402 can remain separate.
