---
name: pancake
description: PancakeSwap,swap,LP,farm,rewards,fees,BSC,Hub
---

# PancakeSwap

## Overview

Use this skill for PancakeSwap token swaps, liquidity provision, farm discovery, reward harvesting, LP fee collection, and PCS Hub partner-channel swap planning.

Keep planning and execution separate:

- Use `vendor/...` skills for discovery, planning, price/pool/farm lookup, APR analysis, and PancakeSwap deep links.
- Use `purr pancake` only for supported BSC on-chain execution.
- Treat non-BSC, Solana, Infinity, and PCS Hub flows as planner/deep-link flows unless a `purr pancake` command explicitly supports the exact action.

Always read the relevant vendor `SKILL.md` before running discovery commands or preparing execution parameters. Vendor skills contain tested endpoint, API, and field guidance; do not improvise curl, jq, or contract calls from memory.

## Routing

| User needs to... | Use |
|---|---|
| Plan a token swap, discover tokens, compare prices, or generate a PancakeSwap swap deep link | [`vendor/swap-planner/SKILL.md`](vendor/swap-planner/SKILL.md) |
| Execute a supported BSC swap after planning and confirmation | `purr pancake swap --execute` |
| Plan liquidity, discover pools, compare TVL/APR/IL, choose V2/V3/StableSwap/Infinity/Solana position parameters, or generate LP deep links | [`vendor/liquidity-planner/SKILL.md`](vendor/liquidity-planner/SKILL.md) |
| Execute supported BSC V2/V3 liquidity actions after planning and confirmation | `purr pancake add-liquidity`, `remove-liquidity`, `v3-mint`, `v3-increase`, `v3-decrease`, or `v3-collect` with `--execute` |
| Discover farms, compare APR, find farm PIDs, plan CAKE staking, or generate farm/staking deep links | [`vendor/farming-planner/SKILL.md`](vendor/farming-planner/SKILL.md) |
| Execute supported BSC farm or Syrup actions after planning and confirmation | `purr pancake stake`, `unstake`, `harvest`, `v3-stake`, `v3-unstake`, `v3-harvest`, `syrup-stake`, or `syrup-unstake` with `--execute` |
| Check LP fees or plan fee collection for V3, Infinity, or Solana positions | [`vendor/collect-fees/SKILL.md`](vendor/collect-fees/SKILL.md) |
| Execute supported BSC V3 fee collection for a known position token ID | `purr pancake v3-collect --execute` |
| Check or plan harvesting pending CAKE or partner-token rewards | [`vendor/harvest-rewards/SKILL.md`](vendor/harvest-rewards/SKILL.md) |
| Execute supported BSC V2 or V3 farm harvest for known PID/token ID | `purr pancake harvest` or `purr pancake v3-harvest --execute` |
| Plan swaps through PCS Hub, Binance Wallet, Trust Wallet, or another partner channel | [`vendor/hub-swap-planner/SKILL.md`](vendor/hub-swap-planner/SKILL.md) |

## Vendor Skills

| Skill | What it does | Path |
|---|---|---|
| `swap-planner` | Token discovery, token verification, swap pricing context, cross-chain swap planning, PancakeSwap X notes, and swap deep links. | [`vendor/swap-planner/SKILL.md`](vendor/swap-planner/SKILL.md) |
| `liquidity-planner` | Pool discovery, token verification, V2/V3/StableSwap/Infinity/Solana LP planning, APY/IL analysis, fee-tier selection, and LP deep links. | [`vendor/liquidity-planner/SKILL.md`](vendor/liquidity-planner/SKILL.md) |
| `farming-planner` | Farm discovery, farm APR comparison, V2/V3/Infinity/Solana farm planning, Syrup Pool discovery, PID/tokenId guidance, and farm deep links. | [`vendor/farming-planner/SKILL.md`](vendor/farming-planner/SKILL.md) |
| `collect-fees` | Pending LP fee checks and collection plans for PancakeSwap V3, Infinity, and Solana positions. | [`vendor/collect-fees/SKILL.md`](vendor/collect-fees/SKILL.md) |
| `harvest-rewards` | Pending CAKE and partner-token reward checks across farms, Syrup Pools, Infinity, and Solana positions. | [`vendor/harvest-rewards/SKILL.md`](vendor/harvest-rewards/SKILL.md) |
| `hub-swap-planner` | PCS Hub quote and channel handoff planning for partner-channel swaps such as Binance Wallet or Trust Wallet. | [`vendor/hub-swap-planner/SKILL.md`](vendor/hub-swap-planner/SKILL.md) |
| `common` | Shared upstream resources used by vendor skills, including token lists and pool/APR/protocol-fee helper scripts. | [`vendor/common/`](vendor/common/) |

## `purr pancake` Execution

Use `purr pancake` only for BSC execution that maps to an existing command. Planning, discovery, and parameter lookup still come from the vendor skills first.

Supported `purr pancake` commands:

| Operation | Command |
|---|---|
| BSC swap | `purr pancake swap --execute` |
| BSC V2 add/remove liquidity | `purr pancake add-liquidity --execute`, `purr pancake remove-liquidity --execute` |
| BSC V2 farm stake/unstake/harvest | `purr pancake stake --execute`, `purr pancake unstake --execute`, `purr pancake harvest --execute` |
| BSC V3 liquidity | `purr pancake v3-mint --execute`, `v3-increase --execute`, `v3-decrease --execute`, `v3-collect --execute` |
| BSC V3 farm | `purr pancake v3-stake --execute`, `v3-unstake --execute`, `v3-harvest --execute` |
| BSC Syrup Pool stake/unstake | `purr pancake syrup-stake --execute`, `purr pancake syrup-unstake --execute` |

Do not use `purr pancake` for Solana, PCS Hub execution, Infinity execution, or unsupported PancakeSwap pool/farm actions. For those cases, use the relevant vendor planner and return a deep link or plan.

## Execution Checklist

Before any `purr pancake ... --execute`:

1. Resolve the current wallet with `purr wallet address --chain-type ethereum`.
2. Check native BNB with `purr wallet balance --chain-type ethereum --chain-id 56`.
3. Check required token balances with `purr wallet balance --token <symbol_or_address> --chain-id 56`.
4. Read the relevant vendor planner to discover or verify token addresses, pool addresses, farm PID, tick range, tokenId, pool address, slippage, deadlines, and expected amounts.
5. Present the exact execution parameters: command, chain, wallet, tokens, amounts, pool/farm identifiers, slippage/min amounts, deadline, and any expected approvals.
6. Ask exactly: `Do you want to execute this action with these parameters? (Yes/No)`
7. Add `--execute` only after the user says yes.

Do not execute PancakeSwap writes with private keys, `cast send`, direct contract write commands, or official UI automation. Use `purr pancake` for supported BSC execution so the platform wallet path owns signing and broadcasting.

## Important Rules

- PancakeSwap pools on DexScreener use `dexId: "pancakeswap"`; version is in `.labels[]` such as `v2`, `v3`, or `v1`. Do not filter by `dexId == "pancakeswap-v3"`.
- V3 farms are common. Do not assume a V3 pool has no farm; verify through `farming-planner`.
- Never guess a V2 farm PID, V3 tokenId, Syrup pool address, tick range, token decimals, or token address.
- For BSC, many common tokens including USDT and USDC use 18 decimals. Verify decimals before computing wei amounts.
- For native BNB paths, use WBNB where required by vendor guidance or CLI arguments.
- If a vendor planner returns a deep link for non-BSC, Solana, Infinity, or Hub, keep it as a user-reviewed UI flow rather than converting it to `purr pancake`.

## Failure Handling

| Error or ambiguity | Fix |
|---|---|
| Multiple token matches | Present candidates and ask the user which token they mean. |
| Unknown token decimals | Verify via token list, RPC, or vendor planner before computing wei amounts. |
| `getAmountsOut` returns zero or reverts | Treat as no liquidity; try a WBNB path, smaller size, or different pool only after explaining the issue. |
| Swap or LP transaction would exceed slippage | Requote, widen slippage only if the user accepts the risk, or reduce size. |
| V2 farm deposit/withdraw fails with unavailable address or PID | Stop and rediscover the PID through `farming-planner`. |
| V3 collect/stake/unstake/harvest fails | Verify wallet owns or has staked the position tokenId and that the position is on BSC. |
| Request is Solana, Infinity, or PCS Hub execution | Use vendor planner/deep link; do not claim `purr pancake` can execute it. |
