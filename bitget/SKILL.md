---
name: bitget
description: Bitget Exchange,UTA,spot,margin,futures,bgc
metadata:
  openclaw:
    primaryEnv: BITGET_API_KEY
    requires:
      bins:
        - bgc
---

# Bitget Exchange

Official Bitget Exchange UTA v3 via the `bgc` CLI
(`@bitget-ai/bitget-agent-cli`). Spot, margin, and futures on one Unified
Trading Account, plus funds, sub-accounts, loans, and broker operations.

This is not `bitget-wallet` (chain wallet, EVM swap, RWA, x402).

## When to use this skill

Use this skill only when the user names Bitget, Bitget Exchange, Bitget UTA, or
`bgc`. Example: "Bitget BTC price", "cancel my Bitget orders", "Bitget 持仓".

Do not claim provider-agnostic requests such as "check my open orders",
"place a market sell", "what's the funding rate", or "BTC现在多少钱". Those
belong to the named venue (Binance, Kraken, Gate, OKX, and so on) or a
clarifying question if no venue was named.

## Hosted execution boundary (authoritative)

This router is the hosted runtime contract. It overrides the vendored official
SKILL.md when that file tells the agent to install packages.

- Hosted images already provide `bgc` at the pinned CLI version.
- Do not install packages at runtime.
- Never run `npm install`, `npm install -g @bitget-ai/bitget-agent-cli`, or any
  other installer to recover from a missing `bgc`.
- If `bgc` is missing, report the exact environment error and stop.
- Read `vendor/bitget/SKILL.md` for grammar, discovery, write-safety, and
  `--dry-run` / `--confirm`. Skip any install instruction in that file.

## Safety

- Public market data does not need credentials.
- Authenticated reads and every write need `BITGET_API_KEY`,
  `BITGET_SECRET_KEY`, and `BITGET_PASSPHRASE` together. See
  `vendor/bitget/references/auth-setup.md`.
- Before any live order, cancel, transfer, leverage change, loan, or
  withdrawal, preview the action and wait for explicit user confirmation.
- High-risk CLI ops (`closeAll`, `cancelAll`, withdraw) still need `--confirm`
  after that user OK. Ordinary writes execute live unless `--dry-run` is used.
- Prefer `--dry-run` to show the would-send payload before a write.

## Routing

This top-level skill is a router. Read the matching vendor file before running
commands.

| User intent | Read |
| --- | --- |
| Bitget grammar, verbs, discovery, write-safety, demo mode | `vendor/bitget/SKILL.md` |
| API key / passphrase setup | `vendor/bitget/references/auth-setup.md` |
| Discover / schema | `vendor/bitget/references/discover-guide.md` |
| Close, TP/SL, withdraw rules | `vendor/bitget/references/trading-safety.md` |
| Static command catalog | `vendor/bitget/references/commands.md` |
| Demo / paper trading | `vendor/bitget/references/demo-trading.md` |
| Error categories | `vendor/bitget/references/error-codes.md` |

If the request is about Bitget Wallet, on-chain swap, RWA stocks, or x402, use
`bitget-wallet` instead of this skill.
