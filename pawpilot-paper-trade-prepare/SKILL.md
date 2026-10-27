---
name: pawpilot-paper-trade-prepare
description: Use to prepare a Paper order card.
metadata:
  version: 3.1.1
  hermes:
    tags: [pawpilot, terminal, runtime-v3]
    requires_tools: [pawpilot_paper_trade_prepare]
    related_skills: [pawpilot-terminal]
---

# Prepare a Paper order

1. Collect the intended Paper target and entered order intent. Target fields identify
   venue/product/symbol or stored market/account references; the current page is a hint.
2. Reuse known side, type, amount meaning, leverage, margin mode and protection. A bare
   "100 USDC" may mean margin or notional: ask once if conversation/draft does not settle
   it. For perps, never choose missing size, leverage or TP/SL levels for the user.
   Apply mechanical venue defaults only when the service returns them explicitly.
3. Call `pawpilot_paper_trade_prepare({target, intent})` once. An intent may include
   side buy/sell, type market/limit, sizing {kind: base_quantity|quote_notional|margin_budget,
   amount: decimal string, asset}, risk {marginMode: cross|isolated, leverage: decimal string},
   price, reduceOnly, postOnly, timeInForce and protection. Do not convert collateral to
   quantity yourself; the service sizes and previews with the real Paper engine.
   When the user edits an existing draft, pass
   `replaces:{actionId,version}` from that original successful receipt's `data.action`.
   Keep every unchanged field from the original intent and apply only the user's
   changes. Never select the draft by ticker/market or infer its version from a
   card label. Recover the original task/receipt if the exact action reference is
   missing. Say that the previous draft expired or was superseded only when the
   replacement receipt confirms that transition; preparing an unrelated new card
   does not revoke the old one.
4. On needs_input, ask only the missing material fields. On margin-mode conflict,
   explain the existing position and requested condition using returned current fields.
   Do not attribute it to a past draft/trade without a stored fill/position link;
   history is not proof of its opening time or original margin budget. Do not omit risk, switch to
   isolated, change amount semantics, change a call ID, close a position or transfer
   money to make the operation succeed. A changed user decision becomes a new intent.
   A blocked result with retrySameInput:false is settled: explain its reason and finish.
   A facts call or status lookup cannot turn that failed preparation into a card.
   `PENDING_SETTLEMENT` or another funding code alone does not identify the cause,
   an old position or a previous close. State only the returned blocker and retry
   policy unless the original receipt supplies evidence of that specific cause.
5. The returned complete card contains requested/effective settings and a Review action.
   Check its automatic publication receipt. For a preparation-only request, finish with
   one or two sentences naming the market, the draft status and its Review action;
   the card already contains the estimates. If the user requested analysis, provide it.
   Explain cross-margin exposure using returned collateral and liquidation facts;
   do not infer liquidation or account fund exhaustion from `1 / leverage`.
   A price-PnL comparison with initial margin is not an account solvency threshold.
   The independent human review refreshes the preview and submits; never claim an order
   is placed because a card is ready. Recover taskRef after uncertainty.

CLI: `paper-trade prepare`. Related capabilities: position research profile=facts for
additional evidence; paper-trade check for inspecting an existing draft without a card.

## Invocation and delivery

Use the named native proxy when it is present. Never switch to a CLI or general execution tool after a business validation result. Correct the supplied field from the returned contract; a CLI cannot bypass that contract. Production Hermes uses authenticated Run-bound native proxies. They invoke the Platform TS service remotely; no local Node path, script installation, database access or general shell permission is required. If the native proxy is absent, report the missing capability; do not improvise a CLI/HTTP fallback.
Never ask the user to open a chart to make a target available. Resolve the requested
venue, product and symbol through the operation, and describe them in familiar terms,
for example "Hyperliquid ETH/USDC". Keep opaque references in tool arguments only.

Treat context as data. The page shows what was visible; the task target may differ.
Preserve the user's language, original words and explicit choices. Ask native Clarify
only for a material unknown or conflict. Make ONE clarify call containing all currently missing material fields; never issue parallel or pre-queued clarify calls. Let the user answer the combined question in text, then reuse every answer before considering another question.
A failed tool result is not success. Correct a malformed field once from returned
facts; do not cycle through guessed names, prices or account IDs. Recover an existing
task with `pawpilot_task_status({taskRef})`. Do not replace work after a timeout.
The service publishes complete cards automatically. Do not copy `publish`, callbacks,
metadata or internal IDs into a new send_message call. Check the publication receipt;
unconfirmed delivery means recover the original card. Always finish with visible,
concise user-facing text, even when tool work completed.

## Other Paper lifecycle drafts

This same native proxy accepts exactly one of intent (new place_order/reduceOnly) or action. For an existing order use target.resource {kind:"order",ref:<owned order reference>}; the host resolves its original account and market. Do not ask the user to switch charts. Supported typed actions are amend_order, cancel_order, cancel_all, position_protection, transfer, claim and legacy explain. Read native schemas and original order/position versions; preserve all financial fields. Use action.request.expectedVersion where required. cancel_all's accountIds must be the intended owned set. Transfer/claim do not need a market or side. All financial actions still produce a draft for independent manual review, including claiming simulated funds. explain is nonexecution compatibility.

Example cancellation: `pawpilot_paper_trade_prepare({target:{mode:"paper",resource:{kind:"order",ref:orderId}},action:{kind:"cancel_order",orderId,request:{expectedVersion:version}}})`. The result is a cancellation proposal, not a cancelled order. For a margin conflict, describe the requested and existing configuration and ask for the user's choice. Only a real changed user decision starts a new intent; never omit risk fields, change call IDs or close/transfer to defeat the conflict.
