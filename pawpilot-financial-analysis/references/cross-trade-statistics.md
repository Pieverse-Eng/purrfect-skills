# Analyse a set of trades

## Evidence and method

State account/Paper-or-Live, market/time filters and trade definition.

- Paper: use the typed statistics queries described in Coach's evidence reference
  over the whole selected scope. Follow nextCursor for individual records. Trade
  pages may be shorter than the requested limit because of the transport budget.
- Live: the current host exposes paginated history, not Paper query/statistics.
  Follow its cursor and preserve coverage.complete=false and field missing reasons,
  even on the last page. Discuss only supported observations; unavailable full-range
  aggregates, opening-stop use or plan-exit ratios must remain unavailable. Do not
  call a nonexistent statistics operation or apply Paper net-PnL definitions.

A fetched page is not the total, and exhausting a cursor does not fill history gaps.

For each result retain sample size, eligible denominator, missing count, period,
unit and source references. Compare like units and venue definitions. Unknown is
not zero; zero profit is not missing. Distinguish fills from completed cycles,
partial exits from separate trades, and sample associations from causal claims.

Patterns such as trading after a large candle need actual price/time evidence.
Counts of “plan followed” need a plan linked before entry and the relevant exit
semantics; a final protection order match cannot establish every partial exit.
Do not encode fixed chase/revenge/edge labels or invent data beyond returned facts.

## Counterevidence and limitations

Look for missing history, different market regimes, costs, survivorship and a
small or selectively chosen sample before generalizing. Reproduce the numerator
and denominator through permitted queries. Do not report calibrated probability
or stable advantage without adequate evidence.

Paper-to-Live readiness covers practice, protection, leverage, recent result and
plan exits. Discuss thresholds with the user; the OnePager numbers are examples,
not backend gates. A good practice record does not establish live profitability;
fees, liquidity, execution and emotional stakes can differ. Ordinary Live access
and human review remain unchanged.
