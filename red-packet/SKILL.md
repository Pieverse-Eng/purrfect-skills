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

The claim submission must use the current instance's authenticated platform API
context.

Use `INSTANCE_ID` as the request `instanceId`; check it is present with
`test -n "${INSTANCE_ID:-}"`.

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

3. Submit the `buyUrl` to the platform API:

POST /v1/redpackets/{code}/merchant-payment

Use this request body:

```json
{
  "instanceId": "<this user's merchant instance id>",
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
