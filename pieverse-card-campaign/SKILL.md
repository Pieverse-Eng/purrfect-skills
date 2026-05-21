---
name: pieverse-card-campaign
description: Use when the user asks to forge or generate a Pieverse/Purrfect Claw agent intro card for the BNB ERC-8183 campaign, Pieverse x BNB partner campaign, OKX onboarding campaign, or Pieverse x OKX partner campaign, and return the image link and share text.
---

# Pieverse Card Campaign

Use this skill inside a hosted instance to generate the Pieverse campaign card
directly through the platform API.

## Run

Determine the routing parameters:

- `channel`: infer from the current session context or campaign prompt. Use
  `telegram` for Telegram and `line` for LINE.
- `partner`: infer from the campaign prompt/card request text. Use `bnb` when
  the prompt says BNB ERC-8183 campaign, Pieverse x BNB, BNB partner campaign,
  BNB Chain, BSC, or Binance. Use `okx` when the prompt says OKX onboarding
  campaign, Pieverse x OKX, OKX partner campaign, or OKX.
- `lv`: use `lv1`.

Call the platform endpoint directly:

```bash
curl -sS -X POST "$WALLET_API_URL/v1/instances/$INSTANCE_ID/erc8183/services/agent-self-intro/card/purchase" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "partner": "<okx-or-bnb>",
    "channel": "<telegram-or-line>",
    "lv": "lv1"
  }'
```

The flow succeeds when the response includes `imageUrl`, `shareUrl`, and
`suggestedTweetText`. Keep command details, raw statuses, purchase ids, and card
ids internal.

## Output

Parse the API response internally. On success, return this chat message:

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

Relevant successful output fields:

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
| Other non-OK response | Say the card could not be generated right now and ask the user to try again. |

The purchase is idempotent within the campaign window; repeated internal attempts
should resume or return the existing purchase.
