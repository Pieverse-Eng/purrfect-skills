---
name: pawpilot-paper-trade-review
description: Use to review an ended Paper trade with actual costs.
version: 3.0.0
metadata:
  hermes:
    tags: [pawpilot, terminal, runtime-v3]
    requires_tools: [pawpilot_paper_trade_review]
    related_skills: [pawpilot-terminal]
---

# Review a closed Paper trade

Use the selected historical cycle/fill reference, or resolve the requested trade by
venue, market and period. A chart selection is not required. If several trades match,
ask which one or show bounded choices; do not assume the most recent page is complete.
Call `pawpilot_paper_trade_review({target})`, with resource {kind:cycle|fill,ref,revision?}
when known. Read actual fills, entry/exit, fees, funding, protection and applicable plan.
Explain outcome, execution/cost contribution, plan adherence, one useful lesson and
what evidence is missing. Distinguish realized, unrealized and net amounts. Do not invent
net profit when costs are missing, or R when initial risk was not recorded. A later
stop is not proof of original risk. Do not prepare an order or auto-save a Lesson.
CLI: `paper-trade review`. Use pawpilot-paper-trade-plan only if the user asks to save
a subsequent plan; completed trades remain historical facts.

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
