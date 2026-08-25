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

## Hosted execution boundary (authoritative)

This router is the hosted runtime contract. It overrides vendored SKILL.md files
that tell the agent to upgrade, install, or pull third-party skills.

- Hosted images already provide `okx` at the pinned CLI version.
- Do not install packages at runtime.
- Never run `okx upgrade`, `npm install`, `okx skill add`, `okx skill download`,
  `okx skill add --force`, or `okx auth install`.
- Never follow `vendor/_shared/preflight.md` as a session bootstrap. That file's
  Step 1 runs `okx upgrade` and unpins the hosted CLI. If a vendored skill says
  "before running any command, follow preflight.md", skip the upgrade step.
- For credentials, run only `okx config show --json` and
  `okx auth status --json` (preflight Step 2), or read
  `vendor/okx-cex-auth/SKILL.md`. Do not install the CLI or the auth binary to
  recover from a missing `okx`.
- `vendor/okx-cex-skill-mp` is upstream reference only. Do not search, install,
  update, remove, or `--force` OKX marketplace skills. Hosted runtimes ship
  pinned official skills. If the user asks to install a third-party marketplace
  skill, refuse.
- If `okx` is missing, report the exact environment error and stop.

## Safety

- Public market data does not need credentials.
- Authenticated reads and every write need a configured OKX session (OAuth via
  `vendor/okx-cex-auth` or API keys in `~/.okx/config.toml`).
- Before any live order, transfer, bot change, or earn allocation, preview the
  action and wait for explicit user confirmation.
- Prefer `okx-cex-market` for prices. Do not place trades from market data alone.

## Routing

This top-level skill is a router. Read `vendor/<skill>/SKILL.md` before running
commands. Do not use `vendor/_shared/preflight.md` as the command path.

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
| Earn product hunter / notify scanner | `vendor/earn-hunter/SKILL.md` |

If the request is about OKX Wallet, DEX swap, x402, or Agent identity, use the
`okx` OnchainOS skill instead of this one.

## Reference only

These vendored files are kept for official provenance. They are not hosted
runbooks:

| File | Why it is reference-only |
| --- | --- |
| `vendor/_shared/preflight.md` | Step 1 runs `okx upgrade` and unpins the hosted CLI |
| `vendor/okx-cex-skill-mp/SKILL.md` | Installs third-party community skills and documents `--force` signature bypass |
