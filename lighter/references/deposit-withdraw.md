# Deposit, withdraw, transfer

All account-changing. Confirmation Contract applies. USDC only
(`assetIndex` 3, the default — do not pass another value).

## ⚠️ Two different amount conventions

This is the most common way to lose money here.

| Command | Flag | Unit | 10 USDC is |
| --- | --- | --- | --- |
| `deposit` | `--amount` | **decimal USDC** | `10` |
| `withdraw` | `--amount-base-units` | **integer base units** | `10000000` |
| `transfer` | `--amount-base-units` | **integer base units** | `10000000` |

USDC has **6 decimals** on Lighter, so `1 USDC = 1000000` base units.

Passing `10` to `--amount-base-units` moves **0.00001 USDC**. Passing
`10000000` to `deposit --amount` attempts **ten million USDC**.

Always show both forms in the confirmation, e.g.
`withdraw 10000000 base units = 10.00 USDC`.

## Deposit

```bash
purr lighter deposit-networks                    # supported chains — read this first
purr lighter deposit --amount 25 --source-chain-id 42161 [--route-type perps]
```

- `--amount` is decimal USDC. **Minimum 1 USDC** — smaller is rejected with
  `LIGHTER_DEPOSIT_AMOUNT_TOO_SMALL`.
- `--source-chain-id` must be one the platform supports. Call
  `deposit-networks` rather than trusting a memorized list; at time of writing
  it covers Ethereum (`1`), Arbitrum One (`42161`), Base (`8453`),
  Avalanche (`43114`), and HyperEVM (`999`). An unsupported chain returns
  `LIGHTER_DEPOSIT_CHAIN_UNSUPPORTED`.
- The USDC must already be on that chain in the instance wallet. Bridging from
  elsewhere is a different skill — do it first.

Track it:

```bash
purr lighter deposits [--limit <n>]
purr lighter deposit-status --request-id <id>
purr lighter reconcile-deposit --request-id <id>    # account-changing
```

`LIGHTER_DEPOSIT_ALREADY_IN_PROGRESS` means a deposit is mid-flight — check
`deposits` and wait; do not start another. Deposits may need an on-chain
approval step; `LIGHTER_APPROVAL_*` codes belong to that flow (see
[errors.md](errors.md)) and are not a reason to resubmit the deposit.

## Withdraw

```bash
purr lighter withdrawal-delay                     # how long funds take — quote this to the user
purr lighter withdraw --amount-base-units 10000000 [--route-type perps|spot]
```

- `--amount-base-units` is an **integer** (see the table above).
- `--route-type` picks which balance it leaves from; defaults to `perps`.
- Withdrawals are delayed by protocol design. Check `withdrawal-delay` and tell
  the user the expected wait *before* they confirm.

A withdraw submit is not an arrival. Verify with `requests` /
`request-status`, and never tell the user funds have landed based on the submit
response alone.

## Transfer

```bash
purr lighter transfer --to-account-index <id> --amount-base-units 10000000 \
  [--from-route-type perps|spot] [--to-route-type perps|spot]
```

Account-to-account move. `--to-account-index` must be a **different** account.
Both route types default to `perps`; set them explicitly when moving between
perp and spot balances so the user can see the direction in the confirmation.

Transfers are irreversible and go to an account index, not a human-readable
name — read the destination back to the user digit by digit before confirming.
A wrong index sends funds to a stranger.

## Reconciling

```bash
purr lighter requests [--limit <n>]
purr lighter request-status --request-id <id>
purr lighter transactions [--offset <n>] [--limit <n>]
purr lighter transaction --tx-hash <hash>
purr lighter l1-transaction --l1-tx-hash <hash>
```

Use these — not a retry — after any timeout or unknown submission.
