# Auditable evidence and complete summaries

Paper terminal_read operation=query accepts typed host query objects:
- statistics: measure count/sum/average/ratio, optional field, filters predicate array and flat
  accountScope=account|portfolio, marketKey/venue/side/from/to. Numeric fields:
  leverage, realizedPnl, netResult, resultR, initialRisk, holdingSeconds,
  entryPrice, exitPrice, openingStop, openingStopSet, openingTarget, closingOrderMatchesOpeningProtection.
  A predicate is {field,operator:eq|gt|gte|lt|lte|known,value} or valueField
  instead of value; known takes neither. Example stop-use query:
  {operation:"statistics",measure:"ratio",field:"openingStopSet",filters:[{field:"openingStopSet",operator:"eq",value:"1"}]}.
  The host reports eligible/missing counts; absent original protection is unknown.
  No arbitrary SQL.
- trades: same scope filters, optional exact cycleId, bounded limit and host nextCursor.
  closingOrderMatchesOpeningProtection describes only the final closing order: it
  shares the first opening parent and original trigger price. It is not proof
  that every partial exit or a written strategy was followed.
- timeline: target {kind:cycle|position,id}, limit/cursor; actual fills,
  command requests, protection changes, funding and immutable linked plan revisions.
- prices: same owned target, tf and bounded limit/to; real OHLC, native units,
  source, coverage and gaps. Missing series must not be drawn as a fabricated line.

Use query results' scope/sample/coverage, metric eligible/missing counts and
source refs. Full-scope statistics are distinct from a page of trades. Follow
pagination when examining individual trades; do not call the visible page all
history. Price-based patterns require actual corresponding market prices and
times; never infer candle shape from PnL or a text Lesson. Compare intended and
actual exits only with linked pre-open evidence; later notes are not initial plans.

Original R uses recorded original cash risk and complete net outcome. Moving a
stop does not rewrite initial risk; missing opening legs, fees, funding or cost
basis keep the result unknown. Do not label observed high return a stable edge.

Live terminal_read supports current account/positions/orders/settings and existing
native closed-position history. Orders and history are paginated; preserve
coverage.complete=false and missing-source reasons. Live original R or full
historical statistical claims require evidence actually returned; Paper facts
never fill Live gaps. Shared worker snapshots have independent component
freshness. Stale data cannot justify an order or a readiness claim.

For Paper-to-Live discuss five themes: practice sample, protection use, leverage,
recent net/R, plan exits. Explain chosen thresholds rather than hard-coding the
OnePager examples. Ordinary Live trading remains available without passing this
advisory checklist. Use a supported Live intent only after the user requests it.
