---
name: okx
description: OKX agent, help, wallet, market news, trade, DeFi, risk, pay
metadata:
  openclaw:
    primaryEnv: OKX_API_KEY
---

# OKX

## Overview

onchainos skills for AI coding assistants. Provides token search, market data, wallet balance queries, swap execution, transaction broadcasting, leaderboard rankings, token cluster analysis, DeFi workflows, payment flows, security checks, and direct third-party DApp access across 20+ blockchains.

For any concrete OKX task, choose the matching vendored capability below, open its `SKILL.md`, and follow its detailed instructions for command syntax, preflight checks, confirmations, chain support, payment handling, and troubleshooting.

## CLI Preflight

If this is a hosted instance, do not run this section.

```bash
ONCHAINOS_VERSION=v3.3.13
ONCHAINOS_TARGET=$(case "$(uname -m)" in
  x86_64) echo x86_64-unknown-linux-gnu ;;
  aarch64|arm64) echo aarch64-unknown-linux-gnu ;;
  i686) echo i686-unknown-linux-gnu ;;
  armv7l) echo armv7-unknown-linux-gnueabihf ;;
  *) echo "Unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac)
ONCHAINOS_BINARY="onchainos-${ONCHAINOS_TARGET}"
curl -fsSL -o /usr/local/bin/onchainos \
  "https://github.com/okx/onchainos-skills/releases/download/${ONCHAINOS_VERSION}/${ONCHAINOS_BINARY}"
chmod +x /usr/local/bin/onchainos
test "$(onchainos --version)" = "onchainos 3.3.13"
```

## Prerequisites

Runtime OKX operations generally require OKX API credentials. Apply at the OKX Developer Portal and configure these environment variables:

```bash
OKX_API_KEY="your-api-key"
OKX_SECRET_KEY="your-secret-key"
OKX_PASSPHRASE="your-passphrase"
```

Never echo secret values. Confirm credential presence or absence only. Guidance-only capabilities may not need credentials, but any live `onchainos` command, wallet operation, market API call, payment action, swap, bridge, DeFi execution, broadcast, or security scan should follow the selected vendor file's credential and confirmation requirements.

## Supported Chains

X Layer, Solana, Ethereum, Base, BSC, Arbitrum, Polygon, and 20+ other chains depending on the selected capability.

## Available Skills

| Skill | Description | Path |
|---|---|---|
| `okx-how-to-play` | Onchain OS onboarding: what it can do, how to start, quick-start menus, and first workflow suggestions. | `vendor/okx-how-to-play/SKILL.md` |
| `okx-ai-support` | OKX.AI support guidance: contact support, talk to a human, file complaints, provide feedback, find FAQs, and report bugs. | `vendor/okx-ai-support/SKILL.md` |
| `okx-agentic-wallet` | Wallet lifecycle: auth, account management, balance, assets, portfolio PnL, send, tx history, contract call, message signing, and Solana Gas Station. | `vendor/okx-agentic-wallet/SKILL.md` |
| `okx-wallet-portfolio` | Public address balance, token holdings, portfolio value, and DeFi positions for an explicit wallet address. | `vendor/okx-wallet-portfolio/SKILL.md` |
| `okx-security` | Security scanning: token risk, DApp phishing, tx pre-execution, signature safety, approval checks, and approval revoke flows. | `vendor/okx-security/SKILL.md` |
| `okx-dex-market` | Real-time prices, K-line charts, index prices, wallet PnL analysis, address tracker activities, and Market API payment/quota notifications. | `vendor/okx-dex-market/SKILL.md` |
| `okx-dex-signal` | Smart money, whale, and KOL activity tracking, aggregated buy signals, custom wallet tracking, and leaderboard rankings. | `vendor/okx-dex-signal/SKILL.md` |
| `okx-dex-trenches` | Meme pump/trenches token scanning, new launches, dev reputation, bundle or sniper detection, bonding curve progress, and aped wallets. | `vendor/okx-dex-trenches/SKILL.md` |
| `okx-dex-swap` | Token swaps via OKX DEX aggregation across 500+ liquidity sources: quotes, approvals, execution, route comparison, calldata, and slippage controls. | `vendor/okx-dex-swap/SKILL.md` |
| `okx-dex-strategy` | Agentic Wallet limit orders: place, cancel, list, resume, take profit, stop loss, buy dips, and chase highs. | `vendor/okx-dex-strategy/SKILL.md` |
| `okx-dex-bridge` | Cross-chain bridge quotes, fee and route comparison, execution, and lifecycle status tracking. | `vendor/okx-dex-bridge/SKILL.md` |
| `okx-dex-token` | Token search, metadata, market cap, rankings, liquidity pools, hot tokens, advanced info, holder analysis, top traders, trade history, and holder cluster analysis. | `vendor/okx-dex-token/SKILL.md` |
| `okx-dex-social` | Crypto news, symbol-filtered articles, news search, article detail, source platforms, market sentiment ranking, per-coin sentiment trends, vibe timelines, and TOP50 KOL leaderboard. | `vendor/okx-dex-social/SKILL.md` |
| `okx-dex-ws` | WebSocket sessions and real-time streams: start, poll, stop, list sessions, inspect channels, and build WebSocket scripts or bots. | `vendor/okx-dex-ws/SKILL.md` |
| `okx-onchain-gateway` | Gas estimation, transaction simulation, raw or signed transaction broadcasting, order tracking, and transaction status checks. | `vendor/okx-onchain-gateway/SKILL.md` |
| `okx-agent-payments-protocol` | Unified payment dispatcher across x402, MPP, and a2a-pay: exact and aggr_deferred schemes, TEE or local-key signing, charge/session intents, vouchers, topups, closes, refunds, payment links, and `a2a_` payment IDs. | `vendor/okx-agent-payments-protocol/SKILL.md` |
| `okx-defi-invest` | DeFi product discovery and execution: APY/TVL search, prepare, deposit, withdraw, redeem, claim rewards, borrow, repay, and LP actions across supported protocols. | `vendor/okx-defi-invest/SKILL.md` |
| `okx-defi-portfolio` | DeFi positions and holdings overview across protocols and chains, including position lists and position details. | `vendor/okx-defi-portfolio/SKILL.md` |
| `okx-dapp-discovery` | Third-party DApp discovery and direct plugin access for named protocols including Polymarket, Aave, Hyperliquid, PancakeSwap, Morpho, Raydium, Curve, Compound, Pendle, Lido, ether.fi, GMX, Kamino, Orca, Meteora, Clanker, pump.fun, and Uniswap. | `vendor/okx-dapp-discovery/SKILL.md` |
| `okx-growth-competition` | Agentic Wallet exclusive trading competitions: list, join, view rules, check leaderboard, inspect participation, and claim rewards. | `vendor/okx-growth-competition/SKILL.md` |
| `okx-audit-log` | Audit log export, command history, log location, and troubleshooting guidance. | `vendor/okx-audit-log/SKILL.md` |

## Skill Workflows

The skills work together in typical DeFi and on-chain flows:

- Search and Buy: `okx-dex-token` (find token) -> `okx-wallet-portfolio` or `okx-agentic-wallet` (check funds) -> `okx-security` (risk check) -> `okx-dex-swap` (execute trade)
- Portfolio Overview: `okx-wallet-portfolio` (holdings) -> `okx-dex-token` (enrich with analytics) -> `okx-dex-market` (price charts)
- Market Research: `okx-dex-token` (trending/rankings) -> `okx-dex-market` (candles/history) -> `okx-dex-social` or `okx-dex-signal` (context)
- Swap and Broadcast: `okx-dex-swap` (get tx data) -> sign locally if required -> `okx-onchain-gateway` (broadcast) -> `okx-onchain-gateway` (track order)
- Pre-flight Check: `okx-onchain-gateway` (estimate gas) -> `okx-onchain-gateway` (simulate tx) -> `okx-onchain-gateway` (broadcast) -> `okx-onchain-gateway` (track order)
- Full Trading Flow: `okx-dex-token` (search) -> `okx-dex-market` (price/chart) -> `okx-wallet-portfolio` or `okx-agentic-wallet` (check balance) -> `okx-dex-swap` or `okx-dex-strategy` (trade)
- Leaderboard to Research to Trade: `okx-dex-signal` (top traders by PnL/win rate) -> `okx-dex-token` (token analytics) -> `okx-security` (risk check) -> `okx-dex-swap` (execute trade)
- Follow Smart Money: `okx-dex-signal` (KOL/smart money buys) -> `okx-dex-token` (token details and holder cluster) -> `okx-dex-market` (price chart) -> `okx-dex-swap` (trade)
- Cross-chain Move: `okx-wallet-portfolio` or `okx-agentic-wallet` (check source funds) -> `okx-dex-bridge` (quote and execute) -> `okx-dex-bridge` or `okx-onchain-gateway` (track status)
- DeFi Yield: `okx-defi-invest` (discover products) -> `okx-security` (risk check) -> `okx-defi-invest` (deposit/redeem/claim) -> `okx-defi-portfolio` (review positions)
- Named DApp Action: `okx-dapp-discovery` for specific DApps such as Polymarket, Aave, Hyperliquid, PancakeSwap, Morpho, Raydium, Curve, Lido, GMX, Pendle, or pump.fun.
- Payment Flow: `okx-agent-payments-protocol` for HTTP 402, x402, MPP charge/session flows, vouchers, payment links, and `a2a_` payment IDs.
