---
name: pawpilot-paper-trading
description: Use when the user requests a Paper Trading order, buy or sell, open or close, order amendment, cancellation, TP/SL, simulated deposit or transfer in the PawPilot terminal.
version: 1.0.0
author: Pieverse
metadata:
  hermes:
    tags: [pawpilot, paper-trading, orders, hyperliquid, lighter, orderly]
    related_skills: [pawpilot-trading-coach]
    requires_tools: [paper_read, paper_prepare_card]
---

# PawPilot Paper Trading

Prepare Paper actions for the current terminal through the host tools. The
user's existing Agent remains the conversational agent. A request to trade
authorizes preparation; only the terminal's separate human review confirms
execution.

## Start here

Read the reference for the requested operation before preparation.

| Request | Reference |
| --- | --- |
| Buy, sell, open or close; amount, leverage or market ambiguity | [Order intent](references/order-intent.md) |
| Amend, cancel, batch cancel or protect an existing target | [Order lifecycle](references/order-lifecycle.md) |
| Simulated deposit or transfer | [Account actions](references/account-actions.md) |
| Rejection, stale evidence, partial or unknown execution | [Recovery](references/errors-and-recovery.md) |
| Venue/product identity or unsupported capability | [Venues](references/venues.md) |

1. Read the bound account and the relevant market/target using `paper_read`.
   Use returned native identities, versions, units and capabilities.
2. Resolve missing intent with `clarify`; never infer whether a money amount
   means notional or collateral. Read the relevant plan and confirmed Lessons
   when the user asks to apply them.
3. Call `paper_prepare_card` with the explicit intent. The host calculates,
   previews and registers the proposal. Treat a non-ready result as a blocker.
4. Publish the returned text and inline keyboard through `send_message`,
   preserving its registered callback references. Do not hand-build financial
   `metadata.actions`, invent a reference or bypass preparation.
5. Tell the user to review the native card. A natural-language “yes”, including
   “帮我下单”, is not a host financial confirmation.

## Boundaries and verification

Stay in this Run's Paper account and market; changing the page does not rebind
an old Run or card. Ask the user to switch the page/account and send a new
request for a different scope. Never call a live venue CLI, SDK, signer,
wallet, fee-approval, onboarding or withdrawal operation.

Preparation does not reserve money or prove execution. Accepted is not filled.
Use `paper_read` receipt results for the original registered action; report
partial, pending, failed and unknown separately. Do not retry an unknown
command as a new order. Missing book, mark, funding, risk or historical evidence
is a reason to stop and explain, never a license to invent a value.

