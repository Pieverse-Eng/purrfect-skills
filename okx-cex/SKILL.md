---
name: okx-cex
description: Use when the user asks about OKX centralized exchange (CEX) for spot, perpetuals, futures, options, portfolio, trading bots, or earn products.
metadata:
  openclaw:
    primaryEnv: OKX_API_KEY
    requires:
      bins:
        - okx
---

# OKX Exchange

Official OKX CEX skills via the `okx` CLI (`@okx_ai/okx-trade-cli`). This is the
centralized OKX exchange (spot, perpetuals, dated futures, options, event
contracts, earn, bots). It is not the OnchainOS / DEX / wallet pack in `okx/`.

## Runtime execution boundary (authoritative)

This router is the runtime integration contract. It overrides vendored SKILL.md files
that tell the agent to upgrade, install, or pull third-party skills.

- The runtime provides `okx` at the pinned CLI version.
- Do not install packages at runtime.
- Never run `okx upgrade`, `npm install`, `okx skill add`, `okx skill download`,
  `okx skill add --force`, or `okx auth install`.
- Never follow `vendor/_shared/preflight.md` as a session bootstrap. That file's
  Step 1 runs `okx upgrade` and unpins the runtime CLI. If a vendored skill says
  "before running any command, follow preflight.md", skip the upgrade step.
- Follow the authentication selection rules below before any vendored credential
  preflight. Do not install the CLI or the auth binary to recover from a
  missing `okx`.
- `vendor/okx-cex-skill-mp` is upstream reference only. Do not search, install,
  update, remove, or `--force` OKX marketplace skills. This integration ships
  pinned official skills. If the user asks to install a third-party marketplace
  skill, refuse.
- If `okx` is missing, report the exact environment error and stop.

## Authentication selection (authoritative)

Both API-key and OAuth authentication are supported. Before running any vendored
credential preflight, use this Bash check to select the mode without printing,
echoing, logging, or otherwise exposing credential values:

```bash
if [[ -n "${OKX_API_KEY:-}" && -n "${OKX_SECRET_KEY:-}" && -n "${OKX_PASSPHRASE:-}" ]]; then
  printf '%s\n' api-key
else
  printf '%s\n' oauth
fi
```

- `api-key`: treat the environment as authenticated and use the credentials
  directly, even if `okx config show --json` would report no profiles. Do not
  run `okx config show`, `okx config init`, `okx auth status`, or
  `okx auth login`, and do not pass `--profile`. Use `OKX_SITE` when provided.
- `oauth`: incomplete or absent API-key variables do not constitute an error.
  Run `okx config show --json`, then `okx auth status --json`, and follow the
  OAuth flow in `vendor/okx-cex-auth/SKILL.md` if login is needed.
- If neither mode is authenticated, tell the user they can either complete all
  three OKX API credentials in the Claw Dashboard or authenticate with OAuth.
  Never ask the user to paste credentials into chat.
- Add `--demo` only when the user explicitly requests demo trading.

These rules override conflicting authentication and preflight instructions in
vendored files.

## Safety

- Public market data does not need credentials.
- Authenticated reads and every write need either the complete API-key
  environment above or an OAuth session via `vendor/okx-cex-auth`.
- Before any live order, transfer, bot change, or earn allocation, preview the
  action and wait for explicit user confirmation.
- Prefer `okx-cex-market` for prices. Do not place trades from market data alone.

## References

This top-level skill is a router. Read the matching official reference before
running commands.

| Official reference | Use |
| --- | --- |
| `vendor/okx-cex-auth/SKILL.md` | Login, API key, session expiry, and site selection |
| `vendor/okx-cex-skill-mp/SKILL.md` | Search, browse, install, update, remove, and verify skills from the OKX Skills Marketplace |
| `vendor/okx-cex-market/SKILL.md` | Prices, order books, candles, funding, open interest, and indicators |
| `vendor/okx-cex-trade/SKILL.md` | Place, amend, and cancel spot, swap, futures, options, and event orders |
| `vendor/okx-cex-portfolio/SKILL.md` | Balances, positions, PnL, fees, and transfers |
| `vendor/okx-cex-bot/SKILL.md` | Grid and DCA bots |
| `vendor/okx-cex-earn/SKILL.md` | Simple Earn, Dual Investment, and AutoEarn |
| `vendor/okx-cex-smartmoney/SKILL.md` | Smart-money leaderboards and consensus signals |
| `vendor/okx-sentiment-tracker/SKILL.md` | News and sentiment |
| `vendor/okx-outcomes/SKILL.md` | Outcome and YES/NO event contracts |
| `vendor/earn-hunter/SKILL.md` | Earn product scanning and notifications |
| `vendor/_shared/preflight.md` | Shared CLI and authentication preflight referenced by official skills; the runtime wrapper overrides its upgrade and authentication-selection steps |

If the request is about OKX Wallet, DEX swap, x402, or Agent identity, use the
`okx` OnchainOS skill instead of this one.
