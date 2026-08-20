# Typical Workflows

End-to-end recipes. Follow the Confirmation Contract in `SKILL.md` for every
account-changing action. Use only the parameterized commands in
[order-commands.md](order-commands.md); never construct or submit raw order,
modify, or cancel payloads.

Perform preparatory queries silently and surface only decisions,
confirmations, meaningful results, or errors that change the workflow.

## Shared Preflight

At the start of any exchange workflow:

```bash
purr hyperliquid status
```

If disabled, explain and confirm `enable`. Only `status`, `enable`, and
`disable` work while disabled.

Resolve every new market:

```bash
purr hyperliquid symbol --coin <coin> [--dex <dex>]
```

On `HYPERLIQUID_SYMBOL_AMBIGUOUS`, present each candidate's `coin`, `dex`,
`assetId`, and `szDecimals` and wait for the user. Use the selected candidate
directly; do not resolve it again.

Before `limit-order`, `bracket-order`, `stop-loss`, `take-profit`, or
`protect-position`, follow **Order Fee Preflight** in
[preflight.md](preflight.md). Never authorize or retry automatically.

## A. First-Time Fund and Status

1. Read integration, identity, and Arbitrum USDC:

```bash
purr hyperliquid status
purr hyperliquid account
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
```

2. Confirm a deposit of at least 5 USDC, then run:

```bash
purr hyperliquid deposit --amount <amount>
```

3. Recheck:

```bash
purr hyperliquid state --kind both
```

Report the Hyperliquid address, remaining Arbitrum USDC, and credited perp
collateral.

## B. Open a Perp Position

1. Resolve the market and read target collateral:

```bash
purr hyperliquid symbol --coin <coin> [--dex <dex>]
purr hyperliquid state --kind perp [--dex <dex>]
purr hyperliquid prices [--dex <dex>]
purr hyperliquid l2 --coin <canonical-coin>
```

2. Run fee preflight. Check size precision, margin, and any requested leverage
change.

3. For an ordinary entry, confirm and run:

```bash
purr hyperliquid limit-order \
  --asset <asset-id> \
  --side buy|sell \
  --size <asset-size> \
  --price <price> \
  --tif Gtc|Ioc|Alo|FrontendMarket \
  --reduce-only false
```

4. When the user wants entry plus TP/SL, use one bracket action:

```bash
purr hyperliquid bracket-order \
  --asset <asset-id> \
  --side buy|sell \
  --size <asset-size> \
  --entry-price <price> \
  --entry-tif Gtc|Ioc|Alo|FrontendMarket \
  --take-profit-price <tp-trigger> \
  --stop-loss-price <sl-trigger> \
  --execution market \
  --take-profit-worst-price <tp-worst> \
  --stop-loss-worst-price <sl-worst>
```

For limit-executed children, replace both worst-price options with their
matching TP/SL limit-price options. Confirm all three legs. For long entries,
TP should be above and SL below the intended entry/current market; reverse
that for shorts.

5. If leverage is changing, include it in the same final confirmation, run it
first, and submit the order only after it succeeds.

6. Reconcile:

```bash
purr hyperliquid orders --kind frontend [--dex <dex>]
purr hyperliquid state --kind perp [--dex <dex>]
purr hyperliquid fills
```

Capture entry and child OIDs instead of relying on conversational context.

## C. Equity / HIP-3 Perp

Resolve the exact builder-dex market:

```bash
purr hyperliquid symbol --coin TSLA --dex xyz
# or
purr hyperliquid symbol --coin xyz:TSLA
```

Run fee preflight, then inspect both default and builder-dex collateral:

```bash
purr hyperliquid state --kind both
purr hyperliquid state --kind both --dex xyz
```

Only the target dex's available collateral funds this order. If it is short
and default perp has enough, confirm `send-asset` separately:

```bash
purr hyperliquid send-asset --destination-dex xyz --amount <amount>
```

Re-read target state before leverage or order submission. Then use the ordinary
or bracket perp workflow above with the builder-dex `assetId`. Optional funding
context:

```bash
purr hyperliquid funding --coin xyz:TSLA --start-time <ms>
```

## D. Spot Buy

1. Inspect balances and move USDC from perp to spot if needed:

```bash
purr hyperliquid state --kind both
purr hyperliquid usd-class-transfer --amount <amount> --to-perp false
```

The transfer requires its own confirmation.

2. Resolve the spot market, run fee preflight, and place a typed
`limit-order` with the spot `assetId`.

3. Recheck `state --kind spot`, `fills`, and open orders.

## E. Add TP/SL to an Existing Position

1. Read the live position; do not use the historical entry size:

```bash
purr hyperliquid state --kind perp [--dex <dex>]
purr hyperliquid prices [--dex <dex>]
purr hyperliquid l2 --coin <canonical-coin>
```

2. Verify the exact asset, non-zero position side, and absolute current size.
For a long, TP normally belongs above current price and SL below it. For a
short, reverse this. Stop if a trigger is already crossed.

3. Run fee preflight. Confirm every trigger and execution boundary.

4. Add paired market protection:

```bash
purr hyperliquid protect-position \
  --asset <asset-id> \
  --position-side long|short \
  --size <current-position-size> \
  --take-profit-price <tp-trigger> \
  --stop-loss-price <sl-trigger> \
  --execution market \
  --take-profit-worst-price <tp-worst> \
  --stop-loss-worst-price <sl-worst>
```

Use `stop-loss` or `take-profit` when only one leg is requested or limit
trigger execution is needed.

5. Capture the new protection OIDs:

```bash
purr hyperliquid orders --kind frontend [--dex <dex>]
```

The filled entry OID is not the target and is not required.

## F. Modify TP/SL or an Entry

1. Locate and verify the exact open target:

```bash
purr hyperliquid orders --kind frontend [--dex <dex>]
purr hyperliquid order-status --oid <oid-or-cloid>
```

2. Reconstruct the complete replacement parameters from the current order plus
the requested change. Confirm the target OID and all fields.

3. Use `modify-limit-order` for an open entry/ordinary limit,
`modify-stop-loss` for an SL child, or `modify-take-profit` for a TP child.

A bracket or paired position protection is not modified as one object. Modify
each still-open leg by its own OID. A filled entry cannot be modified; manage
the position or its protection instead.

4. Re-read frontend orders or exact status.

## G. Close or Reduce a Position

1. Read the current position, resolve the asset, and run fee preflight.
2. Confirm an opposite-side, reduce-only order sized to the requested amount.
3. Run:

```bash
purr hyperliquid limit-order \
  --asset <asset-id> \
  --side <opposite-side> \
  --size <close-size> \
  --price <price-or-frontend-market-boundary> \
  --tif Gtc|Ioc|FrontendMarket \
  --reduce-only true
```

There is no separate `close-position` command. `FrontendMarket` still requires
an explicit user-confirmed protection price.

4. Verify the remaining position with `state`. Do not claim flat from the
submission response alone.

## H. Cancel an Open Order

```bash
purr hyperliquid orders --kind frontend [--dex <dex>]
purr hyperliquid order-status --oid <oid-or-cloid>
```

After confirming the exact target:

```bash
purr hyperliquid cancel --asset <asset-id> --oid <numeric-oid>
# or
purr hyperliquid cancel-by-cloid --asset <asset-id> --cloid <cloid>
```

Re-list open/frontend orders. A filled historical order cannot be cancelled.

## I. Withdraw Profits

1. Read free collateral with `state --kind both`.
2. Confirm and submit `withdraw --amount <amount>`.
3. Keep the returned `nonce`. A successful submit is not proof of Arbitrum
arrival.
4. When requested, check:

```bash
purr hyperliquid withdraw-status --nonce <nonce>
```

`pending` means wait without resubmitting. On `arrived`, report
`amountUsdc`, `feeUsdc`, and `txHash`. If no nonce was captured, reconcile
balances only; never invent one.

## J. Research Only

Trading must still be enabled for gateway reads:

```bash
purr hyperliquid symbol --coin <coin> [--dex <dex>]
purr hyperliquid markets --kind both [--dex <dex>]
purr hyperliquid prices [--dex <dex>]
purr hyperliquid l2 --coin <coin>
purr hyperliquid candles --coin <coin> --interval 1h --start-time <ms>
purr hyperliquid funding --coin <coin> --start-time <ms>
```

Do not place or change orders in this path.

## K. Dead-Man Switch

Confirm a human-readable time before scheduling:

```bash
purr hyperliquid schedule-cancel --time <unix-ms>
```

Confirm clear intent before removing a schedule:

```bash
purr hyperliquid schedule-cancel
```

## L. Disable Trading Integration

Inspect all exposure:

```bash
purr hyperliquid snapshot
purr hyperliquid state --kind both
purr hyperliquid orders --kind frontend
```

Close positions and cancel open orders with separate confirmations. Then
confirm `disable`. On `HYPERLIQUID_TRADING_DISABLE_BLOCKED`, show the blockers
and obtain a new confirmation only after exposure is clear.
