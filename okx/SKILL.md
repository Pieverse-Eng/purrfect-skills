---
name: okx
description: Use when the user wants OKX-powered token research, market data, public wallet portfolio analysis, smart-money signals, meme token scanning, security checks, swaps, wallet operations, x402 payment, audit-log troubleshooting, or gateway preflight queries. All capabilities via vendor skills using the onchainos CLI.
metadata:
  {
    "openclaw":
      {
        "primaryEnv": "OKX_API_KEY",
        "requires": { "env": ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE"] },
      },
  }
---

# OKX

`okx` is the OKX domain router. It classifies user intent and dispatches to the appropriate vendor read skill.

All vendor skills under `vendor/` use the `onchainos` CLI to interact with OKX APIs. No purr CLI is required.

## Credentials

All OKX skills require API credentials. Ask the user directly if they are not configured:

| Credential | Env var | Description |
|---|---|---|
| **API Key** | `OKX_API_KEY` | API key from the OKX Developer Portal |
| **Secret Key** | `OKX_SECRET_KEY` | Secret key paired with the API key |
| **Passphrase** | `OKX_PASSPHRASE` | Passphrase set during API key creation |

If the user hasn't set up OKX credentials yet, they need to:
1. Apply at the [OKX Developer Portal](https://web3.okx.com/onchain-os/dev-portal)
2. Create an API key and note the key, secret, and passphrase
3. Configure the three env vars above in their instance

Do not proceed with any `onchainos` commands until all three credentials are present.

## Scope

- Read:
  - token search, metadata, rankings, holders, clusters
  - prices, candles, address activity, wallet PnL
  - public wallet portfolio lookup by address
  - smart-money / whale / KOL signals
  - meme / trenches token scanning
  - token / DApp / tx / signature risk checks
  - OKX audit-log troubleshooting
  - OKX gateway chains / gas / gas-limit / simulate / orders
- Write:
  - swap quote, approve, and execute via DEX aggregation
  - wallet lifecycle, auth, balance, send, tx history, contract call
  - x402 payment authorization for payment-gated resources

## Vendor Skills

Each vendor skill's `SKILL.md` teaches the agent the exact `onchainos` commands and parameters for that domain. Follow those instructions as-is.

| Vendor Skill | What it does |
|---|---|
| `vendor/okx-dex-token` | Token search, metadata, market cap, rankings, liquidity pools, hot tokens, holder analysis, top traders, trade history, holder cluster analysis |
| `vendor/okx-dex-market` | Real-time prices, K-line charts, index prices, wallet PnL analysis, address tracker activities |
| `vendor/okx-wallet-portfolio` | Public address balance, token holdings, portfolio value |
| `vendor/okx-dex-signal` | Smart money / whale / KOL signal tracking, leaderboard rankings |
| `vendor/okx-dex-trenches` | Meme pump / trenches token scanning, dev reputation, bundle detection, aped wallets |
| `vendor/okx-security` | Token risk, DApp phishing, tx pre-execution, signature safety, approval management |
| `vendor/okx-audit-log` | Audit log export and troubleshooting guidance |
| `vendor/okx-onchain-gateway` | Gas estimation, tx simulation, broadcasting status, order tracking |
| `vendor/okx-dex-swap` | Swap quote, approve, and execute via DEX aggregation (500+ liquidity sources) |
| `vendor/okx-agentic-wallet` | Wallet lifecycle, auth, balance, portfolio PnL, send, tx history, contract call |
| `vendor/okx-x402-payment` | x402 payment authorization for payment-gated resources |

## Setup / Pre-flight Checks

Before using this skill, verify the `onchainos` CLI is available:

```bash
if command -v onchainos &>/dev/null; then
  echo "onchainos is available"
else
  echo "onchainos is NOT available"
fi
```

If it is **not available**, install it from the OKX GitHub release:

```bash
ONCHAINOS_VERSION="v2.1.0"
ONCHAINOS_TARGET=$(case "$(uname -m)" in x86_64) echo x86_64-unknown-linux-gnu ;; aarch64|arm64) echo aarch64-unknown-linux-gnu ;; i686) echo i686-unknown-linux-gnu ;; armv7l) echo armv7-unknown-linux-gnueabihf ;; *) echo "Unsupported architecture: $(uname -m)" &>&2; exit 1 ;; esac)
ONCHAINOS_BINARY="onchainos-${ONCHAINOS_TARGET}"
curl -fsSL -o /tmp/onchainos "https://github.com/okx/onchainos-skills/releases/download/${ONCHAINOS_VERSION}/${ONCHAINOS_BINARY}"
curl -fsSL -o /tmp/onchainos-checksums.txt "https://github.com/okx/onchainos-skills/releases/download/${ONCHAINOS_VERSION}/checksums.txt"
ONCHAINOS_EXPECTED_SHA=$(grep "${ONCHAINOS_BINARY}" /tmp/onchainos-checksums.txt | awk '{print $1}')
ONCHAINOS_ACTUAL_SHA=$(sha256sum /tmp/onchainos | awk '{print $1}')
test -n "${ONCHAINOS_EXPECTED_SHA}" && test "${ONCHAINOS_ACTUAL_SHA}" = "${ONCHAINOS_EXPECTED_SHA}"
install -m 0755 /tmp/onchainos /usr/local/bin/onchainos
rm -f /tmp/onchainos /tmp/onchainos-checksums.txt
onchainos --version
```

---

### Pre-flight notes

The upstream vendor SKILL.md files include `onchainos` installer / updater / integrity-check steps. Use the setup check above instead, then follow the vendor SKILL.md as-is for everything else: command syntax, parameter formats, chain naming, and wallet operations.

## Supported Chains

Upstream OKX skills support: X Layer, Solana, Ethereum, Base, BSC, Arbitrum, Polygon, and 20+ additional chains depending on the specific capability.

## Routing

| User intent | Route to |
|---|---|
| "find token", "token metadata", "top holders", "cluster analysis", "hot tokens", "token rankings" | `vendor/okx-dex-token` |
| "price", "chart", "kline", "wallet pnl", "address activity", "index price" | `vendor/okx-dex-market` |
| "check this address", "public portfolio", "wallet holdings by address", "address balance" | `vendor/okx-wallet-portfolio` |
| "smart money", "whale", "kol", "leaderboard", "top traders by PnL" | `vendor/okx-dex-signal` |
| "meme scanner", "trenches", "pump token", "dev reputation", "bundle detection" | `vendor/okx-dex-trenches` |
| "is this token safe", "scan dapp", "scan tx", "check signature risk", "approval management" | `vendor/okx-security` |
| "audit log", "okx log path", "export audit log" | `vendor/okx-audit-log` |
| "supported gateway chains", "gas price", "gas limit", "simulate tx", "track order", "broadcast status" | `vendor/okx-onchain-gateway` |
| "swap tokens", "buy tokens", "sell tokens", "trade", "get swap quote" | `vendor/okx-dex-swap` |
| "wallet balance", "wallet login", "send tokens", "tx history" | `vendor/okx-agentic-wallet` |
| "x402 payment", "pay for resource", "payment-gated" | `vendor/okx-x402-payment` |

## Routing Rules

- Route queries directly to the matching vendor skill — the vendor SKILL.md has the full command reference
- If a read result leads to an on-chain action, follow the vendor skill's execution flow

## Typical Workflows

Vendor skills compose naturally in common DeFi flows.

- **Portfolio overview**: `vendor/okx-wallet-portfolio` → `vendor/okx-dex-token` → `vendor/okx-dex-market`
- **Market research**: `vendor/okx-dex-token` → `vendor/okx-dex-market`
- **Search and buy**: `vendor/okx-dex-token` (find token) → `vendor/okx-wallet-portfolio` (check funds) → `vendor/okx-dex-swap` (execute trade)
- **Pre-flight check**: `vendor/okx-onchain-gateway` (gas / simulate / order tracking)
- **Swap and broadcast**: `vendor/okx-dex-swap` (get tx data) → sign locally → `vendor/okx-onchain-gateway` (broadcast + track)
- **Leaderboard to trade**: `vendor/okx-dex-signal` (top traders) → `vendor/okx-dex-token` (token analytics) → `vendor/okx-dex-swap` (execute)
- **Follow smart money**: `vendor/okx-dex-signal` → `vendor/okx-dex-token` → `vendor/okx-dex-market` → `vendor/okx-dex-swap`
- **Security check before trade**: `vendor/okx-security` (token / DApp / tx scan) → `vendor/okx-dex-token` (confirm details)
- **Meme research**: `vendor/okx-dex-trenches` (scanning) → `vendor/okx-dex-token` (holder clusters) → `vendor/okx-security` (risk check)
- **Full trading flow**: `vendor/okx-dex-token` (search) → `vendor/okx-dex-market` (price/chart) → `vendor/okx-wallet-portfolio` (check balance) → `vendor/okx-dex-swap` (get tx) → `vendor/okx-onchain-gateway` (simulate + broadcast + track)

## Operational Checklist

1. Verify OKX credentials are configured — if not, ask the user to set them up
2. Detect user intent
3. Match intent to the read routing table above
4. Follow the vendor skill's SKILL.md for the exact `onchainos` commands
5. Return the result directly

## File Map

| What | Path |
|---|---|
| OKX domain router (this file) | `skills/okx/SKILL.md` |
| Token research | `skills/okx/vendor/okx-dex-token/` |
| Market data | `skills/okx/vendor/okx-dex-market/` |
| Public wallet portfolio | `skills/okx/vendor/okx-wallet-portfolio/` |
| Smart money signals | `skills/okx/vendor/okx-dex-signal/` |
| Trenches / meme scan | `skills/okx/vendor/okx-dex-trenches/` |
| Security checks | `skills/okx/vendor/okx-security/` |
| Audit-log troubleshooting | `skills/okx/vendor/okx-audit-log/` |
| Gateway queries / preflight | `skills/okx/vendor/okx-onchain-gateway/` |
| DEX swap | `skills/okx/vendor/okx-dex-swap/` |
| Agentic wallet | `skills/okx/vendor/okx-agentic-wallet/` |
| x402 payment | `skills/okx/vendor/okx-x402-payment/` |
