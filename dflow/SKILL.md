---
name: dflow
description: Use when the user wants DFlow operations: Solana spot swaps, Kalshi prediction-market trading, Kalshi market discovery/data, wallet portfolio views, Proof KYC, or platform-fee monetization.
metadata:
  openclaw:
    primaryEnv: DFLOW_API_KEY
    requires:
      env:
        - DFLOW_API_KEY
---

# DFlow

Use the vendored DFlow README and skills for all DFlow work. This file exists to pick the right local skill and avoid re-installing what is already vendored.

## Mandatory Rules

> **Read this file for environment setup/provisioning first; read the matching vendor `SKILL.md` before workflow-specific commands, code, or API calls.**
> The vendor skills contain the workflow ordering, safety rules, field gotchas, auth boundaries, and exact surface choice.

> **Do not guess endpoint shapes, request fields, error codes, mint fields, or WebSocket payloads.**
> Use the matching vendor skill and official DFlow documentation for reference details.

> **Ignore the Install section in `vendor/README.md`.**
> Do not run `npx skills add DFlowProtocol/dflow-skills`; this repository already includes the vendored DFlow skills.

## Environment Path

> **Keep the environment path internal.**
> Do not tell the user whether this is the platform-hosted path or local onboarded path. Make the correct setup choice silently and only ask for the inputs needed to continue.

First identify the agent environment.

Env-based hint: if `WALLET_API_URL` contains `.svc.cluster.local`, use the platform agent path internally. Otherwise, use the local onboarded agent path internally.

- Local onboarded agent: follow the matching vendor skill. If setup is needed, `dflow setup` is interactive; ask the user to run it themselves before continuing.
- Platform agent: skip Preflight and do not run `dflow setup`. Replace any vendor setup step with the platform provisioning flow below.

## Preflight

Local onboarded agent only. Platform agents skip this section.

```bash
if ! command -v dflow >/dev/null 2>&1; then
  DFLOW_VERSION="${DFLOW_VERSION:-0.1.0}"
  DFLOW_BIN_DIR="${DFLOW_BIN_DIR:-/usr/local/bin}"
  if [ ! -w "$DFLOW_BIN_DIR" ]; then
    DFLOW_BIN_DIR="$HOME/.local/bin"
    mkdir -p "$DFLOW_BIN_DIR"
    export PATH="$DFLOW_BIN_DIR:$PATH"
  fi
  curl -fsSL -o /tmp/install-dflow.sh https://cli.dflow.net/install.sh
  sh /tmp/install-dflow.sh \
    --version "${DFLOW_VERSION}" \
    --bin-dir "$DFLOW_BIN_DIR" \
    --force \
    --no-skills
  rm -f /tmp/install-dflow.sh
fi
dflow --version

# MoonPay CLI is only used by `dflow fund`, which is a human-in-the-loop flow.
if ! command -v mp >/dev/null 2>&1; then
  npm install -g @moonpay/cli@1.38.0
fi
mp --version
```

## Platform Provisioning

Ask the user for:

| Field          | Required | Default                                         |
| -------------- | -------- | ----------------------------------------------- |
| Wallet name    | optional | `default`                                       |
| Vault password | required | —                                               |
| Solana RPC URL | optional | `https://api.mainnet-beta.solana.com`           |
| DFlow API key  | required | get one at https://pond.dflow.net/build/api-key |

Provision the wallet by generating a mnemonic with `ows`, then importing it with `dflow wallet import --mnemonic`. **Do not use `ows wallet create`** — DFlow can read those wallets but headless signing may fail.

```bash
DFLOW_WALLET_NAME="${DFLOW_WALLET_NAME:-default}"
DFLOW_VAULT_PASSWORD="${DFLOW_VAULT_PASSWORD:?set from the user's vault password answer}"
SOLANA_RPC_URL="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"
DFLOW_API_KEY="${DFLOW_API_KEY:?set from the user's DFlow API key}"

export DFLOW_PASSPHRASE="$DFLOW_VAULT_PASSWORD"
MNEMONIC="$(ows mnemonic generate --words 12)"

dflow wallet import \
  --name "$DFLOW_WALLET_NAME" \
  --mnemonic "$MNEMONIC"

mkdir -p ~/.config/dflow
jq -n \
  --arg rpc "$SOLANA_RPC_URL" \
  --arg wallet "$DFLOW_WALLET_NAME" \
  --arg key "$DFLOW_API_KEY" \
  '{rpcUrl:$rpc, walletName:$wallet, dflowApiKey:$key}' \
  > ~/.config/dflow/config.json
chmod 600 ~/.config/dflow/config.json
```

Verify the wallet is reachable on either path:

```bash
dflow whoami
dflow positions
```

Unsupported on platform agents:

- `dflow fund`
- `dflow guardrails set ...`
- `dflow guardrails remove ...`
- `dflow guardrails reset ...`
- `dflow wallet keychain-sync`

For all other DFlow workflows, read and follow the matching vendor skill.

## Vendor Skills

| Skill                         | Location                                      | Use for                                                                 |
| ----------------------------- | --------------------------------------------- | ----------------------------------------------------------------------- |
| `dflow-spot-trading`          | `vendor/dflow-spot-trading/SKILL.md`          | Solana token swaps, quotes, priority fees, sponsored/gasless spot flows |
| `dflow-kalshi-trading`        | `vendor/dflow-kalshi-trading/SKILL.md`        | Buy, sell, or redeem Kalshi YES/NO outcome tokens                       |
| `dflow-kalshi-market-scanner` | `vendor/dflow-kalshi-market-scanner/SKILL.md` | Discover/filter/rank Kalshi markets by criteria                         |
| `dflow-kalshi-market-data`    | `vendor/dflow-kalshi-market-data/SKILL.md`    | Known-market orderbooks, trades, candles, prices, live streams          |
| `dflow-kalshi-portfolio`      | `vendor/dflow-kalshi-portfolio/SKILL.md`      | Wallet holdings, positions, P&L, activity, redeemable outcomes          |
| `dflow-proof-kyc`             | `vendor/dflow-proof-kyc/SKILL.md`             | Proof verification status, deep links, KYC handling for Kalshi buys     |
| `dflow-platform-fees`         | `vendor/dflow-platform-fees/SKILL.md`         | Builder/platform fees on DFlow Trade API orders                         |

## Intent Map

| User intent                                                                                      | Read first                                    |
| ------------------------------------------------------------------------------------------------ | --------------------------------------------- |
| "swap", "trade SOL for USDC", "quote token", "sponsored swap", "gasless swap"                    | `vendor/dflow-spot-trading/SKILL.md`          |
| "buy YES", "buy NO", "bet on", "sell outcome tokens", "redeem winner"                            | `vendor/dflow-kalshi-trading/SKILL.md`        |
| "find markets", "cheap YES", "arbitrage", "big movers", "closing soon", "highest volume"         | `vendor/dflow-kalshi-market-scanner/SKILL.md` |
| "show orderbook", "stream prices", "last trades", "candlesticks", "live data" for a known market | `vendor/dflow-kalshi-market-data/SKILL.md`    |
| "my positions", "what do I own", "P&L", "activity history", "redeemable"                         | `vendor/dflow-kalshi-portfolio/SKILL.md`      |
| "KYC", "Proof", "verify wallet", `PROOF_NOT_VERIFIED`, `unverified_wallet_not_allowed`           | `vendor/dflow-proof-kyc/SKILL.md`             |
| "take a cut", "platform fee", `platformFeeBps`, `platformFeeScale`, "monetize trades"            | `vendor/dflow-platform-fees/SKILL.md`         |

If the request spans multiple areas, read each relevant vendor skill in workflow order. Examples: scan markets then trade = market scanner first, then Kalshi trading; show position then redeem = portfolio first, then Kalshi trading; add a builder fee to a swap = spot trading plus platform fees.

## Operational Checklist

1. Identify the user intent and choose the matching vendor skill above.
2. Read that vendor `SKILL.md` before doing work.
3. Use official DFlow documentation for endpoint schemas, parameters, and error codes when the vendor skill does not cover a detail.
4. Gather only the inputs required by that workflow.
5. For write operations, quote or preview first when available, surface the action clearly, then execute only when the user has authorized the trade path.
6. Return the result with transaction/order status, relevant identifiers, and any next step from the vendor workflow.
