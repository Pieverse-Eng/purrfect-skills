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

This router is the runtime integration contract.

- The runtime provides `okx` at the pinned CLI version.
- Follow the authentication selection rules below before authenticated commands,
  except for OKX Outcomes, which has an independent authentication flow.
- If `okx` is missing, report the exact environment error and stop.

## Authentication selection (authoritative)

API-key authentication (hosted environment variables or a local CLI profile)
and OAuth are supported. Before an authenticated command, first use this Bash
check without printing, echoing, logging, or otherwise exposing credential
values:

This selection does not apply to `vendor/okx-outcomes/SKILL.md`. Outcomes uses
its own OAuth session and signing-key setup; follow that reference directly.

```bash
if [[ -n "${OKX_API_KEY:-}" && -n "${OKX_SECRET_KEY:-}" && -n "${OKX_PASSPHRASE:-}" ]]; then
  printf '%s\n' env-api-key
elif [[ -n "${OKX_API_KEY:-}" || -n "${OKX_SECRET_KEY:-}" || -n "${OKX_PASSPHRASE:-}" ]]; then
  printf '%s\n' partial-api-key
else
  printf '%s\n' no-env-api-key
fi
```

- `env-api-key`: treat the environment as authenticated and use the credentials
  directly, even if `okx config show --json` would report no profiles. Do not
  run `okx config show`, `okx config init`, `okx auth status`, or
  `okx auth login`, and do not pass `--profile`. Use `OKX_SITE` when provided.
- `partial-api-key`: stop before running any `okx` command. Tell the user to
  either complete all three OKX credentials in the Claw Dashboard or clear the
  partial API-key configuration to use a local profile or OAuth. Never print or
  identify which credential values are present.
- `no-env-api-key`: run `okx config show --json` without exposing its output. If
  it contains a profile with complete API credentials, use that local API-key
  profile and pass its name with `--profile`. If the selected local profile has
  only some API credential fields, stop and tell the user to complete or remove
  that profile. If no local API credentials exist, run `okx auth status --json`
  and follow the OAuth flow in `vendor/okx-cex-auth/SKILL.md` if login is needed.
- If no local profile exists and OAuth is not authenticated, tell the user they
  can either complete all three OKX API credentials in the Claw Dashboard or
  authenticate with OAuth. Never ask the user to paste credentials into chat.
- For environment API keys and OAuth, add `--demo` only when the user explicitly
  requests demo trading. For a local API-key profile, select a demo profile only
  when the user explicitly requests demo trading.

Except for `okx-outcomes`, these rules override conflicting authentication
instructions in vendored files.
Any `--profile` shown in a vendored command example applies only when the
top-level selection chose a local API-key profile; otherwise omit it.

## Safety

- Public market data does not need credentials.
- Authenticated reads and every write need either the complete API-key
  environment above or an OAuth session via `vendor/okx-cex-auth`. Outcomes is
  the exception and uses the independent credentials described in
  `vendor/okx-outcomes/SKILL.md`.
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
| `vendor/okx-outcomes/SKILL.md` | Outcome and YES/NO event contracts with independent OAuth and signing-key setup |
| `vendor/earn-hunter/SKILL.md` | Earn product scanning and notifications |

If the request is about OKX Wallet, DEX swap, x402, or Agent identity, use the
`okx` OnchainOS skill instead of this one.
