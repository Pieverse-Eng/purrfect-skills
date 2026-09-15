# Preflight — integration, readiness, account

Everything under the Lighter gateway requires the trading integration to be
enabled. Only `status`, `enable`, and `disable` work while it is off.

## Integration

```bash
purr lighter status
purr lighter enable
purr lighter disable
```

| Command | Purpose |
| --- | --- |
| `status` | Whether Lighter Trading is enabled for this instance |
| `enable` | Turn on Lighter Trading so gateway routes work; confirm first |
| `disable` | Turn off Lighter Trading; blocked until the account is empty |

Run `status` silently at the start of any Lighter workflow.

| Result | Action |
| --- | --- |
| `enabled: true` | Continue |
| `enabled: false` | Explain, confirm → `enable`. Never enable silently |
| Error | Report and stop; do not assume enabled |

### Disable requires an empty account

The platform refuses disable while the Lighter account still has:

- open / active orders
- open positions
- non-USDC spot balances
- non-terminal deposit or account-action requests

Accounts that have never been opened can be disabled directly.

For an opened, ready account, inspect the relevant blockers before proposing
disable (unopened accounts skip credential-dependent reads):

```bash
purr lighter active-orders
purr lighter positions
purr lighter balances
purr lighter deposits --limit 10
purr lighter requests --limit 10
```

Present blockers from `LIGHTER_DISABLE_REQUIRES_EMPTY_ACCOUNT` or
`LIGHTER_DISABLE_HAS_ACTIVE_REQUESTS`, flatten exposure, then re-confirm disable.
`disable` does not cancel or close anything for you.

## Account readiness

```bash
purr lighter account
purr lighter sdk-status
purr lighter system-status
purr lighter system-info
purr lighter system-config
purr lighter layer1-basic-info
purr lighter withdrawal-delay
```

**`account` is the readiness call.** On a fresh instance it tells you which
onboarding step is outstanding. Prefer it before promising any trade or
interpreting empty balances.

| `account.status` | Meaning | Next step |
| --- | --- | --- |
| `account_opening_required` | No Lighter account for this TEE wallet | Confirm → `open-account` with initial USDC. Response includes `nextAction: "open_account"` and `minimumDeposit` |
| `initializing` | Opening deposit / registration still reconciling | Wait; poll `account`, `deposits`, `requests`. Do not resubmit blindly |
| `account_discovered` | Account exists; key registration can continue | Platform continues registration; wait / resume open if `nextAction` says so |
| `verifying_key` | API key registration or verification in progress | Wait and re-read `account` |
| `ready` | Account + credential ready | Trading and funding routes work |
| `error` | Last automatic step failed | Report `state` / error; escalate platform recovery — never ask for API keys |

When opening is still in progress, async responses may include
`nextAction: "resume_account_opening"` and (from the CLI) a `resumeCommand`.
Re-run the same `open-account` parameters only when the platform/CLI indicates
resume — identical active operations resume rather than double-funding.

## Select Checks by Readiness and Operation

Read `status`, then inspect `account.status` before scheduling dependent reads.
A successful CLI exit does not imply `ready`; do not chain credential-dependent
commands after `account` with `&&` without inspecting its JSON status.

| State / task | Checks and preparation |
| --- | --- |
| `account_opening_required` | Read [deposit-withdraw.md](deposit-withdraw.md); select a supported source and verify wallet USDC/gas. Prepare initial funding and public market parameters. Skip `balances`, `positions`, order reads, and `partner-fee-status` until ready. |
| Opening/registration in progress | Observe the existing account/deposit request using the readiness table above. No duplicate funding or credential-dependent trading calls. |
| `ready`, prepare an order | Resolve market/depth, relevant balances/positions/orders, and `partner-fee-status`. Follow fee consent in [SKILL.md](../SKILL.md#transaction-fee-authorization). |
| `ready`, cancel or inspect orders | Read relevant active orders; no funding or order fee approval needed for cancellation. |
| `ready`, deposit/withdraw | Follow the funding reference; inspect source funds or withdrawal balance/preview for that operation. |
| Account error or unreadable readiness | Report the blocker; do not assume readiness or zero balances. |

After integration is enabled, independent public market reads can run alongside
account or wallet checks; they do not require account opening. Batch independent
reads, but keep readiness decisions and dependent writes sequential. Reuse
verified market metadata and command syntax within the workflow; refresh
volatile quotes, balances, and order state when needed for execution.

`open-account` owns initial funding and credential setup. Ordinary `deposit`
requires an opened account. Neither is authorized by read-only preparation.
Fee status can be checked only after readiness; before then, describe that
remaining prerequisite without attempting the call or claiming approval.

## Portfolio reads

```bash
purr lighter balances
purr lighter positions
purr lighter limits
purr lighter pnl --resolution <1h|1d> --start-at <rfc3339> --end-at <rfc3339> --count-back <n>
purr lighter orders
purr lighter active-orders
purr lighter inactive-orders
purr lighter transactions [--offset <n>] [--limit <n>]
purr lighter transaction --tx-hash <hash>
purr lighter l1-transaction --l1-tx-hash <ethereum-l1-tx-hash>
purr lighter requests [--limit <n>]
purr lighter request-status --request-id <id>
```

Notes:

- `balances` / `positions` share the account readiness handler. Before `ready`,
  inspect `.status` instead of treating the payload as empty holdings.
- **`orders` and `active-orders` are the same call** (live working orders only).
  Prefer one of them. Past fills / completed orders: `inactive-orders` and
  `trades` — not `orders`.
- PnL resolutions accepted on mainnet today: **`1h`**, **`1d`** only. Timestamps
  must be RFC 3339 with timezone (`Z` or offset).
- Read paths use a **20s** client timeout and are safe to retry. Writes wait for
  the platform and must not be auto-retried after timeout.
