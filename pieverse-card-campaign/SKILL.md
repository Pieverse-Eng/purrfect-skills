---
name: pieverse-card-campaign
description: Use when the user asks to forge or generate a Pieverse/Purrfect Claw agent intro card for the BNB ERC-8183 campaign, Pieverse x BNB partner campaign, BNB Chain Agent Intro Card, or pieverse-card-generation-v1, and return the image link and share text.
---

# Pieverse Card Campaign

Use this skill inside a hosted instance to generate the Pieverse BNB Chain
ERC-8183 campaign card through the staged `purr pieverse card` on-chain flow.

## Parameters

- `partner`: always use `bnb` for this campaign.
- `channel`: infer from the current session context. Use `telegram` for Telegram
  and `line` for LINE.
- `lv`: use `lv1`.
- `pieName`: optional. If provided, it must match the hosted wallet's claimed
  `.pie` handle.
- `purchaseId`: use the returned purchase id when resuming `create-job`, `fund`,
  or `deliverable`.

## Run

Start or resume the BNB-only card purchase:

```bash
purr pieverse card purchase --partner bnb --channel <telegram-or-line>
```

Equivalent purchase API example. Use this curl path when a user supplies
`pieName`; omit the `pieName` field when it is not provided.

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

Then run the ERC-8183 on-chain steps on BNB Smart Chain mainnet (chain ID 56):

```bash
purr pieverse card create-job --purchase-id <purchaseId>
purr pieverse card fund --purchase-id <purchaseId>
purr pieverse card deliverable --purchase-id <purchaseId> --wait
```

The flow succeeds when the deliverable response status is `submitted` or
`completed` and includes `imageUrl`, `shareUrl`, and `suggestedTweetText`. Keep
command details, raw statuses, purchase ids, and card ids internal.

## Output

Parse command/API responses internally. On success, return this chat message:

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

Relevant successful output fields. `purr` may print these fields at the top
level; curl returns them under `data`.

```json
{
  "ok": true,
  "data": {
    "purchaseId": "...",
    "imageUrl": "https://...",
    "shareUrl": "https://...",
    "suggestedTweetText": "..."
  }
}
```

## Errors

Summarize errors in plain language without mentioning commands. Match backend
`code` values or response text internally, then use the user-facing response
below.

| Internal match | User-facing response |
| -------------- | -------------------- |
| Missing hosted env, `INSTANCE_TOKEN_REQUIRED`, `AGENT_SELF_INTRO_HOSTED_INSTANCE_REQUIRED` | Explain that hosted Pieverse instance wallet access is required. |
| `AGENT_SELF_INTRO_DISABLED` | Say the campaign is currently unavailable. |
| `AGENT_SELF_INTRO_HANDLE_REQUIRED` | Ask the user to claim a `.pie` handle before generating the card. |
| Missing `imageUrl`, `shareUrl`, or `suggestedTweetText` | Say the card response is incomplete and ask the user to try again shortly. |
| On-chain payment/funding failure, insufficient balance, gas failure | Say the BNB Chain payment step could not be completed and ask the user to retry after funding the hosted wallet. |
| Other non-OK response | Say the card could not be generated right now and ask the user to try again. |

The purchase is idempotent within the campaign window; repeated internal attempts
should resume or return the existing purchase.
