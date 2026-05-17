---
name: red-packet-claim
description: Use when the user wants to view pending P2P redpackets, claim all pending redpackets, claim redpackets from a specific .pie sender handle, or claim specific envelope ids through the platform redpacket API.
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

When showing senders, prefer `sender.renderedHandle`, then `sender.handle`, then
an abbreviated `sender.walletAddress`.

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

Claim by sender handle when the user says things like `claim redpackets from
machi.pie`, `claim machi.pie`, or `claim from machi`:

1. First call the pending endpoint with `senderHandle`.
2. Match by the envelope sender snapshot returned by the platform. Do not call
   `GET /v2/handles/:handle` for this flow; claims should use the sender
   recorded on each envelope, not current handle ownership.
3. Accept a rendered handle such as `machi.pie`. If the user gives a bare
   handle such as `machi`, pass it as `senderHandle=machi`; do not use bare
   names for wallet resolution and do not auto-append `.pie` for send flows.
4. If no pending envelope matches, say there are no pending redpackets from
   that sender.
5. If one or more envelopes match, claim all matching envelope ids in one call.

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpackets/pending?senderHandle=<senderHandle>" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"

curl -sS -X POST "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpackets/claim" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "envelopeIds": ["<matching-envelope-id-1>", "<matching-envelope-id-2>"]
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
