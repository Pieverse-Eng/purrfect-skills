# Pieverse Built-in Skills

This directory contains the Pieverse built-in skills. Each folder is a skill unit organized by domain or protocol.

# Current Layout

### Routers & Runtime

| Skill | Description |
|-------|-------------|
| `onchain` | Top-level on-chain operations router. Classifies user intent and dispatches requests to the matching sibling skill for execution. |
| `purrfect-runtime` | Setup and skill store. Use only when the user explicitly asks to configure the runtime or manage plugins/skills. |

### Trading & DeFi

| Skill | Description |
|-------|-------------|
| `aster` | Aster DEX v3 skills — futures/spot API docs, market data, signed futures v3 calls, websocket v3 references, and on-chain deposit step building. |
| `balancer` | Balancer reviewed pool discovery, exact-input/exact-output swaps, and V2/V3 standard, boosted, and nested liquidity operations through `purr balancer`. |
| `binance` | Binance CEX via `binance-cli` — Spot, USD-S Futures, and Convert trading + market data (incl. bStocks spot pairs). Requires Binance API keys (auth). |
| `binance-agentic-wallet` | Binance Web3 Agentic Wallet via `baw` CLI — sign-in, balances, transfers, DEX swaps, limit orders, prediction markets, and x402 payments. |
| `binance-onchain-pay` | Binance Onchain Pay on-ramp via `purr` — payment methods, quotes, hosted checkout, order status, and reference docs. |
| `bitget-wallet` | Bitget Wallet integration for multi-chain swaps, RWA stock trading, and market data. |
| `dflow` | DFlow Agent CLI — Solana spot swaps, prediction markets, transfers, funding, guardrails, and local vault management. |
| `fourmeme` | four.meme on BSC — token buy, sell, and creation. |
| `gate` | Gate.io domain router — covers CEX (spot, futures, earn, staking, dual investment, loans, transfers), DEX (wallet, swaps, market data), intelligence (coin analysis, risk checks, market overview), and news. |
| `hyperliquid` | Hyperliquid market data, perpetual and spot trading, leverage, collateral moves, Arbitrum USDC deposits and withdrawals, and HIP-3 workflows. |
| `kraken` | Kraken exchange — spot / xStocks / forex trading, earn, staking, funding, and paper trading. |
| `lista-vaults` | Lista DAO lending vaults on BSC — deposit, redeem, and withdraw from ERC-4626 yield vaults. |
| `morph` | Morph L2 domain router — wallet, explorer, DEX swap, cross-chain bridge, EIP-7702 delegation, EIP-8004 agent identity & reputation, and x402 USDC payments. |
| `okx` | OKX domain router — token research, market data, WebSocket streams, portfolio analysis, smart-money signals, meme scanning, security checks, DEX swaps, cross-chain bridging, DeFi invest (APY/TVL discovery + deposit/redeem/stake/lend), DeFi portfolio view, wallet ops, and x402 payments. |
| `opensea` | OpenSea entry point — execute NFT buy/sell via `purr opensea`, and route read operations to `opensea-vendor`. |
| `pancake` | PancakeSwap planning and BSC execution — swaps, liquidity, farms, LP fees, rewards, and PCS Hub handoffs. |

### Data & Intelligence

| Skill | Description |
|-------|-------------|
| `blockbeats` | BlockBeats intelligence — 1,500+ sources including AI-driven insights, Hyperliquid on-chain data, and Polymarket analytics. |
| `bnbchain-mcp` | BNB Chain MCP server — read-only blockchain queries for BNB Chain / opBNB blocks, transactions, contracts, ERC20 / NFTs, balances, and network info. |
| `ddg-search` | DuckDuckGo web search — zero-config, no API key required. Use as a fallback when `web_search` is unavailable. |
| `kaia-skills` | Kaia knowledge bundle — network basics, gas, fee delegation, governance, SDKs, and transaction types. |
| `mantle` | Mantle skill bundle — network reference, address lookup, risk evaluation, portfolio analysis, DeFi planning, indexing, debugging, simulation, and smart-contract lifecycle. |
| `panewslab` | PANewsLab crypto news, Polymarket smart money boards, article publishing, and rendered PANews web pages. |
| `rootdata-crypto` | RootData crypto intelligence — project / investor / people search, funding rounds, trending projects, and personnel job changes. |
| `surf` | Surf crypto intelligence — live prices, wallets, DeFi, on-chain SQL, social analytics, prediction markets, news, search, and fund data via the Surf CLI. |
| `stock-spread` | READ-ONLY cross-venue tokenized-stock price & spread intelligence — resolves an equity to per-venue identifiers and reports the normalized CEX-vs-DEX spread across Gate, Bybit, Binance bStocks, and Solana/Jupiter. Quotes & comparison only; never trades. |
| `binance-tokenized-securities-info` | READ-ONLY Ondo tokenized US-stock data on Binance Web3 (BNB Chain) — token list, RWA metadata + attestations, market/asset trading status (corporate actions), on-chain price/holders/market-cap, US fundamentals, and K-line. Imported from binance-skills-hub. |

### Wallet & Infrastructure

| Skill | Description |
|-------|-------------|
| `cobo` | Cobo Agentic Wallet router — wallet onboarding or pairing, pact workflows, Cobo-managed transfers, contract calls, message signing, DeFi execution, and SDK/MCP integrations. |

### Payments & Protocols

| Skill | Description |
|-------|-------------|
| `instance-billing` | Hosted Purrfect Claw plan, credits, payment-method listing, credit top-up, and one-cycle renewal through `purr instance` with canonical token names or IDs. |
| `pieverse-a2a` | Pieverse HTTP 402 A2A payment flow — probe, confirm, authorize through the hosted wallet, and retry with `X-Pieverse-Payment`. |
| `red-packet` | P2P XLayer USDT0 redpackets through `purr redpacket` — send to `.pie`/EVM address, inspect pending, claim, and view sent history. |
