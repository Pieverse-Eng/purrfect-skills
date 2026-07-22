---
name: osero
description: Use when the user asks to inspect or use Osero, Sky USDS/sUSDS, sUSDS APY or SSR, supported Osero chains, Osero token/contract/balance data, or to preview, plan, or execute USDC to USDS/sUSDS minting and USDS/sUSDS to USDC redemption through the hosted Purrfect Claw wallet.
---

# Osero

## Overview

Osero provides a Purrfect Claw CLI integration for Sky USDS and sUSDS routes.
Use it to discover supported chains, inspect Osero token and contract metadata,
check the hosted wallet's USDC/USDS/sUSDS balances, read the current Sky savings
rate/APY, preview or plan conversions, and execute supported mint/redeem actions
through the instance wallet.

Known chain aliases are `ethereum`, `op`, `unichain`, `base`, and `arbitrum`.
Run `purr osero chains` for the live supported chain list before assuming
support.

## Supported Chains

| Chain | Chain ID |
| --- | ---: |
| Ethereum | 1 |
| OP Mainnet | 10 |
| Unichain | 130 |
| Base | 8453 |
| Arbitrum One | 42161 |

## Amount Units

Amounts must be raw integer token units, not decimal strings.

| Token | Decimals | Example |
| --- | ---: | --- |
| USDC | 6 | `1 USDC = 1000000` |
| USDS | 18 | `1 USDS = 1000000000000000000` |
| sUSDS | 18 | `1 sUSDS = 1000000000000000000` |

## Commands

| Command | Purpose | Syntax |
| --- | --- | --- |
| `chains` | List Osero-supported chains. | `purr osero chains` |
| `chain` | Show one chain's Osero configuration. | `purr osero chain --chain <chain>` or `purr osero chain --chain-id <id>` |
| `tokens` | Show Osero token metadata for a chain. | `purr osero tokens --chain <chain>` |
| `contracts` | Show Osero contract addresses for a chain. | `purr osero contracts --chain <chain>` |
| `balances` | Show the wallet's Osero token balances. | `purr osero balances --chain <chain>` |
| `ssr` | Read the Sky Savings Rate value. | `purr osero ssr --chain <chain>` |
| `apy` | Read the current sUSDS APY from Osero/Sky data. | `purr osero apy --chain <chain>` |
| `preview` | Estimate output and route shape without building transactions. | `purr osero preview --action <action> --chain <chain> --amount <raw-amount> [--receiver <address>] [--slippage-bps <bps>] [--referral-code <raw-int>]` |
| `plan` | Build the transaction plan without broadcasting. | `purr osero plan --action <action> --chain <chain> --amount <raw-amount> [--receiver <address>] [--slippage-bps <bps>] [--referral-code <raw-int>]` |
| `execute` | Sign and broadcast the planned transactions through the hosted wallet. | `purr osero execute --action <action> --chain <chain> --amount <raw-amount> [--receiver <address>] [--slippage-bps <bps>] [--referral-code <raw-int>]` |

## Actions

| Action | Direction | Input Amount Units |
| --- | --- | --- |
| `mint-usds` | USDC to USDS | raw USDC, 6 decimals |
| `mint-susds` | USDC to sUSDS | raw USDC, 6 decimals |
| `redeem-usds` | USDS to USDC | raw USDS, 18 decimals |
| `redeem-susds` | sUSDS to USDC | raw sUSDS, 18 decimals |

## Workflow

1. Identify whether the user wants chain discovery, token/contract metadata,
   balances, yield data, a preview, a transaction plan, or execution. Ask one
   short clarification if the chain, action, or amount is missing or ambiguous.
2. For chain support, run `purr osero chains`; do not assume unsupported chains
   have an independent USDS vault or Osero route.
3. For yield questions, run `purr osero apy --chain <chain>` and, when useful,
   `purr osero ssr --chain <chain>`. Report the returned APY as current data;
   never reuse a previously observed APY.
4. Before an execution, check Osero balances with
   `purr osero balances --chain <chain>` and native gas with
   `purr wallet balance --chain-type ethereum --chain-id <resolved-chain-id>`.
5. Run `preview` first for user-facing estimates. For execution requests, also
   run `plan` and summarize the action, chain, raw input amount, estimated
   output, receiver, approval steps, main transaction steps, and wallet policy
   implications.
6. Ask exactly:
   `Do you want to execute this Osero action with these parameters? (Yes/No)`
7. Execute only after an explicit yes in the immediately preceding user turn and
   only if the parameters are unchanged. If the quote, plan, chain, amount,
   receiver, slippage, or referral code changed, re-run preview/plan and ask for
   confirmation again.
8. After `execute`, report the final transaction hash, per-step transaction
   hashes, chain, receipt status, gas used or block number when returned, and
   final balances from `purr osero balances --chain <chain>`.
9. When the user asks to redeem all or swap back everything, use the exact raw
   USDS or sUSDS balance returned by `purr osero balances`; do not round a
   displayed decimal balance back into raw units.

## Safety Rules

- Treat `purr osero execute` as a financial on-chain action because it signs and
  broadcasts transactions from the hosted wallet.
- Never request, generate, or pass an idempotency key, deduplication key, UUID,
  or client-provided replay key. Platform manages request deduplication.
- Never guess token decimals, raw amounts, receiver addresses, slippage, chain
  IDs, or contract addresses. Use Osero CLI output or ask the user.
- Keep the receiver as the hosted instance wallet unless the user explicitly
  provides another address. If a custom receiver is used, include it in the
  confirmation summary.
- Do not bypass wallet policy. If policy denies or defers an Osero action,
  report the decision and stop.
- Do not retry an execution automatically after timeout, network error,
  `broadcast_unknown`, or partial success. Reconcile balances and transaction
  hashes first.
- Do not describe preview output as guaranteed. It is an estimate and may change
  when the transaction is planned or executed.

## Examples

```bash
# Supported chains and current yield
purr osero chains
purr osero apy --chain base

# Balances and metadata
purr osero balances --chain base
purr osero tokens --chain base
purr osero contracts --chain base

# Preview and plan 1 USDC to sUSDS on Base
purr osero preview --action mint-susds --chain base --amount 1000000
purr osero plan --action mint-susds --chain base --amount 1000000

# Execute only after explicit user confirmation
purr osero execute --action mint-susds --chain base --amount 1000000

# Redeem an exact raw sUSDS balance back to USDC
purr osero balances --chain base
purr osero preview --action redeem-susds --chain base --amount <susds_raw_balance>
purr osero execute --action redeem-susds --chain base --amount <susds_raw_balance>
```

## Error Handling

| Error | Handling |
| --- | --- |
| Unsupported chain or route | Run `purr osero chains`, report supported chains, and ask the user to choose one. |
| Invalid amount or decimal amount | Convert to a raw integer string with the correct token decimals, show the raw value, and retry only after user approval for execution. |
| Insufficient token balance | Show the relevant balance from `purr osero balances --chain <chain>` and ask for a smaller amount or funding. |
| Insufficient native gas | Show native gas from `purr wallet balance --chain-type ethereum --chain-id <resolved-chain-id>` and ask the user to fund gas before executing. |
| Wallet policy denied or deferred | Report the policy result and do not bypass it or repackage the transaction. |
| Slippage, stale quote, or reverted route | Re-run `preview` and `plan`; ask for confirmation again before executing. |
| Timeout, network error, or `broadcast_unknown` | Treat the outcome as uncertain. Check balances and transaction hashes before any retry. |
| Partial success in a multi-step plan | Report successful step hashes, check balances and approvals, and do not resubmit the full action blindly. |
| Auth or hosted runtime error | Report that the hosted runtime needs valid wallet API configuration; do not ask the user to paste secrets. |
