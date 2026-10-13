---
name: pawpilot-paper-trading
description: Use when placing or managing Paper orders.
version: 1.0.1
author: David Zhou (@David-0x221Eight), with Hermes Agent
metadata:
  hermes:
    tags: [pawpilot, paper-trading, orders, hyperliquid, lighter, orderly]
    related_skills: [pawpilot-trading-coach]
    requires_tools: [paper_read, paper_prepare_card]
---

# PawPilot Paper Trading Skill

Prepare Paper actions for the current terminal through the host tools. The
user's existing Agent remains the conversational agent. A request to trade
authorizes preparation; only the terminal's separate human review confirms
execution.

## When to Use

Use for Paper buy/sell, open/close, amendment, cancellation, TP/SL, simulated
deposit or transfer requests. Do not load a financial workflow for greetings.
A Live request needs the Live page and its own permitted workflow; this Skill
cannot operate across modes.

## Prerequisites

The current Run must have a trusted Paper account/market context and both
native `paper_read` and `paper_prepare_card` host tools. These are supplied by
the platform plugin and authenticated backend, not a venue SDK or shell.
Keep the user's disabled-Skill setting. Without the tools or current scope,
explain the missing capability instead of bypassing it.

## How to Run

Use `skills_list` then `skill_view` to read this Skill and the needed Markdown
reference. Read the bound facts, clarify intent, prepare one registered card,
and publish it to the current conversation. Execution remains a separate
human action in the terminal.

## Quick Reference

Read the reference for the requested operation before preparation.

| Request | Reference |
| --- | --- |
| Buy, sell, open or close; amount, leverage or market ambiguity | [Order intent](references/order-intent.md) |
| Amend, cancel, batch cancel or protect an existing target | [Order lifecycle](references/order-lifecycle.md) |
| Simulated deposit or transfer | [Account actions](references/account-actions.md) |
| Rejection, stale evidence, partial or unknown execution | [Recovery](references/errors-and-recovery.md) |
| Tool argument and publication shapes | [Tool contracts](references/tool-contracts.md) |
| Venue/product identity or unsupported capability | [Venues](references/venues.md) |

## Procedure

1. Read the bound account and the relevant market/target using `paper_read`.
   Use returned native identities, versions, units and capabilities.
2. Resolve missing intent with `clarify`; never infer whether a money amount
   means notional or collateral. Read the relevant plan and confirmed Lessons
   when the user asks to apply them.
3. Call `paper_prepare_card` with the explicit intent. The host calculates,
   previews and registers the proposal. Treat a non-ready result as a blocker.
4. Publish the returned text and inline keyboard through `send_message`,
   copying `data.message.text`, `data.message.reply_markup` and `data.metadata`
   from the tool result. Preserve the registered callback references and
   preparedActions metadata together. Do not hand-build financial
   `metadata.actions`, invent a reference or bypass preparation.
5. Tell the user to review the native card. A natural-language “yes”, including
   “帮我下单”, is not a host financial confirmation.

## Pitfalls

Stay in this Run's Paper account and market; changing the page does not rebind
an old Run or card. Ask the user to switch the page/account and send a new
request for a different scope. Never call a live venue CLI, SDK, signer,
wallet, fee-approval, onboarding or withdrawal operation.

Missing book, mark, funding, risk or historical evidence is a reason to stop
and explain, never a license to invent a value. Do not retry an unknown
command as a new order.

## Verification

Preparation does not reserve money or prove execution. Read the original
action/call receipt to recover its command result. A completed action or
command can contain an accepted order snapshot; it is not proof of a fill.
Only describe filled/cancelled state from authoritative current evidence.
The current host orders read lists active orders; absence there proves neither
fill nor cancellation. If final evidence is unavailable, say so and refer the
user to the terminal's order/receipt view. For batch cancellation, the receipt
includes a current job: report its status and skipped/failed counts separately.
