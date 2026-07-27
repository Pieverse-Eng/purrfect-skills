# Errors and failure policy

Prefer stopping and explaining over inventing retries. After any write with an
unknown outcome, reconcile state before acting again.

## Global rules

1. **Do not retry account-changing actions** after unknown submit, write
   timeout, deferred policy, or partial success. Report uncertainty and inspect
   `requests`, deposits, orders, positions, or balances.
2. **Do retry only** when the failure is clearly pre-submit validation (bad
   args, ambiguous market, amount too small) **and** the user re-confirms a
   corrected action.
3. Surface the exact CLI/platform error message and code when present.
4. Never double-`open-account`, double-`deposit`, or double-`withdraw` to “fix”
   a hang. The only exception is re-running the same `open-account` when the
   response has `nextAction: "resume_account_opening"` (see
   [deposit-withdraw.md](deposit-withdraw.md)).
5. Read timeouts (`LIGHTER_REQUEST_TIMEOUT` on 20s reads) are safe to re-run.
   Write timeouts are not automatic retries.

## Integration and readiness

| Code / condition | Meaning | Agent action |
| --- | --- | --- |
| `LIGHTER_TRADING_DISABLED` | Integration off | Explain; confirm → `enable`; then re-confirm original write if needed |
| `LIGHTER_DISABLE_REQUIRES_EMPTY_ACCOUNT` | Still has orders, positions, or non-USDC spot | Present required actions; flatten; re-confirm disable |
| `LIGHTER_DISABLE_HAS_ACTIVE_REQUESTS` | Pending deposits/actions | Wait for terminal requests; then disable |
| `LIGHTER_DISABLE_PREFLIGHT_INVALID_RESPONSE` | Could not verify empty account | Stop; do not force-disable |
| `LIGHTER_ACCOUNT_NOT_READY` | Account not opened | Guide `open-account` (CLI may include the command) |
| `LIGHTER_INITIALIZING` | Open/register still in progress | Poll `account` / `deposits` / `requests`; do not spam writes |
| `LIGHTER_CREDENTIAL_NOT_FOUND` / `LIGHTER_CREDENTIAL_UNVERIFIED` | Key not ready | Read `account` status first; wait through onboarding; escalate only if already `ready`/`error` |
| `LIGHTER_CREDENTIAL_VERIFY_FAILED` | Key verification failed | Platform recovery; never ask user for private keys |

## Markets and orders

| Code / condition | Meaning | Agent action |
| --- | --- | --- |
| `LIGHTER_MARKET_NOT_FOUND` | No match for symbol/type | Try other type, list `markets`, or ask for exact ticker |
| `LIGHTER_MARKET_AMBIGUOUS` | Spot and perp (or multiple) match | Ask user; pass `--market-type` |
| `LIGHTER_MARKET_INVALID_RESPONSE` | Resolve returned bad id | Report; do not invent market id |
| `LIGHTER_PARTNER_FEE_APPROVAL_REQUIRED` | Order blocked pending 0.05% transaction fee approval | Order not submitted. Consent per `SKILL.md` → `approve-partner-fee` → fresh order confirmation |
| `LIGHTER_PARTNER_FEE_STATUS_INVALID` | Fee status unreadable | Stop; do not probe with orders |
| `LIGHTER_INTEGRATOR_NOT_CONFIGURED` | Approve path unavailable | Report; platform config issue |
| Decimal / range validation errors | Bad size/price precision or limits | Re-read `market`; fix inputs; re-confirm |
| IOC + expiry flags | Invalid combination | Remove expiry for IOC market/limit |
| `LIGHTER_SEND_TX_REJECTED` | Venue rejected signed tx | Report; fix if user-correctable; re-confirm only if safe |
| `LIGHTER_SUBMIT_UNKNOWN` | Outcome unknown after submit | Reconcile via `requests` / orders; **do not** resubmit |
| `LIGHTER_PREVIOUS_SUBMISSION_RESOLVED` | Prior op finished differently | Read request status; do not assume success |
| `LIGHTER_REQUEST_ALREADY_EXISTS` | Active operation with same fingerprint | Inspect existing request; wait |

## Funding

| Code / condition | Meaning | Agent action |
| --- | --- | --- |
| `LIGHTER_DEPOSIT_AMOUNT_TOO_SMALL` | Under per-chain minimum | Ask for ≥ 1 USDC (ETH) or ≥ 5 USDC (others) |
| `LIGHTER_DEPOSIT_ALREADY_IN_PROGRESS` | Same deposit mid-flight | Watch `deposit-status`; do not start another |
| `LIGHTER_CROSS_CHAIN_DEPOSIT_ALREADY_IN_PROGRESS` | Another CCTP leg active | Wait on deposits ledger |
| `LIGHTER_DEPOSIT_NOT_FOUND` | Unknown request id | Verify id; do not invent reconcile targets |
| `LIGHTER_DEPOSIT_BRIDGE_FAILED` / source tx reverted | Bridge/source failed | Report terminal error; new deposit only with user intent |
| Policy deferred / `LIGHTER_APPROVAL_NOT_APPROVED` | Human wallet policy pending | Explain; observe deposits; **do not** re-create |
| `LIGHTER_WITHDRAW_AMOUNT_TOO_SMALL` | Secure withdraw under 1 USDC | Increase amount |
| `LIGHTER_FAST_WITHDRAW_AMOUNT_TOO_SMALL` | Fast withdraw under 4 USDC after fee | Increase amount or use secure withdraw |
| `LIGHTER_FAST_WITHDRAW_LIMIT_EXCEEDED` | Over venue cap | Reduce size or split after user confirms |

## Timeouts and transport

| Code / condition | Meaning | Agent action |
| --- | --- | --- |
| `LIGHTER_REQUEST_TIMEOUT` on read/preview | 20s client timeout | Safe to retry read/preview |
| Write hang / unknown | May have submitted | Use `requests` / `deposit-status`; never blind retry |
| `LIGHTER_TRANSPORT_ERROR` / `LIGHTER_HTTP_ERROR` | Network or upstream | If pre-submit likely, may retry after confirm; if post-submit possible, reconcile only |

## Market ambiguity handling

When the CLI reports ambiguous markets, list the candidates (symbol, type, id)
and ask which one. After the user picks, use that market id / type for the rest
of the workflow without guessing again.

## Order failures

| Situation | Action |
| --- | --- |
| Missing or bad market type | Re-resolve with explicit `--market-type` |
| Market price without depth | Pull depth; ask for bound |
| Insufficient margin | Show balances/positions; propose smaller size, margin add, or deposit |
| Cancel missing index | Refresh `active-orders` |
| Transaction fee 428 (`LIGHTER_PARTNER_FEE_APPROVAL_REQUIRED`) | Fee consent flow, then **new** order confirmation |

## What never to do

- Invent market ids, order indexes, or request ids
- Auto-enable trading or auto-approve the transaction fee
- Treat `balances` readiness objects as empty portfolios
- Claim fills or completed withdrawals from submit alone
- Ask the user to paste a Lighter API private key
