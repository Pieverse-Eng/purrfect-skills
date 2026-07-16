# Collateral Transfers

Move USDC inside Hyperliquid without leaving the venue. Confirm every transfer.

## Commands

```bash
purr hyperliquid usd-class-transfer --amount <amount> --to-perp true|false
purr hyperliquid send-asset [--source-dex <dex>] --destination-dex <dex> --amount <amount>
```

| Command | Purpose |
| --- | --- |
| `usd-class-transfer` | Move USDC between **spot** and **perp** ledgers |
| `send-asset` | Move USDC between default perp and builder-dex balances (same wallet) |

## Why This Exists

- Deposits from Arbitrum land on the **perp** collateral side.
- Spot orders need **spot** USDC.
- HIP-3 / builder-dex markets (for example `xyz`) may need USDC on that dex’s
  balance, not only on the default vault.

Always re-read balances after a successful transfer:

```bash
purr hyperliquid state --kind both
purr hyperliquid state --kind both --dex <dex>
```

## Perp ↔ Spot (`usd-class-transfer`)

```bash
# Spot → perp
purr hyperliquid usd-class-transfer --amount 10.5 --to-perp true

# Perp → spot
purr hyperliquid usd-class-transfer --amount 10.5 --to-perp false
```

| Flag | Meaning |
| --- | --- |
| `--amount` | Human-readable USDC amount (positive decimal string) |
| `--to-perp true` | Transfer toward perp collateral |
| `--to-perp false` | Transfer toward spot |

Workflow:

1. `state --kind both` — note free balances on each side.
2. Confirm amount and direction with the user.
3. Run `usd-class-transfer`.
4. Re-run `state --kind both`.

## Default ↔ Builder Dex (`send-asset`)

```bash
# Default (empty source) → xyz builder dex
purr hyperliquid send-asset --destination-dex xyz --amount 25

# Explicit source and destination
purr hyperliquid send-asset --source-dex abc --destination-dex xyz --amount 5
```

| Flag | Meaning |
| --- | --- |
| `--source-dex` | Source perp dex name; omit or empty string for default vault |
| `--destination-dex` | Required; must differ from source |
| `--amount` | USDC amount |

Notes:

- CLI defaults `sourceDex` to `""` when `--source-dex` is omitted (platform
  default vault / empty dex name).
- Body sent is `{ sourceDex, destinationDex, amount }` only; destination wallet
  and USDC token are filled by the platform.
- Dex names may be empty or match `[A-Za-z0-9_.:-]{0,64}`.
- `sourceDex` and `destinationDex` must differ.

Workflow:

1. `state --kind both` and `state --kind both --dex <destination>`.
2. Confirm amount and dex path.
3. Run `send-asset`.
4. Re-check both default and destination dex state.

## Confirmation Template

```text
Action: usd-class-transfer | send-asset
Amount: <USDC>
From → to: <perp/spot or dex names>
Network: Hyperliquid mainnet

Do you want to execute this Hyperliquid action with these parameters? (Yes/No)
```

## Safety

- Never transfer more than free/available collateral shown in `state`.
- Do not auto-balance without user confirmation.
- If a trade failed for missing spot or builder-dex USDC, explain the needed
  transfer, confirm, move funds, then retry the trade only after a new
  confirmation for the trade itself. This is a recovery path only; normal
  order preflight must detect the missing target-ledger collateral before the
  first submission.
