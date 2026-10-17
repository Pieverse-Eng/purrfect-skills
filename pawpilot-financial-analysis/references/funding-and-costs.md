# Costs and funding

## Evidence and method

Separate price PnL, fees by asset, settled funding, pending/unconfirmed funding,
and any final net outcome. Paper `costs.knownNetSubtotal` includes only recorded
price PnL minus USDC fees and settled funding paid. `final=false` is provisional;
`scope=recorded_fills_only` also means historical projection gaps. Explain the
returned missing reasons rather than collapsing every known value to Unknown.

`coverage.incompleteTrades` counts cycle/lifecycle gaps. Zero there does not prove
all metrics are known: inspect each `metricEvidence` and cost completeness.
Original risk missing is distinct from funding missing. Foreign-asset fees need
actual conversion evidence before a final net amount is claimed.

Live keeps its venue-native PnL and explicit fee/funding inclusion. Its normalized
settledFundingSinceOpen is positive received, negative paid; Paper fundingPaid
uses positive paid. Do not subtract a native amount twice or impose Paper net
semantics on Live. State units and conventions alongside comparisons.

## Future periods and limitations

A displayed current or predicted funding rate is not actual daily cost. For
user-supplied rate, interval, reference price and holding period use a scenario
calculation; identify every assumption. Do not turn an annualized or prorated
illustration into scheduled settlement, accrued liability or a forecast. Rate
changes, reference price changes, partial fills and venue settlement timing can
change outcomes. No funding checkpoint is not proof of zero funding.
