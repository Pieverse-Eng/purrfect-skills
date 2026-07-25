# Preflight — integration, credentials, account

Everything under the Lighter gateway requires the trading integration to be
enabled. Only `status`, `enable`, and `disable` work while it is off.

## Integration

```bash
purr lighter status      # current integration state
purr lighter enable      # account-changing — confirm first
purr lighter disable     # account-changing — confirm first, see below
```

`status` is the correct first call whenever you are unsure. Never `enable`
silently: state what enabling does, get an explicit yes, then run it.

### `disable` strands live exposure — check before you flip it

`disable` only flips the integration flag. It does **not** cancel orders, does
**not** close positions, and does **not** settle anything. Afterwards only
`status` / `enable` / `disable` work, so the agent and dashboard can no longer
read those orders and positions — the exposure stays live on Lighter while you
lose the ability to see or manage it through this gateway.

Before disabling:

```bash
purr lighter active-orders
purr lighter positions
purr lighter requests --limit 10   # unresolved deposits/withdrawals
```

Then either resolve the exposure first, or state it back explicitly — "you have
N open orders and a position of X; disabling cancels and closes nothing, and
you will not be able to see or manage them here until you re-enable" — and get
acknowledgement of that specific list before running `disable`.

If any gateway command returns `LIGHTER_TRADING_DISABLED`, stop and go through
the enable flow — do not retry the original command first.

## Readiness

```bash
purr lighter sdk-status        # signer/SDK readiness
purr lighter system-status     # venue status
purr lighter system-info
purr lighter system-config
```

`LIGHTER_INITIALIZING` is **not** only "the signer is starting". The platform
uses it while any of these is still in progress: deposit crediting, account
discovery, API-key registration, or signer setup. Recover by reading state, not
by retrying:

```bash
purr lighter account            # which onboarding step is outstanding
purr lighter deposits --limit 5
purr lighter requests --limit 5
```

Then wait. **Do not resubmit the write** — see [errors.md](errors.md).

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

## Credential errors — the five-step branch

Normal users never configure Lighter API credentials; the platform generates and
registers the key itself. So on **`LIGHTER_CREDENTIAL_NOT_FOUND` or
`LIGHTER_CREDENTIAL_UNVERIFIED`**, do not tell the user to go configure
something. Run the branch:

1. `purr lighter account`.
2. `deposit_required` → guide the first deposit (it creates the account).
3. `initializing` / `account_discovered` / `verifying_key` → **wait and
   reconcile** (`deposits`, `requests`). `account_discovered` is the normal
   pre-key state: the next confirmed write registers the key automatically.
4. Only if `account.status` is already `ready` or `error` **and** the credential
   still fails → escalate as platform-side recovery. That also covers
   `LIGHTER_CREDENTIAL_VERIFY_FAILED`, `LIGHTER_CREDENTIAL_VERIFY_UNAVAILABLE`,
   `LIGHTER_WALLET_MISMATCH` and `LIGHTER_API_KEY_SLOTS_EXHAUSTED`.
5. **Never ask the user for an API private key**, and never accept one pasted
   into chat. `purr lighter` has no command to set one — the CLI exposes only
   `status` / `enable` / `disable`.

When you do escalate, say which `account.status` you observed and what needs
attention, then re-check with `purr lighter account`.

## ⚠️ `balances` and `positions` are the same call as `account`

`GET /balances` and `GET /positions` both route to the **same
account-readiness handler** as `account`. Before the account is `ready` they
return a readiness object, not a balance or position collection:

```json
{ "status": "deposit_required", "nextAction": "deposit" }
```

So an agent that reads `balances` on a fresh instance and sees no array must not
conclude "the user has no funds" or "no open positions" — it has been handed a
*state*, not an empty portfolio. Check `.status` first; only trust
balance/position contents once it is `ready`.

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
