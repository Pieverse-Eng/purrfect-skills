---
name: binance
description: Use Binance exchange accounts and markets via binance-cli.
required_environment_variables:
  - name: BINANCE_API_KEY
    optional: true
    required_for: Authenticated exchange account operations
  - name: BINANCE_SECRET_KEY
    optional: true
    required_for: Authenticated exchange account operations
metadata:
  version: 1.2.0
  author: Binance
  openclaw:
    requires:
      bins:
        - binance-cli
    install:
      - kind: node
        package: '@binance/binance-cli'
        bins: [binance-cli]
        label: Install binance-cli (npm)
license: MIT
---

# Binance

Use `binance-cli` for Binance Spot, Futures (USD-S), and Convert. Private account
operations require authentication.
Public market reads need no credentials. This is the exchange account route;
when the user explicitly chooses Binance Agentic Wallet, use that separate
installed Skill and its own authentication instead.

> **PREREQUISITE:** Read [`auth.md`](./references/auth.md) for auth, global flags, and security rules.

## Helper Commands

| Command | Description |
|---------|-------------|
| [`algo`](./references/algo.md) | Algo Trading |
| [`alpha`](./references/alpha.md) | Alpha |
| [`c2c`](./references/c2c.md) | C2C |
| [`convert`](./references/convert.md) | Convert |
| [`copy-trading`](./references/copy-trading.md) | Copy Trading |
| [`crypto-loan`](./references/crypto-loan.md) | Crypto Loan |
| [`derivatives-options`](./references/derivatives-options.md) | Derivatives Trading (Options) |
| [`derivatives-portfolio-margin`](./references/derivatives-portfolio-margin.md) | Derivatives Trading (Portfolio Margin) |
| [`derivatives-portfolio-margin-streams`](./references/derivatives-portfolio-margin-streams.md) | Derivatives Trading Streams (Portfolio Margin) |
| [`derivatives-portfolio-margin-pro`](./references/derivatives-portfolio-margin-pro.md) | Derivatives Trading (Portfolio Margin Pro) |
| [`derivatives-portfolio-margin-pro-streams`](./references/derivatives-portfolio-margin-pro-streams.md) | Derivatives Trading Streams (Portfolio Margin Pro) |
| [`dual-investment`](./references/dual-investment.md) | Dual Investment |
| [`fiat`](./references/fiat.md) | Fiat |
| [`futures-coin`](./references/futures-coin.md) | Derivatives Trading (COIN-M Futures) |
| [`futures-coin-streams`](./references/futures-coin-streams.md) | Derivatives Trading Streams (COIN-M Futures) |
| [`futures-usds`](./references/futures-usds.md) | Derivatives Trading (USDS-M Futures) |
| [`futures-usds-streams`](./references/futures-usds-streams.md) | Derivatives Trading Streams (USDS-M Futures) |
| [`gift-card`](./references/gift-card.md) | Gift Card |
| [`margin-trading`](./references/margin-trading.md) | Margin Trading |
| [`margin-trading-streams`](./references/margin-trading-streams.md) | Margin Trading Streams |
| [`mining`](./references/mining.md) | Mining |
| [`pay`](./references/pay.md) | Pay |
| [`rebate`](./references/rebate.md) | Rebate |
| [`simple-earn`](./references/simple-earn.md) | Simple Earn |
| [`spot`](./references/spot.md) | Spot Trading |
| [`spot-streams`](./references/spot-streams.md) | Spot Trading Streams |
| [`staking`](./references/staking.md) | Staking |
| [`sub-account`](./references/sub-account.md) | Sub Account |
| [`vip-loan`](./references/vip-loan.md) | VIP Loan |
| [`wallet`](./references/wallet.md) | Wallet |

## Notes

- ⚠️ **Prod transactions** — always ask user to type `CONFIRM` before executing.
- Install binance-cli using `npm install -g @binance/binance-cli`
- Hosted runtimes already supply the pinned CLI. Do not install, upgrade, or
  create a credential profile to perform an ordinary account read. Run the
  documented command directly with the managed environment.
- Use `--help` to get the list of commands and parameters.
- Use the output from both stdout and stderr.
- Preserve the user's explicit existing profile selection (`--profile <name>`
  or `--profile=<name>`); it takes precedence over managed credentials. Do not
  automatically switch to a profile after a managed session failure.
- All authenticated endpoints accept optional `--recvWindow <ms>` (max 60 000).
- Timestamps (`startTime`, `endTime`) are Unix ms.
- For endpoints not listed in the skill, use `binance-cli request (GET|POST|PUT...) <url> [--signed]`. Any Parameters can be added to the request (e.g: `--param1 value --param2 value`).

## Read-only account and market questions

Read only the relevant account and public market references, then run the
documented reads. A holdings list normally starts with `binance-cli spot get-account`;
do not fan out into every wallet, margin and futures product without a reason.
Use the product the user asked about; a Spot buying question needs Spot prices,
not an unlabeled perpetual quote. Bound candles/history by time and count.
Use simple direct calls so private and public reads retain independent
credential binding; a private-session failure must not prevent a keyless public
read. Keep the exchange timeout bounded and report the exact failed stage without repeated
profile/help/auth probes.

On a credential-session or signing failure, preserve the error and stop private
reads. Public evidence can still support a partial answer. An `Invalid private
key` error alone does not establish the owner's key type or justify asking for
replacement credentials: managed placeholders and delivery failures can cause
the same local parser error. Do not print secrets, create profiles, inspect
secret values, or change authentication methods to diagnose it. Report that
account access could not be verified; only a verified credential/configuration
error warrants the matching recovery instructions in the auth reference.
