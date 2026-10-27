---
name: pawpilot-position-deep-research
description: Use to research a position or all Paper/Live holdings.
metadata:
  version: 3.1.1
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
5. Apply the financial methods supplied in this message: position-risk for exposure,
   market-context for catalysts, and funding-and-costs for economics. Already supplied
   method text is fully loaded; use it directly. If a method is missing, read it with
   `skill_view(name="pawpilot-financial-analysis",file_path="references/methods/<method>.md")`.
   These independent method reads can run in the same batch as the first research call.
   A ready deep result means retrieval has FINISHED. Read every returned material page
   and interpret those same facts. Do not start financial-research, repeat ingestion
   or search again because X is unavailable. Explain that gap in the completed analysis.
6. Deliver a concise conditional long/short/neutral bias, analysis horizon, supporting
   evidence, contrary evidence, what would change the view, implications for this
   position's actual exposure, and missing sources. No guarantees, certain target-price
   predictions or pressure to trade. Be useful: explain the balance of evidence rather
   than merely telling the user to decide alone. Never turn research into an order.
   Financial facts must come from returned evidence: a missing native liquidation estimate is 'unavailable', and leverage alone cannot reconstruct liquidation or actual ROE. Entry-versus-mark is a PnL observation, not proof of trend. Prefer an explicit gap to an attractive invented estimate.

## Final delivery shape

Use six compact points in the user's language: (1) conditional view and analysis horizon, (2) supporting and opposing dated evidence, (3) implications for the actual side, (4) known economics and unknown costs, (5) view-change conditions, (6) coverage gaps. Skip a preamble about files you read. Place source/observation times beside their claims. If the time horizon is unknown, distinguish the news observation window from the unconfirmed holding horizon.

For a profitable short facing bullish ETF-inflow news but no time series, useful interpretation is 'the available demand-side headline is adverse to the short; trend and independent directional corroboration are unverified.' Profit since entry does not support a bearish market forecast. Explain the imbalance without turning it into an instruction to hold/add/close or choosing a new price level. Missing collateral, liquidation and ROE remain explicit unknowns, not leverage-derived approximations.

Related Skills: pawpilot-paper-trade-check for an entered draft; pawpilot-paper-trade-review for
closed trades. Reuse existing source services rather than rebuilding ingestion in Skills.

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
Preparation and practice-invite proxies publish their own draft/invite cards;
keep those original callbacks and metadata. Research returns evidence for your
analysis. Publish an analysis panel through send_message only with the canonical
card's actual same-Run fact references, and finish the requested interpretation.
Check any publication receipt;
unconfirmed delivery means recover the original card. Always finish with visible,
concise user-facing text, even when tool work completed.

Large evidence returns a materialRef and page count. Use pawpilot_task_status with {materialRef,page} for every zero-based page, concatenate its JSON fragments and parse the full material. Do not claim full holdings coverage until all pages have been read.

## Facts, assumptions and confirmed context

The same proxy supports profile facts with a typed query for Paper scenario, timeline, prices, statistics, trades or holding_news. A user-defined scenario uses the service calculator and `references/methods/scenario-comparison.md`; do not compute guessed contract economics. Statistics use `references/methods/cross-trade-statistics.md`, preserve the denominator and continue cursors before claiming all trades.

Relevant confirmed plans, owner Playbook and enabled Lessons are included as user-note evidence by default; includeContext can select plans/playbook/lessons explicitly (an empty array requests none). They guide interpretation, not execution. Read full referenced plan text before comparing adherence. State absent original thesis/initial risk instead of inventing them.

Example: an ETH short with bullish ETF news and unavailable X is not automatically a sell recommendation. Explain the bullish evidence as adverse to the short thesis, contrary evidence, horizon, known costs and view-change conditions; cite the actual news time and the X gap. Never call the unavailable X result neutral sentiment.

For analysis, navigation or Playbook panels, read `skill_view(name="pawpilot-terminal",file_path="references/cards-and-memory.md")` before publishing. It defines every supported card, evidence identity and memory confirmation flow.
