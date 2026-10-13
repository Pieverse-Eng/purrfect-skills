# Pre-trade check

Use the current selected market and account. Ask for missing side, product,
amount meaning, order type or intended protection. Load
`pawpilot-paper-trading` before preparing an action.

Read the host's current market/account facts and relevant confirmed plan/Lessons.
Prepare the explicit draft to obtain the actual preview. Explain:
- native market, quantity, price/execution bound, product and settlement scope;
- supported leverage/margin mode and fees/reservation;
- executable book, mark and funding readiness, separately;
- preview coverage and liquidation estimate only when the host supplies them;
- missing protection or conflicts with a user-confirmed plan as observations,
  not an instruction to silently modify or prevent the user's valid order.

A suggested stop is not a submitted protection order. Unsupported or unavailable
risk values must stay unavailable. If the user changes size/price/market,
prepare a new review rather than reusing earlier consent.
