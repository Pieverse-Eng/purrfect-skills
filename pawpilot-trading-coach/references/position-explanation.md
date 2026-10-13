# Position and funding explanation

Read current positions, balances and market inputs from `paper_read`.
Separate observed position PnL, reported fees, available collateral and account
equity. Preserve native quantity and asset units.

A missing stop-loss is a factual check on a nonzero current position. Explain
the risk and offer to prepare protection after the user chooses parameters.
Do not assume a closed position still needs a stop or that changing a historical
entry protects a current position.

Explain funding in two stages: native funding-history confirmation, and actual
pending settlements on this account. Include the affected market and check time.
Missing event/reference evidence cannot be replaced by a current mark or waived.

Do not invent daily funding expense, +1R progress, automatic nudges or estimated
liquidation when the host does not return sufficient evidence. If a model
analysis is requested, label it interpretation and keep it separate from facts.
