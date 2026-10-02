---
name: skyinsights
description: Use when the user asks to check wallet labels, wallet KYA risk, transaction KYT risk, submit or poll SkyInsights screenings, create or manage wallet monitors, investigate address risk, AML risk, sanctions/exposure labels, or screen an EVM wallet through the hosted Purrfect Claw instance.
---

# SkyInsights

## Overview

SkyInsights provides blockchain risk intelligence for wallets and transactions.
It helps identify address labels, entity exposure, sanctions or AML signals,
wallet KYA risk, transaction KYT risk, and screening status for supported EVM
chains. It also supports wallet monitor creation, batch monitor creation,
status updates, detail lookup, and deletion.

## Commands

| Command | Purpose | Syntax |
| --- | --- | --- |
| `kya-labels` | Look up labels and entity metadata for a wallet address. | `purr skyinsights kya-labels --chain <chain> --address <wallet-address>` |
| `kya-risk` | Check KYA risk for a wallet address. | `purr skyinsights kya-risk --chain <chain> --address <wallet-address>` |
| `kyt-risk` | Check KYT risk for a transaction hash. | `purr skyinsights kyt-risk --chain <chain> --tx-hash <transaction-hash>` |
| `screening-submit` | Submit an async wallet screening request. | `purr skyinsights screening-submit --chain <chain> --address <wallet-address> [--rule-set-id <rule-set-id>]` |
| `screening-list` | List recent async screening requests. | `purr skyinsights screening-list [--limit <count>]` |
| `screening-get` | Get the status or result for a screening request ID. | `purr skyinsights screening-get --request-id <request-id>` |
| `monitor-create` | Create a wallet monitor. | `purr skyinsights monitor-create --chain <chain> --address <wallet-address>` |
| `monitor-batch-create` | Create wallet monitors for multiple addresses. | `purr skyinsights monitor-batch-create --chain <chain> --addresses <wallet1,wallet2>` |
| `monitor-list` | List current wallet monitors. | `purr skyinsights monitor-list [--limit <count>]` |
| `monitor-get` | Get monitor detail, labels, risk factors, and recent transactions. | `purr skyinsights monitor-get --monitor-id <monitor-id> [--page <page>] [--size <count>]` |
| `monitor-update` | Set a monitor to running or paused. | `purr skyinsights monitor-update --monitor-id <monitor-id> --status <running|paused>` |
| `monitor-delete` | Delete a wallet monitor. | `purr skyinsights monitor-delete --monitor-id <monitor-id>` |

## Workflow

1. Identify whether the user wants labels, wallet risk, transaction risk, a
   screening submission, a list of screenings, a specific screening result,
   monitor creation, monitor detail, monitor status update, monitor deletion,
   or a monitor list.
2. Ask one short clarification if the required chain, address, transaction hash,
   request ID, monitor ID, or monitor status is missing.
3. For labels, KYA risk, KYT risk, screening list, or an existing screening
   result, run the matching command from the table.
4. For a screening submission, run `screening-submit`, capture the returned
   `requestId`, then run `screening-get --request-id <requestId>` to fetch the
   current status or result.
5. For monitor operations, run the matching `monitor-*` command from the table.
   Preserve returned `monitorId` values exactly for later get, update, or
   delete operations.
6. Summarize the returned JSON without hiding important fields:
   `provider`, `operation`, risk level and verdict when present, labels,
   entities, risk reasons, screening `status`, `requestId`, monitor `status`,
   `monitorId`, risk factors, pagination, and transactions when present.
7. For screening status `pending`, `submitted`, or `running`, tell the user it
   is not complete yet and keep the `requestId` for later polling.
8. For `failed` or `unknown`, surface `errorCode` when present and do not
   submit another screening unless the user explicitly asks to retry.

## Error Handling

| Error | Handling |
| --- | --- |
| `skyinsights_rate_limited` | Report the retry-after hint when present and do not retry immediately. |
| `skyinsights_invalid_response` | Report that SkyInsights returned a response the platform rejected. Do not reinterpret raw provider data. |
| `skyinsights_timeout` or `skyinsights_network_error` | Treat the outcome as uncertain; do not submit a replacement screening or recreate, update, or delete a monitor automatically. List or get existing state first. |
| `skyinsights_request_not_found` | Ask the user to verify the `requestId` or run `purr skyinsights screening-list --limit 20`. |
| `skyinsights_monitor_not_found` | Ask the user to verify the `monitorId` or run `purr skyinsights monitor-list --limit 20`. |
| `skyinsights_monitor_not_ready` | Report that monitor creation is still in progress; use `monitor-get` later instead of deleting or updating immediately. |
| `skyinsights_monitor_conflict` | Report that monitor state changed during the request; run `monitor-list` or `monitor-get` before retrying. |
| Deterministic `4xx` | Fix the chain, address, transaction hash, or request ID input before retrying. |
