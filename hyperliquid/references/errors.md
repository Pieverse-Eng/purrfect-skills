# Errors and Failure Policy

Prefer stopping and explaining over inventing retries. Check state, orders,
fills, or balances when an action may have partially applied.

## Global Rules

1. Do not retry account-changing actions after an unknown outcome, timeout
   after broadcast, deferred policy, or partial success. Reconcile first.
2. A CLI argument error occurs before a platform request. Correct it only from
   known user intent; never guess a missing value, discard an option silently,
   switch order type, or fall back to a raw payload.
3. If corrected execution parameters differ from the confirmed action, present
   the complete correction and obtain confirmation again.
4. Surface the exact CLI/platform error and code when present.
5. Never double-deposit or double-withdraw to fix a hang.

## Common Codes and Conditions

| Code / condition | Meaning | Agent action |
| --- | --- | --- |
| `HYPERLIQUID_TRADING_DISABLED` | Trading integration is off; exchange routes are blocked | Explain; confirm `enable`; require fresh confirmation before retrying account-changing work |
| `HYPERLIQUID_TRADING_DISABLE_BLOCKED` | Open positions or orders prevent disable | Present blockers; close/cancel exposure; re-confirm disable |
| `HYPERLIQUID_TRADING_DISABLE_CHECK_UNAVAILABLE` | Platform could not verify exposure | Stop; inspect `state` / `orders` / `snapshot`; do not force-disable |
| `HYPERLIQUID_SYMBOL_AMBIGUOUS` | Multiple markets match | Present candidates and wait for selection |
| `HYPERLIQUID_SYMBOL_NOT_FOUND` | No matching market | Try exact `dex:COIN`, `--dex default`, or `markets`; never invent an asset ID |
| `HYPERLIQUID_SYMBOL_DEX_MISMATCH` | Coin prefix conflicts with `--dex` | Align them or use one selector |
| `HYPERLIQUID_SYMBOL_INVALID` | Invalid selector | Correct the selector; do not guess a market |
| `HYPERLIQUID_DEPOSIT_AMOUNT_TOO_SMALL` | Deposit is below 5 USDC | Request at least 5 USDC |
| `HYPERLIQUID_BUILDER_FEE_APPROVAL_REQUIRED` | New order requires the fixed additional fee authorization | The order was not submitted; follow the consent fallback below |
| `HYPERLIQUID_MIXED_ORDER_ASSET_CLASSES_UNSUPPORTED` | One request mixes perp and spot | Stop; typed commands do not expose a mixed batch |
| Fee status fails or is unknown | Authorization cannot be established | Stop; do not use an order as a probe |
| `HYPERLIQUID_API_PARTIAL_SUCCESS` | Some multi-leg orders succeeded | Report exact legs; reconcile frontend orders, state, and statuses; do not resubmit the whole action |
| `HYPERLIQUID_API_ERROR` | Venue rejected the action | Report the venue message; fix only with user intent and re-confirm changed parameters |
| `HYPERLIQUID_REQUEST_INVALID` | Platform rejected the CLI-built request | Report as an implementation/compatibility error; never bypass the CLI with raw JSON |
| `HYPERLIQUID_TRANSPORT_ERROR` / timeout | Submission outcome may be unknown | Do not retry a possible write; reconcile first |
| Policy deferred / manual approval | Wallet policy requires another approval path | Explain and wait; do not spam resubmit |
| Insufficient margin / balance | Target account lacks collateral | Show state and offer smaller size, transfer, or deposit choices |
| `--network is not supported` | Network override was attempted | Remove `--network`; mainnet only |

## Typed CLI Validation

The CLI rejects these before sending a platform request:

| Error | Response |
| --- | --- |
| Missing value or required argument | Obtain the actual value; do not substitute `true` or a default |
| Duplicate option | Resolve which value the user intends |
| Unknown option | Check [order-commands.md](order-commands.md); do not silently delete a meaningful parameter |
| Unexpected positional argument | Rebuild using named options only |
| Invalid side, TIF, execution, boolean, integer, decimal, OID, or cloid | Surface the exact invalid value and accepted form |
| Both worst-price and limit-price forms | Preserve the requested execution mode and pass only its matching option |
| Missing market worst price | Ask for an explicit execution boundary |
| Worst price on the wrong side of the trigger | Stop; do not reverse or alter it automatically |
| TP/SL relationship invalid for the position side | Recheck long/short intent and trigger values |
| Removed `order` or `modify` command | Select the matching typed command; never retry with a body |
| `--body-json` / `--body-file` on cancel | Use `--asset` plus numeric `--oid`, or `cancel-by-cloid` |

Syntax correction alone does not authorize a changed trade. If the effective
order remains exactly what the user confirmed, correct only the syntax; if any
field or execution behavior changes, confirm again.

## Order Lifecycle Failures

| Situation | Action |
| --- | --- |
| Wrong size precision | Re-read `szDecimals` from `symbol` |
| Margin insufficient | Show target `state`; offer reduce size, transfer, or deposit |
| Leverage change rejected | Stop; do not submit an order whose confirmation depended on that leverage |
| Missing target OID | Refresh `orders --kind frontend`; do not infer one |
| Order no longer open | Check `order-status`, `historical`, and `fills` |
| Filled entry cannot be modified/cancelled | Manage its resulting position or open protection orders |
| Partially filled entry | Modify/cancel only the open remainder; protect the filled position separately |
| Wrong modify command for order type | Stop and choose the matching limit, SL, or TP modify command |
| Bracket/protection group requested as one modify | Find child OIDs and modify each still-open leg separately |

Modify commands replace a complete order. If current fields cannot be
established from `orders --kind frontend` or `order-status`, do not guess them.

## Transaction Fee Authorization Required

The primary flow is `builder-fee-status` before every order-placement command.
If placement still returns
`HYPERLIQUID_BUILDER_FEE_APPROVAL_REQUIRED`:

1. Stop. The rejected order was not submitted.
2. Use the brief fee wording and exact consent prompt from `SKILL.md`.
3. After explicit consent, run `purr hyperliquid approve-builder-fee`.
4. Present the rejected order again and obtain fresh confirmation before
   submitting it.

Never expose internal builder details or request fee parameters. There is no
CLI revoke command.

## Deposit / Withdraw Failures

| Situation | Action |
| --- | --- |
| Amount under 5 USDC | Request a valid amount |
| Insufficient Arbitrum USDC or gas | Report the shortage; do not blind-retry a smaller amount |
| Bridge or broadcast outcome unknown | Include any tx hash, request ID, or nonce; do not resubmit |
| Withdraw status `pending` | Report settling; do not withdraw again |
| Withdraw status `arrived` | Report amount, fee, and tx hash |
| No captured withdraw nonce | Reconcile state and Arbitrum balance; never invent a nonce |

## Policy Failures

- If wallet policy denies or defers, report the reason and do not bypass it.
- If signing fails, report and stop; do not fall back to local keys.

## Reconciliation

```bash
purr hyperliquid status
purr hyperliquid snapshot
purr hyperliquid state --kind both [--dex <dex>]
purr hyperliquid orders --kind frontend [--dex <dex>]
purr hyperliquid orders --kind historical
purr hyperliquid fills [--start-time <ms>]
purr hyperliquid order-status --oid <oid-or-cloid>
purr hyperliquid withdraw-status --nonce <nonce>
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
```

Use these after uncertain actions before claiming success or opening new risk.
