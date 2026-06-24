---
name: opensea
description: OpenSea,NFT,Seaport orders,swap,x402,sign,execute,tools
license: MIT
metadata:
  openclaw:
    primaryEnv: OPENSEA_API_KEY
---

# OpenSea

## Overview

Agent skills for interacting with OpenSea: query NFT and token data, trade on the Seaport marketplace, swap ERC20 tokens, and build AI agent tools with onchain gating.

Use vendored OpenSea instructions for read-only lookups, quotes, schemas, and payload preparation. When the task requires signing or execution, stop following the official OpenSea execution path and use `purr opensea` instead.

## CLI Preflight

If this is a hosted instance, do not run this section.

```bash
npm install -g @opensea/cli@1.10.0
opensea --version
```

## `purr opensea` Operations

Use `purr opensea` for every OpenSea signing or execution operation. Do not use OpenSea wallet providers, `PRIVATE_KEY`, `--wallet-provider`, `opensea ... execute`, `opensea auth login --private-key`, `npx @opensea/tool-sdk ...` auto-sign commands, or SDK wallet auto-sign helpers.

Before any signing or execution:

1. Resolve the current wallet with `purr wallet address --chain-type ethereum`.
2. Check funds with `purr wallet balance --chain-type ethereum --chain-id <chain_id>`.
3. Inspect the OpenSea payload for chain, target, value, token, NFT, order, spender, and payment details.
4. Ask exactly: `Do you want to execute this action with these parameters? (Yes/No)`

| Operation | Use `purr opensea` | Do not use |
|---|---|---|
| Buy an NFT from listing fulfillment JSON | `purr opensea buy --wallet <wallet> --fulfillment-file <file> [--execute]` | Official WalletAdapter execution or private-key signing |
| Accept an offer or sell an NFT from offer fulfillment JSON | `purr opensea sell --wallet <wallet> --fulfillment-file <file> [--execute]` | Official WalletAdapter execution or private-key signing |
| Execute a single transaction object from mint, deploy, transfer, cancel, fulfillment, or swap APIs | `purr opensea tx --wallet <wallet> --chain-id <chain_id> --tx-file <file> [--execute]` | Official SDK transaction send helpers |
| Execute ordered transaction-only `actions`, `transactions`, `txs`, `swap.actions`, sweep, or cross-chain purchase payloads | `purr opensea actions --wallet <wallet> --chain-id <chain_id> --actions-file <file> [--execute]` | `opensea swaps execute` or official action execution |
| Sign Seaport listing or offer EIP-712 typed data | `purr opensea sign-order --wallet <wallet> --typed-data-file <file>` | SDK/private-key typed-data signing |
| Sign SIWE or other OpenSea auth/sign-in message | `purr opensea sign-message --wallet <wallet> --message-file <file> [--chain-id <chain_id>]` | `opensea auth login --private-key ...` |
| Sign x402 or EIP-3009 payment typed data | `purr opensea sign-payment --wallet <wallet> --payment-file <file>` | `npx @opensea/tool-sdk pay` auto-sign flow |

Keep these boundaries:

- Read-only OpenSea lookup stays in the selected vendored skill.
- Swap quotes stay in `opensea-swaps`; swap execution goes through `purr opensea tx` or `purr opensea actions` using the returned calldata.
- Marketplace fulfillment data stays in `opensea-marketplace`; buy/sell execution goes through `purr opensea buy` or `purr opensea sell`.
- Sweep and cross-chain marketplace preparation stays in `opensea-marketplace`; execute returned action arrays or transaction payloads with `purr opensea actions` or `purr opensea tx`.
- Drop mint, deploy, transfer, and cancel transaction preparation stays in the vendored OpenSea skill; execution goes through `purr opensea tx`.
- Tool discovery and gated-tool payload preparation stays in `opensea-tool-sdk`. Tool registration, updates, monetization setup, and other registry writes are transaction/action flows; execute returned payloads with `purr opensea tx` or `purr opensea actions`.
- Gated-tool payment requests use `purr opensea sign-payment`. OpenSea sign-in, auth, and SIWE messages use `purr opensea sign-message`.
- Do not route signing or execution to `opensea-wallet`; do not set up official OpenSea wallet providers for these operations.
- If the user asks to use an OpenSea wallet provider, private key, or official auto-sign path for a known action, refuse that method and continue with the matching `purr opensea` command after showing parameters and asking for confirmation.
- If `purr opensea actions` returns `signatureRequests`, sign those requests first. Do not use `actions --execute` on mixed transaction/signature payloads.
- `purr opensea sign-payment` signs payment typed data only; a complete HTTP 402 challenge, signed payment header construction, retry, and settlement flow must be handled separately unless a future `purr` command owns that flow.
- After `--execute`, return the transaction hash and explorer link immediately. Do not wait for confirmation unless the user asks.

## OpenSea CLI Command Hints

Use these OpenSea CLI 1.10.0 command families for read-only work and payload preparation. Keep signing and execution in `purr opensea`.

| Need | OpenSea CLI command family |
|---|---|
| Collection details, stats, floor prices, or trends | `opensea collections get <slug>`, `opensea collections stats <slug>`, `opensea collections floor-prices <slug>`, `opensea collections trending`, `opensea collections top` |
| NFT details, collection NFTs, or wallet NFTs | `opensea nfts get <chain> <contract> <token-id>`, `opensea nfts list-by-collection <slug>`, `opensea nfts list-by-account <chain> <address>` |
| Account profile, portfolio, offers, listings, or tokens | `opensea accounts get <address>`, `opensea accounts portfolio <address>`, `opensea accounts offers <address>`, `opensea accounts listings <address>`, `opensea accounts tokens <address>` |
| Search collections, NFTs, tokens, or accounts | `opensea search <query> --types collection,nft,token,account` |
| Listing or offer lookup | `opensea listings best <collection>`, `opensea listings best-for-nft <collection> <token-id>`, `opensea offers best-for-nft <collection> <token-id>` |
| Sweep or cross-chain purchase preparation | `opensea listings sweep ...`, `opensea listings cross-chain-fulfill ...`; execute returned payloads with `purr opensea actions` or `purr opensea tx` |
| Swap quote preparation | `opensea swaps quote ...`; execute returned calldata with `purr opensea actions` or `purr opensea tx` |
| Drop mint or contract deploy preparation | `opensea drops mint <slug>` or `opensea drops deploy`; execute returned transaction with `purr opensea tx` |
| Tool discovery | `opensea tools search`, `opensea tools list`, `opensea tools get ...` |
| Tool registration or monetization setup | Prepare with `opensea-tool-sdk`; execute returned transaction or action payloads with `purr opensea tx` or `purr opensea actions` |
| Transaction receipt or status | `opensea transactions receipt ...` |
| Asset transfer preparation | `opensea assets transfer ...`; execute returned transaction with `purr opensea tx` |

## Decision Tree

| User needs to... | Use |
|---|---|
| Query NFT or token data, search, check collection stats, browse drops, or stream events | [`vendor/opensea-api/SKILL.md`](vendor/opensea-api/SKILL.md) |
| Buy or sell NFTs, fulfill listings or offers, make orders, sweep listings, or handle cross-chain NFT purchases | [`vendor/opensea-marketplace/SKILL.md`](vendor/opensea-marketplace/SKILL.md) |
| Swap ERC20 tokens, get swap quotes, or check token balances for swap planning | [`vendor/opensea-swaps/SKILL.md`](vendor/opensea-swaps/SKILL.md) |
| Build, register, monetize, call, or gate AI-callable tools with ERC-8257, NFT ownership, subscriptions, predicates, or x402 | [`vendor/opensea-tool-sdk/SKILL.md`](vendor/opensea-tool-sdk/SKILL.md); use `purr opensea` for returned signatures, payments, or transactions |
| Sign in to OpenSea, authorize a session, or sign an auth/SIWE message | `purr opensea sign-message` |

## Skills

| Skill | Description | Auth or setup | Entry point |
|---|---|---|---|
| `opensea-api` | Query NFT and token data via the OpenSea CLI, MCP server, or shell scripts. Covers collections, NFTs, tokens, search, drops, events, and account lookups. | `OPENSEA_API_KEY`; get one at OpenSea developer settings or via the instant-key API. | [`vendor/opensea-api/SKILL.md`](vendor/opensea-api/SKILL.md) |
| `opensea-marketplace` | Find marketplace orders, prepare fulfillment data, and inspect Seaport order payloads. Execute buys, sells, and signatures with `purr opensea`. | `OPENSEA_API_KEY`; use `purr opensea` for signing or execution. | [`vendor/opensea-marketplace/SKILL.md`](vendor/opensea-marketplace/SKILL.md) |
| `opensea-swaps` | Get ERC20 swap quotes and balances across supported chains. Execute returned calldata with `purr opensea tx` or `purr opensea actions`. | `OPENSEA_API_KEY`; use `purr opensea` for execution. | [`vendor/opensea-swaps/SKILL.md`](vendor/opensea-swaps/SKILL.md) |
| `opensea-tool-sdk` | Build, register, and gate AI-callable tool endpoints using the OpenSea Tool Registry on Base. Use `purr opensea` for returned signatures, payment typed data, or transaction payloads. | `OPENSEA_API_KEY`; use `purr opensea` for signing or execution. | [`vendor/opensea-tool-sdk/SKILL.md`](vendor/opensea-tool-sdk/SKILL.md) |

## Less-Obvious Routing

| Scenario | Use |
|---|---|
| Browse NFT drops | `opensea-api` |
| Mint or deploy an NFT drop contract | `opensea-api` to prepare the transaction, then `purr opensea tx` |
| Stream real-time marketplace events with WebSockets | `opensea-api` |
| Purchase an NFT with payment from a different chain | `opensea-marketplace` to prepare actions, then `purr opensea actions` or `purr opensea tx` |
| Sweep multiple NFT listings in one transaction | `opensea-marketplace` to prepare actions, then `purr opensea actions` or `purr opensea tx` |
| Check token balances for a wallet before a swap | `opensea-swaps` |
| Gate a tool with NFT ownership, subscriptions, predicates, or x402 payments | `opensea-tool-sdk`; use `purr opensea` for returned signatures, payments, or transactions |
| Pay for an OpenSea-powered tool request | `opensea-tool-sdk`, then `purr opensea sign-payment` |
| Register or update an OpenSea AI tool or monetization rule | `opensea-tool-sdk` to prepare the payload, then `purr opensea tx` or `purr opensea actions` |
| Sign in to OpenSea or authorize an OpenSea session | `purr opensea sign-message` |
| Transfer an NFT or token asset | `opensea-api` to prepare the transaction, then `purr opensea tx` |
| Check an OpenSea transaction receipt or status | `opensea-api` |

## Official Links

- [Developer docs](https://docs.opensea.io/)
- [OpenSea CLI](https://github.com/ProjectOpenSea/opensea-cli)
- [OpenSea MCP Server](https://mcp.opensea.io/)
- [Get an API key](https://docs.opensea.io/reference/api-keys#instant-api-key-for-agents)
