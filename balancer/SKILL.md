---
name: balancer
description: Use when the user asks to find Balancer liquidity pools, swap tokens, or add/remove V2/V3 liquidity.
---

# Balancer

## Overview

Discover reviewed Balancer pools; quote and execute exact-input and exact-output
swaps; and manage V2/V3 standard, boosted/ERC-4626, and nested/composable pool
liquidity. Supports unbalanced, proportional, and single-token exact-BPT adds,
plus proportional, single-token, unbalanced, and recovery removals.

## Supported Chains

| Chain | Chain ID | Protocols |
| --- | ---: | --- |
| Ethereum | 1 | V2, V3 |
| Optimism | 10 | V2, V3 |
| Polygon | 137 | V2 |
| Monad | 143 | V3 |
| Base | 8453 | V2, V3 |
| Arbitrum One | 42161 | V2, V3 |

## Route the Request

| Intent | Read |
| --- | --- |
| Find pools, quote a swap, or swap tokens | [swaps.md](references/swaps.md) |
| Add or remove liquidity, use BPT, or work with boosted/nested pools | [liquidity.md](references/liquidity.md) |
| Interpret a failed, deferred, unknown, or unsupported operation | [errors.md](references/errors.md) |

## Required Workflow

1. Identify the chain, operation, tokens, human-readable amounts, and any pool
   the user explicitly selected. Ask one short clarification if a required
   choice is missing or ambiguous.
2. Resolve the EVM wallet with
   `purr wallet address --chain-type ethereum`. Check input-token and native gas
   balances with `purr wallet balance --chain-type ethereum --chain-id <id>`.
3. For liquidity or a user-constrained swap, discover or verify the pool with
   `purr balancer pools --reviewed-only true --first 50`. If the user supplies
   a pool ID, preserve it and verify it through the matching Balancer quote;
   do not reject it only because it is absent from the first discovery result.
   Let unconstrained swaps use SOR route discovery.
4. Run the matching read-only quote command. Quote commands do not need user
   confirmation.
5. Present the chain, protocol, route or selected pool, input and output, price
   impact and quote expiry when available, slippage, raw execution bounds, and
   likely approval requirements. Do not describe an estimate as guaranteed
   output.
6. Ask exactly: `Do you want to execute this action with these parameters? (Yes/No)`
7. After an explicit yes, execute the matching write command with `--execute`
   and the protective raw values returned by the quote. Never omit, weaken, or
   invent those bounds. Requote if the quote is expired or the requested
   parameters changed.
8. Return the transaction hash, approval transaction hashes, chain, and final
   status. If Wallet Policy defers or denies the action, follow
   [errors.md](references/errors.md) instead of bypassing policy.

## Safety Rules

- Treat token symbols as hints. Use returned or verified contract addresses
  when a symbol is unknown or ambiguous; never guess an address, decimals, pool
  ID, protocol version, or BPT amount.
- Keep `--slippage-bps` within the CLI-supported `1-500` range. Do not increase
  slippage after a failed execution without renewed user approval.
- Let Platform manage deduplication. Do not request, generate, or pass a UUID or
  deduplication key.
- Do not reuse a previous approval for a materially changed amount, token,
  pool, chain, protocol, slippage, or execution bound.
- Stop on `broadcast_unknown`; do not submit a replacement transaction unless
  the original outcome has been reconciled.
