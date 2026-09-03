---
name: okx-cex
description: Use when the user asks about OKX centralized exchange (CEX) for spot, perpetuals, futures, options, portfolio, trading bots, or earn products.
metadata:
  openclaw:
    primaryEnv: OKX_CEX_API_KEY
    requires:
      bins:
        - okx
  pieverse:
    marketSearch: true
    tradeReady:
      env:
        - [OKX_CEX_API_KEY, OKX_CEX_SECRET_KEY, OKX_CEX_PASSPHRASE]
      probe:
        argv: [okx, auth, status, --json]
        jsonEquals:
          status: logged_in
---

# OKX Exchange

Official OKX CEX skills via the `okx` CLI (`@okx_ai/okx-trade-cli`). This is the
centralized OKX exchange (spot, perpetuals, dated futures, options, event
contracts, earn, bots). It is not the OnchainOS / DEX / wallet pack in `okx/`.

## Runtime execution boundary (authoritative)

This router is the runtime integration contract. It overrides vendored files
that tell the agent to install, upgrade, or pull skills at runtime.

- The runtime provides `okx` at the pinned CLI version and ships the reviewed
  official references used by this router.
- Do not install or upgrade packages or skills at runtime.
- Never run `okx upgrade`, `npm install`, `okx skill add`,
  `okx skill download`, `okx skill add --force`, or `okx auth install`.
- `vendor/okx-cex-skill-mp/SKILL.md` is provenance-only. Do not use it to
  search, install, update, remove, or force-install marketplace skills.
- If `okx` is missing, report the exact environment error and stop.

## Authentication

Run the requested `okx` command directly. Enter authentication recovery only if
the command reports an authentication error.

- Offer either all three OKX CEX credential fields in the Claw Dashboard or
  OAuth. Credentials belong in the Dashboard, not chat.
- For OAuth, follow `vendor/okx-cex-auth/SKILL.md`, then retry the original
  command once.
- Add `--demo` only when the user explicitly requests demo trading.
- `vendor/okx-outcomes/SKILL.md` uses an independent OAuth session and signing
  key setup; follow it directly.

## Safety

- Public market data does not need credentials.
- Before any live order, transfer, bot change, or earn allocation, preview the
  action and wait for explicit user confirmation.
- Prefer `okx-cex-market` for prices. Do not place trades from market data alone.

## Market Cost

- For an exact verified Spot or linear USDT perpetual (`SWAP`), retrieve
  bounded public depth with `okx market orderbook <INST_ID> --sz 100 --json` and
  instrument metadata with
  `okx market instruments --instType <SPOT|SWAP> --instId <INST_ID> --json`.
- OKX's official regular/default taker fee is `0.1%` for standard Spot
  (`takerFeeBps: "10"`) and `0.05%` for perpetual/futures
  (`takerFeeBps: "5"`). These defaults apply only when the exact instrument is
  in the standard fee group; exclude instruments whose special fee group cannot
  be verified.
- Fee source: `https://www.okx.com/en-gb/help/trading-fee-rules-faq`. Do not
  call the authenticated `okx account fees` during public venue discovery, and
  exclude VIP or account-specific rates. Pass `additionalFeeBps: "0"`.
- Spot depth sizes are base-asset quantities. For a linear swap, use `ctVal` as
  `baseSizePerUnit` only when `ctValCcy` confirms the base asset; otherwise
  exclude the candidate.

## References

This top-level skill is a router. Read the matching official reference before
running commands.

| Official reference | Use |
| --- | --- |
| `vendor/okx-cex-auth/SKILL.md` | Login, API key, session expiry, and site selection |
| `vendor/okx-cex-market/SKILL.md` | Prices, order books, candles, funding, open interest, and indicators |
| `vendor/okx-cex-trade/SKILL.md` | Place, amend, and cancel spot, swap, futures, options, and event orders |
| `vendor/okx-cex-portfolio/SKILL.md` | Balances, positions, PnL, fees, and transfers |
| `vendor/okx-cex-bot/SKILL.md` | Grid and DCA bots |
| `vendor/okx-cex-earn/SKILL.md` | Simple Earn, Dual Investment, and AutoEarn |
| `vendor/okx-cex-smartmoney/SKILL.md` | Smart-money leaderboards and consensus signals |
| `vendor/okx-sentiment-tracker/SKILL.md` | News and sentiment |
| `vendor/okx-outcomes/SKILL.md` | Outcome and YES/NO event contracts with independent OAuth and signing-key setup |
| `vendor/earn-hunter/SKILL.md` | Earn product scanning and notifications |

## Reference only

The following official file is retained for provenance and must not be used as
a runtime runbook:

| Official reference | Why it is reference-only |
| --- | --- |
| `vendor/okx-cex-skill-mp/SKILL.md` | It installs mutable third-party marketplace skills and documents `--force` signature bypass |

If the request is about OKX Wallet, DEX swap, x402, or Agent identity, use the
`okx` OnchainOS skill instead of this one.
