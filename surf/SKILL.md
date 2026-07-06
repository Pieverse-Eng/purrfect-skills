---
name: surf
description: Crypto price,wallet,token,DeFi,social,onchain,news via Surf
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

Use Surf for crypto data requests, including market, wallet, token, DeFi,
social, prediction-market, news, search, and on-chain data.

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
- For investment advice requests, provide factual Surf data only. Do not give
  buy or sell recommendations.
