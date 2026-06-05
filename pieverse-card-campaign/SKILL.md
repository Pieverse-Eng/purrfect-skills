---
name: pieverse-card-campaign
description: Use when the user asks to forge or generate a Pieverse/Purrfect Claw agent intro card for the BNB ERC-8183 campaign, Pieverse x BNB partner campaign, BNB Chain Agent Intro Card, or pieverse-card-generation-v1, and return the final on-chain image link and share text.
---

# Pieverse Card Campaign

Use this skill inside a hosted instance to generate the Pieverse BNB Chain
ERC-8183 campaign card through the staged `purr pieverse card` on-chain flow on
BNB Smart Chain mainnet (chain ID 56).

## Parameters

- `partner`: always use `bnb` for this campaign.
- `channel`: infer from the current session context. Use `telegram` for Telegram
  and `line` for LINE.
- `lv`: use `lv1`.
- `pieName`: optional. If provided, it must match the hosted wallet's claimed
  `.pie` handle. If omitted, the backend uses the hosted wallet's claimed `.pie`
  handle.
- `purchaseId`: use only when resuming an existing staged flow.

## Run

Determine the routing parameters before creating a purchase:

- `partner`: `bnb`.
- `channel`: `telegram` or `line`, inferred from the current session context.
- `lv`: `lv1`.

Run the full staged flow in order. Do not stop after `purchase`.

### 1. Purchase Intent

Create or reuse the BNB card purchase intent:

```bash
purr pieverse card purchase --partner bnb --channel <telegram-or-line>
```

The CLI purchase command does not require `pieName` or `lv`; the backend uses
`lv1` and the hosted wallet's claimed `.pie` handle. If the user explicitly
provided `pieName`, use the purchase API reference below to create the purchase
intent with that `pieName`, then continue the same staged flow with the returned
`purchaseId`.

Read `purchaseId` from the JSON response. The purchase response is not final,
even if it contains image or share fields. Never return the purchase response to
the user as a successful card generation.

Purchase API reference for debugging only. This curl example creates or reuses
the purchase intent, but it is not the complete success path; after it returns,
continue with `create-job`, `fund`, and `deliverable --wait`. Omit the
`pieName` field when the user did not explicitly provide it.

```bash
curl -sS -X POST "$WALLET_API_URL/v1/instances/$INSTANCE_ID/erc8183/services/agent-self-intro/card/purchase" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "partner": "bnb",
    "channel": "<telegram-or-line>",
    "lv": "lv1",
    "pieName": "<optional-pie-name>"
  }'
```

### 2. Create On-Chain Job

Create and register the ERC-8183 service job:

```bash
purr pieverse card create-job --purchase-id <purchaseId>
```

This step must perform the on-chain job creation/register operation before the
card can be funded.

### 3. Fund On-Chain Job

Fund the registered job:

```bash
purr pieverse card fund --purchase-id <purchaseId>
```

This step must perform the BNB Chain payment flow, including the required `$U`
payment token approval/funding and BNB gas.

### 4. Wait For Deliverable

Wait for the provider to submit the final card deliverable:

```bash
purr pieverse card deliverable --purchase-id <purchaseId> --wait
```

The flow succeeds only when the final `deliverable` response status is
`submitted` or `completed`, includes `imageUrl`, `shareUrl`, and
`suggestedTweetText`, and includes both `erc8183.txHashes.fund` and
`erc8183.txHashes.submit`.

Keep command details, raw statuses, purchase ids, card ids, job ids, and tx
hashes internal unless needed to explain a failure.

Each command is resumable with the same `purchaseId`. If a command reports
existing progress, continue with the next command in sequence instead of
starting a new purchase.

For rejected or expired refundable jobs, run:

```bash
purr pieverse card refund --purchase-id <purchaseId>
```

Use refund only for rejected or expired refundable jobs.

## Output

Parse the final `deliverable` command JSON response internally. On success,
return this chat message:

```text
Pieverse campaign card

[Open image](<imageUrl>)

[Share to X](<xIntentUrl>)
```

For the final success reply, use only the output template above.

Build or verify `xIntentUrl` from `suggestedTweetText`:

```text
https://x.com/intent/tweet?text=<encodeURIComponent(suggestedTweetText)>
```

Put `suggestedTweetText` only inside the `Share to X` link as the encoded `text`
parameter. Do not add `&via=` or other intent params.
`Share to X` opens the X composer with `suggestedTweetText`.
Render `imageUrl` as a clickable Markdown link: `[Open image](<imageUrl>)`.
Do not output the raw image URL as a standalone line.

Relevant final successful `deliverable` output fields:

```json
{
  "purchaseId": "...",
  "status": "submitted",
  "imageUrl": "https://...",
  "shareUrl": "https://...",
  "suggestedTweetText": "...",
  "erc8183": {
    "onChainJobId": "...",
    "txHashes": {
      "fund": "...",
      "submit": "..."
    }
  }
}
```

## Errors

Summarize errors in plain language without mentioning commands. Match backend
`code` values or command error text internally, then use the user-facing
response below. Preserve `purchaseId`, `rejectTxHash`, and `refundTxHash` when
they are available.

| Internal match | User-facing response |
| -------------- | -------------------- |
| Missing hosted env, `INSTANCE_TOKEN_REQUIRED`, `AGENT_SELF_INTRO_HOSTED_INSTANCE_REQUIRED` | Explain that hosted Pieverse instance wallet access is required. |
| `AGENT_SELF_INTRO_DISABLED` | Say the campaign is currently unavailable. |
| `AGENT_SELF_INTRO_HANDLE_REQUIRED` | Ask the user to claim a `.pie` handle before generating the card. |
| Preparing/not found/missing job fields/provider timeout/tx not confirmed/RPC read failure | Say the card is still being prepared or confirmed; keep waiting or resume internally. |
| Transaction failed/reverted/wallet execution failed/insufficient funds/insufficient allowance/gas failure | Say the BNB Chain payment step failed; ask the user to ensure the hosted wallet has enough BNB for gas and enough `$U`, then resume internally. |
| `ERC8183_PROGRESS_TX_MISMATCH`, `JobCreated`/`JobRegistered` event mismatch, transaction target mismatch | Say the on-chain proof did not match the purchase and stop. |
| `ERC8183_PROGRESS_MISSING_FIELD`, `ERC8183_PROGRESS_BACKWARDS`, `ERC8183_PROGRESS_STATUS_UNSUPPORTED` | Say the purchase progress could not be updated because the current state is inconsistent. |
| Missing `erc8183.txHashes.fund` or `erc8183.txHashes.submit` in final deliverable response | Say the on-chain proof is incomplete and keep waiting or resume internally. |
| Missing `imageUrl`, `shareUrl`, or `suggestedTweetText` in final deliverable response | Say the card response is incomplete and keep waiting or resume internally. |
| Deliverable not ready, purchase/job not ready on-chain | Say the card is not ready yet and continue waiting/resuming internally. |
| Purchase already terminal | Return the existing card when final card fields and required tx hashes are present; otherwise say the purchase is already finished. |
| Rejected/expired/not refundable/failed | State the terminal or refund status and preserve tx hashes when present. |
| Other non-OK response | Say the card could not be generated right now and ask the user to try again. |

The purchase is idempotent within the campaign window; repeated internal attempts
should resume or return the existing purchase.
