# Account reads

Existing platform credentials and `INSTANCE_ID` bind every call to the current
Agent and wallet generation. No address, subaccount or network override exists.
Do not reuse cached data or cursors after switching Agent or wallet.

```sh
purr injective status
purr injective account
purr injective balances
purr injective positions --market-type perp --limit 50
purr injective orders --market-type spot --limit 50
purr injective order-history --market-type perp --limit 50
purr injective fills --market-type perp --limit 50
```

`status` is a cheap capability/identity check, not a fresh portfolio or trading
readiness check. The Phase 2 backend reports `mode: read_only` and
`executionEnabled: false`. Preserve returned capability fields if a later backend
changes them; this CLI and skill still expose only reads. Reads work with zero
INJ; never propose enable/open-account/deposit as a read prerequisite.
`account` shares a collection with balances and unfiltered positions. Choose the
smallest query answering the request. Positions are perpetual only; orders,
history and fills require explicit `spot` or `perp`.

History defaults to the backend's fixed last seven days. For another period,
provide both RFC3339 bounds, at most 31 days apart. Preserve those exact bounds
on subsequent pages:

```sh
purr injective fills --market-type perp --start-at 2026-10-01T00:00:00Z --end-at 2026-10-02T00:00:00Z --limit 50
purr injective fills --market-type perp --start-at 2026-10-01T00:00:00Z --end-at 2026-10-02T00:00:00Z --limit 50 --cursor "$NEXT_CURSOR"
```

`NEXT_CURSOR` must be the previous response's opaque value for the same Agent,
wallet generation, product, market, time bounds and page limit. Account pages
can shift as the indexer changes; deduplicate native IDs, retain coverage, and
do not claim a consistent snapshot or all-time history. Limits are 1–100.
Optional `--market-id` filters require a verified native hash.

## Balance interpretation

Keep every exact denom separate even when both display USDC or USDT. Report
`bank`, `exchangeTotal`, `exchangeAvailable`, `held`, `positionMargin`,
`spendable` and `total` as distinct fields. Default subaccount bank/exchange
amounts may overlap. A wallet card is another view of that wallet, not another
holding. Never add these fields together without explicit provenance.

For example, bank=100, exchangeTotal=100 and held=10 do not establish total=200
or spendable=90. Use returned `spendable`/`total`; null means unknown. An
`exchangeAvailable` value is that ledger's observation, not proven overall
trading capacity. Missing decimals/metadata prevent an amount interpretation;
do not guess six decimals for every stablecoin. Unknown PnL, funding and
liquidation values remain unknown. Include component freshness and source time.
