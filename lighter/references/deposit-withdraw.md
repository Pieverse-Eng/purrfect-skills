# Deposit and withdraw

Account-changing funding flows. Confirmation Contract applies to
`open-account`, `deposit`, `reconcile-deposit`, and withdraw execution
(`--yes`). Previews and status reads do not need confirmation.

Trading integration must be enabled. Native **USDC only**.

## Amount convention

All funding commands use **decimal USDC strings**:

| Command | Flag | Example for 10 USDC |
| --- | --- | --- |
| `open-account` | `--amount` | `10` |
| `deposit` | `--amount` | `10` |
| `withdraw` | `--amount` | `10` |
| `fast-withdraw` | `--amount` | `10` |

There is no `--amount-base-units` in this CLI.

## Deposit networks

```bash
purr lighter deposit-networks
```

| Source | `--source-chain-id` | Route | Minimum |
| --- | ---: | --- | ---: |
| Ethereum Mainnet | `1` | Direct gateway deposit | **1 USDC** |
| Arbitrum One | `42161` | Intent address + USDC transfer | **5 USDC** |
| Base | `8453` | Intent address + USDC transfer | **5 USDC** |
| Avalanche C-Chain | `43114` | Intent address + USDC transfer | **5 USDC** |
| HyperEVM | `999` | Intent address + USDC transfer | **5 USDC** |

Treat `deposit-networks` `minAmount` as source of truth. USDC must already be on
the source chain in the instance wallet; bridging from elsewhere is another
skill.

## Open account (first funding)

First use is **not** a normal deposit. USDC must already sit on the source chain,
and the wallet needs enough **native gas** on that chain for the funding
transaction(s).

```bash
# example preflight (chain id must match --source-chain-id)
purr wallet balance --chain-type ethereum --chain-id 8453 --token USDC
purr wallet balance --chain-type ethereum --chain-id 8453   # native gas

purr lighter open-account --amount 25 --source-chain-id 8453 [--route-type perps]
```

This path:

1. Sends the initial USDC from the TEE wallet
2. Creates / discovers the Lighter account for that L1 address
3. Generates and registers the platform-managed API key

### When to re-run `open-account` (do not double-fund)

| Signal | Action |
| --- | --- |
| Response has `nextAction: "resume_account_opening"` (CLI may add `resumeCommand`) | Re-run the **same** `open-account` args (amount + source chain). Platform resumes the active opening op |
| `POLICY_DEFERRED`, `LIGHTER_APPROVAL_NOT_APPROVED`, or other policy-parked state | **Do not** re-run. Observe only (below). Agent cannot approve policy |
| Timeout / unknown after submit, no resume signal | **Do not** re-run. Reconcile via `account` / `deposits` / `deposit-status` |
| Opening still `initializing` without resume signal | Wait and poll; do not invent a second open |

Blind re-runs can create a **second** funding request. The CLI does not send a
client `Idempotency-Key`, so do not treat a re-run as a safe generic retry.
Only re-run when the platform/CLI explicitly indicates resume (for example
`nextAction: "resume_account_opening"`); otherwise observe `deposits` /
`deposit-status` / `requests`.

Track progress:

```bash
purr lighter account
purr lighter deposits --limit 10
purr lighter deposit-status --request-id <id>
```

## Subsequent deposits

Before submitting, confirm the instance wallet has enough **USDC and native gas**
on the chosen source chain (ETH on Ethereum/Arbitrum/Base, AVAX on Avalanche,
etc.). USDC alone is not enough to broadcast the funding txs.

```bash
purr lighter deposit --amount 25 --source-chain-id 42161 [--route-type perps]
```

- Requires an already opened account; otherwise `LIGHTER_ACCOUNT_NOT_READY`
  (CLI suggests `open-account`).
- Below minimum → `LIGHTER_DEPOSIT_AMOUNT_TOO_SMALL`.
- In-flight same deposit → `LIGHTER_DEPOSIT_ALREADY_IN_PROGRESS`.
- Another cross-chain bridge still settling →
  `LIGHTER_CROSS_CHAIN_DEPOSIT_ALREADY_IN_PROGRESS`.

Track and recover:

```bash
purr lighter deposits [--limit <n>]
purr lighter deposit-status --request-id <id>
purr lighter reconcile-deposit --request-id <id>
```

`reconcile-deposit` is account-changing — confirm first. Use it for stuck
async credit recovery, not as a substitute for a new deposit.

### Policy vs on-chain approval

Deposits and account opening may wait on **TEE wallet policy** approval
(`POLICY_DEFERRED` / related codes). That is human approval of a parked wallet
action — the agent cannot approve it.

- Observe with `deposits` / `deposit-status` (not the action `requests` ledger
  alone).
- **Never** re-run `deposit` or `open-account` to “unstick” policy. After a
  human approves, keep observing the **same** request id; do not create a
  second funding request.
- The only intentional re-run of `open-account` is the resume row in the table
  above (`nextAction: "resume_account_opening"`).
- `LIGHTER_APPROVAL_TX_HASH_MISSING` refers to the on-chain ERC-20 approval leg,
  not wallet policy.

## Withdrawals

Two paths:

| Command | Destination | Minimum | Fee |
| --- | --- | --- | --- |
| `withdraw` (secure) | **Ethereum** TEE address | **1 USDC** | Protocol delay; check `withdrawal-delay` |
| `fast-withdraw` | **Arbitrum** TEE address | **4 USDC after fee** | Live transfer fee from venue |

### Preview then execute

Without `--yes`, both commands **preview only**:

```bash
purr lighter withdraw --amount 10
purr lighter fast-withdraw --amount 10
```

With `--yes`, the CLI sets `confirmed: true` and executes. Fast withdraw
**re-fetches a fresh fee quote** at execute time — the executed fee may differ
from an earlier preview. Always re-show the latest preview numbers in the
confirmation when possible.

```bash
purr lighter withdraw --amount 10 --yes
purr lighter fast-withdraw --amount 10 --yes
```

### Preflight

```bash
purr lighter withdrawal-delay
purr lighter balances
purr lighter account
```

Quote expected delay (secure) or fee + net amount (fast) before asking for yes.
Withdraw submit ≠ funds arrived. Track:

```bash
purr lighter requests --limit 10
purr lighter request-status --request-id <id>
purr lighter balances
```

Common failures:

- `LIGHTER_WITHDRAW_AMOUNT_TOO_SMALL` — secure under 1 USDC
- `LIGHTER_FAST_WITHDRAW_AMOUNT_TOO_SMALL` — under 4 USDC after fee
- `LIGHTER_FAST_WITHDRAW_LIMIT_EXCEEDED` — over venue limit

Never double-withdraw to fix an unknown.

## No transfer command

There is **no** `purr lighter transfer`. Do not invent one. Lighter accounts are
not managed with agent-side account-index transfers through this CLI. If the
user wants funds off Lighter, use withdraw / fast-withdraw to the bound TEE
wallet address.
