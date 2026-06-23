# Red Packet Claim

Use pending lookup when the user asks what redpackets are claimable. Use claim
when the user asks to receive pending redpackets.

## Workflow

1. If the user asks what is claimable, run pending lookup.
2. If the user asks to claim without specifying a sender or envelope ids, claim
   all pending redpackets.
3. If the user specifies a sender, use `--sender`. This may be a bare handle or
   rendered `.pie` handle.
4. If the user explicitly names envelope ids, use `--envelope-ids`.
5. Do not combine `--sender` and `--envelope-ids`.
6. Return `data.text` when present plus useful identifiers such as `envelopeId`,
   `txHash`, sender, amount, expiry, status, or failures.

## Syntax

```bash
purr redpacket pending [--sender <handle-or-handle.pie>] [--raw]
purr redpacket claim [--sender <handle-or-handle.pie>] [--envelope-ids <id1,id2>] [--raw]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--sender <handle-or-handle.pie>` | Optional | Filters pending or claimable redpackets by recorded sender. May be a bare handle or rendered `.pie` handle. |
| `--envelope-ids <id1,id2>` | Optional | Claims only explicitly named envelope ids. Do not combine with `--sender`. |
| `--raw` | Optional | Return the platform response shape for debugging. Omit for normal agent-friendly output. |

For sender-filtered claims, bare handles are only for filtering recorded envelope
senders. Do not use bare names for send recipients.

## Commands

```bash
purr redpacket pending
purr redpacket pending --sender bob.pie
purr redpacket claim
purr redpacket claim --sender bob.pie
purr redpacket claim --envelope-ids 11111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222
```

## Response Shape

Success prints one JSON object to stdout. Default output is agent-friendly JSON:

```json
{
  "ok": true,
  "data": {
    "text": "Claimed 1 redpacket totalling 0.1 USDT0 from bob.pie.",
    "claimedCount": 1,
    "failedCount": 0,
    "claimed": [
      {
        "envelopeId": "uuid",
        "txHash": "0x...",
        "amount": "0.1",
        "symbol": "USDT0",
        "sender": "bob.pie",
        "senderWalletAddress": "0x..."
      }
    ],
    "failed": []
  }
}
```

Pending lookup returns `data.pending[]` with sender, amount, envelope id, and
expiry. If no pending redpackets exist, return that plainly.

## Response Errors

On errors, show `code` and `error` plainly. Treat empty claims and double-claim
no-op results as normal, not scary failures.

| Error Code / Message | Meaning |
| --- | --- |
| `REDPACKET_WALLET_NOT_FOUND` | The recipient wallet has not been created yet. |
| `REDPACKET_INVALID_SENDER_HANDLE` | Sender filter is not a valid handle. |
| Missing credential/config error | Hosted runtime or platform wallet credentials are not loaded. |
