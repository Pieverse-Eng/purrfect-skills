---
name: pawpilot-position-deep-research
description: Use to research a position or all Paper/Live holdings.
version: 3.0.0
metadata:
  hermes:
    tags: [pawpilot, terminal, runtime-v3]
    requires_tools: [pawpilot_position_research]
    related_skills: [pawpilot-terminal]
---

# Position and holdings research

1. Identify the task subject and scope. A position button supplies one position resource;
   use that exact position, regardless of the chart. Pilot Analysis supplies holdings:
   explicit account(s) take precedence, otherwise the named portfolio means all accounts.
   Table filters, visible rows and pagination never narrow this scope.
2. For a factual question call `pawpilot_position_research({target,profile:"facts"})`.
   Ordinary greetings and practice navigation need no facts call. For deep research call
   the same operation with profile:"deep", requestedSources:["market","news","x"] and
   an optional lookbackHours. The lookback is publication/post history ending at the
   recorded observation time, not the forecast horizon. News Agent Insight retains the
   existing News workflow and session instead of becoming a holdings task.
3. The server reads actual owned holdings, reuses public evidence across assets, and
   returns account/position coverage with observation time. Never launch an Agent per
   holding. If coverage is incomplete, list the omitted/unavailable scope rather than
   claiming complete Pilot Analysis. Do not prune a large portfolio to a top few positions.
4. Treat news and X as distinct sources. X event search and X opinion/discussion search
   have separate actual statuses. News, PANews, a search-engine snippet or a URL pointing
   to X cannot establish that Twitter search ran. Cite original links and publication
   times; distinguish retrieved discussion from verified facts. An unavailable source
   is a material gap, not an empty or neutral result. Do not retry a billable unknown task.
5. A ready deep result means retrieval has FINISHED. Its `sources.news` includes
   the retrieved news; `sources.x_events` and `sources.x_discussion` say whether X
   actually worked. Use this result immediately. Do not load pawpilot-financial-analysis,
   financial-research or another research workflow, guess reference files, repeat
   ingestion, or search again merely because a requested source is unavailable.
   If the result has material pages, read all pages; otherwise write the final report now.
   Do not finish with "I need to search" or "I will analyze". Those are progress notes,
   not the requested analysis.
6. Deliver a concise conditional long/short/neutral bias, analysis horizon, supporting
   evidence, contrary evidence, what would change the view, implications for this
   position's actual exposure, and missing sources. No guarantees, certain target-price
   predictions or pressure to trade. Be useful: explain the balance of evidence rather
   than merely telling the user to decide alone. Never turn research into an order.

CLI: `position research`. Related Skills: pawpilot-paper-trade-check for an entered draft; pawpilot-paper-trade-review for
closed trades. Reuse existing source services rather than rebuilding ingestion in Skills.

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

Large evidence returns a materialRef and page count. Use pawpilot_task_status with {materialRef,page} for every zero-based page, concatenate its JSON fragments and parse the full material. Do not claim full holdings coverage until all pages have been read.
