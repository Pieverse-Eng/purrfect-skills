---
name: pancake
description: Pancake implementation skill for swaps, LP, and farm operations. Used by onchain router for Pancake intents.
---

# Pancake Implementation (Swap + LP + Farm)

Implementation skill under `onchain`. Use when the routed intent targets PancakeSwap.

## Mandatory Rules

> **ALWAYS read the relevant vendor SKILL.md before running any discovery commands.**
> Do NOT write your own curl/jq commands from memory — the vendor skills contain tested,
> working commands with correct API endpoints and field names.

> **DexScreener:** All PancakeSwap pools use `dexId: "pancakeswap"`.
> Pool version is in `.labels[]` (`"v2"`, `"v3"`, `"v1"`).
> Do NOT filter by `dexId == "pancakeswap-v3"` — that dexId does not exist.

> **V3 farms exist and are common.** MasterChef V3 has 500+ registered pools.
> Do NOT assume V3 pools have no farms — always verify on-chain.

## Vendor Planner Skills (Discovery & Planning)

| Planner | Location | Use for |
|---------|----------|---------|
| `swap-planner` | `vendor/swap-planner/SKILL.md` | Token discovery, price data, swap deep links |
| `liquidity-planner` | `vendor/liquidity-planner/SKILL.md` | Pool discovery, TVL, APY, IL analysis, LP deep links |
| `farming-planner` | `vendor/farming-planner/SKILL.md` | Farm discovery, APR comparison, farm/staking deep links |

Planners generate deep links only — they do NOT execute on-chain.

## Scope

### Executable (BSC only, via purr --execute)

| Operation | Purr command |
|-----------|-------------|
| Swap | `purr pancake swap --execute` |
| V2 LP add/remove | `purr pancake add-liquidity --execute` / `remove-liquidity --execute` |
| V2 Farm | `purr pancake stake --execute` / `unstake --execute` / `harvest --execute` |
| V3 LP | `purr pancake v3-mint --execute` / `v3-increase --execute` / `v3-decrease --execute` / `v3-collect --execute` |
| V3 Farm | `purr pancake v3-stake --execute` / `v3-unstake --execute` / `v3-harvest --execute` |
| Syrup Pool | `purr pancake syrup-stake --execute` / `syrup-unstake --execute` |

### Plan-only (deep link via vendor planners)

- Infinity farm — use `farming-planner`

Out of scope: non-BSC chains, Solana. Hand off to `onchain` router.

## Generic Execution Pattern

Every executable operation follows the same flow:

1. `purr wallet address --chain-type ethereum` (get wallet address)
2. `purr wallet balance --chain-type ethereum --chain-id 56` (native BNB). For token: `purr wallet balance --token <symbol_or_address> --chain-id 56`
3. **Read the relevant vendor planner** for discovery (token lookup, pool/farm PID, tick range, etc.)
4. `purr pancake <command> [args] --execute` (encode + execute in one step)
5. Re-check balance (same as step 2)

Run `purr pancake <command> --help` for full argument reference.

### Operation-specific notes

**Swaps:** Use WBNB (`0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c`) in path for native BNB. Try direct path first, then via-WBNB if no liquidity. Quote on-chain before executing — see below.

**BSC token decimals:** Most BSC tokens (including USDT and USDC) use **18 decimals**, not 6. This differs from Ethereum where USDC/USDT use 6 decimals. Always verify decimals before computing wei amounts. `purr wallet balance --token <symbol> --chain-id 56` returns the `decimals` field — use it.

### Swap quoting (BSC)

Router: `0x10ED43C718714eb63d5aA57B78B54704E256024E`

```bash
# Convert to wei
AMOUNT_WEI=$(cast --to-wei 0.5 18)
# Quote (last value in array is expected output)
cast call 0x10ED43C718714eb63d5aA57B78B54704E256024E \
  "getAmountsOut(uint256,address[])(uint256[])" \
  "$AMOUNT_WEI" "[0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c,0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82]" \
  --rpc-url https://bsc-dataseed1.binance.org
# Slippage: amountOutMin = amountOut * (10000 - slippageBps) / 10000
#   0.5% → amountOut * 9950 / 10000
#   1%   → amountOut * 9900 / 10000
#   3%   → amountOut * 9700 / 10000
```

If `cast` is unavailable, use raw JSON-RPC `eth_call` — see `swap-planner` Step 3B for the `curl` pattern.

**V2 Farms:** NEVER guess a PID. Discover it via `farming-planner` or query MasterChef V2 on-chain. See farming-planner SKILL.md for discovery methods.

**V3 LP:** Requires tick range from `liquidity-planner`. For native BNB pairs, purr auto-wraps into multicall.

**V3 Farms:** Must have an existing V3 position (tokenId). Staking transfers NFT to MasterChef V3 via `safeTransferFrom`.

**Syrup Pools:** Pool address is a SmartChef contract — discover via `farming-planner`.

## Failure Handling

| Error | Fix |
|-------|-----|
| `getAmountsOut` returns 0 / reverts | No liquidity — try via-WBNB path, smaller amount, or different pair |
| Swap reverted | Increase slippage or reduce size |
| V2 farm `address not available to deposit` | Wrong PID — rediscover on-chain |
| V3 `v3-stake` reverted | Wallet must own the position NFT (not already staked) |
| V3 `v3-unstake` reverted | Position must be staked by this wallet |
