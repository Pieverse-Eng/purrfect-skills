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

- `--amount` is decimal USDC.
- **The minimum depends on the source chain.** Ethereum mainnet goes by a direct
  route; every other chain bridges via CCTP and has a higher floor:

  | Source chain | `--source-chain-id` | Route | Minimum |
  | --- | ---: | --- | ---: |
  | Ethereum mainnet | `1` | `ethereum_direct` | **1 USDC** |
  | Arbitrum One | `42161` | `cctp` | **5 USDC** |
  | Base | `8453` | `cctp` | **5 USDC** |
  | Avalanche | `43114` | `cctp` | **5 USDC** |
  | HyperEVM | `999` | `cctp` | **5 USDC** |

  Below the floor the platform rejects with `LIGHTER_DEPOSIT_AMOUNT_TOO_SMALL`.
  Quoting a flat "1 USDC minimum" is wrong for four of the five chains and will
  get a 4 USDC Base deposit rejected.

- `deposit-networks` returns `minAmount` per network — treat that as the source
  of truth and read it before quoting a figure, rather than trusting the table
  above. An unsupported chain returns `LIGHTER_DEPOSIT_CHAIN_UNSUPPORTED`.
- The USDC must already be on that chain in the instance wallet. Bridging from
  elsewhere is a different skill — do it first.

Track it:

```bash
purr lighter deposits [--limit <n>]
purr lighter deposit-status --request-id <id>
purr lighter reconcile-deposit --request-id <id>    # account-changing
```

`LIGHTER_DEPOSIT_ALREADY_IN_PROGRESS` means **this same request** is mid-flight;
`LIGHTER_CROSS_CHAIN_DEPOSIT_ALREADY_IN_PROGRESS` means a **different** CCTP
bridge leg is still settling. Both mean check `deposits` and wait — neither is a
reason to start another deposit.

⚠️ **Two different approval lifecycles — do not merge them.**
`POLICY_DEFERRED`, `LIGHTER_APPROVAL_NOT_APPROVED`, `_INVALID`, `_UNAVAILABLE`
and `_RESUME_IN_PROGRESS` are **wallet-policy manual approval**: a human must
approve a parked request, and the agent cannot approve anything — `requests`
only observes. Only `LIGHTER_APPROVAL_TX_HASH_MISSING` refers to the on-chain
ERC-20 approval transaction. Full recovery path in [errors.md](errors.md).

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

**Transfer moves funds to a different account — it is not how you move money
between perp and spot.** Lighter accounts are unified, so there is no perp↔spot
migration to perform. Sending to your own account index is rejected:

```
LIGHTER_SELF_TRANSFER_NOT_REQUIRED — "Lighter unified accounts do not require
transfers between perps and spot; transfer to a different account index"
```

If a user asks to "move USDC from perp to spot", the answer is that Lighter does
not need it — do not construct a self-transfer to satisfy the request.

`--from-route-type` / `--to-route-type` describe the source and destination
routes on **different account indexes**, not two pockets of one account. Both
default to `perps`.

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
