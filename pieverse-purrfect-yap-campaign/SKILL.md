---
name: pieverse-purrfect-yap-campaign
description: Use when the user asks to judge, check, or calculate PurrfectYap / Yap Score posts for the Pieverse x BNB Survivor Quest campaign through the ERC-8183 social-meme-booster-judge job.
---

# Pieverse PurrfectYap Campaign

Use this skill inside a hosted Pieverse instance to create, fund, and wait for
the BNB Survivor Quest PurrfectYap judge job through the staged
`purr pieverse purrfect-yap` ERC-8183 flow on BNB Smart Chain mainnet
(chain ID 56).

This skill creates a paid scoring job. The provider judges eligible campaign X
posts and submits the score to the campaign score system. The current ERC-8183
purchase result does not directly return a Yap Score field; when the final
response only contains job status, deliverable URI, and transaction hashes,
report the completed job without quoting a score.

## Parameters

- `purchaseId`: used when resuming an existing staged flow.
- Campaign, channel, partner, and `.pie` handle are selected by the platform.
- The user should already have joined the BNB Survivor Quest campaign, claimed a
  `.pie` handle, and posted eligible PurrfectYap content on X.

## Run

Run the staged flow in order. Continue after `purchase` and inspect the judge
input before spending on-chain gas and payment.

### 1. Purchase Intent

Create a PurrfectYap judge purchase intent:

```bash
purr pieverse purrfect-yap purchase
```

Read `purchaseId`, `campaignSlug`, `campaignDay`, and `pieName` from the JSON
response. The purchase response is not final.

### 2. Inspect Judge Input

Before creating or funding the on-chain job, inspect the provider input:

```bash
purr pieverse purrfect-yap input --purchase-id <purchaseId>
```

Continue when `posts` contains at least one eligible post. If `posts` is empty,
pause before on-chain job creation/funding. Tell the user that no eligible
PurrfectYap posts have been discovered for the campaign yet, and resume later
with the same `purchaseId` once the campaign crawler/provider has ingested the
post.

### 3. Create On-Chain Job

Create and register the ERC-8183 service job:

```bash
purr pieverse purrfect-yap create-job --purchase-id <purchaseId>
```

This step must perform the on-chain job creation/register operation before the
judge job can be funded.

### 4. Fund On-Chain Job

Fund the registered job:

```bash
purr pieverse purrfect-yap fund --purchase-id <purchaseId>
```

This step performs the BNB Chain payment flow, including the required `$U`
payment token approval/funding and BNB gas.

### 5. Wait For Judgement Completion

Wait for the provider to submit and complete the PurrfectYap judgement:

```bash
purr pieverse purrfect-yap result --purchase-id <purchaseId> --wait
```

The flow succeeds only when the final result response status is `completed` and
includes `erc8183.txHashes.fund`, `erc8183.txHashes.submit`, and
`erc8183.txHashes.complete`.

Each command is resumable with the same `purchaseId`. If a command reports
existing progress, continue with the next command in sequence instead of
starting a new purchase.

For rejected or expired refundable jobs, run:

```bash
purr pieverse purrfect-yap refund --purchase-id <purchaseId>
```

Use refund only for rejected or expired refundable jobs.

## Output

Parse the final `result` command JSON response internally.

For the current response shape, where the completed ERC-8183 purchase does not
include a score payload, return this chat message:

```text
PurrfectYap judge job completed.

Your eligible PurrfectYap posts were judged and the result was submitted to the BNB Survivor Quest score system.
```

Keep command details, raw statuses, purchase ids, job ids, and tx hashes
internal unless needed to explain a failure or resume an unfinished job.

Relevant final successful `result` output fields:

```json
{
  "serviceSlug": "social-meme-booster-judge",
  "serviceId": "social-meme-booster-judge",
  "purchaseId": "...",
  "campaignSlug": "bnb-survivor-quest",
  "campaignDay": "2026-06-08",
  "pieName": "...pie",
  "status": "completed",
  "completedAt": "...",
  "erc8183": {
    "deliverableUri": "https://...",
    "onChainJobId": "...",
    "txHashes": {
      "fund": "0x...",
      "submit": "0x...",
      "complete": "0x..."
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
| Missing hosted env, `INSTANCE_TOKEN_REQUIRED`, `SOCIAL_MEME_BOOSTER_HOSTED_INSTANCE_REQUIRED` | Explain that hosted Pieverse instance wallet access is required. |
| `SOCIAL_MEME_BOOSTER_DISABLED` | Say the PurrfectYap judge service is currently unavailable. |
| `SOCIAL_MEME_BOOSTER_HANDLE_REQUIRED` | Ask the user to claim a `.pie` handle before running the PurrfectYap judge. |
| `SOCIAL_MEME_BOOSTER_PARTICIPANT_REQUIRED` | Ask the user to join the BNB Survivor Quest campaign before running the PurrfectYap judge. |
| Empty `input.posts`, no eligible posts, no discovered posts | Say no eligible PurrfectYap posts have been discovered yet; ask the user to wait for ingestion or post eligible campaign content, then resume with the same purchase. |
| Preparing/not found/missing job fields/provider timeout/status remains `funded`/status remains `submitted`/tx not confirmed/RPC read failure | Say the PurrfectYap judge job is still being prepared or processed; keep waiting or resume internally. |
| `SOCIAL_MEME_BOOSTER_JUDGEMENT_REQUIRED`, `SOCIAL_MEME_BOOSTER_LIVE_SNAPSHOT_REQUIRED` | Say the judge could not complete because live X engagement data is not ready, and resume later. |
| Transaction failed/reverted/wallet execution failed/insufficient funds/insufficient allowance/gas failure | Say the BNB Chain payment step failed; ask the user to ensure the hosted wallet has enough BNB for gas and enough `$U`, then resume internally. |
| `ERC8183_PROGRESS_TX_MISMATCH`, `JobCreated`/`JobRegistered` event mismatch, transaction target mismatch | Say the on-chain proof did not match the purchase and stop. |
| `ERC8183_PROGRESS_MISSING_FIELD`, `ERC8183_PROGRESS_BACKWARDS`, `ERC8183_PROGRESS_STATUS_UNSUPPORTED` | Say the purchase progress could not be updated because the current state is inconsistent. |
| Missing `erc8183.txHashes.fund`, `erc8183.txHashes.submit`, or `erc8183.txHashes.complete` in final result response | Say the on-chain proof is incomplete and keep waiting or resume internally. |
| Purchase already terminal | Return the existing completion when final fields and required tx hashes are present; otherwise say the purchase is already finished. |
| Rejected/expired/not refundable/failed | State the terminal or refund status and preserve tx hashes when present. |
| Other non-OK response | Say the PurrfectYap judge job could not be completed right now and ask the user to try again. |

Repeated internal attempts should resume from the existing `purchaseId` whenever
one is available.
