---
name: gate
description: Gate CEX/DEX,spot/futures,earn,Web3 Pay,x402,news
---

# Gate

This is the top-level Gate router. Classify the user's intent, choose the
matching vendor skill under `vendor/`, then read that vendor `SKILL.md` before
running commands or explaining a workflow.

## CLI Preflight

If this is a hosted instance, do not run this section.

```bash
sh vendor/gate-cli-installer/setup.sh --version v0.7.7
export PATH="$HOME/.local/bin:$HOME/.openclaw/skills/bin:$PATH"
gate-cli --version

GATE_DEX_ARCH=$(case "$(uname -m)" in
  x86_64) echo x64 ;;
  *) echo "Unsupported architecture for gate-dex: $(uname -m)" >&2; exit 1 ;;
esac)
curl -fsSL -o /usr/local/bin/gate-dex \
  "https://gate-dex-cli.gateweb3.cc/v1.0.6/gate-dex-linux-${GATE_DEX_ARCH}"
chmod +x /usr/local/bin/gate-dex
test "$(gate-dex --version)" = "1.0.6"
```

## Execution Boundary

- Prefer CLI vendor skills whenever CLI and MCP both cover the same capability.
- Use MCP vendor skills only for capabilities that the CLI vendor skill does not
  cover.
- Do not run unpinned installer workflows from this router. For non-hosted
  runtimes, use only the pinned commands in CLI Preflight. Treat
  `vendor/gate-mcp-installer` as upstream reference material only.
- Do not ask the user to paste Gate API secrets, MCP tokens, or private keys
  into chat. Follow the selected vendor skill's local auth/config guidance.
- If a required CLI or MCP service is missing in a hosted runtime, report the
  exact environment error and stop. Do not install packages at runtime in hosted
  instances.

## Scope

- Gate CEX trading: spot, futures, options, TradFi, Alpha, CrossEx, complex
  trading, flash swap, bots, asset swap, and new listings.
- Gate CEX account and assets: balances, transfers, unified account, subaccounts,
  coupons, VIP fees, KYC, welfare, activity center, referrals, affiliate data,
  small-balance conversion, and Gate Pay.
- Gate Earn: Simple Earn, Smart Earn, staking, dual investment, LaunchPool,
  collateral loans, and auto-invest.
- Gate DEX: CLI wallet, balances, transfers, signing, token data, market data,
  swaps, bridges, and MCP-only x402 / DApp / contract flows.
- Gate Info and News: research, market overview, macro, trend, risk, Web3,
  token on-chain, DeFi, address tracking, community sentiment, events, listings,
  and news briefings.

## DEX Routing

Use CLI by default for overlapping DEX capabilities.

| User intent | Route to |
| --- | --- |
| Gate DEX login/logout, wallet status, wallet address, balances, token list, tx history, transfer/send tokens, raw message/tx signing | `vendor/gate-dex-wallet-cli` |
| DEX token price, K-line/OHLCV, token info, token risk/security, rankings, new tokens, liquidity, holder analysis, tx stats, chain config, raw RPC, token address lookup | `vendor/gate-dex-market-cli` |
| DEX quote, swap, buy/sell/convert, same-chain swap, cross-chain bridge, swap history/detail, swappable token list, bridge token list | `vendor/gate-dex-trade-cli` |
| x402 payment, paid URL, HTTP 402, DApp connect/signing, approve/revoke, contract call, EIP-712/Permit/personal_sign, on-chain withdraw to Gate Exchange by UID, direct MCP wallet signing/tool flow | `vendor/gate-dex-wallet` |

Do not route normal market or swap requests to removed MCP market/trade skills.
Those flows now use `vendor/gate-dex-market-cli` and
`vendor/gate-dex-trade-cli`.

## CEX Trading Routing

| User intent | Route to |
| --- | --- |
| Spot buy/sell, market/limit order, trigger order, take profit, stop loss, cancel order, spot balances | `vendor/gate-exchange-spot` |
| Futures/perpetual open or close position, leverage, TP/SL, conditional futures order | `vendor/gate-exchange-futures` |
| Options, call/put, strike, expiration, options close/cancel/amend | `vendor/gate-exchange-options` |
| TradFi, forex, commodities, MT5-style account, TradFi orders/positions | `vendor/gate-exchange-tradfi` |
| Alpha token discovery, Alpha market view, buy/sell Alpha token, Alpha holdings/history | `vendor/gate-exchange-alpha` |
| Cross-exchange trading or positions across Gate, Binance, OKX, Bybit | `vendor/gate-exchange-crossex` |
| Complex trading workflow, margin borrow, combined spot/futures/TradFi/Alpha execution, action draft | `vendor/gate-exchange-trading` |
| Flash swap, instant convert, convert one coin to another, consolidate coins, one-to-many or many-to-one conversion | `vendor/gate-exchange-flashswap-assistant` |
| Simple flash swap reference or direct flash swap domain request | `vendor/gate-exchange-flashswap` |
| Spot allocation optimization, rebalance spot holdings, allocation history | `vendor/gate-exchange-assetswap` |
| Trading bots, AIHub strategy, grid, martingale, running bot query/stop | `vendor/gate-exchange-bot` |
| New listing research, launch calendar, pre-listing due diligence, first buy of a new asset | `vendor/gate-exchange-newcoin` |
| Market depth, liquidity, slippage, funding, basis, manipulation risk, market microstructure | `vendor/gate-exchange-marketanalysis` |

## CEX Account And Assets Routing

| User intent | Route to |
| --- | --- |
| Total assets, account balance, specific coin holdings across accounts | `vendor/gate-exchange-assets` |
| Asset overview plus margin/liquidation risk, earnings snapshots, borrow/add margin/set collateral context | `vendor/gate-exchange-assets-manager` |
| Move funds between own Gate accounts, spot to futures, same-UID internal transfer | `vendor/gate-exchange-transfer` |
| Unified account equity, borrow/repay, margin mode, leverage/collateral config | `vendor/gate-exchange-unified` |
| Sub-account list/create/lock/unlock/status | `vendor/gate-exchange-subaccount` |
| Small balance, dust conversion to GT, small-balance history | `vendor/gate-exchange-smallbalance` |
| Coupons, vouchers, bonus cards, coupon rules/expiry/source | `vendor/gate-exchange-coupon` |
| VIP level, spot/futures fee rate, trading fee | `vendor/gate-exchange-vipfee` |
| KYC, identity verification, withdrawal blocked because of verification | `vendor/gate-exchange-kyc` |
| Welfare center, newcomer rewards, claim tasks/rewards | `vendor/gate-exchange-welfare` |
| Trading competitions, activity center, campaigns, airdrops | `vendor/gate-exchange-activitycenter` |
| CandyDrop activities, registration, task progress, participation/airdrop records | `vendor/gate-exchange-candydrop` |
| Affiliate/partner commissions, referral volume, affiliate application | `vendor/gate-exchange-affiliate` |
| Invite friends, referral links, referral rewards, earn-together rules | `vendor/gate-exchange-referral` |
| Gate Pay, merchant charge, pay-first flow, Gate Pay order/payment | `vendor/gate-exchange-pay` |
| Gate Pay x402 merchant/payment-resource flow | `vendor/gate-pay-x402` |

## Earn Routing

| User intent | Route to |
| --- | --- |
| Broad Earn flow, APY compare, idle-fund ideas, subscribe/redeem across earn products | `vendor/gate-exchange-earn` |
| Simple Earn, flexible earn, fixed earn, subscribe/redeem interest | `vendor/gate-exchange-simpleearn` |
| Staking, stake/redeem/mint POS coins, staking assets/rewards | `vendor/gate-exchange-staking` |
| Dual investment, dual currency, sell-high/buy-low, target/exercise price, dual orders | `vendor/gate-exchange-dual` |
| LaunchPool, pledge/redeem, airdrop rewards, launch pool events | `vendor/gate-exchange-launchpool` |
| Collateral loan, borrow against collateral, repay, add/redeem collateral | `vendor/gate-exchange-collateralloan` |
| Auto-invest, DCA, invest plan, top up/update/stop plan | `vendor/gate-exchange-autoinvest` |

## Info And News Routing

Prefer composite skills for broad questions, and narrow skills for exact
single-purpose questions.

| User intent | Route to |
| --- | --- |
| Broad research, single-coin analysis plus news/risk/technicals, market overview plus extra dimensions, multi-step report | `vendor/gate-info-research` |
| Single-coin comprehensive analysis only | `vendor/gate-info-coinanalysis` |
| Compare two or more coins | `vendor/gate-info-coincompare` |
| Technical analysis only, RSI, MACD, K-line trend, support/resistance | `vendor/gate-info-trendanalysis` |
| Overall crypto market conditions only | `vendor/gate-info-marketoverview` |
| Risk-first token/project/address safety, honeypot, sanctions/compliance, contract risk | `vendor/gate-info-risk` |
| Legacy or MCP-only token/address risk check | `vendor/gate-info-riskcheck` |
| On-chain, protocol, Web3 behavior, reserves, bridges, stablecoins, heatmaps | `vendor/gate-info-web3` |
| DeFi TVL, protocol metrics, APY/yield, stablecoins, bridges, exchange reserves, liquidation heatmaps | `vendor/gate-info-defianalysis` |
| Token holder distribution, token on-chain activity, large transfers | `vendor/gate-info-tokenonchain` |
| Track an address, address info, address transactions, fund flow | `vendor/gate-info-addresstracker` |
| Macro impact, CPI/NFP/Fed/rates and crypto, macro calendar | `vendor/gate-info-macroimpact` |
| Live rooms or replay discovery | `vendor/gate-info-liveroomlocation` |
| News-first broad request, event explain, listing announcements, social/UGC, market move attribution | `vendor/gate-news-intel` |
| Recent news/headlines only | `vendor/gate-news-briefing` |
| Why a coin moved, why crash/pump, event attribution only | `vendor/gate-news-eventexplain` |
| Exchange listings, delistings, maintenance announcements | `vendor/gate-news-listing` |
| Community sentiment, Twitter/X/KOL/social discussion | `vendor/gate-news-communityscan` |

## Routing Rules

- Read exactly one matching vendor `SKILL.md` before executing. If the chosen
  vendor skill points to a reference file for the selected workflow, read that
  reference too.
- If the request is ambiguous between CEX and DEX, ask the user to clarify.
  Example: "buy ETH" can mean Gate CEX spot or DEX swap.
- If an Info/News request has multiple dimensions, prefer
  `vendor/gate-info-research` or `vendor/gate-news-intel` instead of chaining
  several narrow skills.
- If an Info/News request explicitly names exact narrow dimensions, route each
  named dimension directly instead of collapsing it into research. Examples:
  token on-chain activity -> `vendor/gate-info-tokenonchain`, macro calendar or
  CPI/Fed impact -> `vendor/gate-info-macroimpact`, Web3 reserves/bridges ->
  `vendor/gate-info-web3`, live rooms -> `vendor/gate-info-liveroomlocation`.
- If a DEX token contract request includes market dimensions such as price,
  K-line, risk, liquidity, and holders, keep those DEX market dimensions
  together under `vendor/gate-dex-market-cli`.
- If a read-only result leads to a trading, transfer, payment, or signing action,
  switch to the execution skill and follow its confirmation gates.
- For any financial execution or on-chain transaction, show the relevant preview
  and ask for explicit user confirmation before the write command or signing
  call.

## Typical Workflows

| Workflow | Route |
| --- | --- |
| Research to CEX trade | `vendor/gate-info-research` -> `vendor/gate-exchange-spot` or `vendor/gate-exchange-futures` |
| CEX balance to order | `vendor/gate-exchange-assets` -> `vendor/gate-exchange-spot` |
| DEX swap | `vendor/gate-dex-wallet-cli` -> `vendor/gate-dex-market-cli` -> `vendor/gate-dex-trade-cli` |
| DEX x402 or DApp signing | `vendor/gate-dex-wallet` |
| Earn discovery to subscribe/redeem | `vendor/gate-exchange-earn` or the specific earn product skill |
| News to action | `vendor/gate-news-intel` -> `vendor/gate-info-research` -> execution skill |
| Portfolio review | `vendor/gate-exchange-assets` -> `vendor/gate-info-research` |
