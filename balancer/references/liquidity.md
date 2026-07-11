# Balancer Liquidity

Use this reference for standard, boosted/ERC-4626, and nested/composable pool
liquidity. Discover and verify the pool with `purr balancer pools ...
--reviewed-only true` before quoting.

## Pool Types and Limits

| Pool type | Protocol | Add modes | Remove modes |
| --- | --- | --- | --- |
| `standard` | V2 or V3 where supported | unbalanced, proportional, single-token exact-BPT | proportional, single-token, recovery; unbalanced on V2 |
| `boosted` | V3 | unbalanced, proportional | proportional |
| `nested` | V3 on Ethereum, Base, or Arbitrum | unbalanced | proportional |

Pool contracts can disable otherwise supported modes. Treat the quote as the
capability check; do not assume every V3 pool supports unbalanced or
single-token liquidity.

## Add Liquidity

### Unbalanced

```bash
purr balancer add-quote --chain <chain> --protocol-version <2|3> \
  --pool-id <reviewed_pool_id> --pool-type <standard|boosted|nested> \
  --kind unbalanced --amounts-in <TOKEN:DECIMAL,...> \
  [--slippage-bps <1-500>]

purr balancer add --chain <chain> --protocol-version <same_version> \
  --pool-id <same_pool_id> --pool-type <same_pool_type> \
  --kind unbalanced --amounts-in <same_TOKEN:DECIMAL,...> \
  --min-bpt-out <quote.bptOut.minAmountRaw> \
  [--slippage-bps <same_bps>] --execute
```

### Proportional

Specify one pool token and amount as the reference. The quote calculates the
other required token amounts.

For a standard pool:

```bash
purr balancer add-quote --chain <chain> --protocol-version <2|3> \
  --pool-id <reviewed_pool_id> --pool-type standard \
  --kind proportional \
  --reference-token <TOKEN> --reference-amount <DECIMAL> \
  [--slippage-bps <1-500>]

purr balancer add --chain <chain> --protocol-version <same_version> \
  --pool-id <same_pool_id> --pool-type standard \
  --kind proportional \
  --reference-token <same_TOKEN> --reference-amount <same_DECIMAL> \
  --min-bpt-out <quote.bptOut.minAmountRaw> \
  --max-amounts-in <TOKEN:quote.maxAmountsIn[].amountRaw,...> \
  [--slippage-bps <same_bps>] --execute
```

For a boosted pool, `--tokens-in` is required and must select the wrapped or
underlying token for every required pool position:

```bash
purr balancer add-quote --chain <chain> --protocol-version 3 \
  --pool-id <reviewed_pool_id> --pool-type boosted \
  --kind proportional \
  --reference-token <TOKEN> --reference-amount <DECIMAL> \
  --tokens-in <TOKEN,...> [--slippage-bps <1-500>]

purr balancer add --chain <chain> --protocol-version 3 \
  --pool-id <same_pool_id> --pool-type boosted \
  --kind proportional \
  --reference-token <same_TOKEN> --reference-amount <same_DECIMAL> \
  --tokens-in <same_TOKEN,...> \
  --min-bpt-out <quote.bptOut.minAmountRaw> \
  --max-amounts-in <TOKEN:quote.maxAmountsIn[].amountRaw,...> \
  [--slippage-bps <same_bps>] --execute
```

Preserve the quote/pool token selection and never mix unrelated assets.

### Single-Token Exact-BPT

Specify the exact BPT output and cap the token input with the
`amountRaw` from the sole non-zero item in `quote.maxAmountsIn`.

```bash
purr balancer add-quote --chain <chain> --protocol-version <2|3> \
  --pool-id <reviewed_pool_id> --pool-type standard \
  --kind single-token-exact-bpt \
  --token-in <TOKEN> --bpt-amount-out <DECIMAL> \
  [--slippage-bps <1-500>]

purr balancer add --chain <chain> --protocol-version <same_version> \
  --pool-id <same_pool_id> --pool-type standard \
  --kind single-token-exact-bpt \
  --token-in <same_TOKEN> --bpt-amount-out <same_DECIMAL> \
  --max-amount-in <sole_nonzero_quote.maxAmountsIn_item.amountRaw> \
  [--slippage-bps <same_bps>] --execute
```

## Remove Liquidity

### Proportional Remove

For a standard or nested pool:

```bash
purr balancer remove-quote --chain <chain> --protocol-version <2|3> \
  --pool-id <reviewed_pool_id> --pool-type <standard|nested> \
  --kind proportional --bpt-amount-in <DECIMAL> \
  [--tokens-out <TOKEN,...>] [--slippage-bps <1-500>]

purr balancer remove --chain <chain> --protocol-version <same_version> \
  --pool-id <same_pool_id> --pool-type <same_pool_type> \
  --kind proportional --bpt-amount-in <same_DECIMAL> \
  [--tokens-out <same_TOKEN,...>] \
  --min-amounts-out <TOKEN:quote.minAmountsOut[].amountRaw,...> \
  [--slippage-bps <same_bps>] --execute
```

For a boosted pool, `--tokens-out` is required. It must cover every pool token
position and select the corresponding wrapped or underlying token:

```bash
purr balancer remove-quote --chain <chain> --protocol-version 3 \
  --pool-id <reviewed_pool_id> --pool-type boosted \
  --kind proportional --bpt-amount-in <DECIMAL> \
  --tokens-out <TOKEN,...> [--slippage-bps <1-500>]

purr balancer remove --chain <chain> --protocol-version 3 \
  --pool-id <same_pool_id> --pool-type boosted \
  --kind proportional --bpt-amount-in <same_DECIMAL> \
  --tokens-out <same_TOKEN,...> \
  --min-amounts-out <TOKEN:quote.minAmountsOut[].amountRaw,...> \
  [--slippage-bps <same_bps>] --execute
```

Do not omit, duplicate, or substitute boosted pool positions.

### Recovery Exit (Standard Pools Only)

Use recovery only when a standard pool is in recovery mode. Boosted and nested
pools support proportional remove only.

```bash
purr balancer remove-quote --chain <chain> --protocol-version <2|3> \
  --pool-id <reviewed_pool_id> --pool-type standard \
  --kind recovery --bpt-amount-in <DECIMAL> \
  [--slippage-bps <1-500>]

purr balancer remove --chain <chain> --protocol-version <same_version> \
  --pool-id <same_pool_id> --pool-type standard \
  --kind recovery --bpt-amount-in <same_DECIMAL> \
  --min-amounts-out <TOKEN:quote.minAmountsOut[].amountRaw,...> \
  [--slippage-bps <same_bps>] --execute
```

### Single-Token Remove

```bash
purr balancer remove-quote --chain <chain> --protocol-version <2|3> \
  --pool-id <reviewed_pool_id> --pool-type standard \
  --kind single-token --bpt-amount-in <DECIMAL> --token-out <TOKEN> \
  [--slippage-bps <1-500>]

purr balancer remove --chain <chain> --protocol-version <same_version> \
  --pool-id <same_pool_id> --pool-type standard \
  --kind single-token --bpt-amount-in <same_DECIMAL> --token-out <same_TOKEN> \
  --min-amount-out <sole_nonzero_quote.minAmountsOut_item.amountRaw> \
  [--slippage-bps <same_bps>] --execute
```

### Unbalanced Remove (V2 Only)

```bash
purr balancer remove-quote --chain <chain> --protocol-version 2 \
  --pool-id <reviewed_pool_id> --pool-type standard \
  --kind unbalanced --amounts-out <TOKEN:DECIMAL,...> \
  [--slippage-bps <1-500>]

purr balancer remove --chain <chain> --protocol-version 2 \
  --pool-id <same_pool_id> --pool-type standard \
  --kind unbalanced --amounts-out <same_TOKEN:DECIMAL,...> \
  --max-bpt-in <quote.bptIn.maxAmountRaw> \
  [--slippage-bps <same_bps>] --execute
```

## Quote Review

Before confirmation, show:

- pool ID, pool type, protocol, chain, and operation mode;
- each human-readable input and maximum input;
- expected BPT or token outputs and every minimum output;
- slippage and the exact raw bounds that will be passed to execution;
- likely ERC-20, Permit2, Router, or Vault approvals.

Use quote-provided raw amounts unchanged. Requote after any change to the pool,
pool type, kind, token selection, amount, protocol, chain, or slippage.
