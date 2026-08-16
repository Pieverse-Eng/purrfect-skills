# Account and readiness

Inspect the Predict account before trading or explaining balances.
Confirmation is not required for these reads. `set-referral` is a write —
follow the Confirmation Contract in `SKILL.md`.

## Commands

```bash
purr predict-fun account
purr predict-fun balances [--market-id <id>]
purr predict-fun readiness [--market-id <id>]
purr predict-fun approvals [--market-id <id>] [--operation TRADE|SPLIT|MERGE|REDEEM|CONVERT] [--side BUY|SELL]
purr predict-fun orders [--first <1-100>] [--after <cursor>] [--status <status>]
purr predict-fun order --order-hash <0x-hash>
purr predict-fun positions [--first <1-100>] [--after <cursor>] [--market-id <id>] [--sort <sort>]
purr predict-fun address-positions --address <0x-address> [--first <1-100>] [--after <cursor>] [--market-id <id>] [--sort <sort>]
purr predict-fun activity [--first <1-100>] [--after <cursor>]
purr predict-fun matches [--first <1-100>] [--after <cursor>] [--market-id <id>] [--minimum-value <decimal>]
purr predict-fun referral
purr predict-fun set-referral --code <5-char-code>
```

| Command | Purpose |
| --- | --- |
| `account` | Wallet address, Predict account payload, and balances |
| `balances` | USDT, BNB, and (with `--market-id`) that market's outcome tokens |
| `readiness` | Auth + `hasGas` + the same balances |
| `approvals` | Current allowance/operator state for a scope |
| `orders` / `order` | Wallet orders; single order by `0x` + 64 hex hash |
| `positions` | Hosted wallet outcome positions |
| `address-positions` | Public positions for any `0x` + 40 hex address |
| `activity` | Wallet activity |
| `matches` | Wallet fills; `--minimum-value` is a USDT decimal |
| `referral` | Current referral state |
| `set-referral` | Set a five-character referral code |

Paged commands return `{ data, cursor }`. Pass `--after` with the previous
cursor. `--first` is 1–100.

`approvals` does not accept `--operation ALL`. Use `ALL` only on approval
preview/execute — see [positions.md](positions.md).

## Identity

Use the address from `account` (`signerAddress` / `makerAddress`). There is no
enable/disable step.

## Funding

Collateral is **USDT on BNB Chain** (18 decimals). On-chain approvals, cancels,
and position actions also need **BNB** for gas.

This CLI has no deposit command. To add USDT or BNB, use the `onchain` skill /
`purr wallet` on chain id `56`. Stop and ask the user to fund when
`readiness.hasGas` is false or USDT is short.

Typical USDT: `0x55d398326f99059fF775485246999027B3197955`.

## Referral

`set-referral` takes only `--code` (exactly 5 characters). Platform derives
the idempotency key from the caller and code. A retry of the same code resumes
the same action. A different code already set returns
`PREDICT_REFERRAL_ALREADY_SET`; a locked account returns
`PREDICT_REFERRAL_LOCKED`.
