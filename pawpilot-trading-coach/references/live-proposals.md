# Live proposal-only workflow

Require the trusted current Live Run, actual venue/account/market and discoverable
terminal_read + terminal_prepare_card. Otherwise explain the missing capability;
do not invoke another execution tool. Read only requested account/position/settings
facts. Account not connected does not prevent learning or Playbook discussion.

Clarify amount meaning (native quantity, quote notional or collateral budget),
asset, side, type and any requested leverage/margin/protection. margin_budget
requires explicit leverage and marginMode; never guess one. Prepare place_order
with marketKey, side, type, sizing {kind,amount,asset}, optional price/risk and
protection. The host registers intent only; the independent native web review
calculates the fresh actual quantity for base quantity or quote notional, validates
balance/risk and applies supported settings. A collateral budget that the native
ticket cannot guarantee requires the user to explicitly choose quantity or quote
notional in Edit draft; never convert it with budget times leverage or claim the
fees fit that budget. It never borrows Paper balances or quotes.

Publish returned message/metadata unchanged through send_message(target=current).
The user chooses Review/Edit draft, checks the actual native account and fresh
preview, then confirms manually through the existing venue execution path.
A natural-language yes is not a financial confirmation. There is no model submit
tool. Drafts expire; credentials/account changes prevent submission.

Read operation=receipt with the original actionId to recover within the same chat.
Never prepare another action to recover history. Accepted, rejected, pending and
unknown remain distinct. Hyperliquid primary rejection cannot be called accepted
because a protection leg succeeded; Lighter sendTx acknowledgement is still
pending until execution evidence. Acceptance does not prove fill. For pending or
unknown outcomes direct the user to the original receipt, never replay as new.
