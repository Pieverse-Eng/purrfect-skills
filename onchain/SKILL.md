---
name: onchain
description: Use for wallet address, balance checks, and user transfers. Classify user intent, discover available sibling skills, and route to the matching skill for execution.
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

**Default chain is BNB Smart Chain (chain ID 56)** for executable / chain-specific actions (transfer, swap, balance check, contract call) when the user does not specify a chain. This default does NOT apply to identity reads — an EVM wallet address is the same on every EVM chain, so do not pin a single "default chain" onto the address when sharing it (see [Get wallet address](#get-wallet-address)).

| Chain           | Chain ID | Native Token | purr chain code             |
| --------------- | -------- | ------------ | --------------------------- |
| BNB Smart Chain | 56       | BNB          | bnb                         |
| Ethereum        | 1        | ETH          | eth                         |
| Base            | 8453     | ETH          | base                        |
| Arbitrum One    | 42161    | ETH          | arbitrum                    |
| Polygon         | 137      | MATIC        | matic                       |
| Optimism        | 10       | ETH          | optimism                    |
| X Layer         | 196      | OKB          | xlayer                      |
| Solana          | —        | SOL          | (use `--chain-type solana`) |

### Common Token Addresses (BSC)

| Token | Address                                      |
| ----- | -------------------------------------------- |
| USDT  | `0x55d398326f99059fF775485246999027B3197955` |
| USDC  | `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d` |
| WBNB  | `0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c` |
| CAKE  | `0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82` |

### Common Token Addresses (X Layer, chain ID 196)

| Token | Symbol on-chain | Address | Decimals | Explorer |
| ----- | --------------- | ------- | -------- | -------- |
| USDT0 | `USD₮0`         | `0x779ded0c9e1022225f8e0630b35a9b54be713736` | 6 | [OKLink](https://www.oklink.com/x-layer/token/0x779ded0c9e1022225f8e0630b35a9b54be713736) |
| USDC  | `USDC`          | `0x74b7f16337b8972027f6196a17a631ac6de26d22` | 6 | [OKLink](https://www.oklink.com/x-layer/token/0x74b7f16337b8972027f6196a17a631ac6de26d22) |
| USDG  | `USDG`          | `0x4ae46a509f6b1d9056937ba4500cb143933d2dc8` | 6 | [OKLink](https://www.oklink.com/x-layer/token/0x4ae46a509f6b1d9056937ba4500cb143933d2dc8) |

All three are 6 decimals (verified via `decimals()` against `https://rpc.xlayer.tech`).

`purr` registers all three under their canonical tickers on chain 196: `USDC`, `USDT0`, and `USDG` — so `--token USDC --chain-id 196`, `--token USDT0 --chain-id 196`, and `--token USDG --chain-id 196` all resolve.

**Do NOT use `--token USDT --chain-id 196`.** The bare `USDT` ticker is intentionally unmapped on X Layer: it used to alias the legacy bridged Tether (`0x1E4a5963aBFD975d8c9021ce480b42188849D41d`), which is deprecated. The canonical Tether-family asset on X Layer is `USD₮0` — always use `USDT0`. `purr` will surface `Unknown token "USDT" on chain 196` with `USDT0` in the available-tickers list if you forget.

## Wallet Operations

> **Default provider is `purr wallet`.**
> Route to OWS **only when the `ows` skill is present in this workspace AND the user explicitly names it** (e.g. "using OWS", "via my OWS vault").
> When both conditions are met, read `skills/ows/SKILL.md` → "Per-Skill Integration Guide" for the specific downstream skill. Do NOT fall back to `purr wallet` commands once OWS is explicitly chosen.

### Get wallet address

```bash
purr wallet address --chain-type ethereum   # EVM (all chains)
purr wallet address --chain-type solana     # Solana
```

The EVM address returned by `--chain-type ethereum` is the **same on every EVM chain** (BNB Smart Chain, Ethereum, Base, Arbitrum, Optimism, Polygon, …). When sharing it, surface that multi-chain reality instead of naming a single "default" chain. A correct reply looks like:

> Your hosted wallet address (works on all EVM chains — BSC, Ethereum, Base, Arbitrum, Optimism, Polygon):
> `0x…`
>
> Fund it with the native token of whichever chain you plan to transact on (BNB on BSC, ETH on Base/Arbitrum/Optimism/Ethereum, MATIC on Polygon, …).

Do NOT pin the address to one chain or ask for "a small amount of BNB" by default — the user may intend to operate on Base, Arbitrum, or elsewhere. Only mention a specific gas token once the user has confirmed (or the surrounding skill has fixed) the target chain. Solana uses a separate address; never conflate the two.

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

**Never guess an ERC-20 contract address.** If you don't already know the canonical address for a token on a given chain (e.g. USDT on X Layer), do NOT invent one or carry over a value from a different chain — different chains have different deployments for the same ticker. Instead:

1. Check the "Common Token Addresses" tables above. If the token is listed for that chain, use that address.
2. Otherwise call purr with the ticker — `purr wallet balance --token <TICKER> --chain-id <N>`. If the ticker is in purr's per-chain registry, it returns the address and balance; if not, it prints `Available tickers: ...` for that chain so you can pick the right one.
3. If the ticker is genuinely not in purr's registry (purr's error message lists every ticker that IS registered for that chain), ask the user for the contract address rather than guessing.

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
