# Errors and Failure Policy

Prefer stopping and explaining over inventing retries. Check state, orders,
fills, or balances when an action may have partially applied.

## Global Rules

1. **Do not retry account-changing actions** after unknown outcome, timeout
   after broadcast, or deferred policy. Report uncertainty and inspect the
   resulting state.
2. **Do retry only** when the failure is clearly pre-broadcast validation (bad
   args, ambiguous symbol, amount too small) **and** the user re-confirms a
   corrected action.
3. Surface the exact CLI/platform error message and code when present.
4. Never double-`deposit` or double-`withdraw` to “fix” a hang.

## Common Codes and Conditions

| Code / condition | Meaning | Agent action |
| --- | --- | --- |
| `HYPERLIQUID_SYMBOL_AMBIGUOUS` | Multiple markets match the coin | Present `data.candidates`, ask the user to pick, then use the selected candidate directly without resolving again |
| `HYPERLIQUID_SYMBOL_NOT_FOUND` | No market for coin/dex | Try full `dex:COIN`, `--dex default`, or `markets`; do not invent `assetId` |
| `HYPERLIQUID_SYMBOL_DEX_MISMATCH` | Coin prefix conflicts with `--dex` | Align prefix and `--dex`, or use only one form |
| `HYPERLIQUID_SYMBOL_INVALID` | Bad selector (e.g. coin `default:…`) | Use `--dex default` instead of embedding `default:` in coin |
| `HYPERLIQUID_DEPOSIT_AMOUNT_TOO_SMALL` | Deposit under 5 USDC | Refuse; ask for at least 5 USDC |
| `HYPERLIQUID_BUILDER_FEE_APPROVAL_REQUIRED` | A perpetual order needs authorization for the fixed additional `0.05%` transaction fee | The order was not submitted. Briefly request authorization using the exact user-facing prompt in `SKILL.md`, run `approve-builder-fee` after consent, then obtain fresh confirmation before retrying the order |
| Fee status check fails or returns an unknown value | Authorization cannot be established safely | Stop before order confirmation; report the status error and do not submit an order as a probe |
| CLI: `--network is not supported` | Network override attempted | Remove `--network`; mainnet only |
| `HYPERLIQUID_API_PARTIAL_SUCCESS` | Some batch legs succeeded | Report partial; reconcile with `orders` / `state` / `order-status`; do not resubmit whole batch blindly |
| `HYPERLIQUID_API_ERROR` | Venue rejected the action | Report venue message; fix inputs with user; re-confirm if retrying |
| `HYPERLIQUID_REQUEST_INVALID` | Payload failed validation (extra keys, bad types, size/price) | Fix body (wire format, types); re-confirm |
| `HYPERLIQUID_TRANSPORT_ERROR` / timeouts | Network or gateway issue | If pre-broadcast likely: may retry after user confirm. If deposit/withdraw/order may have submitted: **do not** auto-retry; reconcile |
| Policy deferred / manual approval | Wallet policy needs approval | Explain reason; wait for approval path; do not spam resubmit |
| Insufficient margin / balance | Not enough HL collateral or Arbitrum USDC | Show `state` and/or Arbitrum USDC balance; propose fund or transfer steps |
| Pass either `--body-json` or `--body-file` | Both body inputs set | Use exactly one |
| Invalid boolean / integer flags | Bad CLI args | Correct flag values; re-run only after user intent still holds |

## Symbol Failures

- Ambiguous: present `data.candidates`; after the user picks, use its `coin`,
  `dex`, `assetId`, and `szDecimals` directly. Do not resolve it again.
- Not found: try full `dex:COIN`, `markets --dex`, or ask for the exact ticker.
- Never invent an `assetId` when resolve fails.

## Deposit / Withdraw Failures

| Situation | Action |
| --- | --- |
| Amount under 5 USDC | Stop before or after platform reject; request valid amount |
| Insufficient Arbitrum USDC or gas | Report shortage; do not attempt smaller blind retries without user intent |
| Bridge / broadcast unknown | Report uncertainty; include any `txHash` / request id; **do not redeposit** |
| Withdraw pending settlement | Report pending; later check Arbitrum USDC only when user asks |

## Order Failures

| Situation | Action |
| --- | --- |
| Bad wire fields | Fix using [order-wire-format.md](order-wire-format.md) |
| Wrong size decimals | Re-read `szDecimals` from `symbol` |
| Margin insufficient | Show `state`; suggest reduce size, transfer collateral, or deposit |
| Leverage change rejected | Report; leave leverage as-is unless user chooses another path |
| Cancel missing oid | Refresh `orders --kind open`; do not invent oids |

### Transaction fee authorization required

The primary flow is to run `builder-fee-status` before confirming a perpetual
order as described in [preflight.md](preflight.md). If an order still returns
`HYPERLIQUID_BUILDER_FEE_APPROVAL_REQUIRED`:

1. Stop. The rejected order was not submitted.
2. Use only the brief transaction-fee wording and exact consent prompt from
   `SKILL.md` unless the user asks for details.
3. Use the exact fee consent prompt in `SKILL.md`.
4. Only after an explicit yes, run `purr hyperliquid approve-builder-fee` and
   report `approved` or `already_approved`.
5. Re-present the rejected order parameters and obtain a fresh order
   confirmation before submitting it again. Never auto-retry it.

Never say “builder fee” to the user or request fee/builder parameters. There is
no CLI revoke command.

## Policy Failures

- If wallet policy denies or defers: quote the reason; do not bypass.
- If signing errors: report and stop; do not fall back to local keys.

## Reconciliation Cheatsheet

```bash
purr hyperliquid state --kind both [--dex <dex>]
purr hyperliquid orders --kind open [--dex <dex>]
purr hyperliquid order-status --oid <oid-or-cloid>
purr hyperliquid fills --start-time <ms>
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
```

Use these after any uncertain action before claiming success or opening a new
risk-increasing order.
