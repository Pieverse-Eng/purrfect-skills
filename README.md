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
| `aster` | Aster DEX perpetual futures — market data, trading, and account management. |
| `binance-connect` | Fiat on-ramp via Binance Connect. Buy crypto with card, Apple Pay, or bank transfer directly to wallet. |
| `bitget-wallet` | Bitget Wallet integration for multi-chain swaps, RWA stock trading, and market data. |
| `dflow-swap` | Solana on-chain swap implementation, executed via dflow. |
| `fourmeme` | four.meme on BSC — token buy, sell, and creation. |
| `gate` | Gate.io domain router — covers CEX (spot, futures, earn, staking, dual investment, loans, transfers), DEX (wallet, swaps, market data), intelligence (coin analysis, risk checks, market overview), and news. |
| `kraken` | Kraken exchange — spot / xStocks / forex trading, earn, staking, funding, and paper trading. |
| `lista-vaults` | Lista DAO lending vaults on BSC — deposit, redeem, and withdraw from ERC-4626 yield vaults. |
| `morph` | Morph L2 domain router — wallet, explorer, DEX swap, cross-chain bridge, EIP-7702 delegation, EIP-8004 agent identity & reputation, and x402 USDC payments. |
| `okx` | OKX domain router — token research, market data, portfolio analysis, smart-money signals, meme scanning, security checks, swaps, wallet ops, and x402 payments. |
| `opensea` | OpenSea entry point — execute NFT buy/sell via `purr opensea`, and route read operations to `opensea-vendor`. |
| `pancake` | PancakeSwap implementation — swaps, liquidity pools (LP), and farms. |

### Data & Intelligence

| Skill | Description |
|-------|-------------|
| `blockbeats` | BlockBeats intelligence — 1,500+ sources including AI-driven insights, Hyperliquid on-chain data, and Polymarket analytics. |
| `bnbchain-mcp` | BNB Chain MCP server — read-only blockchain queries for BNB Chain / opBNB blocks, transactions, contracts, ERC20 / NFTs, balances, and network info. |
| `ddg-search` | DuckDuckGo web search — zero-config, no API key required. Use as a fallback when `web_search` is unavailable. |
| `mantle` | Mantle skill bundle — network reference, address lookup, risk evaluation, portfolio analysis, DeFi planning, indexing, debugging, simulation, and smart-contract lifecycle. |
| `panewslab` | PANewsLab skill bundle — crypto news reading, article publishing, and rendered web viewing. |
| `rootdata-crypto` | RootData crypto intelligence — project / investor / people search, funding rounds, trending projects, and personnel job changes. |

### Wallet & Infrastructure

| Skill | Description |
|-------|-------------|
| `ows` | Open Wallet Standard (OWS) — local wallet custody, policy-gated signing, and API-key access. Manages the `~/.ows/` vault. |

### Payments & Protocols

| Skill | Description |
|-------|-------------|
| `pieverse-a2a` | Pieverse HTTP 402 A2A payment flow — probe, confirm, authorize through the hosted wallet, and retry with `X-Pieverse-Payment`. |
