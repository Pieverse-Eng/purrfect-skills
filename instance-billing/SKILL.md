---
name: instance-billing
description: Use when a hosted Purrfect Claw user asks about its plan, expiration, AI credits, payment methods, top-up, renewal, extension, or billing status.
---

# Instance Billing

Manage only this hosted Purrfect Claw through `purr instance`, never a generic wallet transfer or AI Gateway top-up.

## Guardrails

- Require `WALLET_API_URL`, `WALLET_API_TOKEN`, and `INSTANCE_ID`. If any is missing, explain that this operation requires a hosted instance.
- Before paying, run `purr instance --help`. Stop if the runtime lacks billing commands.
- Use only `purr instance`. Never call Pieverse App S2S/admin APIs, credit-grant endpoints, `purr wallet`, `onchain`, contracts, or `curl` for payment. Never replace the billing flow with a manual wallet transfer.
- Never use legacy or deprecated renewal commands or flags. The supported command is `purr instance renew`.
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
4. "Top up 100 credits" authorizes that one payment. Use `--yes` without another confirmation.

```bash
purr instance topup --credits 100 --yes
purr instance topup --credits 100 --token USDT --yes
```

Use `--dry-run` instead of `--yes` only when the user asks to preview or quote without paying.

## Renewal

Renew or extend means one 30-day cycle and authorizes that payment.

```bash
purr instance renew --yes
purr instance renew --token PIEVERSE --yes
```

Omit `--token` when none was requested; the CLI selects the lowest-priced affordable quote, preferring BSC on ties, then stablecoins, then token IDs. Do not use deprecated `--chain-id` or `--token-address`.

If the user chooses a non-PIEVERSE token, honor it and proceed, but briefly mention that PIEVERSE renewal can receive a lower discounted price. Do not switch tokens or ask again.

## Result Handling

- `fulfilled`: state that the top-up or renewal completed.
- `confirming`: report that payment was broadcast but fulfillment is pending. Include only returned identifiers, then poll the same Invoice with `purr instance billing-status --invoice <invoice-id>`.
- Network interruption or unknown timeout with no transaction hash: retry the exact original `purr instance renew ... --yes` or `purr instance topup ... --yes` command once. Stable request IDs resume the same quote. Never change token, invoice, or quote. If the retry still returns no transaction hash, stop and report the result; do not keep polling as if payment is progressing by itself.
- Deterministic HTTP `4xx`: stop immediately and report the exact response. Do not retry and do not describe `paying` as a background process that will finish on its own.
- `paying` without the network-interruption or unknown-timeout condition above is not proof of broadcast or completion. Stop and report the returned state; do not retry, poll, or claim success.
- `failed`: surface the reason. Do not improvise another transfer.
- Insufficient token balance or gas: report the specific shortage and stop.
