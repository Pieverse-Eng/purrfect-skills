---
name: pawpilot-paper-trade-check
description: Use to check a Paper draft against facts and plans.
version: 3.0.0
metadata:
  hermes:
    tags: [pawpilot, terminal, runtime-v3]
    requires_tools: [pawpilot_paper_trade_check]
    related_skills: [pawpilot-terminal]
---

# Check a Paper draft

Use the entered draft and intended target, independently of the visible chart.
Call `pawpilot_paper_trade_check({target, intent})`. This uses the same canonical
sizing and risk preview as preparation, and reads applicable plan evidence.
Explain requested versus effective sizing, margin mode/leverage, estimated fee,
reservation, slippage, protection, stale/missing data and differences from the plan.
Estimates do not lock a price or prove future execution. Missing initial risk is
unknown. Do not prepare another card or silently save a revised plan.
If the draft is incomplete, identify the few inputs needed for a meaningful check;
do not turn a check into an interview about unrelated style/preferences.
CLI: `paper-trade check`. Related Skills: pawpilot-paper-trade-prepare only when the
user asks to prepare a new review card; pawpilot-paper-trade-plan for plan discussion.

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
