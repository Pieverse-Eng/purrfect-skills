# Errors and failure policy

Prefer stopping and explaining over inventing retries.

## Global rules

1. After an `*-execute` that may have started, resume with the **same**
   `--preview-id` and the same execute command. Resume when JSON `status` is
   `in_progress`, `broadcasted`, `chain_confirmed`, or `upstream_pending`.
   `replayed: true` means this already ran — report it.
2. After `set-referral` that may have started, resume with the same `--code`.
   There is no preview id.
3. **Do retry with a new preview** only when the failure is clearly
   pre-broadcast validation (bad flags, expired unconsumed preview, stale
   market, below minimum, missing approval) **and** the user re-confirms the
   corrected action.
4. Surface the exact CLI/platform `code` and message.
5. On an invalid `--sort`, `--status`, `--market-variant`, or `--resolution`,
   use the tables in this skill or `purr predict-fun help`, then retry that
   command once. A CLI-local reject means no HTTP request was sent.
6. After a MARKET execute, `order` showing `OPEN` / 0 filled while
   `positions` or `balances` already moved is Predict REST lag. Follow
   **Verify a MARKET fill** in [trading.md](trading.md).

## Common codes

| Code / condition | Meaning | Agent action |
| --- | --- | --- |
| `PREDICT_PREVIEW_EXPIRED` | Unconsumed preview older than TTL | New preview; new confirmation; then execute |
| `PREDICT_PREVIEW_NOT_FOUND` | Preview id does not exist | Re-preview if you never executed; if you did, reconcile with `orders` / `positions` |
| `PREDICT_PREVIEW_STALE` | Market, fees, tokens, or MARKET book moved | New preview from live book; new confirmation |
| `PREDICT_PREVIEW_ACTION_MISMATCH` / `PREDICT_PREVIEW_SCOPE_MISMATCH` | Execute route or cancel/approval mode does not match the preview | Use the matching `*-execute` for that preview |
| `PREDICT_ORDER_BELOW_MINIMUM` | Qty &lt; 0.01, value &lt; 0.9 USDT, or MARKET BUY spend &lt; 1 | Ask for a valid size |
| `PREDICT_INSUFFICIENT_LIQUIDITY` | Book cannot support the MARKET size/value | Show the book; reduce size or use LIMIT |
| `order` is `OPEN` / 0 filled, `positions` or `balances` already moved | Predict REST lag after a fill | `matches --market-id`, `activity`, wait a few seconds, re-read `order`. Check dust with `balances --market-id` |
| `PREDICT_INSUFFICIENT_BALANCE` | Not enough USDT or outcome tokens | Show `readiness` / `positions`; ask to fund or reduce |
| `PREDICT_APPROVAL_REQUIRED` | Protocol allowance/operator missing | `approval-preview` → confirm → `approval-execute` → **new** order/position preview → confirm → execute |
| `PREDICT_APPROVAL_ALREADY_SET` | Requested allowance/operator already matches | Skip `approval-execute`. Run a new order or position preview |
| `PREDICT_APPROVAL_AMOUNT_REQUIRED` | Exact ERC-20 approve needs `--amount` | Add amount or, only if the user asked, `--unlimited true` |
| `PREDICT_NO_APPROVAL_REQUIRED` | That operation has no steps | Continue without an approval execute |
| `PREDICT_MARKET_NOT_OPEN` / `PREDICT_INVALID_MARKET` | Market closed or payload unusable | Report the error, list candidates, and wait for the user to choose |
| `PREDICT_CANCEL_ALL_REQUIRES_BATCHING` | Open orders span more than one page | Cancel explicit `--order-hashes` batches of ≤ 25 |
| `PREDICT_NO_OPEN_ORDERS` | Nothing to cancel-all | Report; stop |
| `PREDICT_RISK_ACKNOWLEDGEMENT_REQUIRED` | Remove-from-book execute missing ack | Only if the user accepted the risk: add `--acknowledge-risk true` |
| `PREDICT_REMOVE_FROM_BOOK_REJECTED` | One or more hashes not removed | Report the per-hash results |
| `PREDICT_REFERRAL_ALREADY_SET` / `PREDICT_REFERRAL_LOCKED` | Different code set, or settings locked | Report and wait for the user |
| `PREDICT_INVALID_POSITION_ACTION` | Wrong position flags (for example `--amount` on a standard redeem) | Drop `--amount` unless `market` shows `isNegRisk` |
| `POLICY_DEFERRED` | Wallet policy parked the write | After approval, same `*-execute --preview-id` (or same `--code` for referral) |
| `PREDICT_ORDER_OUTCOME_UNKNOWN` / `PREDICT_BROADCAST_OUTCOME_UNKNOWN` | Submit/broadcast unconfirmed | Reconcile; same previewId only |
| `PREDICT_*_TRANSACTION_REVERTED` | On-chain revert | Show the returned txs |
| `PREDICT_STREAM_TOPICS_INVALID` / `PREDICT_STREAM_TOPIC_UNSUPPORTED` | Bad or too many topics | Use the allowlist; ≤ 8 unique |
| `PREDICT_STREAM_LIMIT_EXCEEDED` / `PREDICT_STREAM_CAPACITY_EXCEEDED` | Instance or process stream cap | Wait; close other streams; retry later |
| `PREDICT_RATE_LIMITED` / `PREDICT_PLATFORM_RATE_LIMITED` | Upstream or platform quota | Honor `Retry-After`; back off |
| `PREDICT_AUTH_REJECTED` | Predict rejected the platform JWT | Report the error |
| `PREDICT_TIMEOUT` / `PREDICT_NETWORK_ERROR` / `PREDICT_UPSTREAM_ERROR` | Transport / Predict down | If pre-execute: may retry the **read or preview**. If execute may have started: reconcile only |
| Unsupported / duplicate / positional argument | CLI rejected before HTTP | Fix flags from the skill tables or `purr predict-fun help` |
| Invalid `--sort` / `--status` / `--market-variant` / `--resolution` | Enum is not on that command | Use the table in [discovery.md](discovery.md) or [preflight.md](preflight.md), or `purr predict-fun help`, then retry once |

## Policy deferred

Wallet policy can park a write (`POLICY_DEFERRED`). After the user or
platform approves, resume the same `*-execute --preview-id` (or
`set-referral --code` for referral). A new preview is a second write. If later
`PREDICT_APPROVAL_NOT_APPROVED`, stop.

## Reconciliation

```bash
purr predict-fun readiness --market-id <id>
purr predict-fun orders --status OPEN
purr predict-fun order --order-hash <hash>
purr predict-fun positions --market-id <id>
purr predict-fun approvals --market-id <id> --operation TRADE --side BUY
purr predict-fun activity --first 10
purr wallet balance --chain-type ethereum --chain-id 56 --token USDT
```

Use these after any uncertain write before claiming success or opening more
risk.
