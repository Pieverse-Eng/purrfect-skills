---
name: pieverse-staking
description: Use when the user asks about Pieverse staking, staking or unstaking PIEVERSE, listing their stakes, withdrawing one or more matured stakes, or batch withdraw on Ethereum or BNB Chain.
---

# Pieverse Staking

## Overview

Pieverse staking lets users lock PIEVERSE for a fixed term on Ethereum or BNB
Chain mainnet and withdraw after the lock ends. It covers contract discovery,
balance and position checks, opening a stake, and withdrawing one or more
matured stakes through the hosted wallet.

## Supported Networks

| Network | Chain ID | Explorer tx URL |
| --- | ---: | --- |
| Ethereum | `1` | `https://etherscan.io/tx/<hash>` |
| BNB Chain | `56` | `https://bscscan.com/tx/<hash>` |

If the network is missing, ask which one. Use only these chain IDs in commands
and user-facing text.

Both mainnets use these deployed contracts:

| Contract | Address |
| --- | --- |
| PIEVERSE token | `0x0E63B9C287E32A05E6b9AB8ee8dF88A2760225A9` |
| Staking proxy | `0xaE4c8Ca1dC8127C380099657774CB09ca8197e78` |

## Durations

| Alias | Meaning |
| --- | --- |
| `90d` | 90 days |
| `180d` | 180 days |
| `365d` | 365 days |

## Amount Units

CLI needs `--amount-wei` (18 decimals). Convert human amounts for commands:

| User says | `--amount-wei` |
| --- | --- |
| `0.01` | `10000000000000000` |
| `1` | `1000000000000000000` |
| `1.23` | `1230000000000000000` |
| `0.5` | `500000000000000000` |
| `10` | `10000000000000000000` |

Accept at most 2 decimal places with a minimum increment of `0.01 PIEVERSE`.
If the user provides more precision, ask for a new amount. Never round or
truncate it. Convert an accepted human amount to wei exactly.

In **user-facing** text, show human amounts only (for example `100 PIEVERSE`).
Do not print wei next to the human amount in confirmations or summaries.

## Stake Status

`positions` returns open stakes only:

| Status | Withdrawable |
| --- | --- |
| `active` | No |
| `matured` | Yes |

Withdraw only `matured` stakes. Use stake IDs only from the latest positions
result. Never invent IDs. If `paused` is true, stop and tell the user staking
is paused — do not print `paused: false` when things are fine.

## Confirmation Format

Required before every `--execute` (stake, withdraw, withdraw-batch).

Present a compact Markdown table. **Do not use code fences.** Do not show raw
calldata, contract addresses, plan JSON, or internal execution chain IDs.

### Stake example

| Field | Value |
| --- | --- |
| Network | Ethereum |
| Amount | 100 PIEVERSE |
| Duration | 180 days |
| Agent wallet | `0x…` |
| Available | 10,000 PIEVERSE |
| Transactions | Approve → Stake |

Then ask exactly:

`Proceed with execute? (Yes/No)`

### Withdraw example

| Field | Value |
| --- | --- |
| Network | BNB Chain |
| Stake ID | `0` |
| Amount | 50 PIEVERSE |
| Agent wallet | `0x…` |
| Transactions | Withdraw |

Then ask exactly:

`Proceed with execute? (Yes/No)`

Rules:

- Run `--execute` only after **Yes** in the immediately preceding turn with
  unchanged parameters.
- Re-confirm if the user says No, changes parameters, or sends another request.
- Steps-only (no `--execute`) needs no confirmation and should not dump plan
  JSON to the user unless they ask.

## After Execute

For each non-empty `results[].hash` (skip empty / skipped steps), return an
explorer link using the public chain id:

- `1` → `https://etherscan.io/tx/<hash>`
- `56` → `https://bscscan.com/tx/<hash>`

List each broadcast step with its label and full URL. Do not leave the user
with only a bare hash. Then re-check positions.

## Workflow: Stake

1. Resolve chain (`1` or `56`).
2. `purr pieverse staking positions --chain-id <chainId>` — stop if paused or
   available balance is too low.
3. Agree a human amount in `0.01 PIEVERSE` increments and a duration. If the
   amount has more than 2 decimal places, ask for a new amount; never round or
   truncate it. Convert the accepted amount to wei only for the CLI command.
4. Confirm with the stake table above, then after Yes:

   ```bash
   purr pieverse staking stake \
     --amount-wei <wei> \
     --duration <90d|180d|365d> \
     --chain-id <chainId> \
     --execute
   ```

5. Report explorer links; re-run positions and show the new stake in human terms.

## Workflow: List → Choose → Withdraw

1. Resolve chain (both networks if needed).
2. `purr pieverse staking positions --chain-id <chainId>`.
3. List open stakes for the user (id, amount as PIEVERSE, status, unlock time).
   Mark only `matured` as selectable. Stop if paused.
4. User chooses: one id, several ids, all matured, or cancel.
5. Refuse `active` ids.
6. Confirm with the withdraw table, then after Yes:

   ```bash
   purr pieverse staking withdraw --stake-id <id> --chain-id <chainId> --execute
   # or
   purr pieverse staking withdraw-batch --stake-ids <id1,id2,...> --chain-id <chainId> --execute
   ```

7. Report explorer links; re-run positions (withdrawn ids gone); report balance
   in human PIEVERSE.

## Commands

### Help

```bash
purr pieverse staking help
```

### Contracts

```bash
# Both networks
purr pieverse staking contracts

# One network
purr pieverse staking contracts --chain-id 1
purr pieverse staking contracts --chain-id 56
```

### Positions

Agent wallet PIEVERSE balance and open stakes (wallet resolved automatically).

```bash
purr pieverse staking positions --chain-id 1
purr pieverse staking positions --chain-id 56
```

### Stake

Amount is wei (convert an amount with at most 2 decimal places from human units
first). Durations: `90d` | `180d` | `365d`.

```bash
# Plan only (no broadcast) — no user confirmation
purr pieverse staking stake \
  --amount-wei 1000000000000000000 \
  --duration 90d \
  --chain-id 1

# Execute only after Yes
purr pieverse staking stake \
  --amount-wei 1000000000000000000 \
  --duration 90d \
  --chain-id 1 \
  --execute
```

### Withdraw one

```bash
# Plan only
purr pieverse staking withdraw \
  --stake-id 0 \
  --chain-id 1

# Execute only after Yes
purr pieverse staking withdraw \
  --stake-id 0 \
  --chain-id 1 \
  --execute
```

### Withdraw batch

Comma-separated stake IDs; no duplicates.

```bash
# Plan only
purr pieverse staking withdraw-batch \
  --stake-ids 0,1,2 \
  --chain-id 56

# Execute only after Yes
purr pieverse staking withdraw-batch \
  --stake-ids 0,1,2 \
  --chain-id 56 \
  --execute
```

Omit `--execute` to print steps for agent use only. Do not dump those steps to
the user as code fences or tables in the confirmation message.

## Safety

- Explicit Yes required before `--execute`.
- Accept stake amounts in `0.01 PIEVERSE` increments; never round or truncate.
- Only withdraw `matured` stakes.
- Public chains only: `1`, `56`.
- Do not auto-retry after timeout, unknown broadcast, or partial failure —
  re-check positions first.

## Error Handling

| Situation | Action |
| --- | --- |
| Chain missing / unsupported | Ask Ethereum or BNB Chain |
| Empty stakes | Nothing to withdraw |
| Only `active` | Show unlock times; do not withdraw |
| Non-matured id | Refuse; re-list matured |
| Low balance | Show available PIEVERSE (human) |
| Low gas | Check native balance on that chain |
| More than 2 amount decimal places | Ask for a new amount; do not round or execute |
| Bad duration | Only `90d` / `180d` / `365d` |
| Paused | Stop stake and withdraw |
| Duplicate batch ids | Fix list before execute |
