---
name: rootdata-crypto
description: RootData crypto intelligence — search projects/investors/people, project details, funding rounds, trending projects, and personnel job changes in Web3.
metadata:
  { "openclaw": { "primaryEnv": "ROOTDATA_SKILL_KEY" } }
---

# RootData Crypto Intelligence

Use the vendored RootData skill for all crypto project research, investor lookups, funding history, trending projects, and personnel movement queries.

**Always read `vendor/SKILL.md` before executing any commands.**

## Scope

- In scope: Project search, project details (by ID or contract address), investor/institution lookup, funding rounds, trending projects, personnel job changes
- Out of scope: On-chain execution, trading, portfolio management — this is a read-only data skill

## Credentials

| Credential | Env var | Description |
|---|---|---|
| **API Key** | `ROOTDATA_SKILL_KEY` | Anonymous low-privilege key for RootData public data endpoints |

If `ROOTDATA_SKILL_KEY` is not set, auto-provision it via the `/skill/init` endpoint described in `vendor/SKILL.md`. The key has no access to personal account data.

## Vendor Skill

| Vendor Skill | Location | What it does |
|---|---|---|
| `rootdata-crypto-vendor` | `vendor/SKILL.md` | Full API reference — all 6 endpoints, request/response formats, rate limits, error handling |

## Routing

All intents route to `vendor/SKILL.md`. Read it for exact API endpoints, request formats, and response fields.

| User intent | Category |
|---|---|
| "find project", "search investor", "who is [name]" | Search |
| "tell me about [project]", "token info", "contract lookup" | Project detail |
| "funding rounds", "how much did X raise", "who invested in X" | Funding data |
| "what's hot", "trending projects", "top projects this week" | Trending |
| "who joined", "who left", "executive changes", "personnel moves" | Job changes |
| "list all projects", "all investor IDs" | Bulk ID listing |

## Operational Checklist

1. Verify `ROOTDATA_SKILL_KEY` is set — if not, read `vendor/SKILL.md` for the auto-provision flow
2. Detect user intent and match to a category above
3. Read `vendor/SKILL.md` for the matching API details
4. Execute and return the result
