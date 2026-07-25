# Preflight — integration, credentials, account

Everything under the Lighter gateway requires the trading integration to be
enabled. Only `status`, `enable`, and `disable` work while it is off.

## Integration

```bash
purr lighter status      # current integration state
purr lighter enable      # account-changing — confirm first
purr lighter disable     # account-changing — confirm first
```

`status` is the correct first call whenever you are unsure. Never `enable`
silently: state what enabling does, get an explicit yes, then run it.

If any gateway command returns `LIGHTER_TRADING_DISABLED`, stop and go through
the enable flow — do not retry the original command first.

## Readiness

```bash
purr lighter sdk-status        # signer/SDK readiness
purr lighter system-status     # venue status
purr lighter system-info
purr lighter system-config
```

`LIGHTER_INITIALIZING` means the signer is still starting: wait and re-read,
do not resubmit a write.

## First use — read `account`, then branch on its status

**`purr lighter account` is the readiness call**, not just a balance view. On a
fresh instance it tells you exactly which onboarding step is outstanding. Run
this before `sdk-status` or `balances` — those answer narrower questions and
will not tell you *why* trading is unavailable.

```bash
purr lighter status            # 1. integration enabled?
purr lighter account           # 2. readiness — branch on .status
purr lighter deposit-networks  # 3. only when a first deposit is needed
```

| `account.status` | What it means | What to do |
| --- | --- | --- |
| `deposit_required` | No Lighter account for this TEE wallet yet | Tell the user a **first USDC deposit creates the account**. The response carries `requiresFirstDeposit`, `nextAction: deposit`, and `minimumDeposit` (`ethereumMainnet: 1`, `crossChain: 5`). |
| `initializing` | Deposit seen, account still being created | Wait; poll `deposits` / `requests`. Do **not** resubmit. |
| `account_discovered` | Account exists, no API key registered yet | Normal. The **next write registers the key automatically** — no manual credential step. |
| `verifying_key` | Key registered, verification pending | Wait and re-read `account`. |
| `ready` | Credential verified | Trading is available. |
| `error` | Key registration failed | Stop and report; check the returned `state` for the reason. |

The key point: `account_discovered` and `verifying_key` are **normal states in
the onboarding sequence**, not failures. Do not tell the user something is
broken because a credential is not yet verified — say which step is pending.

## When a credential error *is* terminal

`purr lighter` exposes no command to set an account index, API key index, or API
private key — the CLI has only `status` / `enable` / `disable`. So if a
credential error appears **outside** the onboarding sequence above — the account
is `ready` or `error` and you still get `LIGHTER_CREDENTIAL_VERIFY_FAILED`,
`LIGHTER_CREDENTIAL_VERIFY_UNAVAILABLE`, `LIGHTER_WALLET_MISMATCH`, or
`LIGHTER_API_KEY_SLOTS_EXHAUSTED` — it needs platform-side attention:

1. Stop. Do not attempt a CLI workaround, and **never** ask the user to paste a
   private key into chat.
2. Say which state you observed from `account` and what needs configuring.
3. Re-check with `purr lighter account` afterwards.

Seeing `LIGHTER_CREDENTIAL_NOT_FOUND` while `account.status` is
`account_discovered` is *expected* — proceed with the write that registers it,
after the usual confirmation.

## Account reads (no confirmation needed)

```bash
purr lighter account          # account summary
purr lighter balances
purr lighter positions
purr lighter limits           # account limits
purr lighter pnl [--resolution 1h] [--start-timestamp <unix>] [--end-timestamp <unix>] [--count-back <n>]
purr lighter orders
purr lighter active-orders
purr lighter inactive-orders
purr lighter transactions [--offset <n>] [--limit <n>]
purr lighter transaction --tx-hash <hash>
purr lighter l1-transaction --l1-tx-hash <hash>
purr lighter requests [--limit <n>]
purr lighter request-status --request-id <id>
```

Check `balances` and `positions` before sizing any order, and `limits` before a
large one. Read commands use a 20s client timeout and are safe to retry.

## Before an order — the short checklist

1. `status` — integration enabled?
2. `account` — is `.status` `ready`? If not, resolve the onboarding step above
   before promising the user a trade.
3. `market --market <SYM> --market-type <perp|spot>` — market exists, and note
   its size/price decimals.
4. `order-book-depth --market <SYM> --market-type <t>` — derive the price bound
   (mandatory for market orders; see [trading.md](trading.md)).
5. `balances` / `positions` — is there collateral for this, and does it change
   an existing position?
6. Confirm with the user, then submit.

There is **no fee-authorization step on Lighter**. Do not prompt for one.
