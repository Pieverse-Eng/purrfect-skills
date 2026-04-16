---
name: binance-connect
description: Fiat on-ramp via Binance Connect. Buy crypto with fiat (card, Apple Pay, bank transfer) directly to wallet.
---

# Binance Connect (Fiat On-Ramp)

## Scope
- In scope: Buying crypto with fiat currency (USD, EUR, VND, 100+ currencies)
- NOT a swap — Binance handles payment processing, KYC, and on-chain delivery
- No on-chain tx from our wallet — crypto is delivered by Binance directly
- Supports 300+ cryptocurrencies, 300+ payment methods

## Execution Flow

1. `wallet_address` with chain_type "ethereum" — get wallet address
2. Run: `purr binance-connect quote --fiat <currency> --crypto <token> --amount <fiat_amount> --network <chain>`
   - Show quote to user: estimated crypto amount, exchange rate, fees
   - Ask user to confirm before proceeding
3. Run: `purr binance-connect buy --fiat <currency> --crypto <token> --amount <fiat_amount> --network <chain> --wallet <address>`
4. Send the checkout URL to the user — they complete payment on Binance's page
5. Wait for user to confirm they paid, then poll: `purr binance-connect status --order-id <id>`
6. `wallet_balance` to confirm crypto was received

## Commands

### purr binance-connect pairs
No arguments. Returns supported fiat and crypto currencies.

### purr binance-connect networks
No arguments. Returns supported blockchain networks for crypto delivery.

### purr binance-connect quote
| Flag | Required | Description |
|------|----------|-------------|
| --fiat | yes | Fiat currency code (e.g. USD, EUR, VND) |
| --crypto | yes | Crypto to buy (e.g. USDT, USDC, BNB) |
| --amount | yes | Fiat amount (e.g. "50") |
| --network | yes | Delivery network: BSC, ETH, BASE, SOL |
| --payment-method | no | Payment method (e.g. BUY_CARD) |

### purr binance-connect buy
| Flag | Required | Description |
|------|----------|-------------|
| --fiat | yes | Fiat currency code |
| --crypto | yes | Crypto to buy |
| --amount | yes | Fiat amount |
| --network | yes | Delivery network: BSC, BASE, ETH, SOL |
| --wallet | yes | Destination wallet address |
| --payment-method | no | Payment method |
| --order-id | no | Custom external order ID (auto-generated if omitted) |

### purr binance-connect status
| Flag | Required | Description |
|------|----------|-------------|
| --order-id | yes | Order ID from buy command response |

## Network to Chain ID Mapping

Use the correct `--network` value for Binance Connect and `--chain-id` for wallet balance checks:

| Network (Binance) | Chain ID | Use for balance check |
|---|---|---|
| BSC | 56 | `purr wallet balance --chain-id 56 --token <addr>` |
| ETH | 1 | `purr wallet balance --chain-id 1 --token <addr>` |
| BASE | 8453 | `purr wallet balance --chain-id 8453 --token <addr>` |
| SOL | — | `purr wallet balance --chain-type solana` |

## Important Notes
- This is a FIAT on-ramp, not a swap — no `onchain_execute` needed
- The checkout URL opens Binance's hosted payment page
- Binance handles all KYC and payment processing
- Crypto is delivered on-chain directly to the wallet address by Binance
- Always show the quote and get user confirmation before creating an order
- To check received balance: `purr wallet balance --token <symbol> --chain-id <id>` (e.g. `--token USDT --chain-id 56`)

## Failure Handling

| Error | Solution |
|-------|----------|
| "Missing env vars" | BINANCE_CONNECT_CLIENT_ID, BINANCE_CONNECT_ACCESS_TOKEN, BINANCE_CONNECT_PRIVATE_KEY, and BINANCE_CONNECT_BASE_URL must be configured in the environment |
| "payment expired" | Order has a time limit — create a new one |
| "order failed" | Payment was rejected — ask user to try a different payment method |
| "no route found" | Currency pair or network not supported — check with `pairs` and `networks` |
| error 1130450 | Amount below minimum for this currency. Try a larger amount (e.g. JPY minimum ~5000, USD minimum ~20) |
