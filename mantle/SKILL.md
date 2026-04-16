---
name: mantle
description: Mantle skill bundle — routes to the correct sub-skill for network reference, address lookup, risk evaluation, portfolio analysis, DeFi planning, indexing, debugging, simulation, and smart contract lifecycle on Mantle.
---

## Setup / Pre-flight Checks

Before using this skill, verify the `mantle` MCP server is registered in your agent:

```bash
if command -v mantle-mcp &>/dev/null; then
  echo "mantle-mcp is available globally"
elif [ -f .mcp.json ] && grep -q '"mantle"' .mcp.json; then
  echo "mantle-mcp is configured in .mcp.json"
elif [ -f openclaw.json ] && grep -q '"mantle"' openclaw.json; then
  echo "mantle-mcp is pre-configured by the platform"
else
  echo "mantle-mcp is NOT configured — follow the Setup steps below"
fi
```

If it is **not configured**, install and register it:

1. **Install the `mantle-mcp` binary**:
   `mantle-mcp` is not yet published to npm. Build from source or download a pre-built binary from the [mantle-agent-scaffold](https://github.com/mantle-xyz/mantle-agent-scaffold) repository, then place it on your `PATH`.
2. **Register the MCP server** in your agent's MCP settings:
   - **Claude Code**: Add the following to your project root `.mcp.json` (or user settings):
     ```json
     {
       "mcpServers": {
         "mantle": {
           "command": "mantle-mcp",
           "args": [],
           "env": {
             "MANTLE_MCP_TRANSPORT": "stdio",
             "MANTLE_RPC_URL": "https://rpc.mantle.xyz",
             "MANTLE_SEPOLIA_RPC_URL": "https://rpc.sepolia.mantle.xyz"
           }
         }
       }
     }
     ```
   - **Other agents** (Cursor, Windsurf, etc.): Copy the same `mantle` entry into your agent's MCP configuration panel.
3. **No API keys required**: Uses public Mantle RPC. For high-rate production use, set `MANTLE_RPC_URL` to a dedicated provider.
4. **Reload**: Restart or reload your agent so the MCP tools are discovered.

**Note:** All Mantle skills in this bundle are read-only (mantle-mcp v0.2). No skill signs, broadcasts, or executes transactions.

# Mantle (Network, DeFi, Contracts, Analytics)

Router skill for all Mantle L2 operations. Dispatch to the narrowest matching sub-skill.

**All skills are read-only (mantle-mcp v0.2). No skill signs, broadcasts, or executes transactions — state-changing operations produce handoff packages for an external signer.**

## Sub-Skills

| Sub-skill | Location | Use for |
|-----------|----------|---------|
| `mantle-network-primer` | `vendor/mantle-network-primer/SKILL.md` | Mantle fundamentals: MNT gas, chain IDs, RPCs, inclusion vs settlement, developer onboarding |
| `mantle-address-registry-navigator` | `vendor/mantle-address-registry-navigator/SKILL.md` | Verified address lookup, token/contract resolution, anti-phishing, whitelist validation |
| `mantle-risk-evaluator` | `vendor/mantle-risk-evaluator/SKILL.md` | Pre-execution risk checks: slippage, liquidity, allowance scope, gas/deadline — returns pass/warn/block |
| `mantle-portfolio-analyst` | `vendor/mantle-portfolio-analyst/SKILL.md` | Read-only wallet analysis: MNT balance, token holdings, allowance exposure, approval risk |
| `mantle-data-indexer` | `vendor/mantle-data-indexer/SKILL.md` | Historical queries via GraphQL/SQL indexers (requires user-provided endpoint URL) |
| `mantle-readonly-debugger` | `vendor/mantle-readonly-debugger/SKILL.md` | Triage read-path failures: RPC errors, quote reverts, balance inconsistencies, root-cause analysis |
| `mantle-tx-simulator` | `vendor/mantle-tx-simulator/SKILL.md` | Pre-signing simulation: state-diff review, revert analysis, WYSIWYS summaries |
| `mantle-defi-operator` | `vendor/mantle-defi-operator/SKILL.md` | DeFi orchestrator: discovery, venue comparison, execution-ready planning with verified contracts |
| `mantle-smart-contract-developer` | `vendor/mantle-smart-contract-developer/SKILL.md` | Contract architecture, requirements, dependency selection, dev briefs — routes code authoring to OpenZeppelin MCP |
| `mantle-smart-contract-deployer` | `vendor/mantle-smart-contract-deployer/SKILL.md` | Deployment readiness, signer handoff, receipt capture, explorer verification |

**Always read the relevant sub-skill SKILL.md before executing any commands.**

## Intent Routing

| User intent | Route to |
|-------------|----------|
| What is Mantle / how does MNT gas work / chain setup | `mantle-network-primer` |
| Look up a contract or token address / is this address safe | `mantle-address-registry-navigator` |
| Check risk before a swap / slippage / liquidity check | `mantle-risk-evaluator` |
| What's in my wallet / token balances / approval exposure | `mantle-portfolio-analyst` |
| Historical activity / past transactions / time-windowed metrics | `mantle-data-indexer` |
| RPC failing / quote reverts / balance mismatch / debug | `mantle-readonly-debugger` |
| Simulate this transaction / what will happen if I sign | `mantle-tx-simulator` |
| Swap tokens on Mantle / add liquidity / DeFi planning | `mantle-defi-operator` |
| Compound intent: check wallet then swap / discover + compare + execute | `mantle-defi-operator` (orchestrates sub-skills internally) |
| Design a smart contract / architecture / requirements | `mantle-smart-contract-developer` |
| Deploy a contract / verify on explorer | `mantle-smart-contract-deployer` |

## Interdelegation

Skills delegate to each other rather than duplicating work:

```
mantle-defi-operator (orchestrator)
  ├── address resolution  → mantle-address-registry-navigator
  ├── pre-flight risk     → mantle-risk-evaluator
  └── allowance/balance   → mantle-portfolio-analyst

mantle-smart-contract-developer
  ├── code authoring      → OpenZeppelin MCP (external)
  └── deployment          → mantle-smart-contract-deployer

mantle-tx-simulator
  └── simulation backend  → Anvil fork or Tenderly (external)
```

## General Principles

- Mantle chain IDs: **mainnet = 5000**, **testnet = 5003**
- Start with the **narrowest** skill that matches the task
- Use `mantle-defi-operator` only when the request genuinely spans discovery + verification + execution planning
- All skills fail closed — block rather than guess when data is missing or unverified
- Never fabricate contract addresses, RPC endpoints, or indexer URLs
- `mantle-data-indexer` requires a user-provided endpoint URL — if none is available, the skill will output a blocked report
- Every skill produces mandatory structured output — prose-only answers are not allowed

## Ambiguity Resolution

- If the user asks about Mantle concepts without a specific on-chain task, route to `mantle-network-primer`
- If the user needs just an address, route to `mantle-address-registry-navigator` — not `mantle-defi-operator`
- If the user needs just a risk check, route to `mantle-risk-evaluator` — not `mantle-defi-operator`
- If the user wants to debug a failed read/quote, route to `mantle-readonly-debugger` — not `mantle-tx-simulator`
- For contract work, split between `mantle-smart-contract-developer` (design) and `mantle-smart-contract-deployer` (deploy) — do not combine
- When in doubt, prefer the specialized skill over the orchestrator
