# Red Packet Send

Use send when the user wants to send an XLayer USDT0 redpacket to a `.pie`
handle or raw EVM address. Use sent history when the user wants to review
redpackets they already sent.

## Workflow

1. Identify the recipient and amount. If either is missing, ask one short
   clarification question.
2. Reject bare names, `@` usernames, Telegram/LINE ids, ENS, Space ID, and
   instance names. Do not auto-append `.pie`.
3. Include `--channel telegram` or `--channel line` only when trusted runtime
   context clearly says the current chat channel is Telegram or LINE.
4. Run the matching send command.
5. Return `data.text` when present plus useful identifiers such as
   `envelopeId`, recipient, amount, expiry, status, or failures.

## Syntax

```bash
purr redpacket send --recipient <recipient> --amount <amount> [--channel <telegram|line>] [--raw]
purr redpacket sent [--limit <n>] [--offset <n>] [--raw]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--recipient <recipient>` | Required for `send` | `.pie` handle such as `alice.pie`, or raw EVM address such as `0x2222222222222222222222222222222222222222`. |
| `--amount <amount>` | Required for `send` | Human-readable XLayer USDT0 amount such as `0.1`, `$0.10`, or `1 USDT0`. |
| `--channel <telegram|line>` | Optional | Include only when trusted runtime context clearly says the current chat channel is Telegram or LINE. |
| `--limit <n>` | Optional for `sent` | Number of sent records to return. |
| `--offset <n>` | Optional for `sent` | Pagination offset for sent records. |
| `--raw` | Optional | Return the platform response shape for debugging. Omit for normal agent-friendly output. |

## Chat Channel Rules

Hermes may expose chat channel through `Current Session Context` or `Source`.
OpenClaw/PurrfectClaw may expose it through trusted inbound metadata such as
`channel`, `provider`, or `surface`.

Standalone agents, local shells, and agents without trusted chat-channel context
must omit `--channel`. Never infer the channel from casual user text.

## Commands

```bash
purr redpacket send --recipient alice.pie --amount 0.1
purr redpacket send --recipient 0x2222222222222222222222222222222222222222 --amount 1
purr redpacket send --recipient alice.pie --amount 0.1 --channel telegram
purr redpacket sent --limit 20 --offset 0
```

## Response Shape

Success prints one JSON object to stdout. Default output is agent-friendly JSON:

```json
{
  "ok": true,
  "data": {
    "text": "Sent 0.1 USDT0 redpacket to alice.pie. Expires in 24h.",
    "envelopeId": "uuid",
    "amount": "0.1",
    "symbol": "USDT0",
    "recipient": "alice.pie",
    "recipientWalletAddress": "0x...",
    "expiresAt": "2026-..."
  }
}
```

Sent history returns `data.sent[]` with status, recipient, amount, expiry, and
claim transaction fields when available.

## Response Errors

On errors, show `code` and `error` plainly. For insufficient sender balance, the
CLI includes the XLayer USDT0 deposit hint when available.

| Error Code / Message | Meaning |
| --- | --- |
| `REDPACKET_INVALID_RECIPIENT` | Recipient is not a valid `.pie` handle or raw EVM address. |
| `REDPACKET_RECIPIENT_NOT_FOUND` | The `.pie` handle could not be resolved. |
| `REDPACKET_SELF_SEND` | Sender and recipient resolve to the same wallet. |
| `REDPACKET_INVALID_AMOUNT` | Amount is invalid or non-positive. |
| `REDPACKET_AMOUNT_TOO_LARGE` | Amount exceeds the configured redpacket limit. |
| `REDPACKET_INSUFFICIENT_BALANCE` | Sender lacks enough XLayer USDT0. Use the included deposit hint. |
| Missing credential/config error | Hosted runtime or platform wallet credentials are not loaded. |
