---
name: pawpilot-terminal
description: Use for PawPilot Terminal tasks and exchange routing.
version: 3.0.0
metadata:
  hermes:
    tags: [pawpilot, terminal, runtime-v3]
    requires_tools: [pawpilot_task_status]
    related_skills: [pawpilot-paper-trade-prepare, pawpilot-paper-trade-check, pawpilot-paper-trade-plan, pawpilot-paper-trade-review, pawpilot-paper-trade-practice, pawpilot-position-deep-research, hyperliquid, lighter, orderly, binance, okx, bitget, gate, kraken, binance-agentic-wallet, news2trading, financial-research]
---

# PawPilot Terminal

Route the user's request directly to the smallest relevant operation. A greeting,
style discussion or concept question needs no financial preflight or Skill chain.
The structured button action is a task hint; the actual user message determines intent.
A Live BTC page does not prevent Paper ETH preparation, a plan save or an ETH review.

## Task routes

| User goal | Read only this related Skill | Operation |
| --- | --- | --- |
| Prepare a Paper order draft | pawpilot-paper-trade-prepare | paper-trade prepare |
| Check an existing Paper draft | pawpilot-paper-trade-check | paper-trade check |
| Discuss or save a Paper plan | pawpilot-paper-trade-plan | paper-trade plan-save, only when saving is requested |
| Review a closed Paper trade | pawpilot-paper-trade-review | paper-trade review |
| Go to Paper practice | pawpilot-paper-trade-practice | paper-trade invite |
| Read a holding or investigate external evidence | pawpilot-position-deep-research | position research |
| Recover earlier work | no extra Skill | task status |

## Live exchange routing

For a live exchange operation, read that exchange Skill and follow its original
account selection, preparation, user confirmation, submission and status procedure.
Use `hyperliquid` for Hyperliquid, `lighter` for Lighter, `orderly` for Orderly,
`binance` for Binance, `okx` for OKX, `bitget` for Bitget, `gate` for Gate, and
`kraken` for Kraken. These names exist in the pinned Skill catalog.
Prefer a user-specified applicable Skill or method, including `binance-agentic-wallet`
or an applicable nested OKX wallet Skill. Otherwise use the action's venue default.
When the venue is absent from this table, discover a matching installed Skill through
skills_list and read its actual instructions. Do not invent an uninstalled Skill.
The Agent's installed abilities are not limited to venues displayed by Terminal.
Do not impose a DEX/CEX credential category or redirect an explicitly requested
applicable method because another credential happens to be stored.
There is no PawPilot live-trade CLI or intermediate live Skill. Paper proxies never
submit a live order. Report execution only with the original venue's order receipt;
a preparation or unconfirmed submission is not a fill.

## Existing News behavior

Keep automatic subscribed news analysis and the existing News conversation unchanged.
News Agent Insight uses news.research with its original material and session. Reuse
news2trading and financial-research when their existing workflow calls for them;
do not rerun subscription ingestion or rebuild that workflow through position research.
Trenches context is descriptive extension data; no new token trading/research workflow
is implied by its presence.

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
