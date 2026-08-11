---
name: pieverse-staking
description: Use when the user asks about Pieverse staking, staking or unstaking PIEVERSE, listing their stakes, withdrawing one or more matured stakes, or batch withdraw on Ethereum or BNB Chain.
---

# Pieverse Staking

## Overview

Pieverse staking lets users lock PIEVERSE for a fixed term on Ethereum or BNB
Chain and withdraw after the lock ends. It covers contract discovery, balance
and position checks, opening a stake, and withdrawing one or more matured
stakes through the hosted wallet.

## Supported Networks

| Network | Chain ID | Explorer tx URL |
| --- | ---: | --- |
| Ethereum | `1` | `https://etherscan.io/tx/<hash>` |
| BNB Chain | `56` | `https://bscscan.com/tx/<hash>` |

If the user does not name a network, ask which one before any chain-specific step.

## Durations

Only these fixed terms are valid:

| Alias | Meaning |
| --- | --- |
| `90d` | 90 days |
| `180d` | 180 days |
| `365d` | 365 days |

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
  "chainId": 1,
  "wallet": "0x...",
  "pieverseBalanceWei": "1000000000000000000",
  "paused": false,
  "stakes": [
    {
      "stakeId": "0",
      "amountWei": "500000000000000000",
      "unlockAt": "2026-07-01T00:00:00.000Z",
      "status": "matured"
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `wallet` | Agent wallet (resolved automatically) |
| `pieverseBalanceWei` | Free PIEVERSE balance in wei |
| `paused` | Staking contract paused |
| `stakes[].stakeId` | Stake id for withdraw |
| `stakes[].amountWei` | Staked amount in wei |
| `stakes[].unlockAt` | Unlock time (ISO string) |
| `stakes[].status` | `active` or `matured` |

### Contracts response shape

Each entry: `chainId`, `pieverse`, `staking`, `durations`.

## Execution Confirmation

Required for every `--execute` (stake, withdraw, withdraw-batch).

1. Summarize the action (chain, amount or stake id(s), duration if staking).
2. Ask exactly: `Proceed with execute? (Yes/No)`
3. Run `--execute` only if the user answers **Yes** in the immediately
   preceding turn and parameters are unchanged.
4. If No, parameters change, or another request intervenes — do not execute;
   re-summarize and ask again if they still want to proceed.
5. Steps-only (no `--execute`) does not need confirmation.

## After Execute: Explorer Links

After every successful on-chain write (`--execute` on stake, withdraw, or
withdraw-batch), always return explorer links to the user. Do not stop at a raw
tx hash alone.

1. Parse the execute JSON. For each entry in `results[]` that has a non-empty
   `hash` and `status` is not `skipped`, build a link from the command's
   public chain id (`1` or `56`):

   | Chain ID | Link |
   | ---: | --- |
   | `1` | `https://etherscan.io/tx/<hash>` |
   | `56` | `https://bscscan.com/tx/<hash>` |

2. Present every successful step with its label (if any) and full URL, for
   example:

   ```text
   Approve: https://etherscan.io/tx/0x...
   Stake: https://etherscan.io/tx/0x...
   ```

3. Multi-step runs (approve + stake) must list a link per broadcast step.
4. Skip empty hashes (`status: skipped` with no hash). If no hash is returned
   for a step that should have broadcast, report that the explorer link is
   unavailable and do not invent a hash.
5. Then re-check positions as usual.

## Workflow: Stake

1. **Resolve chain** — Ethereum (`1`) or BNB Chain (`56`).
2. **Check readiness** — agent wallet balance and `paused`:

   ```bash
   purr pieverse staking positions --chain-id <chainId>
   ```

   Stop if `paused` is true or `pieverseBalanceWei` is too low for the amount.
3. **Agree amount and duration** — amount is wei (18 decimals); duration from
   Durations above.
4. **Optional plan** (no confirmation):

   ```bash
   purr pieverse staking stake \
     --amount-wei <wei> \
     --duration <90d|180d|365d> \
     --chain-id <chainId>
   ```

5. **Confirm and execute** — follow Execution Confirmation, then:

   ```bash
   purr pieverse staking stake \
     --amount-wei <wei> \
     --duration <90d|180d|365d> \
     --chain-id <chainId> \
     --execute
   ```

6. **Report explorer links** — follow After Execute: Explorer Links for every
   non-skipped hash in the execute result.
7. **Verify** — re-run positions; show the new stake in `stakes`.

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
   `pieverseBalanceWei`, and `paused`. Stop if `paused` is true — do not
   withdraw.
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

7. **Report explorer links** — follow After Execute: Explorer Links for every
   non-skipped hash in the execute result.
8. **Verify** — re-run positions; withdrawn ids should no longer appear in
   `stakes`; report `pieverseBalanceWei`.

## Command Reference

### Help

```bash
purr pieverse staking help
```

### Contracts

```bash
purr pieverse staking contracts
purr pieverse staking contracts --chain-id 1
purr pieverse staking contracts --chain-id 56
```

### Positions

Agent wallet PIEVERSE balance and open stakes for a chain.

```bash
purr pieverse staking positions --chain-id 1
purr pieverse staking positions --chain-id 56
```

### Stake

```bash
# Plan only
purr pieverse staking stake \
  --amount-wei 1000000000000000000 \
  --duration 90d \
  --chain-id 1

# Execute (after Yes)
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

# Execute (after Yes)
purr pieverse staking withdraw \
  --stake-id 0 \
  --chain-id 1 \
  --execute
```

### Withdraw batch

Comma-separated ids; no duplicates.

```bash
# Plan only
purr pieverse staking withdraw-batch \
  --stake-ids 0,1,2 \
  --chain-id 56

# Execute (after Yes)
purr pieverse staking withdraw-batch \
  --stake-ids 0,1,2 \
  --chain-id 56 \
  --execute
```

## Safety

- Never use `--execute` without explicit Yes in the immediately preceding turn.
- After every successful `--execute`, always return explorer tx links (see
  After Execute: Explorer Links). Never leave the user with only a bare hash.
- Only withdraw `matured` stakes.
- Stake ids only from the latest positions result for that chain.
- If `paused` is true, do not stake or withdraw.
- Supported chains only: `1`, `56`.
- Do not auto-retry after timeout, unknown broadcast, or partial failure —
  re-check positions first.

## Error Handling

| Situation | Action |
| --- | --- |
| Chain missing or unsupported | Ask Ethereum or BNB Chain; only `1` and `56` |
| Empty `stakes` | Nothing open to withdraw; offer stake if relevant |
| Only `active` stakes | Show `unlockAt`; do not withdraw |
| User picks non-matured id | Refuse; re-list matured |
| Low token balance | Show `pieverseBalanceWei` from positions |
| Low gas | `purr wallet balance --chain-type ethereum --chain-id <id>` |
| Invalid duration | Use only `90d` / `180d` / `365d` |
| Duplicate batch ids | Fix the list before executing |
| Contract paused | Stop stake and withdraw |
