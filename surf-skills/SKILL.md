---
name: surf-skills
description: Use Surf for crypto price,wallet,token,DEX,DeFi,onchain,news
metadata:
  openclaw:
    primaryEnv: SURF_API_KEY
    tags:
      - crypto
      - market-data
      - wallet-intelligence
      - defi
      - onchain
      - prediction-markets
  version: "0.0.6"
---

# Surf

## Routing

In hosted sessions, delegate supported market research to `market_analyst` and
external evidence to `financial_researcher`; do not run Surf as a competing
research route. Supplied-news restrictions remain in force. Use Surf for an
explicit Surf request or capabilities outside those roles, such as standalone
wallet intelligence or prediction-market data.

For any Surf request:

1. Read [`vendor/SKILL.md`](vendor/SKILL.md).
2. Apply the runtime setup and overrides below.
3. Follow the vendor skill for discovery, exact flags, auth, output, pagination,
   quota handling, and gotchas.

## Runtime Setup

Always run `surf sync` at the start of every session.

## Runtime Overrides

- Skip the vendor "Setup" section.
- Ignore the vendor "First-run: inject routing rules" section. Do not edit
  `AGENTS.md` / `CLAUDE.md`, create routing files, or make git commits.
- Return sourced data and its limitations. In hosted sessions the main agent
  owns strategy discussion and proposals under the platform contract.
