# Native Spot

Use the current Agent wallet and the platform's exact Spot market hash. Check
installed help for `spot readiness`, `spot order` and `spot cancel`; they ship in
CLI v0.2.71 and require the corresponding deployed backend. Perpetual
readiness does not qualify Spot. Read current capability and native spendable
assets for the selected market; reuse current per-turn facts:

```sh
purr injective spot readiness --market-id "$SPOT_MARKET_HASH"
```

If the action is disabled, balances/metadata are unavailable or INJ cannot cover
the reviewed gas maximum, report that blocker. Do not switch to raw signing,
another account or sponsored gas. Readiness is an observation, not approval.

Spot orders use base quantity and quote price. A limit price is explicit and a
market buy needs a maximum price. Native market-sell price protection has not been
qualified; that business action is refused. Offer a limit sell and obtain approval
of its exact limit rather than claiming an unproven minimum market fill or silently
changing order kind. Use actual ticks and denoms; symbols do not prove identity.
These examples only produce local drafts, without HTTP or execution:

```sh
purr injective spot order --market-id "$SPOT_MARKET_HASH" --kind limit --side buy --quantity 0.1 --price 2 --max-fee-inj 0.001
purr injective spot cancel --market-id "$SPOT_MARKET_HASH" --order-hash "$ORDER_HASH" --max-fee-inj 0.001
```

The numbers are examples, not a recommendation or default. Before execution,
confirm the unchanged exact market/base/quote denoms, buy/sell, base quantity,
worst/limit price, quote-denominated fees and separate INJ ceiling under the main
skill's confirmation rule. Unknown fee metadata blocks execution. Submit once with
current `--wallet-generation`, original `--idempotency-key` and `--execute true`.
Cancel only an exact owned order observed on that Spot market. Policy holds and
unknown results follow [original-request recovery](errors.md).

Spot has no margin, leverage, TP/SL or reduce-only in this integration. A sell spends
owned base assets; it does not close a perpetual position or bypass opening-trade
policy/region controls. Use native spendable balances rather than adding Bank and
Exchange deposits. Fees and gas also reserve funds, including when INJ is the
base or quote asset. Unknown metadata is not zero or unlimited buying capacity.

After submission, use `orders`, `order-history` and `fills` with `--market-type
spot`, plus balances, to verify order/fill and asset receipts. A submitted receipt
is not a fill. Pending orders can freeze assets; cancellation inclusion alone
does not prove an indexed balance has caught up. Preserve exact denoms, raw
amounts and coverage; do not describe holdings as perpetual margin or PnL.
