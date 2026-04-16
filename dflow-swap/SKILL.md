---
name: dflow-swap
description: Swap implementation skill for Solana. Used by onchain router when chain is SOL, executed via dflow_swap.
---

# DFlow Swap Implementation (Solana)

This is an implementation skill under `onchain`.
Use it only when the routed swap chain is Solana.

## Scope

- In scope: Solana token swaps through `dflow_swap`
- Out of scope: EVM swaps (use `pancake` or `bitget` skill)

If user asks for non-Solana swap here, hand off back to `onchain` routing policy.

## Execution Flow

1. `wallet_address` with `chain_type: "solana"` (ensure wallet exists)
2. `wallet_balance` (check funds)
3. Execute `dflow_swap` with `chain: "SOL"`
4. `wallet_balance` (confirm output)

## Tool Contract (`dflow_swap`)

- `from_token`: source Solana mint (`So11111111111111111111111111111111111111112` for SOL)
- `to_token`: destination Solana mint
- `from_amount`: human-readable input amount
- `chain`: must be `"SOL"`
- `slippage`: decimal `0-1` (`0.03` default)

Example:

```yaml
Use dflow_swap:
  from_token: So11111111111111111111111111111111111111112
  to_token: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
  from_amount: "0.1"
  chain: "SOL"
  slippage: 0.01
```

## Solana Reference Tokens

- SOL: `So11111111111111111111111111111111111111112`
- USDC: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- USDT: `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB`
- BONK: `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263`

## Failure Handling

- `dflow-swap is Solana-only`: set `chain: "SOL"`
- `No route / quote failure`: reduce size or try a different pair
- `DFlow swap transaction failed on-chain`: retry with higher slippage or smaller amount
