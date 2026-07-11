# Balancer Pools and Swaps

Use this reference for reviewed pool discovery, exact-input swaps, and
exact-output swaps. All swaps are single-chain.

## Discover Pools

```bash
purr balancer pools \
  --chain <ethereum|optimism|polygon|monad|base|arbitrum> \
  --tokens <TOKEN,TOKEN> \
  --protocol-version <2|3> \
  --reviewed-only true \
  [--first <1-50>] [--min-tvl <usd>]
```

Use a raw token address when a ticker is ambiguous or absent from the local
registry. Prefer reviewed pools with meaningful liquidity. Verify that the
returned chain, protocol version, token addresses, and pool ID match the
intended operation.

Do not pass `--reviewed-only false` for execution planning. A quote can succeed
against an unreviewed or empty pool while the on-chain transaction still
reverts.

## Exact-Input Swap

Use exact-input when the user specifies how much to spend.

```bash
purr balancer quote \
  --chain <chain> \
  --from <TOKEN> --to <TOKEN> \
  --amount <human_input_amount> \
  --kind exact-in \
  [--protocol-version <2|3>] \
  [--slippage-bps <1-500>] \
  [--pool-ids <reviewed_pool_id,...>]
```

Read `amountIn`, `estimatedAmountOut`, `minAmountOut`, `minAmountOutRaw`,
`priceImpact`, `expiresAt`, and `route.pools` from the quote. Execute only after
confirmation:

```bash
purr balancer swap \
  --chain <chain> \
  --from <TOKEN> --to <TOKEN> \
  --amount <same_human_input_amount> \
  --kind exact-in \
  --min-amount-out <quote.minAmountOutRaw> \
  --protocol-version <quote.protocolVersion> \
  [--slippage-bps <same_bps>] \
  [--pool-ids <same_reviewed_pool_ids>] \
  --execute
```

Always pass `--min-amount-out`. Although the CLI accepts an exact-input
execution without it, omitting it removes the user's durable output floor when
Platform requotes before execution.

## Exact-Output Swap

Use exact-output when the user specifies the amount they want to receive.

```bash
purr balancer quote \
  --chain <chain> \
  --from <TOKEN> --to <TOKEN> \
  --amount <human_output_amount> \
  --kind exact-out \
  [--protocol-version <2|3>] \
  [--slippage-bps <1-500>] \
  [--pool-ids <reviewed_pool_id,...>]
```

Read `amountOut`, `amountIn`, `maxAmountIn`, `maxAmountInRaw`, `priceImpact`,
`expiresAt`, and `route.pools`. Execute only after confirmation:

```bash
purr balancer swap \
  --chain <chain> \
  --from <TOKEN> --to <TOKEN> \
  --amount <same_human_output_amount> \
  --kind exact-out \
  --max-amount-in <quote.maxAmountInRaw> \
  --protocol-version <quote.protocolVersion> \
  [--slippage-bps <same_bps>] \
  [--pool-ids <same_reviewed_pool_ids>] \
  --execute
```

Never convert the human-readable maximum back to raw units yourself. Pass the
quote's `maxAmountInRaw` unchanged.

## Route Selection

- Omit `--pool-ids` to let Balancer SOR discover the best available route,
  including multi-hop routes.
- Pass `--pool-ids` only when the user selected a specific pool or the task
  requires a constrained route. Select those IDs from
  `purr balancer pools ... --reviewed-only true` and preserve the same IDs for
  quote and execution.
- Do not describe an unconstrained SOR route as reviewed; Platform does not
  currently enforce that property for automatically selected route pools.
- Treat “no available path” as a route/liquidity limitation. Try a different
  reviewed pool, protocol version, or amount only after explaining the change.
- Do not reinterpret a cross-chain request as a Balancer route. Bridge first,
  wait for destination-chain settlement, then quote a new destination-chain
  swap.

## Execution Result

A successful execution includes the final swap `hash`, receipt, and zero or
more `approvalTransactions`. Report each approval hash separately from the
swap hash. If `idempotent` is true, explain that Platform returned the existing
workflow result rather than broadcasting another swap.
