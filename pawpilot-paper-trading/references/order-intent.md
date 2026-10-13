# Order intent

Read `paper_read(operation="account")` and `paper_read(operation="market")`.
The host binds owner, Agent, portfolio, account and selected market. Use its
marketKey, native base/quote units, quantity step, price tick, size/notional
limits, margin modes, leverage range and supported order/protection types.
Do not reconstruct an identity from a ticker or a live signing asset ID.

## Amount and risk

- Explicit base quantity: sizing kind `base_quantity`, decimal amount in
  returned native base units.
- Explicit trade value: `quote_notional`, decimal amount and returned quote
  asset. Do not treat leverage as multiplying a notional amount.
- Explicit collateral budget: `margin_budget`, decimal amount and returned
  collateral asset, plus the user's leverage and supported margin mode.
- “Use $100 at 5x” is ambiguous. Ask whether $100 is trade value or collateral
  budget; also resolve side and product if missing. A previous Lesson cannot
  supply permission or silently choose current size.
- Percent/all requests require a verified balance or position and an explicit
  sizing choice. Never calculate from a stale UI amount or assume 1% reserve.

The host performs Decimal conversion, step rounding, fee/reservation checks
and risk evaluation. Never compute base size, liquidation or fee values with
mental arithmetic. If it cannot prove a budget-safe quantity, explain the
returned unsupported/blocked reason instead of proposing a guessed size.

## Prepare and publish

Call `paper_prepare_card` with kind `place_order`, the verified marketKey,
side, type, explicit sizing and any requested price, risk, TIF, slippage or
protection. Missing policy choices are not consent to invent aggressive defaults.
Show the prepared values and advisory coverage exactly; estimated fills and
liquidation are not guarantees. Preserve the tool's action reference.

For a close/reduction, read the exact current position and use an opposite-side
reduce-only proposal with the desired native quantity. Identify full vs partial
close. Do not reuse a historical filled entry as an open order.
If the host reports a changed target, stop and refresh; do not silently enlarge
or retarget the action.
