---
name: pawpilot-financial-analysis
description: Use when analysing financial evidence or holdings.
version: 1.1.0
author: David Zhou (@David-0x221Eight), with Hermes Agent
metadata:
  hermes:
    tags: [pawpilot, finance, analysis, news, risk, review]
    related_skills: [pawpilot-trading-coach, financial-research]
    requires_tools: []
---

# PawPilot Financial Analysis Skill

## When to Use

Use for financial explanations, evidence changes, holdings, costs, explicit user
scenarios and reviews. Useful qualitative analysis does not require a price
target or exact number. Coach handles conversation and cards; this Skill supplies
analysis methods. It changes neither model weights nor tool permissions.

## Prerequisites

Respect disabled Skills, required tools and current Run scope. On Hermes, use
native `skills_list` and `skill_view`, with `file_path` for references. On
OpenClaw, follow its available-Skills catalogue and current runtime's native
Skill/file-reading instructions. Resolve references relative to the Skill
directory and read the complete relevant reference.
Use supplied evidence when sufficient. Account facts require bound host reads;
external research requires the separately available `financial-research` Skill
and its access policy. Never claim that a search ran when it did not.

## How to Run

1. Identify the user's question, selected holding and decision context.
2. Choose a method below and identify the evidence it needs.
3. Retrieve only missing evidence through available authorised reads.
4. Keep observations, deterministic calculations, assumptions and interpretations
   distinct. Use host calculations for account numbers; never replace quote values.
5. Explain the result, counterevidence, missing information and what would change
   the interpretation. Preserve source references for the Coach card or reply.

## Quick Reference

| Question | Reference |
| --- | --- |
| News, events and broader conditions | [Market context](references/market-context.md) |
| Holding, exposure and plan consistency | [Position risk](references/position-risk.md) |
| Fees, funding and net outcome | [Funding and costs](references/funding-and-costs.md) |
| User-chosen prices or holding duration | [Scenario comparison](references/scenario-comparison.md) |
| A completed trade | [Trade review](references/trade-review.md) |
| Patterns across trades | [Cross-trade statistics](references/cross-trade-statistics.md) |

## Procedure

Load only the method needed now, then follow its evidence, computation and
interpretation steps. The current product system policy always takes priority;
this Skill neither grants unavailable tools nor widens trading permissions.

## Pitfalls

Do not convert relevance into verification, sentiment into a price forecast, or
one profitable outcome into an edge. Do not select a direction, entry/exit time,
position size, leverage or protective price for the user. Renaming a
recommendation a scenario does not change it. Explain trade-offs and ask what
assumption or option the user wants compared; do not stop at a disclaimer.

## Verification

Check identity, units, data time, coverage, known costs and missing evidence.
Mention a current uncertainty that could reverse the interpretation. Never save
an observation as a user rule or claim an order/card succeeded without its actual
receipt. Human review remains separate from analysis.
