For Live read terminal_read account/positions/orders/settings and native history as needed. Preserve component freshness and unknown protection. Do not use Paper-only market/notes/review operations in Live. Current settledFundingSinceOpen is not a forecast of daily cost.

# Position and funding explanation

Read current positions, balances and market inputs from `terminal_read`.
Separate observed position PnL, reported fees, available collateral and account
equity. Preserve native quantity and asset units.

For a Paper holding card, request operation=query with a timeline query targeting
the owned position id. For Live, operation=positions returns citeable snapshot
facts. Publish holding only with the exact position id in those facts.

A missing stop-loss is a factual check on a nonzero current position. Explain
the risk and discuss protection. Paper can prepare a supported protection draft
after the user chooses parameters. Live currently prepares new place_order
intents only; use the existing manual position controls for protection changes
instead of calling an unsupported Live prepare kind.
Do not assume a closed position still needs a stop or that changing a historical
entry protects a current position.

Explain funding in two stages: native funding-history confirmation, and actual
pending settlements on this account. Include the affected market and check time.
Missing event/reference evidence cannot be replaced by a current mark or waived.

Do not invent daily funding expense, +1R progress, automatic nudges or estimated
liquidation when the host does not return sufficient evidence. If a model
analysis is requested, label it interpretation and keep it separate from facts.
