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

Before proposing disable, inspect:

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

## First use: open-account

```bash
purr lighter deposit-networks
purr wallet balance --chain-type ethereum --chain-id <source> --token USDC
purr wallet balance --chain-type ethereum --chain-id <source>   # native gas
purr lighter open-account --amount <USDC> --source-chain-id <1|42161|8453|43114|999> [--route-type perps]
```

- `open-account` owns **initial funding + credential setup**. It is not the same
  as a later `deposit`.
- USDC **and native gas** must already sit on the chosen source chain in the
  instance TEE wallet.
- Minimums: Ethereum mainnet (`1`) **1 USDC**; other chains **5 USDC**. Confirm
  with `deposit-networks` / `minAmount`.
- `--route-type` currently defaults to `perps` (platform only accepts `perps`).
- Re-run only when `nextAction` is `resume_account_opening`. Policy deferred →
  observe deposits; never open a second funding request. Details in
  [deposit-withdraw.md](deposit-withdraw.md).

After open succeeds (or while initializing), re-check:

```bash
purr lighter account
purr lighter deposits --limit 5
```

Ordinary `deposit` before open fails with `LIGHTER_ACCOUNT_NOT_READY`; the CLI
suggests the matching `open-account` command.

## Transaction fee

Fixed additional **0.05%** transaction fee on orders.

```bash
purr lighter partner-fee-status
purr lighter approve-partner-fee
```

| Status | Meaning |
| --- | --- |
| `not_configured` | Fee authorization not required for orders |
| `approval_required` | Approval missing or insufficient for the fixed 0.05% fee |
| `approved` | Current approval covers maker/taker spot and perp |
| `expired` | Prior approval past `approvalExpiry` |

When required, check status **before** order confirmation or any
account-changing preparation for an order. Consent language lives in
`SKILL.md` (Transaction Fee Authorization). `approve-partner-fee` is
account-changing and needs its own yes.

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

## Silent preflight checklist

Run without narrating the plan:

1. `status` — enable if needed (with confirmation).
2. `account` — if not `ready`, follow open / wait / escalate branches above.
3. For orders: resolve market, depth, balances/positions, partner-fee-status.
4. Confirm the user-facing action, then submit.
