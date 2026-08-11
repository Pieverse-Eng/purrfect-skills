---
name: pieverse-staking
description: Use when the user asks about Pieverse staking, staking or unstaking, listing their stakes, withdrawing one or more matured stakes, or batch withdraw on Sepolia or BSC Testnet.
---

# Pieverse Staking

## Overview

Pieverse staking lets users lock tokens for a fixed term on Sepolia or BSC
Testnet and withdraw them after the lock ends. It covers contract discovery,
balance and position checks, opening a stake, and withdrawing one or more
matured stakes through the hosted wallet.

## Supported Networks

| Network | Chain ID |
| --- | ---: |
| Ethereum Sepolia | `11155111` |
| BSC Testnet | `97` |

If the user does not name a network, ask which one before any chain-specific step.

## Durations

Only these fixed terms are valid:

| Alias | Seconds |
| --- | ---: |
| `5m` | `300` |
| `10m` | `600` |
| `15m` | `900` |

## Stake Status

`positions` returns only **open** stakes (`active` and `matured`). Closed stakes
are omitted.

| Status | Meaning | Withdrawable |
| --- | --- | --- |
| `active` | Still locked | No |
| `matured` | Lock ended | Yes |

Only withdraw stakes with status `matured`. Never invent stake IDs — use only
IDs from the latest positions result for that chain.

### Positions response shape

```json
{
  "chainId": 11155111,
  "wallet": "0x...",
  "burrBalanceWei": "1000000000000000000",
  "paused": false,
  "stakes": [
    {
      "stakeId": "0",
      "amountWei": "500000000000000000",
      "unlockAt": "2026-01-01T00:05:00.000Z",
      "status": "matured"
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `wallet` | Agent wallet (resolved automatically) |
| `burrBalanceWei` | Free BURR balance in wei |
| `paused` | Staking contract paused |
| `stakes[].stakeId` | Stake id for withdraw |
| `stakes[].amountWei` | Staked amount in wei |
| `stakes[].unlockAt` | Unlock time (ISO string) |
| `stakes[].status` | `active` or `matured` |

### Contracts response shape

Each entry is compact: `chainId`, `burr`, `staking`, `durations`.

## Execution Confirmation

Required for every `--execute` (stake, withdraw, withdraw-batch).

1. Summarize the action (chain, amount or stake id(s), duration if staking).
2. Ask exactly: `Proceed with execute? (Yes/No)`
3. Run `--execute` only if the user answers **Yes** in the immediately
   preceding turn and parameters are unchanged.
4. If No, parameters change, or another request intervenes — do not execute;
   re-summarize and ask again if they still want to proceed.
5. Steps-only (no `--execute`) does not need confirmation.

## Workflow: Stake

1. **Resolve chain** — Sepolia (`11155111`) or BSC Testnet (`97`).
2. **Check readiness** — agent wallet balance and `paused`:

   ```bash
   purr pieverse staking positions --chain-id <chainId>
   ```

   Stop if `paused` is true or `burrBalanceWei` is too low for the amount.
3. **Agree amount and duration** — amount is wei (18 decimals); duration from
   Durations above.
4. **Optional plan** (no confirmation):

   ```bash
   purr pieverse staking stake \
     --amount-wei <wei> \
     --duration <5m|10m|15m> \
     --chain-id <chainId>
   ```

5. **Confirm and execute** — follow Execution Confirmation, then:

   ```bash
   purr pieverse staking stake \
     --amount-wei <wei> \
     --duration <5m|10m|15m> \
     --chain-id <chainId> \
     --execute
   ```

6. **Verify** — re-run positions; show the new stake in `stakes`.

## Workflow: List → Choose → Withdraw

Use whenever the user wants to see stakes, unstake, withdraw one, or withdraw
several.

1. **Resolve chain** — if both networks matter, run positions on each.
2. **List open stakes:**

   ```bash
   purr pieverse staking positions --chain-id <chainId>
   ```

3. **Present a table** — for each stake: `stakeId`, `amountWei`, `status`,
   `unlockAt`. Mark only `matured` rows as selectable. Also show `wallet`,
   `burrBalanceWei`, and `paused`. Stop if `paused` is true — do not withdraw.
4. **Ask the user to choose:**
   - one matured id → single withdraw
   - several matured ids → batch withdraw
   - all matured → batch with every matured id
   - cancel → stop
5. **Refuse** `active` ids; re-list matured options.
6. **Confirm and execute** — follow Execution Confirmation, then:

   ```bash
   # One stake
   purr pieverse staking withdraw \
     --stake-id <id> \
     --chain-id <chainId> \
     --execute

   # Several stakes
   purr pieverse staking withdraw-batch \
     --stake-ids <id1,id2,...> \
     --chain-id <chainId> \
     --execute
   ```

7. **Verify** — re-run positions; withdrawn ids should no longer appear in
   `stakes`; report `burrBalanceWei`.

## Command Reference

### Help

```bash
purr pieverse staking help
```

### Contracts

Compact list: `chainId`, `burr`, `staking`, `durations`.

```bash
purr pieverse staking contracts
purr pieverse staking contracts --chain-id 11155111
purr pieverse staking contracts --chain-id 97
```

### Positions

Agent wallet BURR balance and open stakes for a chain.

```bash
purr pieverse staking positions --chain-id 11155111
purr pieverse staking positions --chain-id 97
```

### Stake

```bash
# Plan only
purr pieverse staking stake \
  --amount-wei 1000000000000000000 \
  --duration 5m \
  --chain-id 11155111

# Execute (after Yes)
purr pieverse staking stake \
  --amount-wei 1000000000000000000 \
  --duration 5m \
  --chain-id 11155111 \
  --execute
```

### Withdraw one

```bash
# Plan only
purr pieverse staking withdraw \
  --stake-id 0 \
  --chain-id 11155111

# Execute (after Yes)
purr pieverse staking withdraw \
  --stake-id 0 \
  --chain-id 11155111 \
  --execute
```

### Withdraw batch

Comma-separated ids; no duplicates.

```bash
# Plan only
purr pieverse staking withdraw-batch \
  --stake-ids 0,1,2 \
  --chain-id 97

# Execute (after Yes)
purr pieverse staking withdraw-batch \
  --stake-ids 0,1,2 \
  --chain-id 97 \
  --execute
```

## Safety

- Never use `--execute` without explicit Yes in the immediately preceding turn.
- Only withdraw `matured` stakes.
- Stake ids only from the latest positions result for that chain.
- If `paused` is true, do not stake or withdraw.
- Supported chains only: `11155111`, `97`.
- Do not auto-retry after timeout, unknown broadcast, or partial failure —
  re-check positions first.

## Error Handling

| Situation | Action |
| --- | --- |
| Chain missing or unsupported | Ask Sepolia or BSC Testnet; only `11155111` and `97` |
| Empty `stakes` | Nothing open to withdraw; offer stake if relevant |
| Only `active` stakes | Show `unlockAt`; do not withdraw |
| User picks non-matured id | Refuse; re-list matured |
| Low token balance | Show `burrBalanceWei` from positions |
| Low gas | `purr wallet balance --chain-type ethereum --chain-id <id>` |
| Invalid duration | Use only `5m` / `10m` / `15m` (or 300 / 600 / 900) |
| Duplicate batch ids | Fix the list before executing |
| Contract paused | Stop stake and withdraw |
