---
name: pieverse-card-campaign
description: Use only from a hosted Pieverse instance when the agent needs to buy, generate, or resume the Pieverse ERC-8183 campaign card, including requests like Pieverse card campaign, campaign card, buy card, buy-card, or `$purr erc8183 buy-card`.
---

# Pieverse Card Campaign

Use this skill inside a hosted instance to buy, generate, or resume the Pieverse
ERC-8183 campaign card.

## Requirements

Check the hosted instance environment:

```bash
test -n "${WALLET_API_URL:-}" && test -n "${WALLET_API_TOKEN:-}" && test -n "${INSTANCE_ID:-}"
case "${WALLET_API_URL:-}" in
  *".svc.cluster.local"*) ;;
  *) echo "not_hosted_instance"; exit 1 ;;
esac
```

Required env vars:

| Env var | Meaning |
|---|---|
| `WALLET_API_URL` | Platform API base URL |
| `WALLET_API_TOKEN` | Hosted instance token |
| `INSTANCE_ID` | Hosted instance ID |

If a check fails, explain that the campaign must run from a hosted Pieverse
instance.

## Run

Before running, ask the user to confirm the purchase or resume action. After
confirmation, run:

```bash
purr erc8183 buy-card
```

The CLI handles the user-side flow:

1. Create or reuse the card purchase.
2. Create the ERC-8183 job through `/wallet/execute`.
3. Recover `onChainJobId` from the create transaction receipt.
4. Set budget, approve the payment token when needed, and fund the job.
5. Record progress with the platform backend.
6. Wait for provider submission.
7. Complete the job as evaluator.
8. Claim refund when rejected or expired and refundable.

The CLI constructs user-side transaction steps for `/wallet/execute`.
Backend/provider side handles provider submission.

## Output

Parse the CLI JSON response. On success, return a concise chat message with:

- Card image from `imageUrl` using Markdown image syntax.
- Suggested tweet text from `suggestedTweetText`.
- X Web Intent URL from `xIntentUrl`.
- Share URL from `shareUrl`.

Relevant successful output fields:

```json
{
  "purchaseId": "...",
  "status": "completed",
  "imageUrl": "https://...",
  "shareUrl": "https://...",
  "suggestedTweetText": "...",
  "xIntentUrl": "https://x.com/intent/tweet?text=...",
  "erc8183": {
    "onChainJobId": "..."
  }
}
```

## Errors

Summarize the CLI error in plain language. Preserve `purchaseId`,
`rejectTxHash`, and `refundTxHash` when the CLI includes them.

| Case | Response |
|---|---|
| Missing hosted env | Explain that hosted instance wallet access is required. |
| Missing `.pie` handle | Ask the user to claim a `.pie` handle before buying the card. |
| Insufficient funds | Explain which wallet asset or chain needs funds when named by the CLI. |
| Rejected | Say the ERC-8183 job was rejected and show any reject or refund tx hash. |
| Expired | Say the ERC-8183 job expired and show any refund tx hash. |
| Failed | Say the purchase failed and include the purchase ID when present. |
| Provider timeout | Tell the user they can run `purr erc8183 buy-card` again to resume. |

The purchase is idempotent within the reward window; repeated runs should resume
or return the existing purchase.

## Staging Check

For staging validation, run the same command from a hosted staging or canary
instance:

```bash
purr erc8183 buy-card
```

Pass criteria:

- command exits successfully
- status is `completed`
- output includes `imageUrl`, `shareUrl`, and `xIntentUrl`
- chat response shows the image and share URL
- no-handle, no-funds, expired, and rejected cases are summarized cleanly
