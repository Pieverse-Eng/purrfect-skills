# Workspace Skill Organization

This directory is the platform-managed skill catalog copied into each tenant workspace.

## Naming Rules

- Use domain/protocol folders, not single-intent folders, when one protocol exposes multiple operations.
- Keep `name` in frontmatter equal to folder name.
- Keep routing/orchestrator skills separate from implementation skills.

## Current Layout

- `onchain`: top-level router (chain + intent classification only)
- `opensea`: OpenSea marketplace implementation (official OpenSea workflow + `purr opensea` execution path)
- `pancake`: Pancake implementation (swap + LP + farm)
- `dflow-swap`: Solana swap implementation
- `lista-vaults`: Lista vault implementation
- `okx`: OKX domain router — all vendor skills via `onchainos` CLI (token research, market data, portfolio, smart-money, trenches, security, swap, wallet, audit-log, gateway, x402 payment)
- `gate`: Gate.io domain router — 38 vendor skills via Gate MCP tools covering CEX (spot, futures, TradFi, Alpha, flash swap, earn, staking, dual investment, loans, transfers), DEX (wallet, swaps, market data), Info (coin analysis, trends, risk checks, market overview, address tracking), and News (briefings, event attribution, listings)
- `rootdata-crypto`: RootData crypto intelligence — project search, investor lookup, funding rounds, trending projects, personnel job changes (read-only, auto-provisions API key)
- `kraken`: Kraken CEX — spot/xStocks/forex trading, earn/staking, funding
- `morph`: Morph L2 domain router — wallet, explorer, DEX swap, cross-chain bridge, alt-fee gas, EIP-7702 delegation, EIP-8004 agent identity & reputation, x402 USDC payment via Python scripts (`morph_api.py`)
- `pieverse-a2a`: Pieverse HTTP 402 A2A payment flow — probe, confirm, authorize through hosted wallet, retry with `X-Pieverse-Payment`
- `ddg-search`: DuckDuckGo web search — zero config, no API key (fallback for `web_search`)
- `access-pass`: optional execution utility (inactive)

### Staging (`../skills-staging/`)

Candidate skills not yet shipped in the container image. Move them into `workspace-templates/skills/` to promote them to built-in.

- `htx`: HTX CEX — spot trading and USDT-M futures via signed REST API

## When Adding New Features

- If the feature belongs to an existing protocol domain, extend that domain skill (example: new Pancake actions go in `pancake`).
- If the feature is a new protocol domain, create a new skill folder and wire routing in `onchain`.
- Keep tool contracts and execution checklist in the implementation skill, not in `onchain`.
