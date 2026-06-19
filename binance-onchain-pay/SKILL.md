---
name: binance-onchain-pay
description: Onchain Pay:buy/send,routes/methods,quotes,checkout,contract
metadata:
  openclaw:
    primaryEnv: BINANCE_CONNECT_CLIENT_ID
---

# Binance Onchain Pay

## Overview

This Skill covers Binance Onchain Pay flows for buying or sending crypto through
Binance hosted checkout and delivering crypto to external on-chain addresses,
merchant checkouts, or supported contract destinations.

Out of scope: off-ramp sell flows, manual Binance API calls, user-signed
on-chain transactions, direct custody of the user's Binance account, and swaps
outside supported Binance Onchain Pay pre-order flows.

Use the scenarios below for user intent, then read the relevant command group
reference before running commands or explaining the workflow.

## Important Notes

- Use Binance Onchain Pay checkout/pre-order flows. Do not replace them with
  `onchain_execute` or swap commands.
- When route, asset, amount, or network details are already known, run discovery
  and quote commands before asking for fields that are only needed for
  Pre-Order. Trading Pairs, Crypto Network, Payment Method List, and Estimated
  Quote do not require the receiving wallet address; Pre-Order does.
- The checkout or action URL opens Binance's hosted page.
- Binance handles KYC, payment processing, or account confirmation where
  applicable.
- Binance delivers crypto on-chain to the receiving wallet address or supported
  destination.
- Always show quote, transfer, checkout, or contract details and get explicit
  user confirmation before creating a pre-order.
- To check received balance, use the Onchain skill. For common EVM checks, use
  `purr wallet balance --token <symbol> --chain-id <id>`, such as
  `purr wallet balance --token USDT --chain-id 56`.

## Runtime Credentials

The runtime provides Binance Onchain Pay partner credentials through environment
variables. If required env vars are missing, report that Binance Onchain Pay
runtime credentials are not configured. Keep authentication details for
troubleshooting only; never request or expose partner secrets in user-facing
flows.

For credential/signing troubleshooting only, see
[authentication.md](references/authentication.md). Do not manually sign requests
in user flows.

| Runtime env | Official usage |
| --- | --- |
| `BINANCE_CONNECT_CLIENT_ID` | Partner client ID |
| `BINANCE_CONNECT_ACCESS_TOKEN` | Sign access token |
| `BINANCE_CONNECT_PRIVATE_KEY` | RSA private key material used by the CLI |
| `BINANCE_CONNECT_BASE_URL` | Binance API base URL |

These are not authentication secrets, but pre-order defaults supplied by the
runtime:

| Runtime env | Official usage |
| --- | --- |
| `BINANCE_CONNECT_MERCHANT_CODE` | Default `merchantCode` for pre-orders |
| `BINANCE_CONNECT_MERCHANT_NAME` | Default `merchantName` for pre-orders |

## Command Groups

| Group | What It Does | Reference |
| --- | --- | --- |
| Trading Pairs | Lists supported fiat and crypto currencies. | [trading-pairs.md](references/trading-pairs.md) |
| Crypto Network | Lists supported blockchain delivery networks, fees, and limits. | [crypto-network.md](references/crypto-network.md) |
| P2P Trading Pairs | Lists P2P-specific fiat routes, optionally filtered by fiat. | [p2p-trading-pairs.md](references/p2p-trading-pairs.md) |
| Payment Method List | Lists broad or pair-specific payment methods. | [payment-method-list.md](references/payment-method-list.md) |
| Estimated Quote | Previews rate, fees, and estimated crypto amount. | [estimated-quote.md](references/estimated-quote.md) |
| Pre-Order | Creates Binance hosted checkout, transfer, merchant, or contract-interaction orders after user confirmation. | [pre-order.md](references/pre-order.md) |
| Order | Queries order status and details by `externalOrderId`. | [order.md](references/order.md) |

## Use Cases & Scenarios

### 1. Fiat-to-Crypto Purchase & Send

When to use: The user wants to buy crypto with fiat currency and send it
directly to an external on-chain wallet address.

Examples:

- Buy USDT with USD, EUR, or TWD using credit card and send it to a MetaMask
  address on BSC.
- Purchase BTC with Google Pay and transfer it to a hardware wallet.
- Buy USDC with P2P and send it to a DeFi protocol contract address.

Command groups: Trading Pairs -> Payment Method List -> Estimated Quote ->
Pre-Order -> Order.

### 2. Direct Crypto Transfer / Send Primary

When to use: The user has crypto in a Binance account and wants to send it to an
external address.

Examples:

- Send existing USDT from Binance Spot to a friend's wallet address.
- Transfer ETH to Uniswap contract for trading.
- Move crypto from Binance to a self-custodial wallet such as Trust Wallet or a
  hardware wallet.

Command groups: Pre-Order with `SEND_PRIMARY` customization.

### 3. Cross-Chain Bridge Operations

When to use: The user needs to buy crypto on one chain and transfer it to
another network.

Examples:

- Buy USDC on Ethereum and bridge to Polygon for lower fees.
- Purchase tokens on BSC and transfer to Base network.
- Fiat to crypto on Solana and send to Arbitrum for DeFi.

Command groups: Crypto Network -> Pre-Order with network selection.

### 4. Merchant Payment Integration

When to use: The user wants to integrate a crypto payment gateway for e-commerce
or services.

Examples:

- Accept fiat payments and auto-convert to crypto.
- Enable "Pay with Crypto" checkout flow.
- Process subscription payments with crypto.

Command groups: Pre-Order with `externalOrderId` tracking.

### 5. Smart Contract Interaction / Onchain-Pay Easy

When to use: The user wants to buy crypto and execute a smart contract in one
transaction.

Examples:

- Buy USDT and deposit to a lending protocol.
- Purchase tokens and stake in a DeFi pool.
- Fiat on-ramp directly to GameFi or NFT marketplace.

Command groups: Pre-Order with `ON_CHAIN_PROXY_MODE` customization.

### 6. Query & Monitoring

When to use: The user wants to check order status, available networks, or
payment methods.

Examples:

- Monitor order processing status, such as pending, completed, or failed.
- List supported fiat currencies and cryptocurrencies.
- Check available payment methods for a specific country or amount.
- Verify network fees and limits.

Command groups: Order, Crypto Network, Trading Pairs, Payment Method List.

## Core Flow

1. Identify the scenario from Use Cases & Scenarios.
2. Read the relevant command group references.
3. Confirm route, amount, asset, network, destination, and payment or
   customization details.
4. Show quote, checkout, transfer, or contract implications before creating any
   pre-order.
5. Ask for explicit user confirmation.
6. Create the pre-order and give the user the Binance checkout URL or returned
   action details.
7. Poll order status by `externalOrderId`.
8. After completion, check the receiving wallet balance or destination state.

## Common Delivery Networks

Use the Binance network value for Onchain Pay delivery. Use the Onchain skill for
wallet address and balance command details.

| Binance Network | Wallet Family | Chain ID |
| --- | --- |
| `BSC` | EVM | 56 |
| `ETH` | EVM | 1 |
| `BASE` | EVM | 8453 |
| `SOL` | Solana | n/a |
