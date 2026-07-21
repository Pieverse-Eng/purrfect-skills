---
name: instance-billing
description: Use when a hosted Purrfect Claw user asks about its plan, expiration, AI credits, payment methods, top-up, renewal, extension, or billing status.
---

# Instance Billing

Manage this hosted Purrfect Claw through the standard `purr instance` billing commands.

## Guardrails

- Require `WALLET_API_URL`, `WALLET_API_TOKEN`, and `INSTANCE_ID`. If any is missing, explain that this operation requires a hosted instance.
- Run billing transactions only with the `purr instance topup` and `purr instance renew` commands below. The CLI handles quote selection, token resolution, approval or x402 signing, and settlement; do not construct or send a wallet transaction yourself.
- When the user names a payment token, pass it with `--token` using a canonical ID from the examples below. Omit `--token` when none was requested; the CLI picks the lowest-priced affordable quote (BSC on ties, then stablecoins, then token ID).
- `USDC` alone is ambiguous (Base / Monad / X Layer). If the user does not name a chain, ask which one before payment confirmation. Do not pass bare `--token USDC`.
- Before any `topup` or `renew` command with `--yes`, summarize the credit quantity or 30-day extension and the requested token or automatic selection, warn that it will initiate a real on-chain payment, and wait for explicit confirmation. Only confirmation in the immediately preceding user turn authorizes one unchanged command; the initial request, any changed payment detail, or an intervening request requires confirmation again.
- Never claim success while the result is `paying` or `confirming`. Report completion only when it is `fulfilled`.
- When the user already supplied the credit quantity for a top-up, or asked for a renewal, prepare exactly one matching command with the optional payment token. Do not call `payment-methods`, repeat balance checks, or probe CLI help before requesting confirmation.

## Read Operations

```bash
purr instance status
purr instance credits
purr instance payment-methods
purr instance billing-status --invoice <invoice-id>
```

Use `status` for plan, next billing date, renewal price, and trusted-wallet balances for payment methods. Copy the renewal price exactly from the command output or raw `effectiveRenewalPriceUsd`; never infer price from the plan name, docs, or default pricing because discounts and campaigns can change the effective renewal price.
Use `credits` to read the Purrfect Claw's current AI credit balance.
Use `payment-methods` only when the user asks which tokens are accepted or which chain a symbol maps to.
Use `billing-status` only when the user explicitly asks to recheck an existing Invoice. Do not call it automatically after `topup` or `renew`.

## Credit Top-Up

1. If the user did not state a quantity, ask how many credits to add. Do not request a quote yet.
2. Require an integer of at least `100`. Reject decimals or smaller values without calling `purr`.
3. If the user specified a payment token, append the matching `--token` from the examples below.
4. Follow the payment confirmation guardrail above. Only after the user confirms may you run one matching command with `--yes`.

```bash
purr instance topup --credits <credits> --yes
purr instance topup --credits <credits> --token bnb --yes
purr instance topup --credits <credits> --token eth-base --yes
purr instance topup --credits <credits> --token usdt-bsc --yes
purr instance topup --credits <credits> --token usdc-base --yes
purr instance topup --credits <credits> --token pieverse-bsc --yes
purr instance topup --credits <credits> --token u-bsc --yes
purr instance topup --credits <credits> --token usdc-monad --yes
purr instance topup --credits <credits> --token usdg-xlayer --yes
purr instance topup --credits <credits> --token usdt0-xlayer --yes
purr instance topup --credits <credits> --token usdc-xlayer --yes
```

Use `--dry-run` instead of `--yes` only when the user asks to preview or quote without paying.

## Renewal

Renew or extend means one 30-day cycle. Follow the payment confirmation guardrail before running a command with `--yes`.

```bash
purr instance renew --yes
purr instance renew --token bnb --yes
purr instance renew --token eth-base --yes
purr instance renew --token usdt-bsc --yes
purr instance renew --token usdc-base --yes
purr instance renew --token pieverse-bsc --yes
purr instance renew --token u-bsc --yes
purr instance renew --token usdc-monad --yes
purr instance renew --token usdg-xlayer --yes
purr instance renew --token usdt0-xlayer --yes
purr instance renew --token usdc-xlayer --yes
```

If the user chooses a non-PIEVERSE token, honor it and briefly mention in the confirmation summary that PIEVERSE renewal can receive a lower discounted price. Do not switch tokens; payment confirmation is still required.

## Result Handling

- `fulfilled`: state that the top-up or renewal completed. This can also arrive with `requiresPayment: false` (for example a credit-covered renewal that needed no on-chain pay). Report completion and stop; do not invent a payment.
- `confirming`: report that payment was submitted and fulfillment is pending. Include the Invoice ID and transaction hash returned by the command, then end the current turn. Do not rerun the payment command or poll `billing-status` in the same turn. The same shape can appear with `requiresPayment: false` when an already-started payment is recovered; report confirming and stop.
- If the user later explicitly asks to recheck a `confirming` payment, run `purr instance billing-status --invoice <invoice-id>` exactly once. If it is still `confirming`, report that state and stop. If it is `fulfilled`, report completion.
- Network interruption or unknown timeout: report that the outcome is uncertain and stop. Do not rerun the payment command, because a new invocation can create another payment. If an Invoice ID was returned, the user can explicitly ask to recheck that Invoice later.
- Deterministic HTTP `4xx`: stop immediately and report the exact response. Do not retry and do not describe `paying` as a background process that will finish on its own.
- `paying` without the network-interruption or unknown-timeout condition above is not proof of broadcast or completion. Stop and report the returned state; do not retry, poll, or claim success.
- `failed`: surface the reason. Do not improvise another transfer.
- Insufficient token balance or gas: report the specific shortage and stop. x402 methods (`usdc-monad`, `usdc-xlayer`, `usdg-xlayer`, `usdt0-xlayer`) check ERC-20 balance only and do not require native gas for the payment path. Invoice-registry methods (`bnb`, `eth-base`, `usdt-bsc`, `usdc-base`, `pieverse-bsc`, `u-bsc`) may still need native gas for approve/pay.
