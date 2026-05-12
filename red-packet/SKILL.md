---
name: red-packet
description: Use when a Purr-Fect Claw user agent is asked to claim or prepare a red packet.
metadata:
  hermes:
    related_skills: []
---

# Red Packet

Use this skill inside a user instance when the user asks to claim a red packet
through their agent/merchant skill.

## Requirements

The current instance runtime must expose the merchant MCP tool
`purrfect_order_create`.

The claim submission must use this instance's platform API auth:

- `WALLET_API_URL`
- `WALLET_API_TOKEN`
- `INSTANCE_ID`

Before submitting, check they are present:

```bash
test -n "${WALLET_API_URL:-}" && test -n "${WALLET_API_TOKEN:-}" && test -n "${INSTANCE_ID:-}"
```

Use `Authorization: Bearer ${WALLET_API_TOKEN}` and use `INSTANCE_ID` as the
request `instanceId`. Do not use `PIEVERSE_API_KEY`, `PLATFORM_FORWARD_SECRET`,
or a user app token for this call.

## OKX x402 Workflow

1. Identify the red packet code and amount. Use the campaign amount in base
   units. Call the already-exposed MCP tool `purrfect_order_create` with:

```json
{
  "amount_base_units": "<campaign amount base units>",
  "paymentMethod": "okx-x402"
}
```

2. Read the returned `buyUrl`.

3. Submit the `buyUrl` to the platform API using this instance's auth:

POST /v1/redpackets/{code}/merchant-payment

Use this request body:

```json
{
  "instanceId": "<INSTANCE_ID>",
  "buyUrl": "<merchant buyUrl>",
  "orderCode": "<merchant order code>"
}
```

4. The platform pays the URL with the campaign funder wallet through OKX x402
   support, updates the red packet claim, and returns the tx hash.

## Safety Rules

- Do not ask the funder wallet to transfer directly for the OKX flow.
- Do not create a second order after submitting one unless the platform API
  reports the claim did not complete.
- If the merchant order amount does not equal the red packet claim amount, cancel
  and recreate the order before submitting.
- If the platform returns `403 "Token not authorized for this instance"`, stop.
  The runtime token is not authorized for the submitted `INSTANCE_ID`.
