---
name: pieverse-card-campaign
description: Use when the agent needs to buy, generate, fund, submit, receive, refund, or resume a Pieverse Agent Intro Card / campaign card through the staged card flow, including requests mentioning the pieverse-card-generation-v1 service, Pieverse service job, Agent Intro Card, final card image, campaign card, buy card, or buy-card.
---

# Pieverse Card Campaign

Use this skill inside a hosted instance to buy, generate, or resume the Pieverse
campaign card.

## Run

Before running, ask the user to confirm the purchase or resume action once. After
confirmation, run the full flow end-to-end without asking again unless a
terminal error requires user action. Treat the flow as three visible phases:
submit task, charge/payment, and receive deliverable.

While running, briefly report which phase is in progress: submitting task,
charging payment, or waiting for deliverable. Keep command details, raw
statuses, purchase ids, job ids, tx hashes, and resume instructions internal.

The campaign card flow succeeds when the deliverable response includes the card
links and share text.

### 0. Preflight

Before creating the purchase, determine the campaign routing parameters:

- `channel`: inspect the system prompt or runtime context for the current chat
  platform. If the current chat is Telegram, use `telegram`; otherwise use
  `line`. Do not infer `channel` from the user's campaign wording.
- `partner`: infer from the user's request. Use `bnb` when the request says BNB
  ERC-8183 campaign, Pieverse x BNB, BNB partner campaign, BNB Chain, BSC, or
  Binance. Use `okx` when the request says OKX onboarding campaign, Pieverse x
  OKX, OKX partner campaign, or OKX. If the user mentions both or the partner is
  not clear, ask one concise clarification before creating the purchase.

Do this preflight before the first `purchase` command. Do not create a default
purchase first and then try to change `partner` or `channel`; the purchase is
idempotent by campaign variant.

### 1. Submit Task

Create or reuse the card purchase:

```bash
purr pieverse card purchase --partner <okx|bnb> --channel <telegram|line>
```

Read `purchaseId` from the JSON response. Then create/register the service job:

```bash
purr pieverse card create-job --purchase-id <purchaseId>
```

This phase submits the campaign card task and records the job id with the
backend.

### 2. Charge / Payment

Fund the task:

```bash
purr pieverse card fund --purchase-id <purchaseId>
```

This phase records payment progress, then lets the backend/provider submit the
deliverable.

### 3. Receive Deliverable

Wait for the provider deliverable:

```bash
purr pieverse card deliverable --purchase-id <purchaseId> --wait
```

Continue only when the response includes the card fields such as `imageUrl`,
`shareUrl`, and `suggestedTweetText`.

When `deliverable --wait` returns with the card fields present, stop the
campaign card flow and report success.

Each command is resumable with the same `purchaseId`. If a command reports
existing progress, continue with the next command in sequence instead of
starting a new purchase.

For rejected or expired refundable jobs, run:

```bash
purr pieverse card refund --purchase-id <purchaseId>
```

Use refund only for rejected or expired refundable jobs.

## Output

Parse the final command JSON response internally. On success, return this chat
message:

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
  "purchaseId": "...",
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
| Transaction failed/reverted/wallet execution failed/insufficient funds/insufficient allowance | Say the on-chain payment step failed; ask the user to ensure the hosted wallet has enough funds and gas, then resume internally. |
| `ERC8183_PROGRESS_TX_MISMATCH`, `JobCreated`/`JobRegistered` event mismatch, transaction target mismatch | Say the on-chain proof did not match the purchase and stop. |
| `ERC8183_PROGRESS_MISSING_FIELD`, `ERC8183_PROGRESS_BACKWARDS`, `ERC8183_PROGRESS_STATUS_UNSUPPORTED` | Say the purchase progress could not be updated because the current state is inconsistent. |
| Deliverable not ready, purchase/job not ready on-chain | Say the card is not ready yet and continue waiting/resuming internally. |
| Purchase already terminal | Return the existing card when fields are present; otherwise say the purchase is already finished. |
| Rejected/expired/not refundable/failed | State the terminal or refund status and preserve tx hashes when present. |

The purchase is idempotent within the campaign window; repeated internal attempts
should resume or return the existing purchase.
