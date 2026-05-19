---
name: pieverse-card-campaign
description: Use only from a hosted Pieverse instance when the agent needs to buy, generate, submit, fund, receive, accept, or resume a Pieverse ERC-8183 Agent Intro Card / campaign card, including requests mentioning the pieverse-card-generation-v1 service, Pieverse ERC-8183 service job, Agent Intro Card, final card image, campaign card, buy card, buy-card, `$purr erc8183 card`, or `$purr erc8183 buy-card`.
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

| Env var            | Meaning               |
| ------------------ | --------------------- |
| `WALLET_API_URL`   | Platform API base URL |
| `WALLET_API_TOKEN` | Hosted instance token |
| `INSTANCE_ID`      | Hosted instance ID    |

If a check fails, explain that the campaign must run from a hosted Pieverse
instance.

## Run

Before running, ask the user to confirm the purchase or resume action. Then run
the flow as four visible phases: submit task, charge/payment, receive
deliverable, and confirm receipt.

While running, briefly report which phase is in progress: submitting task,
charging payment, waiting for deliverable, or confirming receipt. Keep command
details and resume instructions internal.

### 1. Submit Task

Create or reuse the card purchase:

```bash
purr erc8183 card purchase
```

Read `purchaseId` from the JSON response. Then create/register the ERC-8183 job:

```bash
purr erc8183 card create-job --purchase-id <purchaseId>
```

This phase submits the campaign card task and records the on-chain job id with
the backend.

### 2. Charge / Payment

Fund the submitted task:

```bash
purr erc8183 card fund --purchase-id <purchaseId>
```

This phase sets the budget, approves the payment token when needed, funds the
job, and lets the backend/provider submit the deliverable.

### 3. Receive Deliverable

Wait for the provider deliverable:

```bash
purr erc8183 card deliverable --purchase-id <purchaseId> --wait
```

Continue only when the response status is `submitted` or `completed` and the
response includes the card fields such as `imageUrl`, `shareUrl`, and
`suggestedTweetText`.

### 4. Confirm Receipt

Accept/settle the delivered job:

```bash
purr erc8183 card accept --purchase-id <purchaseId>
```

Report success only after the final response status is `completed`.

The CLI constructs user-side transaction steps for `/wallet/execute`; the
backend/provider handles provider-side submission. If a step was already done,
rerun the same command with the same `purchaseId`; the backend and CLI should
resume from the existing state.

For rejected or expired refundable jobs, run:

```bash
purr erc8183 card refund --purchase-id <purchaseId>
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
