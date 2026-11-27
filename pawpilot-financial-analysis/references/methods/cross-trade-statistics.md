# Cross-trade statistics method

State account/portfolio scope, time window, qualifying closed trade count, denominator and coverage. Continue returned cursors for a requested full scope; a page or visible table is not the population. Distinguish partial observations from aggregate totals returned by the server.

For the Paper Trade Performance evaluation and the results topic in Live readiness, use the `outcomes` query for the selected scope and window. Cite the returned observation time. The overall confirmed sample in `confirmed.trades` includes wins, losses and breakevens with final net evidence. Use `confirmed.winRatePercent` when the user asks for the rate. A currency-specific pattern uses that settlement row's `netKnown` and `settled` outcomes. Describe the remaining closes as unknown net outcomes. Use the recorded price and confirmed net columns for their respective measures.

Keep amounts in the statistics panel for a button-triggered evaluation. Give a short qualitative assessment of the sample and one practice adjustment. When the user asks for numbers, preserve exact per-asset amounts. The optional `confirmed.approximateUsdNet` has its own count and sums confirmed USD, USDC and USDT at 1:1. Use the returned amount and label the approximation. Other currencies retain their own settlement rows.

Use `pending.fundingConfirmationMissing` for trades whose funding evidence has yet to be confirmed, and `pending.fundingSettlementPending` when the ledger has a pending settlement. Fee conversion and other evidence gaps have their own counts. Use “awaiting funding verification” when an older receipt gives only the combined funding count.

Live readiness discusses practice, stop use, leverage, results and planned exits. Match each topic to its own evidence and eligible sample. Opening protection, leverage and exit behavior need the corresponding facts, in addition to the outcome summary. Leverage describes exposure. Proximity to liquidation needs a native estimate and its same-snapshot reference price. Treat topics with missing support as unknown and keep the assessment advisory.

Describe win rate, return/cost distributions, drawdown or R only when the corresponding metric evidence supports them. Missing initial risk differs from missing costs. Do not turn a zero lifecycle-gap count into proof that every metric is complete. Avoid comparing incompatible assets, cost currencies or native PnL conventions.

Use small samples descriptively, not as predictive certainty or causal claims. Control for market regime, side and holding period before attributing outcomes to behavior. Distinguish observed patterns from confirmed preferences. Suggest a falsifiable practice question or lesson; obtain human confirmation before saving guidance, and a separate natural request before changing Playbook.
