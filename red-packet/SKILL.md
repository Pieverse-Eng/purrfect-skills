---
name: red-packet
description: Use when a hosted Purr-Fect Claw user agent is asked to claim or prepare a red packet, including creating an OKX x402 merchant order and submitting the resulting buyUrl to the Pieverse app backend.
metadata:
  hermes:
    related_skills:
      - purrfect-merchant-skill
---

# Red Packet

Use this skill inside a hosted user pod when the user asks to claim a red
packet through their agent/merchant skill.

## Requirements

Use the sibling `purrfect-merchant-skill` to create and inspect merchant
orders.

Use the user's existing app auth context/token if available in the host. If no
app auth is available, stop and ask the user to open the red packet page once so
the app can authenticate the claim.

## OKX x402 Workflow

1. Identify the red packet code and amount. Use the campaign amount in base
   units. Through `purrfect-merchant-skill`, call `purrfect_order_create` with:

```json
{
  "amount_base_units": "<campaign amount base units>",
  "paymentMethod": "okx-x402"
}
```

2. Read the returned `buyUrl`.

3. Submit the `buyUrl` to the app backend:

POST /api/redpackets/{code}/merchant-payment

Use this request body:

```json
{
  "instanceId": "<this user's app instance id>",
  "buyUrl": "<merchant buyUrl>",
  "orderCode": "<merchant order code>"
}
```

4. The app backend pays the URL with the campaign funder wallet through platform
   OKX x402 support, updates the red packet claim, and returns the tx hash.

## Safety Rules

- Do not ask the funder wallet to transfer directly for the OKX flow.
- Do not create a second order after submitting one unless the app backend
  reports the claim did not complete.
- If the merchant order amount does not equal the red packet claim amount, cancel
  and recreate the order before submitting.
