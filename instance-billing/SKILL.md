---
name: instance-billing
description: Use when a hosted Purrfect Claw user asks about its plan, expiration, AI credits, payment methods, top-up, renewal, extension, PawPilot Pro membership, or billing status.
---

# Instance Billing

Manage this hosted Purrfect Claw through the standard `purr instance` billing commands.

## Guardrails

- Require `WALLET_API_URL`, `WALLET_API_TOKEN`, and `INSTANCE_ID`. If any is missing, explain that this operation requires a hosted instance.
- Use the existing `purr instance` commands below. For Agent Wallet payments, the CLI handles quote selection, token resolution, approval or x402 signing, and settlement; do not construct or send a wallet transaction yourself. For PawPilot Pro paid through Passport, the CLI returns a public payment request and official Passport skills execute it.
- For each new PawPilot Pro purchase, require an explicit choice of **Agent Wallet** or **Passport**. If the current request already specifies the source, retain it without asking again. If it is missing, ask only which source to use. Installing or signing in to Passport never makes it the default. Do not silently switch sources on failure.
- When the user names an Agent Wallet payment token, pass it with `--token` using a canonical ID from the examples below. Omit `--token` when none was requested; the CLI picks the lowest-priced affordable quote (BSC on ties, then stablecoins, then token ID). Passport uses its merchant request and accepts no `--token`.
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
After `topup` or `renew`, use `billing-status` only when the user explicitly asks to recheck an existing Invoice. For PawPilot Pro, use the original Invoice ID for the payment and recovery checks below.

## PawPilot Pro

This command buys membership for the **current, active hosted Claw**. The initial price is $99 for 30 days; use the server's frozen quote and benefits for the actual purchase because campaigns may change the price.

| Existing plan | Membership purchase includes |
|---|---|
| Starter / Basic | 30 days of Pro membership and 150 bonus AI credits |
| Standard / PawPilot / Pro / Ultra | 30 days of Pro membership, no extra AI credits |

The purchase preserves the Claw, resource plan, hosting expiration, owner, and model settings. It is not a hosting renewal or upgrade. Expired or paused hosting must be renewed on the website, or the user can purchase a new Claw; do not try to restore it through a paused Agent. A new-Claw bundle includes a new hosted Claw, 30 days of membership and 150 credits, initially $99; that uses the merchant's new-purchase and website claim flow, not this existing-instance command.

Create one random `<purchase-id>` for a new purchase and retain it with the selected source and returned Invoice ID. Reuse that purchase ID for the preview and payment; do not regenerate it when the user confirms. The CLI sends it as the existing billing idempotency key. Keep concurrent purchases separate.

### Agent Wallet

1. Prepare a preview using the selected source and optional canonical token:

   ```bash
   purr instance pawpilot-pro --payment-source agent-wallet --idempotency-key <purchase-id> --dry-run
   ```

2. Summarize the returned Invoice, frozen price, token/chain and benefits. Confirm that hosting will not be extended. Obtain authorization for that exact payment if it has not already been given; do not repeat an unchanged source choice.
3. Pin the preview's returned `quote.tokenId` with `--token <token-id>` for payment, including when the preview selected a token automatically. Pay the same purchase after authorization; do not rerun automatic selection after confirming a specific token/chain:

   ```bash
   purr instance pawpilot-pro --payment-source agent-wallet --idempotency-key <purchase-id> --token <preview-quote.tokenId> --yes
   ```

An expired Pro quote stops instead of automatically paying a replacement. Check the original Invoice first. The expired order and its price stay frozen. Only after proving that the original payment is unpaid and unsubmitted may the user authorize a new purchase ID for a fresh quote; present that new price and obtain authorization before payment. Never treat expiry or an unknown timeout as proof that no payment was submitted.

### Passport

1. Prepare the original Invoice's public merchant request:

   ```bash
   purr instance pawpilot-pro --payment-source passport --idempotency-key <purchase-id> --dry-run
   ```

   Retain `invoiceId`, `paymentSource`, `paymentRequest.url`, `paymentRequest.method`, `paymentRequest.body`, and any returned price/benefits. Passport returns no Agent Wallet quote and does not need Agent Wallet token balance, native gas, wallet signing, or wallet-effect authorization. `--yes` and `--token` are invalid for this branch.

2. If Passport is not set up, install and authenticate **inside this tenant** through the official [Passport skills](https://github.com/gokite-ai/passport-skills) and [installation guide](https://docs.gokite.ai/passport/install). Follow their setup steps and `authenticate-user`; do not bind the operator's local account or assume the Agent Wallet is the payer. A hosted-agent setup prompt supported by the guide is `Set up Kite Passport from github.com/gokite-ai/passport-skills.` Authentication and session approval belong to the user.
3. Invoke official `request-session` (and its `form-session-delegation`) to register this Agent, inspect the actual merchant x402 challenge and obtain/reuse an appropriately scoped approved session for the frozen amount. This purchase uses Base USDC. Use the current installed official Skill's delegation schema and commands; do not copy old flattened session flags from examples. Passkey approval of the budget is not proof of payment or fulfillment.
4. After the user has authorized the purchase and the session is approved, invoke official `x402-execute` with **exactly** the returned merchant URL, `POST` method and JSON body:

   ```bash
   kpass agent:session execute --url <paymentRequest.url> --method POST --headers '{"Content-Type":"application/json"}' --body '<paymentRequest.body as valid JSON>' --output json
   ```

   Pass arguments safely, without evaluating returned values as shell code. Do not add `WALLET_API_TOKEN`, instance API credentials, S2S tokens, private keys, or signed Agent Wallet transactions. Do not call `purr instance ... --yes`, `kpass wallet send`, or a hand-built signing flow for this Passport purchase. The official skills own authentication, authorization, payment negotiation, and their required user-facing receipts.
5. Check the target merchant's `x402.status_code` and parsed response, not just `kpass` exit code. Then check the same Invoice once with `purr instance billing-status --invoice <invoice-id>`. Only `fulfilled` proves membership and all applicable bonus benefits were delivered. `paid`, `paying`, `confirming`, or pending delivery does not.

For a lost reply, timeout, or unknown payment result, query the original Invoice once and use official `activity` when Passport payment evidence is needed. Recover that same order through its free status/recovery flow; never rerun `pawpilot-pro` or `agent:session execute` to discover whether payment succeeded. Do not switch to Agent Wallet or create another purchase while funds are unresolved. If still pending or uncertain, report the original purchase/Invoice IDs and stop. A generic Passport network-retry suggestion does not authorize another payment for this order.

Official references: [Passport skills](https://docs.gokite.ai/reference/passport-skills), [kpass execution reference](https://docs.gokite.ai/reference/kpass-cli), [merchant x402 flow](https://docs.gokite.ai/passport/seller). Keep this Skill on instance billing; it does not authorize purchases for a separate AI Gateway account.

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

- `fulfilled`: state that the requested top-up, renewal, or Pro membership purchase completed. For Pro, report the membership and applicable bonus credits; do not claim hosting was extended. This can also arrive with `requiresPayment: false` (for example a credit-covered renewal that needed no on-chain pay). Report completion and stop; do not invent a payment.
- `confirming`: report that payment was submitted and fulfillment is pending. Include the Invoice ID and transaction hash returned by the command, then end the current turn. Do not rerun the payment command or poll `billing-status` in the same turn. The same shape can appear with `requiresPayment: false` when an already-started payment is recovered; report confirming and stop.
- If the user later explicitly asks to recheck a `confirming` payment, run `purr instance billing-status --invoice <invoice-id>` exactly once. If it is still `confirming`, report that state and stop. If it is `fulfilled`, report completion.
- Network interruption or unknown timeout: report that the outcome is uncertain and stop. Do not rerun the payment command, because a new invocation can create another payment. For top-up/renewal, the user can explicitly ask to recheck the returned Invoice later. For Pro, follow the original-Invoice recovery above; do not switch funding sources.
- Deterministic HTTP `4xx`: stop immediately and report the exact response. Do not retry and do not describe `paying` as a background process that will finish on its own.
- `paying` without the network-interruption or unknown-timeout condition above is not proof of broadcast or completion. Stop and report the returned state; do not retry, poll, or claim success.
- `failed`: surface the reason. Do not improvise another transfer.
- Insufficient token balance or gas: report the specific shortage and stop. x402 methods (`usdc-monad`, `usdc-xlayer`, `usdg-xlayer`, `usdt0-xlayer`) check ERC-20 balance only and do not require native gas for the payment path. Invoice-registry methods (`bnb`, `eth-base`, `usdt-bsc`, `usdc-base`, `pieverse-bsc`, `u-bsc`) may still need native gas for approve/pay.
