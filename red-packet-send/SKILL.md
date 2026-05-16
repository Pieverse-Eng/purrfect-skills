---
name: red-packet-send
description: Use when the user wants to send a P2P XLayer USDC redpacket to a .pie handle or raw EVM address through the platform redpacket API.
---

# Red Packet Send

Use when the user asks to send a USDC redpacket.

## Requirements

Required env:

- `WALLET_API_URL`
- `WALLET_API_TOKEN`
- `INSTANCE_ID`

Check:

```bash
test -n "${WALLET_API_URL:-}" && test -n "${WALLET_API_TOKEN:-}" && test -n "${INSTANCE_ID:-}"
```

If any are missing, ask the user to load platform wallet credentials.

## Inputs

Recipient must be one of:

- `.pie` handle, e.g. `colin.pie`
- raw EVM address, e.g. `0x2222222222222222222222222222222222222222`

Reject bare names, `@` usernames, Telegram/LINE ids, ENS, Space ID, and instance
names. Do not auto-append `.pie`.

XLayer USDC has 6 decimals:

- `0.1 USDC` -> `100000`
- `1 USDC` -> `1000000`

If the user gives base units, pass that integer string unchanged. Convert
decimal USDC exactly; do not use floating point.

## Send

If amount and recipient are clear, send directly. If either is missing, ask one
short clarification question.

```bash
curl -sS -X POST "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpackets" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "colin.pie",
    "amountBaseUnits": "100000"
  }'
```

Show `data.ackText` on success.

On failure, show `code` if present and `error` plainly. Common codes:

- `REDPACKET_INVALID_RECIPIENT`
- `REDPACKET_RECIPIENT_NOT_FOUND`
- `REDPACKET_SELF_SEND`
- `REDPACKET_INVALID_AMOUNT`
- `REDPACKET_AMOUNT_TOO_LARGE`
- `REDPACKET_INSUFFICIENT_BALANCE`
- `REDPACKET_SENDER_HANDLE_REQUIRED`
- `REDPACKET_WALLET_NOT_FOUND`
