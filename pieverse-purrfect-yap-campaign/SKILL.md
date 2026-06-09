---
name: pieverse-purrfect-yap-campaign
description: Use when running Purrfect Yap Judge service for BNB Survivor Quest to evaluate X/Twitter posts for today's Yap Score.
---

# Pieverse PurrfectYap Campaign

Use inside a hosted Pieverse instance to run the paid BNB Survivor Quest
PurrfectYap judge through `purr pieverse purrfect-yap` on BNB Smart Chain
mainnet (chain ID 56).

## Rules

- Required context: hosted Pieverse instance wallet access and a claimed `.pie`
  handle.
- Campaign, channel, partner, and `.pie` handle are selected by the platform.
- Do not check the user's personal BNB balance before running this flow.
- Each purchase is a paid one-shot judge job. The provider checks the current
  eligible X posts for this instance, submits a result, and the job ends.
- Eligible PurrfectYap content is recommended, but not required for completion.
  If no eligible posts are found, the job should still complete with a
  no-eligible-posts deliverable.
- Do not wait for future posts on the same purchase. If the user posts later and
  wants those posts judged, start a new paid judge purchase.
- Users may judge multiple times in the same UTC campaign day. The campaign
  keeps only the latest completed judgement for that instance/day, even if the
  latest score is lower.

## Run

Run the staged flow in order. Commands are resumable with the same `purchaseId`
while the current paid job is in progress.

### 1. Purchase Intent

```bash
purr pieverse purrfect-yap purchase
```

Create the paid PurrfectYap judge purchase intent. Read `purchaseId`,
`campaignSlug`, `campaignDay`, and `pieName` from the JSON response. The
purchase response is not final.

Use this `purchaseId` for every later command in this staged flow.

### 2. Create On-Chain Job

```bash
purr pieverse purrfect-yap create-job --purchase-id <purchaseId>
```

Create and register the ERC-8183 job. If the command reports existing progress,
continue with the next command.

### 3. Fund On-Chain Job

```bash
purr pieverse purrfect-yap fund --purchase-id <purchaseId>
```

Perform the `$U` payment token approval/funding and BNB gas flow. The provider
input is readable only after funding is confirmed.

### 4. Inspect Judge Input

```bash
purr pieverse purrfect-yap input --purchase-id <purchaseId>
```

Run this only after funding. If it returns `ERC8183_PURCHASE_NOT_FUNDED`, finish
or resume `create-job` and `fund`, then retry `input`. Treat `input.posts` as a
snapshot for this paid job; continue to judgement completion whether it has
posts or is empty.

### 5. Wait For Result

```bash
purr pieverse purrfect-yap result --purchase-id <purchaseId> --wait
```

The flow succeeds only when final `status` is `completed` and
`erc8183.txHashes.fund`, `submit`, and `complete` are present.

### Refund

```bash
purr pieverse purrfect-yap refund --purchase-id <purchaseId>
```

Use `refund` only for rejected or expired refundable jobs.

## Output

Keep raw command output, purchase ids, job ids, and tx hashes internal unless
they are needed to explain a failure or resume an unfinished job.

The current CLI result does not include a numeric Yap Score, so do not quote one.

When the final result is completed and eligible posts were judged:

```text
PurrfectYap judge job completed.

Your eligible PurrfectYap posts were judged and the result was submitted to the BNB Survivor Quest score system.
```

When `input.posts` was empty or the completed deliverable says no eligible posts
were found:

```text
PurrfectYap judge job completed.

No eligible PurrfectYap posts were found for this .pie handle at judgement time. This paid judge job is finished. Post with the required campaign signals and run Judge again to submit a new daily result.
```

## Errors

Summarize errors in plain language. Match backend `code` values internally.
Preserve `purchaseId`, `rejectTxHash`, and `refundTxHash` when available.

| Internal match | Response |
| -------------- | -------- |
| Missing hosted env, `INSTANCE_TOKEN_REQUIRED`, `SOCIAL_MEME_BOOSTER_HOSTED_INSTANCE_REQUIRED` | Hosted Pieverse instance wallet access is required. |
| `SOCIAL_MEME_BOOSTER_DISABLED` | The PurrfectYap judge service is unavailable. |
| `SOCIAL_MEME_BOOSTER_HANDLE_REQUIRED` | Ask the user to claim a `.pie` handle. |
| `SOCIAL_MEME_BOOSTER_PARTICIPANT_REQUIRED` | Ask the user to join the campaign. |
| `ERC8183_PURCHASE_NOT_FUNDED` from `input` | Resume `create-job` and `fund` first. |
| Empty `input.posts`, no eligible posts, no discovered posts | Not an error after completion; return the no-eligible-posts completion message. |
| Preparing/not found/missing job fields/provider timeout/status remains `funded` or `submitted`/tx not confirmed/RPC read failure | The job is still being prepared or processed; keep waiting or resume internally. |
| `SOCIAL_MEME_BOOSTER_JUDGEMENT_REQUIRED` | The provider completion payload is incomplete; resume later. |
| `SOCIAL_MEME_BOOSTER_LIVE_SNAPSHOT_REQUIRED` | Live X engagement data is not ready; resume later. |
| Transaction failed/reverted/wallet execution failed/insufficient funds, allowance, or gas | The payment step failed; preserve the purchase id and contact the Pieverse team. |
| Progress mismatch, missing progress fields, backwards progress, unsupported status, transaction target mismatch | The on-chain proof or purchase state is inconsistent; stop. |
| Missing final `fund`, `submit`, or `complete` tx hashes | On-chain proof is incomplete; keep waiting or resume internally. |
| Purchase already terminal | Return existing completion if final fields are present; otherwise state the terminal status. |
| Rejected/expired/not refundable/failed | State the terminal or refund status. |
| Other non-OK response | The job could not be completed right now. |
