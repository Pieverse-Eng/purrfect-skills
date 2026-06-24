---
name: mantle
description: Mantle L2,network,addresses,DeFi,risk,contracts
---

# Mantle

Mantle is a general skill bundle for working with Mantle L2 across network reference, address safety, portfolio reads, risk checks, DeFi planning, analytics, debugging, simulation handoffs, and smart contract lifecycle work.

The bundle is organized as specialized Mantle skills under `vendor/`. Each bundled skill owns a focused part of the Mantle workflow and carries its own guardrails, reference files, and output format. This top-level skill provides the shared catalog and selection guidance so Mantle tasks start from the right specialized workflow.

## CLI Preflight

If this is a hosted instance, do not run this section.

```bash
npm install -g @mantleio/mantle-cli@0.1.19
mantle-cli --version
```

## Directory Convention

- `mantle/SKILL.md`: general trigger conditions, skill selection guidance, and shared guardrails.
- `mantle/vendor/<skill-name>/agents/openai.yaml`: runtime-facing metadata for each bundled skill, if present.
- `mantle/vendor/<skill-name>/SKILL.md`: specialized Mantle workflows, guardrails, and output formats.
- `mantle/vendor/<skill-name>/references/`: playbooks, policies, templates, and supporting notes that the selected skill may ask you to load.
- `mantle/vendor/<skill-name>/assets/`: machine-readable local data used by the selected skill.

## Skill Catalog

| Skill | Role |
| --- | --- |
| `mantle-network-primer` | Clarifies Mantle fundamentals such as MNT gas, chain IDs, official endpoints, and inclusion vs settlement. |
| `mantle-address-registry-navigator` | Resolves verified Mantle addresses and blocks unsafe address guessing. |
| `mantle-risk-evaluator` | Returns `pass`, `warn`, or `block` verdicts for state-changing intents. |
| `mantle-portfolio-analyst` | Inspects balances, allowances, and spender exposure with read-only data. |
| `mantle-data-indexer` | Retrieves historical wallet activity and time-windowed Mantle analytics. |
| `mantle-readonly-debugger` | Triages RPC failures, quote reverts, and ambiguous read-path behavior. |
| `mantle-tx-simulator` | Prepares external simulation handoffs and WYSIWYS summaries. |
| `mantle-defi-operator` | Orchestrates venue discovery, comparison, and execution-ready DeFi planning. |
| `mantle-smart-contract-developer` | Frames Mantle-specific contract design and deployment-readiness decisions. |
| `mantle-smart-contract-deployer` | Prepares deployment, verification, and external signer handoff steps. |

## How to Pick a Skill

Start with the narrowest skill that matches the task. Read the selected bundled skill before acting, and stay within its scope:

- Use `mantle-network-primer` when Mantle-specific assumptions need to be checked before execution work.
- Use `mantle-address-registry-navigator` when the task is address lookup, token or contract resolution, whitelist validation, or anti-phishing review.
- Use `mantle-risk-evaluator` when the user asks whether a planned state-changing action is safe enough to continue.
- Use `mantle-portfolio-analyst` when the user asks about wallet holdings, balances, allowances, spender exposure, or approval risk.
- Use `mantle-data-indexer` for historical activity, time-windowed metrics, analytics, or indexer-backed questions.
- Use `mantle-readonly-debugger` for RPC errors, quote failures, balance mismatches, read-path uncertainty, or root-cause triage.
- Use `mantle-tx-simulator` when the user asks what a transaction will do before signing, or needs an external simulation handoff.
- Use `mantle-defi-operator` only when the request genuinely spans discovery, address verification, risk evidence, and execution-ready DeFi planning.
- Use `mantle-smart-contract-developer` for contract architecture, design tradeoffs, requirements, and development readiness.
- Use `mantle-smart-contract-deployer` for deployment preparation, verification, receipt capture, and external signer handoff.

Split contract work between `mantle-smart-contract-developer` and `mantle-smart-contract-deployer` rather than treating deployment as part of design.
