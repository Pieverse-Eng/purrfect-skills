---
name: red-packet-claim
description: Use when the user wants to view pending P2P redpackets, claim all pending redpackets, or claim specific envelope ids through the platform redpacket API.
---

# Red Packet Claim

Use when the user asks to claim redpackets or check pending redpackets.

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

## Preview

Use when the user asks what is claimable:

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpackets/pending" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Show sender, expiry, envelope id, and amount in `token.symbol`. Display
`amountBaseUnits` in token units using `token.decimals`; do not show the raw
base-unit integer as the amount. If `data.pending` is empty, say there are no
pending redpackets.

## Claim

Claim all pending redpackets:

```bash
curl -sS -X POST "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpackets/claim" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Claim selected envelope ids only if the user names them:

```bash
curl -sS -X POST "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpackets/claim" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "envelopeIds": ["<envelopeId>"]
  }'
```

For claim responses:

- If `data.ackText` exists, show it directly.
- If `data.failed[]` is non-empty, also list failed envelope ids and errors,
  then suggest retrying later.
- If `data.claimed[]` and `data.failed[]` are empty, say there are no pending
  redpackets.
- Treat double-claim/no-op results as normal, not scary failures.

On failure, show `code` if present and `error` plainly. Common code:

- `REDPACKET_WALLET_NOT_FOUND`
