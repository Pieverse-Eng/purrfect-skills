---
name: pieverse-card-campaign
description: Use when the agent needs to buy, generate, submit, fund, receive, accept, refund, or resume a Pieverse Agent Intro Card / campaign card through the staged card flow, including requests mentioning the pieverse-card-generation-v1 service, Pieverse service job, Agent Intro Card, final card image, campaign card, buy card, or buy-card.
---

# Pieverse Card Campaign

Use this skill inside a hosted instance to buy, generate, or resume the Pieverse
campaign card.

## Run

Before running, ask the user to confirm the purchase or resume action once. After
confirmation, run the full flow end-to-end without asking again unless a
terminal error requires user action. Treat the flow as four visible phases:
submit task, charge/payment, receive deliverable, and confirm receipt.

While running, briefly report which phase is in progress: submitting task,
charging payment, waiting for deliverable, or confirming receipt. Keep command
details, raw statuses, purchase ids, job ids, tx hashes, and resume instructions
internal.

### 1. Submit Task

Create or reuse the card purchase:

```bash
purr pieverse card purchase
```

Read `purchaseId` from the JSON response. Then create/register the service job:

```bash
purr pieverse card create-job --purchase-id <purchaseId>
```

This phase submits the campaign card task and records the job id with the
backend.

### 2. Charge / Payment

Fund the submitted task:

```bash
purr pieverse card fund --purchase-id <purchaseId>
```

This phase records the budget, approval, and funding progress, then lets the
backend/provider submit the deliverable.

### 3. Receive Deliverable

Wait for the provider deliverable:

```bash
purr pieverse card deliverable --purchase-id <purchaseId> --wait
```

Continue only when the response status is `submitted` or `completed` and the
response includes the card fields such as `imageUrl`, `shareUrl`, and
`suggestedTweetText`.

For this flow, `submitted` means the provider deliverable is ready. When
`deliverable --wait` returns `submitted` with the card fields present,
immediately proceed to confirm receipt; do not keep polling for `completed`
before running accept.

### 4. Confirm Receipt

Accept/settle the delivered job:

```bash
purr pieverse card accept --purchase-id <purchaseId>
```

Report success only after the final response status is `completed`.

The CLI constructs user-side transaction steps for `/wallet/execute`; the
backend/provider handles provider-side submission. If a step was already done,
rerun the same command with the same `purchaseId`; the backend and CLI should
resume from the existing state.

For rejected or expired refundable jobs, run:

```bash
purr pieverse card refund --purchase-id <purchaseId>
```

## Output

Parse the final command JSON response internally. On success, return this chat
message:

```text
Pieverse campaign card

[Open image](<imageUrl>)

[Share to X](<xIntentUrl>)
[Open card](<shareUrl>)
```

For the final success reply, use only the output template above.

Build or verify `xIntentUrl` from `suggestedTweetText`:

```text
https://x.com/intent/tweet?text=<encodeURIComponent(suggestedTweetText)>
```

Put `suggestedTweetText` only inside the `Share to X` link as the encoded `text`
parameter. Do not add `&via=` or other intent params.
`Share to X` opens the X composer with `suggestedTweetText`; `Open card` opens the
campaign card page.
Render `imageUrl` as a clickable Markdown link: `[Open image](<imageUrl>)`.
Do not output the raw image URL as a standalone line.

Relevant successful output fields:

```json
{
  "purchaseId": "...",
  "status": "completed",
  "imageUrl": "https://...",
  "shareUrl": "https://...",
  "suggestedTweetText": "...",
  "erc8183": {
    "onChainJobId": "...",
    "txHashes": {
      "fund": "...",
      "complete": "..."
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
| Transaction failed/reverted/wallet execution failed/insufficient funds | Say the on-chain payment step failed; mention the asset or chain needing funds when the error names one. |
| `ERC8183_PROGRESS_TX_MISMATCH`, `JobCreated`/`JobRegistered` event mismatch, transaction target mismatch | Say the on-chain proof did not match the purchase and stop. |
| `ERC8183_PROGRESS_MISSING_FIELD`, `ERC8183_PROGRESS_BACKWARDS`, `ERC8183_PROGRESS_STATUS_UNSUPPORTED` | Say the purchase progress could not be updated because the current state is inconsistent. |
| Purchase not submitted, job not submitted on-chain, accept attempted too early | Say the deliverable is not ready yet and continue waiting/resuming internally. |
| Purchase already completed/terminal | Return the existing completed card when fields are present; otherwise say the purchase is already finished. |
| Rejected/expired/not refundable/failed | State the terminal or refund status and preserve tx hashes when present. |

The purchase is idempotent within the reward window; repeated internal attempts
should resume or return the existing purchase.
