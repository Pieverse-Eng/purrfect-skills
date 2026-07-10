---
name: instance-billing
description: Use when a hosted Purrfect Claw user asks about plan or expiration, AI credits, payment methods, credit top-up, renewal or extension, billing status, or token payment.
---

# Instance Billing

Manage only this hosted Purrfect Claw through `purr instance`, never a generic wallet transfer or AI Gateway top-up.

## Guardrails

- Require `WALLET_API_URL`, `WALLET_API_TOKEN`, and `INSTANCE_ID`. If any is missing, explain that this operation requires a hosted instance.
- Before payment, run `purr instance --help`. Stop if the runtime lacks a billing-capable `purr` CLI.
- Use only `purr instance`. Never call Pieverse App S2S/admin APIs, credit-grant endpoints, `purr wallet`, `onchain`, contracts, or `curl` for payment.
- Never ask for or accept a token address on the new flow. Pass a token ID or name to `--token`; the CLI resolves the backend list and rejects ambiguity.
- Never claim success while the result is `paying` or `confirming`. Report completion only when it is `fulfilled`.

## Read Operations

```bash
purr instance status
purr instance credits
purr instance payment-methods
purr instance billing-status --invoice <invoice-id>
```

Use `credits` for Purrfect Claw AI credits, not AI Gateway balance.

## Credit Top-Up

1. If the user did not state a quantity, ask how many credits to add. Do not request a quote yet.
2. Require an integer of at least `100`. Reject decimals or smaller values without calling `purr`.
3. If the user specified a payment token, append `--token <name-or-id>`. Quote `$U` in the shell: `--token '$U'`.
4. A direct instruction containing a valid quantity, such as "top up 100 credits", is authorization for this one payment. Use `--yes` without asking again.

```bash
purr instance topup --credits 100 --yes
purr instance topup --credits 100 --token USDT --yes
```

Use `--dry-run` instead of `--yes` only when the user asks to preview or quote without paying.

## Renewal

An instruction to renew or extend the instance means one 30-day cycle. A direct renewal instruction is authorization for that one payment.

```bash
purr instance renew --yes
purr instance renew --token PIEVERSE --yes
```

Omit `--token` when none was requested; the CLI selects the lowest-priced affordable quote, preferring BSC on ties, then stablecoins, then token IDs. Do not use deprecated `--chain-id` or `--token-address`.

If the user chooses a non-PIEVERSE token, honor it and proceed, but briefly mention that PIEVERSE renewal can receive a lower discounted price. Do not switch tokens or ask again.

## Result Handling

- `fulfilled`: state that the top-up or renewal completed.
- `confirming`: state that payment was broadcast and fulfillment is still pending; include all identifiers returned by the CLI, never invent a missing transaction ID, then use `purr instance billing-status --invoice <invoice-id>` for a later read-only check.
- `paying`: state that wallet execution has started, do not initiate a second payment, and use `purr instance billing-status --invoice <invoice-id>` to check the same invoice again.
- `failed`: surface the reason. Do not improvise another transfer.
- Insufficient token balance or gas: report the specific shortage and stop.
