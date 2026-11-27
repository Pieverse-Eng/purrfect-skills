# Compare user-selected scenarios

## Inputs

Use only the user's chosen prices or rate/time assumptions. Ask for missing
inputs; never supply an attractive target, leverage or stop as an unselected
“example” for this user's trade. No probability is implied by a scenario.

Paper terminal_read uses operation=query, query={operation:"scenario",positionId,
assumptions}. Live uses operation=scenario, positionId, assumptions directly.
`assumptions` contains source="user", prices (one to five positive decimal
strings), and optionally funding={ratePerInterval,intervalHours,holdingHours,
referencePrice}. Rate and referencePrice are decimal strings; hours are numbers.
Preserve the user's amount meaning; funding rate is a fraction per interval,
not percentage points. Do not invoke an unsupported operation repeatedly.

## Interpretation

The host uses owned quantity, entry and native contract size; it returns native
quote-unit notional and price PnL for unchanged quantity. Its funding amount is
a constant-price, constant-rate prorated illustration, with explicit precision
and half-even rounding to 18 decimal places. A negative paid amount represents
receipt. `finalNet=null` is deliberate: execution fees, slippage and actual
future funding are not established. It does not simulate liquidation or margin
paths and is not an executable quote. Preserve the returned numbers, units and
limitations without replacing them with model estimates.

Compare the outcomes symmetrically, explain which assumption drives the difference,
and what evidence would make the comparison stale. No default winner, hidden
trade selection or automatic prepare follows the calculation. Stale Live position
data must be refreshed through the existing account read path before calculation.
