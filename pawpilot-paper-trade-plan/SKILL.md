---
name: pawpilot-paper-trade-plan
description: Use to discuss or save a complete Paper trading plan.
version: 3.0.0
metadata:
  hermes:
    tags: [pawpilot, terminal, runtime-v3]
    requires_tools: [pawpilot_paper_trade_plan_save]
    related_skills: [pawpilot-terminal]
---

# Discuss or save a Paper plan

Discuss the user's objective, thesis, time horizon, invalidation/protection, constraints
and review conditions using facts only when needed. Reuse confirmed conversation details.
Discussion alone does not request a write. Do not choose risk budgets, size, leverage
or numerical entry/exit conditions for the user. Explain missing assumptions plainly.
When the user naturally asks to save/remember the plan, resolve the destination using
venue and symbol. Ask for the destination only if it is genuinely ambiguous. The user
never needs to change charts; say "Hyperliquid ETH/USDC", not an internal identifier.
Call `pawpilot_paper_trade_plan_save({target, content})` with the complete agreed plan,
or `contentRef` for an owned full-content reference. Never silently shorten it to 512
characters or replace it with a summary. For a revision include edit {id,version} from
the existing record receipt. Read complete content when the source is a reference;
an excerpt cannot authorize replacing the original full plan.
Confirm saving only after the versioned ready receipt. A saved note does not change an
order, its initial risk, a Lesson, Playbook or any live trading permission.
CLI: `paper-trade plan-save`. Use position research profile=facts for necessary evidence.

## Invocation and delivery

Use the named native proxy when it is present. Never switch to a CLI or general execution tool after a business validation result. Correct the supplied field from the returned contract; a CLI cannot bypass that contract. The independent developer CLI uses the same
operation contract: `node /usr/local/lib/pawpilot/pawpilot.mjs <command> --input request.json`.
Use `--help` for syntax. CLI access requires a current authorized Run broker; an
unavailable proxy is not permission to invent an HTTP endpoint or query a database.
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

Content references: use contentRef="message:<native message ID>" for complete saved text in this same conversation, or "current-user-message" for the current complete user text. Never use a UI excerpt as the complete plan. The current 8000-character content limit fails explicitly; it never truncates.
