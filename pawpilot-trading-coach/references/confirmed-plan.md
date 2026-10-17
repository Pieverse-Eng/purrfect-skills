# Discuss, confirm and revise a Paper plan

A Plan belongs to a particular account and market/trade; it is not a user's
long-term Playbook. Discuss the user's goal and chosen limits, then show a short
editable summary. Save only after the user explicitly confirms that summary.
Passive hints and prefilled text are not consent. Do not force a plan to trade.

When the current Paper Run advertises paper_save_plan, use it only after that
confirmation. Read the actual tool schema; the input includes confirmed=true,
the complete exact initiating user message as authorizingMessage (at most 512
characters), and plan with kind=plan, the bound marketKey, concise content (at
most 512 characters), and optional verified orderId or actionId/actionVersion links when present. Do
not send an invented evidence property; provenance is recorded by the host. For revision
read the original record and supply its real edit.id and edit.version. Never
use a made-up version. If the confirmation is too long, request a short explicit
confirmation in a new turn; do not truncate or paraphrase authorizingMessage.

This host capability is optional. If absent, retain the discussion as unsaved
and use the existing Plans edit/confirm UI; do not improvise a shell/database
write, a new tool, a Playbook card or an order preparation. In a scoped research
Run it is deliberately unavailable: discuss first and confirm in a normal
Paper conversation.

Only status=ready with data.record containing the saved id/version proves
persistence. A timeout or stopped call cannot be described as saved. Reopen/read
that original record where available; do not blindly save again. A version
conflict requires reading the current plan and confirming the intended change.
Saving a note does not place a stop or enforce a maximum dollar loss.

The backend records timing and all versions. Plans confirmed after entry must
be called after-entry additions, never evidence of an entry-time plan. Original
opening risk stays immutable. Missing original stop/risk means R remains unknown;
a later 20-dollar budget cannot fill it. Keep preference, confirmed principle,
plan and observed performance distinct.
