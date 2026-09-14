---
name: chain-market-brief
description: External financial evidence: filings, announcements, economic exposures, news and project narratives.
---

# External financial research

In a hosted main-agent session, delegate external evidence questions through
`financial_researcher`; do not run a second MCP, CLI or browser research flow.
Inside that role, read [Research method](references/research.md) (approved ID
`research/methods`) when useful. Only the role's granted tools and reference IDs
are available. Supplied-news trading forbids supplementary external searches.

Investigate the assigned question and return sourced findings, counterevidence
and uncertainty. Respect specified assets; broad theses may justify comparing
economic exposures without assuming indirect exposure is better. Market identity,
availability, candles, indicators and venue costs belong to `market_analyst`.
Return measurement needs to the main agent; do not invoke another role.

General concepts live in the shared `trading-knowledge` references. No fixed
research sequence, score, position size or order-opening procedure is required.
The main agent owns synthesis, proposals, confirmation and execution.

[Standalone chain CLI lookup](references/standalone-chain-lookup.md) remains
available outside the hosted role surface for explicitly requested chain reads.
