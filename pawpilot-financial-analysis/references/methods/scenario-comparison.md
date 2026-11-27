# User-defined scenario method

Use the existing deterministic query calculator for numerical outcomes. Preserve the user's supplied price/time/rate assumptions; request only missing assumptions that materially change the result. Do not turn a desired price into a prediction or silently choose a forecast horizon.

Compare like-for-like scope, side, native quantity, contract multiplier, reference price and observation time. Explain gross price PnL separately from known fees, settled funding and future estimates. When future costs are unknown, explain the calculated subtotal and unknown net instead of inventing final net. Show assumptions and what the calculation excludes (gaps, liquidity, rate changes, liquidation path).

Use the scenario receipt's `baseline.markPrice` and `baseline.pricePnl` as the comparison point, then use the returned `pricePnl` and `pricePnlDelta` for each target. They use one position snapshot and one price-based calculation. A native unrealized PnL figure may use an exit-side quote with a different basis. If the receipt lacks its own baseline, give the hypothetical price PnL and state that the change from the current mark is unavailable. Include the scenario's quote unit and observation time.

A terminal scenario is not a full path simulation: a position can be liquidated or stopped before the assumed end price. Reference liquidation/protection snapshots carefully with their timestamps. User-defined scenarios describe consequences; they do not authorize an order or recommend unrequested parameters.
