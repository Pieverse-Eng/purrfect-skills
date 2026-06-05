---
name: pieverse-card-campaign
description: Use when the agent needs to buy, generate, submit, fund, receive, refund, or resume a Pieverse Agent Intro Card for the BNB Chain ERC-8183 campaign through the staged on-chain card flow, including requests mentioning pieverse-card-generation-v1, BNB 8183, Pieverse x BNB, Agent Intro Card, final card image, campaign card, buy card, or buy-card.
---

# Pieverse BNB ERC-8183 Card Campaign

Use this skill inside a hosted instance to buy, generate, or resume the Pieverse
Agent Intro Card for the BNB Chain ERC-8183 campaign. This skill is BNB-only:
do not infer a partner, and do not call the platform card purchase endpoint
directly.

The card service is `pieverse-card-generation-v1`. The on-chain campaign runs on
BNB Smart Chain mainnet (chain ID 56).

## Before Running

If the request would create or fund an ERC-8183 job, ask the user to confirm once
before starting the flow. Explain that the hosted instance will create the
service job, fund it on BNB Chain, and wait for the provider-submitted card
deliverable.

Do not ask for confirmation again when resuming an existing `purchaseId` unless
the user asks to start over.

## Run

Always use the staged hosted-instance CLI flow:

```bash
purr pieverse card purchase
```

Read the returned `purchaseId`, then create the ERC-8183 job:

```bash
purr pieverse card create-job --purchase-id <purchaseId>
```

Fund the job on BNB Chain:

```bash
purr pieverse card fund --purchase-id <purchaseId>
```

Wait for the provider-submitted deliverable:

```bash
purr pieverse card deliverable --purchase-id <purchaseId> --wait
```

The flow succeeds when the deliverable response includes card fields and status
is `submitted` or `completed`.

The flow is resumable. If any step returns an existing `purchaseId`, continue
from the latest status instead of creating a new purchase.

## Output

Parse command responses internally. On success, return only this chat message:

```text
Pieverse BNB Agent Intro Card

[Open image](<imageUrl>)

[Share to X](<xIntentUrl>)

[Open card](<shareUrl>)
```

Build or verify `xIntentUrl` from `suggestedTweetText`:

```text
https://x.com/intent/tweet?text=<encodeURIComponent(suggestedTweetText)>
```

Put `suggestedTweetText` only inside the `Share to X` link as the encoded `text`
parameter. Do not add `&via=` or other intent params. Do not output raw URLs as
standalone lines.

Relevant successful output fields:

```json
{
  "purchaseId": "...",
  "cardId": "...",
  "imageUrl": "https://...",
  "shareUrl": "https://...",
  "suggestedTweetText": "...",
  "erc8183": {
    "chainId": 56,
    "onChainJobId": "...",
    "txHashes": {
      "create": "0x...",
      "fund": "0x...",
      "complete": "0x..."
    }
  }
}
```

## Errors

Summarize errors in plain language without mentioning commands.

| Internal match | User-facing response |
| -------------- | -------------------- |
| Missing hosted env, `INSTANCE_TOKEN_REQUIRED`, `AGENT_SELF_INTRO_HOSTED_INSTANCE_REQUIRED` | Explain that hosted Pieverse instance wallet access is required. |
| `AGENT_SELF_INTRO_DISABLED` | Say the BNB ERC-8183 card campaign is currently unavailable. |
| `AGENT_SELF_INTRO_HANDLE_REQUIRED` | Ask the user to claim a `.pie` handle before generating the card. |
| Missing `imageUrl`, `shareUrl`, or `suggestedTweetText` | Say the card response is incomplete and ask the user to try again shortly. |
| On-chain payment/funding failure, insufficient balance, gas failure | Say the BNB Chain payment step could not be completed and ask the user to retry after funding the hosted wallet. |
| On-chain job/proof/receipt mismatch | Say the on-chain job state could not be verified and ask the user to retry the resume flow. |
| Other non-OK response | Say the card could not be generated right now and ask the user to try again. |

The purchase is idempotent within the campaign window; repeated attempts should
resume or return the existing purchase.
