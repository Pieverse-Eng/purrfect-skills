---
name: okx-cex
description: OKX CEX,spot,perp,futures,options,portfolio,bots,earn
metadata:
  openclaw:
    primaryEnv: OKX_API_KEY
---

# OKX Exchange

Official OKX CEX skills via the `okx` CLI (`@okx_ai/okx-trade-cli`). This is the
centralized OKX exchange (spot, perpetuals, dated futures, options, event
contracts, earn, bots). It is not the OnchainOS / DEX / wallet pack in `okx/`.

Hosted runtimes already provide `okx`. Do not install packages at runtime.

## Safety

- Public market data does not need credentials.
- Authenticated reads and every write need a configured OKX session (OAuth via
  `vendor/okx-cex-auth` or API keys in `~/.okx/config.toml`).
- Before any live order, transfer, bot change, or earn allocation, preview the
  action and wait for explicit user confirmation.
- Prefer `okx-cex-market` for prices. Do not place trades from market data alone.

## Routing

This top-level skill is a router. Read `vendor/<skill>/SKILL.md` before running
commands. Shared credential checks live in `vendor/_shared/preflight.md`.

| User intent | Read |
| --- | --- |
| Login, API key, session expired, site selection | `vendor/okx-cex-auth/SKILL.md` |
| Price, book, candles, funding, OI, indicators | `vendor/okx-cex-market/SKILL.md` |
| Place, amend, cancel spot / swap / futures / options / event orders | `vendor/okx-cex-trade/SKILL.md` |
| Balances, positions, PnL, fees, transfers | `vendor/okx-cex-portfolio/SKILL.md` |
| Grid or DCA bots | `vendor/okx-cex-bot/SKILL.md` |
| Simple Earn, Dual Investment, AutoEarn | `vendor/okx-cex-earn/SKILL.md` |
| Smart-money leaderboard / consensus | `vendor/okx-cex-smartmoney/SKILL.md` |
| News and sentiment | `vendor/okx-sentiment-tracker/SKILL.md` |
| Outcomes / YES-NO event contracts | `vendor/okx-outcomes/SKILL.md` |
| Install or update official skill packs | `vendor/okx-cex-skill-mp/SKILL.md` |
| Earn product hunter / notify scanner | `vendor/earn-hunter/SKILL.md` |

If the request is about OKX Wallet, DEX swap, x402, or Agent identity, use the
`okx` OnchainOS skill instead of this one.
