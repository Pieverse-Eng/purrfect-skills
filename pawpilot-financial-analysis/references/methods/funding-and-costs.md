# Cost and funding method

Keep price PnL, realized/unrealized components, fees by asset, settled funding and estimates separate. Use each source's explicit sign and inclusion conventions. Paper fundingPaid is positive paid; normalized Live funding received is positive. Never subtract fees/funding already included in a native net figure twice.

Recorded partial cost evidence permits a known subtotal with its scope and missing components, not a final net. A foreign-asset fee needs conversion evidence. No funding checkpoint is not evidence of zero funding. State lifecycle/history gaps independently of metric gaps.

Current/predicted funding is not settled cost or a daily guarantee. A future illustration needs user-defined rate, interval, holding period and reference assumptions and the existing deterministic scenario calculation. Label estimates and assumptions; variable rates, settlement schedules, partial fills and liquidity change outcomes. An entry-price stop is not guaranteed breakeven after costs and slippage.
