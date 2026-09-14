---
name: agentkey
description: AgentKey access and standalone compatibility; hosted evidence is delegated to financial_researcher.
metadata:
  version: 1.13.0
  author: Chainbase Labs
license: MIT
---

# AgentKey access

Hosted research uses `financial_researcher`, which owns the scoped AgentKey tool
workflow. Delegate the evidence question there. Do not install or reconnect an
AgentKey MCP server, request an upstream key, or run a duplicate CLI research
workflow in the main agent. Research uses platform AI Credits and reports any
unavailable capability or budget gap.

Intentional standalone CLI callers retain `purr agentkey discover`, `describe`,
`execute` and `request`; inspect their current help and the returned schemas.
An uncertain execute must be reconciled through its receipt, not automatically
executed again. [Legacy MCP setup and usage](references/standalone-mcp.md) is
reference material only for explicitly requested non-hosted MCP use. Its hosted
setup instructions are historical and must not be applied to hosted agents.
