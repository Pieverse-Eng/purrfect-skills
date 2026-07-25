# Errors and reconcile policy

The platform returns a stable `code`. Match on the code, not the message.

## The one rule that matters most

**A failed write and an unknown write are different things.** If you cannot
tell whether an action was applied, treat it as *possibly applied*. Retrying a
possibly-applied order is how you end up with two positions.

Unknown-state codes — **never auto-retry**:

| Code | Meaning |
| --- | --- |
| `LIGHTER_SUBMIT_UNKNOWN` | Submission outcome unknown |
| `LIGHTER_PREVIOUS_SUBMISSION_UNKNOWN` | An earlier submission is unresolved |
| `LIGHTER_PREVIOUS_SUBMISSION_RESOLVED` | An earlier submission already landed |
| `LIGHTER_REQUEST_ALREADY_EXISTS` | This request was already accepted |
| `LIGHTER_NONCE_LOCK_NOT_HELD` / `LIGHTER_NONCE_LOCK_RELEASE_FAILED` | Concurrent write; ordering unclear |
| a client timeout on a write | Platform may still have applied it |

Reconcile instead: `active-orders`, `inactive-orders`, `trades`, `positions`,
`requests`, `request-status`. Report what you actually observe, then ask the
user how to proceed.

`LIGHTER_REQUEST_HASH_MISMATCH` means you re-sent a request id with different
content — do not "fix" it by mutating parameters and retrying; investigate.

## Gating and credentials

**Read `purr lighter account` before concluding a credential error is terminal.**
During onboarding these codes are expected states, not failures — see the
readiness table in [preflight.md](preflight.md).

| Code | Action |
| --- | --- |
| `LIGHTER_TRADING_DISABLED` | Integration off → confirm, then `enable`. Do not retry the original command first. |
| `LIGHTER_CREDENTIAL_NOT_FOUND` | If `account.status` is `account_discovered`, this is **normal** — the next write registers the key. Only terminal if the account is already `ready`/`error`. |
| `LIGHTER_CREDENTIAL_UNVERIFIED` | Matches `verifying_key` → wait and re-read `account`, don't escalate |
| `LIGHTER_CREDENTIAL_VERIFY_FAILED` / `_UNAVAILABLE` | Verification genuinely failing → platform-side, stop |
| `LIGHTER_API_KEY_SLOTS_EXHAUSTED` | No key slots left → platform-side, stop |
| `LIGHTER_WALLET_MISMATCH` | Wallet does not match the credential → stop, escalate |

Never ask the user to paste an API private key into chat.

## Transient — safe to wait and re-read

| Code | Action |
| --- | --- |
| `LIGHTER_INITIALIZING` | Signer starting; wait, re-read status. Do **not** resubmit a write. |
| `LIGHTER_SIGNER_UNAVAILABLE` / `LIGHTER_SIGNER_ERROR` | Signer trouble; re-read state before any retry |
| `LIGHTER_REQUEST_TIMEOUT` on a **read** | Safe to retry (reads are 20s, idempotent) |

## Input errors — fix the input, do not retry unchanged

| Code | Fix |
| --- | --- |
| `LIGHTER_MARKET_NOT_FOUND` | Wrong symbol or wrong `--market-type`; check `markets` |
| `LIGHTER_MARKET_DECIMALS_MISSING` | Market metadata incomplete; do not guess precision |
| `LIGHTER_DECIMAL_INVALID` / `LIGHTER_DECIMAL_PRECISION_UNSUPPORTED` | Too many decimals; re-round to the market's decimals |
| `LIGHTER_AMOUNT_OUT_OF_RANGE` | Size outside venue limits |
| `LIGHTER_PRICE_OUT_OF_RANGE` | Price outside venue limits — on a market order this usually means your bound is unreasonable |
| `LIGHTER_PNL_TIME_RANGE_INVALID` | Bad start/end/countBack combination |
| ambiguous-market CLI error | Symbol is dual-listed; ask the user perp or spot ([symbols.md](symbols.md)) |

## Deposit / withdraw

| Code | Action |
| --- | --- |
| `LIGHTER_DEPOSIT_AMOUNT_TOO_SMALL` | Below the **chain's** minimum — Ethereum mainnet (`1`) is 1 USDC, every other chain is 5 USDC via CCTP. Read `minAmount` from `deposit-networks`; do not assume a flat 1 USDC. |
| `LIGHTER_DEPOSIT_CHAIN_UNSUPPORTED` | Check `deposit-networks` |
| `LIGHTER_DEPOSIT_ALREADY_IN_PROGRESS` | One in flight; check `deposits`, wait |
| `LIGHTER_DEPOSIT_NOT_FOUND` / `LIGHTER_DEPOSIT_REQUIRED` | Wrong request id, or no funds deposited yet |
| `LIGHTER_APPROVAL_NOT_APPROVED` / `_INVALID` / `_UNAVAILABLE` / `_TX_HASH_MISSING` / `_RESUME_IN_PROGRESS` | On-chain approval leg; check `requests`, do not resubmit the deposit |
| `LIGHTER_INTENT_ADDRESS_INVALID` | Bad destination; stop |
| `LIGHTER_SEND_TX_REJECTED` | Chain rejected it; report the reason, do not blind-retry |

## Reporting to the user

- Say what state you verified, not what you assume. "The submit timed out; I
  checked open orders and trades and see no order — nothing was placed" is
  useful. "It failed" is not.
- Never present an unverified write as done.
- When you stop on a platform-side blocker (credentials, key slots), say exactly
  what needs configuring so the user can act.
