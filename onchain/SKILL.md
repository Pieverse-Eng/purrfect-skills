---
name: onchain
description: On-chain operations orchestrator. Classify user intent, discover available sibling skills, and route to the matching skill for execution.
---

# On-Chain Orchestrator

`onchain` is the top-level routing skill. It classifies user intent and dispatches to the appropriate sibling skill.

## Skill Discovery

This instance has built-in skills for third-party vendors installed as sibling skill directories. Each skill's frontmatter `description` field explains when to invoke it. Identify user intent and route to the matching skill — the skill's SKILL.md contains all execution details, CLI commands, and tool references.

Do not hardcode vendor-specific routing here. Read sibling skill descriptions at runtime to determine the best match for user intent.

## Routing Policy

1. Detect target chain and intent (swap, LP, farm, research, CEX trade, NFT, etc.).
2. Match intent against available sibling skills by reading their `description` fields.
3. Route to the matched skill — it owns all execution details.
4. If multiple skills could match, prefer the one the user explicitly names (e.g. "via OKX", "on Kraken", "on Gate").
5. If no skill matches, fall back to JSON-RPC / explorer workflows for raw on-chain queries.
6. Do not ask the user to choose between skills for the same intent. Routing is deterministic.
7. For LP/farm discovery and planning (APY, pools, deep links), route to `pancake` — it owns the planner sub-skills. LP/farm execution is BSC-only.
8. For HTTP payment-gated resources, route to a matching payment protocol sibling skill before treating the request as a wallet transfer or swap.

## Confirmation Contract (Mandatory)

Any executable action (swap, trade, LP, farm, transfer, order placement) requires explicit user confirmation before execution.

### Before execution, show:

- action type (swap, LP add, stake, order, etc.)
- chain
- key parameters (tokens, amounts, slippage, leverage, etc.)

Then ask exactly:

`Do you want to execute this action with these parameters? (Yes/No)`

- If user says Yes: execute.
- If user says No: do not execute; offer edit or cancel.
- If any parameter changes after confirmation: ask again.

## Chain Reference

**Default chain is BNB Smart Chain (chain ID 56)** when the user does not specify a chain.

| Chain           | Chain ID | Native Token | purr chain code             |
| --------------- | -------- | ------------ | --------------------------- |
| BNB Smart Chain | 56       | BNB          | bnb                         |
| Ethereum        | 1        | ETH          | eth                         |
| Base            | 8453     | ETH          | base                        |
| Arbitrum One    | 42161    | ETH          | arbitrum                    |
| Polygon         | 137      | MATIC        | matic                       |
| Optimism        | 10       | ETH          | optimism                    |
| Solana          | —        | SOL          | (use `--chain-type solana`) |

### Common Token Addresses (BSC)

| Token | Address                                      |
| ----- | -------------------------------------------- |
| USDT  | `0x55d398326f99059fF775485246999027B3197955` |
| USDC  | `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d` |
| WBNB  | `0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c` |
| CAKE  | `0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82` |

## Wallet Operations

> **Default provider is `purr wallet`.**
> Route to OWS **only when the `ows` skill is present in this workspace AND the user explicitly names it** (e.g. "using OWS", "via my OWS vault").
> When both conditions are met, read `skills/ows/SKILL.md` → "Per-Skill Integration Guide" for the specific downstream skill. Do NOT fall back to `purr wallet` commands once OWS is explicitly chosen.

### Get wallet address

```bash
purr wallet address --chain-type ethereum   # EVM (all chains)
purr wallet address --chain-type solana     # Solana
```

### Check balance

```bash
purr wallet balance --chain-id 56                   # native BNB (default chain)
purr wallet balance --chain-id 8453                 # native ETH on Base
purr wallet balance --token USDT --chain-id 56      # USDT on BSC
purr wallet balance --token USDC --chain-id 8453    # USDC on Base
purr wallet balance --chain-type solana              # native SOL
purr wallet balance --chain-type solana --token USDC # USDC on Solana
```

`--token` accepts a ticker (e.g. `USDT`) or contract address. Case-insensitive. Always include `--chain-id` so the correct chain is queried (default: 56/BSC). Pass an unknown ticker and purr will list all available tickers for that chain.

### Transfer

```bash
purr wallet transfer --to 0x... --amount 0.01 --chain-id 56                    # native BNB
purr wallet transfer --to 0x... --amount 10 --chain-id 56 --token USDT         # USDT on BSC
purr wallet transfer --to 0x... --amount 5 --chain-id 8453 --token USDC        # USDC on Base
purr wallet transfer --to FuQPd1q... --amount 0.5 --chain-type solana          # native SOL
purr wallet transfer --to FuQPd1q... --amount 100 --chain-type solana --token USDC  # USDC on Solana
```

## Non-Swap On-Chain Tasks

Use JSON-RPC / explorer workflows for:

- transaction lookup
- receipt / log decoding
- sender tracing
- balance and token state checks

### RPC Endpoints

| Chain           | RPC URL                                   | Chain ID |
| --------------- | ----------------------------------------- | -------- |
| BNB Smart Chain | `https://bsc-rpc.publicnode.com`          | 56       |
| Ethereum        | `https://ethereum-rpc.publicnode.com`     | 1        |
| Base            | `https://base-rpc.publicnode.com`         | 8453     |
| Arbitrum One    | `https://arbitrum-one-rpc.publicnode.com` | 42161    |
| Optimism        | `https://optimism-rpc.publicnode.com`     | 10       |
| Polygon         | `https://polygon-bor-rpc.publicnode.com`  | 137      |
