---
name: skyinsights
description: Use when the user asks to check wallet labels, wallet KYA risk, transaction KYT risk, submit or poll SkyInsights screenings, investigate address risk, AML risk, sanctions/exposure labels, or screen an EVM wallet through the hosted Purrfect Claw instance.
---

# SkyInsights

## Overview

SkyInsights provides blockchain risk intelligence for wallets and transactions.
It helps identify address labels, entity exposure, sanctions or AML signals,
wallet KYA risk, transaction KYT risk, and screening status for supported EVM
chains.

## Commands

| Command | Purpose | Syntax |
| --- | --- | --- |
| `kya-labels` | Look up labels and entity metadata for a wallet address. | `purr skyinsights kya-labels --chain <chain> --address <wallet-address>` |
| `kya-risk` | Check KYA risk for a wallet address. | `purr skyinsights kya-risk --chain <chain> --address <wallet-address>` |
| `kyt-risk` | Check KYT risk for a transaction hash. | `purr skyinsights kyt-risk --chain <chain> --tx-hash <transaction-hash>` |
| `screening-submit` | Submit an async wallet screening request. | `purr skyinsights screening-submit --chain <chain> --address <wallet-address> [--rule-set-id <rule-set-id>]` |
| `screening-list` | List recent async screening requests. | `purr skyinsights screening-list [--limit <count>]` |
| `screening-get` | Get the status or result for a screening request ID. | `purr skyinsights screening-get --request-id <request-id>` |

## Workflow

1. Identify whether the user wants labels, wallet risk, transaction risk, a
   screening submission, a list of screenings, or a specific screening result.
2. Ask one short clarification if the required chain, address, transaction hash,
   or request ID is missing.
3. For labels, KYA risk, KYT risk, screening list, or an existing screening
   result, run the matching command from the table.
4. For a screening submission, run `screening-submit`, capture the returned
   `requestId`, then run `screening-get --request-id <requestId>` to fetch the
   current status or result.
5. Summarize the returned JSON without hiding important fields:
   `provider`, `operation`, risk level and verdict when present, labels,
   entities, risk reasons, screening `status`, and `requestId`.
6. For screening status `pending`, `submitted`, or `running`, tell the user it
   is not complete yet and keep the `requestId` for later polling.
7. For `failed` or `unknown`, surface `errorCode` when present and do not
   submit another screening unless the user explicitly asks to retry.

## Error Handling

| Error | Handling |
| --- | --- |
| `skyinsights_rate_limited` | Report the retry-after hint when present and do not retry immediately. |
| `skyinsights_invalid_response` | Report that SkyInsights returned a response the platform rejected. Do not reinterpret raw provider data. |
| `skyinsights_timeout` or `skyinsights_network_error` | Treat the outcome as uncertain; do not submit a replacement screening automatically. |
| `skyinsights_request_not_found` | Ask the user to verify the `requestId` or run `purr skyinsights screening-list --limit 20`. |
| Deterministic `4xx` | Fix the chain, address, transaction hash, or request ID input before retrying. |
