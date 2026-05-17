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

## Sender Channel Hint

Include `senderChatContext` only when the runtime exposes a reliable current
message channel and the value is exactly `telegram` or `line`.

For OpenClaw, use the current message/runtime channel context if it is exposed
to skill execution. Do not assume a fixed env var name for this.

Do not infer the current channel from the recipient, installed integrations,
user text, or available channel bindings. If the current channel is unknown or
ambiguous, omit `senderChatContext` entirely.

Never include chat ids, user ids, room ids, or LINE user ids. The platform
resolves sender notification targets from its DB channel bindings.

## Send

If amount and recipient are clear, send directly. If either is missing, ask one
short clarification question.

When no reliable current channel is available:

```bash
curl -sS -X POST "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpackets" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "<recipient>",
    "amountBaseUnits": "<amountBaseUnits>"
  }'
```

When the runtime reliably reports the current channel as `telegram` or `line`,
include only that channel hint:

```bash
curl -sS -X POST "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpackets" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "<recipient>",
    "amountBaseUnits": "<amountBaseUnits>",
    "senderChatContext": {
      "channel": "<telegram-or-line>"
    }
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
