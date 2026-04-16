---
name: gate
description: Use when the user wants Gate.io CEX trading (spot, futures, TradFi, Alpha, flash swap, earn, staking, dual investment, loans, transfers), DEX on-chain operations (wallet, swaps, market data), market intelligence (coin analysis, trend analysis, risk checks, market overview, address tracking), or news (briefings, event attribution, listings). All capabilities via vendor skills using Gate MCP tools.
---

## Setup / Pre-flight Checks

Before using this skill, verify the required Gate components are available:

```bash
if command -v gate-mcp &>/dev/null && command -v gate-wallet-cli &>/dev/null; then
  echo "Gate CLI tools are available globally"
elif [ -f .mcp.json ] && grep -q '"gate"' .mcp.json; then
  echo "Gate MCP is configured in .mcp.json"
elif [ -f openclaw.json ] && grep -q '"gate"' openclaw.json; then
  echo "Gate MCP is pre-configured by the platform"
else
  echo "Gate is NOT configured — follow the Setup steps below"
fi
```

If any component is **not configured**, install and register it:

1. **Install the packages globally**:
   ```bash
   npm install -g gate-mcp gate-wallet-cli
   ```
2. **Register the MCP servers** in your agent's MCP settings:
   - **Claude Code**: Add the following to your project root `.mcp.json` (or user settings):
     ```json
     {
       "mcpServers": {
         "gate": {
           "command": "gate-mcp",
           "env": {
             "GATE_API_KEY": "${GATE_API_KEY}",
             "GATE_API_SECRET": "${GATE_API_SECRET}"
           }
         },
         "gate-dex": {
           "type": "http",
           "url": "https://api.gatemcp.ai/mcp/dex"
         },
         "gate-info": {
           "type": "http",
           "url": "https://api.gatemcp.ai/mcp/info"
         },
         "gate-news": {
           "type": "http",
           "url": "https://api.gatemcp.ai/mcp/news"
         }
       }
     }
     ```
   - **Other agents** (Cursor, Windsurf, etc.): Copy the same entries into your agent's MCP configuration panel.
3. **Reload**: Restart or reload your agent so the MCP tools are discovered.

# Gate

`gate` is the Gate.io domain router. It classifies user intent and dispatches to the appropriate vendor skill.

All vendor skills under `vendor/` use Gate MCP tools. No purr CLI is required.

## Scope

- **CEX** (exchange): spot trading, futures, TradFi, Alpha tokens, flash swap, cross-exchange, assets, transfers, unified account, sub-accounts, earn products, staking, dual investment, LaunchPool, collateral loans, coupons, VIP fees, KYC, affiliate, welfare, activities
- **DEX** (on-chain): wallet auth/balances/transfers/x402/DApp, market data/K-lines/rankings/security, swap execution
- **Info** (market intelligence): research copilot, coin analysis, coin comparison, trend analysis, risk checks, market overview, address tracking, live rooms
- **News**: briefings, event attribution, listing/delisting announcements
- **Growth**: referral program

## Vendor Skills

Each vendor skill's `SKILL.md` teaches the agent the exact MCP tools and parameters for that domain. Follow those instructions as-is.

### DEX (On-Chain)

| Vendor Skill             | What it does                                                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `vendor/gate-dex-wallet` | Wallet account management: auth, balances, addresses, transfers, x402 payment, tx history, DApp interactions, CLI       |
| `vendor/gate-dex-market` | Read-only market data: token prices, K-lines, rankings, new tokens, holder analysis, security audits, volume, liquidity |
| `vendor/gate-dex-trade`  | Swap execution: buy, sell, exchange, convert tokens, cross-chain bridge — all on-chain transactions                     |

### CEX — Trading

| Vendor Skill                           | What it does                                                                                 |
| -------------------------------------- | -------------------------------------------------------------------------------------------- |
| `vendor/gate-exchange-spot`            | Spot trading: market/limit orders, trigger orders, TP/SL, batch operations, account queries  |
| `vendor/gate-exchange-futures`         | USDT perpetual futures: open/close positions, TP/SL, conditional orders, leverage management |
| `vendor/gate-exchange-tradfi`          | TradFi (traditional finance): stocks, forex, commodities — orders, positions, market data    |
| `vendor/gate-exchange-alpha`           | Gate Alpha tokens: discovery, market viewing, buy/sell, holdings, order management           |
| `vendor/gate-exchange-flashswap`       | Flash swap: instant coin-to-coin conversion, quotes, one-to-many/many-to-one swaps           |
| `vendor/gate-exchange-crossex`         | CrossEx: cross-exchange trading across Gate, Binance, OKX, Bybit                             |
| `vendor/gate-exchange-trading-copilot` | Trading copilot: end-to-end analysis → risk control → execution for spot/futures             |
| `vendor/gate-exchange-marketanalysis`  | Market analysis: liquidity, momentum, liquidation, funding arbitrage, slippage simulation    |

### CEX — Account & Assets

| Vendor Skill                      | What it does                                                                             |
| --------------------------------- | ---------------------------------------------------------------------------------------- |
| `vendor/gate-exchange-assets`     | Asset queries: total assets, account balances across spot/futures/margin/options/finance |
| `vendor/gate-exchange-transfer`   | Internal transfers: move funds between spot, futures, margin accounts                    |
| `vendor/gate-exchange-unified`    | Unified account: equity, borrow/repay, leverage config, collateral management            |
| `vendor/gate-exchange-subaccount` | Sub-account management: create, list, lock/unlock sub-accounts                           |

### CEX — Earn Products

| Vendor Skill                          | What it does                                                                       |
| ------------------------------------- | ---------------------------------------------------------------------------------- |
| `vendor/gate-exchange-simpleearn`     | Simple Earn: flexible (Uni) and fixed-term products, subscribe/redeem, APY queries |
| `vendor/gate-exchange-staking`        | On-chain staking (earn): stake/redeem/mint, positions, rewards, product queries    |
| `vendor/gate-exchange-dual`           | Dual investment: product queries, settlement simulation, order placement           |
| `vendor/gate-exchange-launchpool`     | LaunchPool: staking events, airdrop rewards, pledge/redeem                         |
| `vendor/gate-exchange-collateralloan` | Multi-collateral loans: query/manage loans, repay, add/redeem collateral           |

### CEX — Account Services

| Vendor Skill                          | What it does                                                                 |
| ------------------------------------- | ---------------------------------------------------------------------------- |
| `vendor/gate-exchange-coupon`         | Coupon management: list, details, usage rules, source tracking               |
| `vendor/gate-exchange-vipfee`         | VIP tier and fee rates: spot/futures fee queries                             |
| `vendor/gate-exchange-kyc`            | KYC guidance: identity verification portal                                   |
| `vendor/gate-exchange-affiliate`      | Affiliate program: commission, trading volume, team performance, application |
| `vendor/gate-exchange-welfare`        | Welfare center: new user tasks, rewards, claim guidance                      |
| `vendor/gate-exchange-activitycenter` | Activity center: platform campaigns, trading competitions, airdrops          |

### Info (Market Intelligence)

| Vendor Skill                        | What it does                                                                         |
| ----------------------------------- | ------------------------------------------------------------------------------------ |
| `vendor/gate-info-research`         | Research copilot: multi-dimension analysis (fundamentals + technicals + news + risk) |
| `vendor/gate-info-coinanalysis`     | Single-coin comprehensive analysis                                                   |
| `vendor/gate-info-coincompare`      | Multi-coin comparison                                                                |
| `vendor/gate-info-trendanalysis`    | Technical indicators and trend analysis                                              |
| `vendor/gate-info-riskcheck`        | Token and address risk assessment                                                    |
| `vendor/gate-info-marketoverview`   | Overall market conditions and sentiment                                              |
| `vendor/gate-info-addresstracker`   | On-chain address tracking and fund flow analysis                                     |
| `vendor/gate-info-liveroomlocation` | Live streams and replay discovery                                                    |

### News

| Vendor Skill                    | What it does                                   |
| ------------------------------- | ---------------------------------------------- |
| `vendor/gate-news-briefing`     | Recent news and headline summaries             |
| `vendor/gate-news-eventexplain` | Event attribution: why did a price move happen |
| `vendor/gate-news-listing`      | Exchange listing/delisting announcements       |

### Growth

| Vendor Skill                  | What it does                                                 |
| ----------------------------- | ------------------------------------------------------------ |
| `vendor/gate-growth-referral` | Referral program: invite rewards, commission, referral links |

## Routing

| User intent                                                                       | Route to                                                       |
| --------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| "buy BTC", "sell ETH", "spot order", "limit buy", "cancel order", "trigger order" | `vendor/gate-exchange-spot`                                    |
| "open long", "close short", "futures", "perpetual", "leverage", "TP/SL"           | `vendor/gate-exchange-futures`                                 |
| "TradFi", "stocks", "forex", "commodities"                                        | `vendor/gate-exchange-tradfi`                                  |
| "Alpha tokens", "alpha market", "buy alpha"                                       | `vendor/gate-exchange-alpha`                                   |
| "flash swap", "convert BTC to USDT", "quick exchange"                             | `vendor/gate-exchange-flashswap`                               |
| "cross exchange", "trade on Binance via Gate"                                     | `vendor/gate-exchange-crossex`                                 |
| "analyze before buying", "check risk before trading"                              | `vendor/gate-exchange-trading-copilot`                         |
| "liquidity", "momentum", "funding rate", "slippage simulation"                    | `vendor/gate-exchange-marketanalysis`                          |
| "my balance", "total assets", "account value", "how much BTC"                     | `vendor/gate-exchange-assets`                                  |
| "transfer spot to futures", "move funds", "internal transfer"                     | `vendor/gate-exchange-transfer`                                |
| "unified account", "borrow", "repay", "collateral"                                | `vendor/gate-exchange-unified`                                 |
| "sub-account", "create sub-account", "lock sub-account"                           | `vendor/gate-exchange-subaccount`                              |
| "simple earn", "flexible savings", "fixed term", "subscribe", "APY"               | `vendor/gate-exchange-simpleearn`                              |
| "staking", "stake USDT", "redeem", "earn rewards"                                 | `vendor/gate-exchange-staking`                                 |
| "dual investment", "dual currency", "sell high buy low"                           | `vendor/gate-exchange-dual`                                    |
| "launchpool", "staking event", "airdrop"                                          | `vendor/gate-exchange-launchpool`                              |
| "collateral loan", "borrow against collateral", "repay loan"                      | `vendor/gate-exchange-collateralloan`                          |
| "my coupons", "voucher", "bonus card"                                             | `vendor/gate-exchange-coupon`                                  |
| "VIP level", "trading fee", "fee rate"                                            | `vendor/gate-exchange-vipfee`                                  |
| "KYC", "verify identity", "why can't I withdraw"                                  | `vendor/gate-exchange-kyc`                                     |
| "affiliate", "commission", "referral earnings"                                    | `vendor/gate-exchange-affiliate`                               |
| "welfare", "new user rewards", "claim rewards"                                    | `vendor/gate-exchange-welfare`                                 |
| "activities", "trading competition", "campaign"                                   | `vendor/gate-exchange-activitycenter`                          |
| "on-chain wallet", "wallet balance", "wallet address", "transfer tokens"          | `vendor/gate-dex-wallet`                                       |
| "token price", "K-line", "token rankings", "holder analysis", "security audit"    | `vendor/gate-dex-market`                                       |
| "on-chain swap", "buy token on-chain", "DEX trade", "bridge"                      | `vendor/gate-dex-trade`                                        |
| "analyze coin", "research BTC", "is ETH worth buying"                             | `vendor/gate-info-research` or `vendor/gate-info-coinanalysis` |
| "compare BTC vs ETH", "which is better"                                           | `vendor/gate-info-coincompare`                                 |
| "technical analysis", "RSI", "MACD", "trend"                                      | `vendor/gate-info-trendanalysis`                               |
| "is this token safe", "contract risk", "honeypot"                                 | `vendor/gate-info-riskcheck`                                   |
| "how is the market", "market overview", "crypto sentiment"                        | `vendor/gate-info-marketoverview`                              |
| "track address", "fund flow", "who owns this address"                             | `vendor/gate-info-addresstracker`                              |
| "live streams", "replays", "live room"                                            | `vendor/gate-info-liveroomlocation`                            |
| "crypto news", "what happened recently", "headlines"                              | `vendor/gate-news-briefing`                                    |
| "why did BTC crash", "what caused the pump"                                       | `vendor/gate-news-eventexplain`                                |
| "new listings", "what got listed", "delisted"                                     | `vendor/gate-news-listing`                                     |
| "invite friends", "referral link", "referral bonus"                               | `vendor/gate-growth-referral`                                  |

## Routing Rules

- Route queries directly to the matching vendor skill — the vendor SKILL.md has the full command reference
- If a query spans multiple dimensions (e.g., "analyze + risk check"), prefer `vendor/gate-info-research` which handles composite queries
- For ambiguous balance/price queries, ask the user to clarify CEX vs DEX
- If a read result leads to a trading action, follow the vendor skill's execution flow

## Typical Workflows

- **Research to trade**: `vendor/gate-info-research` → `vendor/gate-exchange-spot` or `vendor/gate-exchange-futures`
- **Check before buy**: `vendor/gate-exchange-assets` (balance) → `vendor/gate-exchange-spot` (order)
- **DEX flow**: `vendor/gate-dex-wallet` (auth + balance) → `vendor/gate-dex-market` (price check) → `vendor/gate-dex-trade` (swap)
- **Earn discovery**: `vendor/gate-exchange-simpleearn` or `vendor/gate-exchange-staking` → subscribe
- **Risk-aware trading**: `vendor/gate-info-riskcheck` → `vendor/gate-exchange-trading-copilot`
- **News to action**: `vendor/gate-news-eventexplain` → `vendor/gate-info-coinanalysis` → `vendor/gate-exchange-spot`
- **Portfolio review**: `vendor/gate-exchange-assets` → `vendor/gate-info-coinanalysis` per holding

## Operational Checklist

1. Detect user intent
2. Match intent to the routing table above
3. Follow the vendor skill's SKILL.md for the exact MCP tools and workflows
4. Return the result directly
