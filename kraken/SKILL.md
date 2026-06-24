---
name: kraken
description: Kraken,spot,futures,xStocks,forex,earn,paper,MCP
metadata:
  openclaw:
    primaryEnv: KRAKEN_API_KEY
  requires:
    env:
      - KRAKEN_API_KEY
      - KRAKEN_API_SECRET
---

# Kraken

Kraken covers crypto exchange workflows through the `kraken` CLI, including
market data, spot trading, xStocks, forex, futures, earn/staking, deposits,
withdrawals, portfolio/account analysis, paper trading, MCP integration, and
multi-step trading or reporting recipes.

Use this skill when the user wants to inspect Kraken markets, test strategies
with paper trading, manage Kraken account state, or prepare/execute Kraken
trading, funding, earn, futures, or portfolio workflows.

## CLI Preflight

If this is a hosted instance, do not run this section.

```bash
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/krakenfx/kraken-cli/releases/download/v0.3.2/kraken-cli-installer.sh \
  | KRAKEN_CLI_UNMANAGED_INSTALL=/usr/local/bin sh -s -- --quiet
kraken --version
```

## Scope

- Public market data: assets, pairs, tickers, OHLC, order books, trades,
  spreads, WebSocket market streams, alerts, and multi-pair screening.
- Account reads: balances, open/closed orders, trade history, ledgers, P&L,
  portfolio snapshots, fee tier progress, and tax/export reports.
- Spot trading: crypto spot, xStocks/tokenized assets, forex, order validation,
  order placement, edits, cancels, stops, take-profit, TWAP, DCA, grid trading,
  and rebalancing.
- Futures: futures market data, futures paper trading, live futures orders,
  positions, leverage, funding, margin, liquidation risk, basis trades, carry
  strategies, and hedge workflows.
- Funding and earn: deposits, withdrawals, wallet transfers, earn/staking
  strategies, allocations, deallocations, and yield comparisons.
- Account operations: subaccounts, capital rotation, operational risk controls,
  emergency flattening, and drawdown circuit breakers.
- MCP: native MCP integration for clients that call `kraken` through structured
  tools.

Live trades, withdrawals, earn allocations/deallocations, subaccount transfers,
WebSocket order mutations, and other financial writes require a preview and
explicit user confirmation before execution. Read-only market data and paper
trading do not require live Kraken credentials.

## Credentials

Use ambient credentials when they are already available. Do not put API keys,
API secrets, OTPs, or env assignments into runnable command text.

| Credential | Env Var | Description |
|------------|---------|-------------|
| **API Key** | `KRAKEN_API_KEY` | From kraken.com Settings > API |
| **API Secret** | `KRAKEN_API_SECRET` | From kraken.com Settings > API |

For futures trading (optional, separate key pair):

| Credential | Env Var | Description |
|------------|---------|-------------|
| **Futures API Key** | `KRAKEN_FUTURES_API_KEY` | From Kraken Futures Settings > Create Key |
| **Futures API Secret** | `KRAKEN_FUTURES_API_SECRET` | From Kraken Futures Settings > Create Key |

For public market data and paper trading commands, do not ask for live
credentials. For authenticated reads or live actions, if the selected vendor
skill requires missing credentials, ask the user to configure or provide them
through the host environment or platform credential flow, then rely on those
environment variables.

## Skill Reference

This top-level skill is a router. Do not duplicate command recipes here.

Use [vendor/INDEX.md](vendor/INDEX.md) as the authoritative skill index:

1. Classify the user's Kraken request into the closest market data, account,
   spot execution, futures, strategy, funding/earn, portfolio, risk, MCP, or
   recipe category.
2. Read `vendor/INDEX.md`, choose the matching vendor skill or recipe, then
   read that selected `SKILL.md` before explaining a workflow or running
   commands.
3. If a request spans multiple domains, read each relevant vendor skill and
   combine their guidance. Prefer shared safety/reference skills such as
   `kraken-shared`, `kraken-risk-operations`, `kraken-error-recovery`,
   `kraken-rate-limits`, and `kraken-order-types` when they affect the task.
4. Apply the credential and confirmation gates from this top-level router
   together with the more specific rules from the selected vendor skill.
5. If there is no exact match, choose the closest vendor skill from the index,
   state the routing assumption briefly, and proceed with that skill's
   workflow.
