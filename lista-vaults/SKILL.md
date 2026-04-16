---
name: lista-vaults
description: Lista DAO lending vault skill for BSC. Deposit, redeem, and withdraw from ERC-4626 yield vaults via purr lista commands.
---

# Lista DAO Lending Vaults (BSC)

Interact with Lista DAO's ERC-4626 lending vaults on BNB Smart Chain.
Users deposit tokens (e.g. USDT) and receive yield-bearing vault shares.

## Scope

- In scope: BSC vault deposits, redeems, withdraws via `purr lista` commands
- Out of scope: swaps (use `pancake` or `bitget` skill), non-BSC vaults

## Commands

| Command | Purpose |
|---------|---------|
| `purr lista list-vaults` | Browse available vaults with APY and TVL |
| `purr lista deposit --execute` | Deposit tokens into a vault (auto-handles approval) |
| `purr lista redeem --execute` | Burn vault shares to get underlying tokens back |
| `purr lista withdraw --execute` | Withdraw a specific amount of underlying tokens |

## Execution Flows

### Deposit

1. `purr wallet address --chain-type ethereum` (ensure BSC wallet)
2. `purr wallet balance --chain-id 56 --token <symbol_or_address>` (check funds)
3. `purr lista list-vaults` (find target vault, note `vault_address` and `token_address`)
4. `purr lista deposit --vault <vault_address> --amount-wei <amount> --token <token_address> --wallet <addr> --chain-id 56 --execute`
5. `purr wallet balance --chain-id 56 --token <symbol_or_address>` (confirm deduction)

### Check Position

1. `purr lista list-vaults --zone <classic|alpha|aster>` (optional zone filter)
2. Pick a vault, use its `vault_address` — the position is returned by the deposit/redeem commands or can be checked via vault share balance

### Redeem (by shares)

1. `purr lista redeem --vault <vault_address> --shares-wei <shares> --wallet <addr> --chain-id 56 --execute`
2. `purr wallet balance --chain-id 56 --token <symbol_or_address>` (confirm tokens received)

### Withdraw (by asset amount)

1. `purr lista withdraw --vault <vault_address> --amount-wei <amount> --token <token_address> --wallet <addr> --chain-id 56 --execute`
2. `purr wallet balance --chain-id 56 --token <symbol_or_address>` (confirm tokens received)

## Command Reference

### `purr lista list-vaults`

- `--zone` (optional): `classic`, `alpha`, or `aster`. Omit for all zones.

Returns array of vaults with: `vaultAddress`, `tokenAddress`, `tokenSymbol`, `apy`, `tvl`, `zone`.

### `purr lista deposit --execute`

- `--vault`: vault contract address (from `purr lista list-vaults`)
- `--amount-wei`: deposit amount in wei
- `--token`: underlying token contract address
- `--wallet`: sender wallet address
- `--chain-id`: `56` (BSC)

### `purr lista redeem --execute`

- `--vault`: vault contract address
- `--shares-wei`: share amount to redeem in wei
- `--wallet`: sender wallet address
- `--chain-id`: `56` (BSC)

### `purr lista withdraw --execute`

- `--vault`: vault contract address
- `--amount-wei`: asset amount to withdraw in wei
- `--token`: underlying token contract address
- `--wallet`: sender wallet address
- `--chain-id`: `56` (BSC)

## Generic Execution Pattern

All write operations follow the same pattern — the `--execute` flag handles on-chain execution directly:

1. `purr wallet address --chain-type ethereum` (get BSC wallet)
2. `purr wallet balance --chain-id 56 --token <symbol_or_address>` (check funds)
3. `purr lista <command> --execute ...` (deposit/redeem/withdraw — executes on-chain)
4. `purr wallet balance --chain-id 56 --token <symbol_or_address>` (confirm result)

## Vault Zones

- **classic**: established vaults, lower risk
- **alpha**: higher yield, moderate risk
- **aster**: newer vaults

## BSC Reference Tokens

- USDT: `0x55d398326f99059fF775485246999027B3197955`
- USDC: `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d`
- BNB (native): `0x0000000000000000000000000000000000000000`
- WBNB: `0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c`

## Example

```bash
# Find USDT vaults
purr lista list-vaults --zone classic

# Deposit 10 USDT into a vault
purr lista deposit --vault 0x6d6783c146f2b0b2774c1725297f1845dc502525 \
  --amount-wei 10000000000000000000 --token 0x55d398326f99059fF775485246999027B3197955 \
  --wallet 0xYourWallet --chain-id 56 --execute

# Redeem 5 shares
purr lista redeem --vault 0x6d6783c146f2b0b2774c1725297f1845dc502525 \
  --shares-wei 5000000000000000000 --wallet 0xYourWallet --chain-id 56 --execute

# Withdraw 3 USDT worth
purr lista withdraw --vault 0x6d6783c146f2b0b2774c1725297f1845dc502525 \
  --amount-wei 3000000000000000000 --token 0x55d398326f99059fF775485246999027B3197955 \
  --wallet 0xYourWallet --chain-id 56 --execute
```

## Failure Handling

- `Insufficient token balance`: user needs more tokens, check with `purr wallet balance`
- `Insufficient shares`: user is trying to redeem/withdraw more than they have
- `Lista vaults are BSC-only`: wallet must be on chain 56
- `ERC-20 approval transaction reverted`: retry or try smaller amount
- `Deposit transaction reverted on-chain`: vault may be at capacity or paused
- `Invalid vault address`: double-check address from `purr lista list-vaults`
- `No vaults found`: Lista API may be temporarily unavailable, retry later
