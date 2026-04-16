---
name: bitget-wallet
description: Bitget Wallet integration for multi-chain swaps, RWA stock trading, and market data.
---

# Bitget Wallet (Swap + RWA + Market Data)

Implementation skill for Bitget Wallet API. Follows the Bitget order flow (check-swap-token → quote → confirm → makeOrder → sign → send → get-order-details) but replaces the vendor signing scripts (`order_sign.py`, `order_make_sign_send.py`) with `purr wallet sign-transaction` — managed custody instead of local private keys.

**NEVER use or reference**: `order_sign.py`, `order_make_sign_send.py`, `social_order_make_sign_send.py`, `social-wallet.py`, `key_utils.py`, `x402_pay.py`. These do not exist here. All signing goes through `purr wallet sign-transaction`.

**Out of scope**: Social Login Wallet, x402 payments, local mnemonic/private-key management, Tron swaps (no Tron wallet). If the user asks for any of these, explain they are not supported and suggest alternatives.

## Mandatory Rules

> **First time using this skill?** Read [`vendor/README.md`](vendor/README.md) for capabilities overview and [`vendor/SKILL.md`](vendor/SKILL.md) for market tools architecture, chain identifiers, stablecoin addresses, and common pitfalls.

> **ALWAYS read the relevant `vendor/docs/*.md` before any API call.**
> Do NOT write your own curl/jq commands from memory — the vendor docs contain tested,
> working commands with correct API endpoints and field names.

> **NEVER handle private keys or mnemonics.** Wallets are managed by the runtime; signing goes through `purr wallet sign-transaction`.

> **User confirmation required before any fund-moving action.** Before executing a swap or trade, show the quote details (amounts, gas, slippage) and wait for explicit confirmation ("confirm" / "yes"). Once confirmed, execute all remaining steps (makeOrder → sign → send) without pausing again.

> **Always show tx results with explorer links.** After a successful write operation, reply with the transaction hash(es) and clickable explorer links using the chain's explorer URL from the Supported Chains table (e.g. `https://bscscan.com/tx/{txId}`, `https://solscan.io/tx/{txId}`). For cross-chain swaps, show both fromTxId and toTxId links.

> **Use API-returned values exactly as-is.** When an API response returns a field (e.g. `market.id`, `market.protocol`, `contract`, `orderId`), pass it verbatim to subsequent calls. Never guess or transform these values.

## Tools — Read

All read operations go through the vendor Python API client directly — no purr involved.

```bash
cd ./skills/bitget-wallet/vendor
python3 bitget-wallet-agent-api.py <command> [args...]
```

| Tool | Load First | Commands |
|------|------------|----------|
| bgw_token_find | [`vendor/docs/market-data.md`](vendor/docs/market-data.md) | `search-tokens-v3`, `search-tokens`, `launchpad-tokens`, `rankings`, `historical-coins`, `get-token-list` |
| bgw_token_check | [`vendor/docs/market-data.md`](vendor/docs/market-data.md) | `coin-market-info`, `security`, `coin-dev`, `kline`, `tx-info`, `liquidity`, `token-info`, `token-price`, `batch-token-info` |
| bgw_token_analyze | [`vendor/docs/token-analyze.md`](vendor/docs/token-analyze.md) | `simple-kline`, `trading-dynamics`, `transaction-list`, `holders-info`, `profit-address-analysis`, `top-profit`, `compare-tokens` |
| bgw_address_find | [`vendor/docs/address-find.md`](vendor/docs/address-find.md) | `recommend-address-list` |
| Balance | [`vendor/docs/swap.md`](vendor/docs/swap.md) | `batch-v2` |
| Risk check | [`vendor/docs/swap.md`](vendor/docs/swap.md) | `check-swap-token` |
| RWA stock | [`vendor/docs/rwa.md`](vendor/docs/rwa.md) | `rwa-get-user-ticker-selector`, `rwa-stock-info`, `rwa-get-config`, `rwa-stock-order-price`, `rwa-kline`, `rwa-get-my-holdings` |
| Order status | [`vendor/docs/swap.md`](vendor/docs/swap.md) | `get-order-details` |
| Command ref | [`vendor/docs/commands.md`](vendor/docs/commands.md) | All subcommands and params |

All token discovery output **must** include **chain** and **contract address** for every token.

## Execution Flow — Swap (Bitget Order Mode)

**Load [`vendor/docs/swap.md`](vendor/docs/swap.md) before any swap.** It contains pre-trade check details, gasless thresholds, cross-chain limits, per-step response handling, and common pitfalls.

**Vendor docs override:** The vendor docs reference signing scripts (`order_sign.py`, `order_make_sign_send.py`, `social_order_make_sign_send.py`) and mnemonic/private-key workflows. **Ignore all of those.** Steps 6-7-8 below replace the vendor's signing with `purr wallet sign-transaction`. Everything else in the vendor docs (API params, response handling, thresholds, pitfalls) applies as-is.

1. `purr wallet address --chain-type ethereum` (or `solana`) → get wallet address
2. Vendor API `batch-v2` → verify fromToken balance + native gas balance
3. Vendor API `check-swap-token` → risk check both tokens
4. Vendor API `quote` → show **all** market results to user, recommend first
5. Vendor API `confirm` → pass `--feature no_gas` if native balance ≈ 0 (gasless, requires >= ~$5 USD), otherwise `--feature user_gas`. Display outAmount, minAmount, gasTotalAmount; check `recommendFeatures` in response to verify gas mode is viable. **Wait for user confirmation**
6. Vendor API `make-order` → unsigned txs to file (60s expiry!)
7. `purr wallet sign-transaction --txs-json "$(cat file)"` → sign txs to file
8. Vendor API `send --json-file` → submit signed txs
9. Vendor API `get-order-details` → check result
10. `purr wallet balance` → confirm result

**Steps 6-7-8 must complete within 60 seconds** (makeOrder expires). **Never copy makeOrder/sign hex data through the conversation — LLMs silently truncate long hex calldata strings, causing on-chain reverts that appear as "slippage" errors. Always redirect output to files and pipe between steps.**

```bash
# Steps 6-8 as one fast sequence:
cd ./skills/bitget-wallet/vendor

# 6. makeOrder → file (hex data stays out of conversation)
python3 bitget-wallet-agent-api.py make-order --order-id <id> \
  --from-chain bnb --from-contract <addr> --from-symbol USDT \
  --to-chain bnb --to-contract "" --to-symbol BNB \
  --from-address <wallet> --to-address <wallet> \
  --from-amount 5 --slippage 0.03 \
  --market <market_id> --protocol <protocol> > /tmp/bgw_order.json

# 7. Sign unsigned txs ($(cat) reads file in shell, not through LLM)
purr wallet sign-transaction --txs-json "$(cat /tmp/bgw_order.json)" > /tmp/bgw_signed.json

# 8. Send signed txs
python3 bitget-wallet-agent-api.py send --json-file /tmp/bgw_signed.json
```

`purr wallet sign-transaction` accepts raw makeOrder JSON (`{ data: { orderId, txs } }` or `{ orderId, txs }`), signs all txs, returns `{ orderId, txs, address }` with `sig` fields filled. Handles all modes: EVM raw tx, EIP-712, Solana Ed25519, gasPayMaster.

## Execution Flow — RWA Stock Trading

Load [`vendor/docs/rwa.md`](vendor/docs/rwa.md) first. Same swap flow with RWA-specific pre-trade steps:

1. `purr wallet address --chain-type ethereum` → EVM wallet
2. `purr wallet balance --chain-type ethereum --chain-id 56` → check USDT/USDC (min $20)
3. Vendor API `rwa-get-user-ticker-selector` → find stock ticker
4. Vendor API `rwa-stock-info` → check `market_status`, `tx_minimum_buy_usd`
5. Vendor API `rwa-get-config` → get stablecoin contracts
6. Vendor API `quote` → stablecoin↔RWA token
7. Steps 5-10 from swap flow (confirm → makeOrder → sign → send → check)

RWA trades produce 2 tx items (`approve` + `signTypeData`). Both signed by `purr wallet sign-transaction` automatically.

## Supported Chains

| Chain | Code | Chain ID | Explorer |
|-------|------|----------|----------|
| Ethereum | eth | 1 | `https://etherscan.io/tx/{txId}` |
| BNB Chain | bnb | 56 | `https://bscscan.com/tx/{txId}` |
| Base | base | 8453 | `https://basescan.org/tx/{txId}` |
| Arbitrum | arbitrum | 42161 | `https://arbiscan.io/tx/{txId}` |
| Polygon | matic | 137 | `https://polygonscan.com/tx/{txId}` |
| Morph | morph | 100283 | `https://explorer.morphl2.io/tx/{txId}` |
| Solana | sol | 100278 | `https://solscan.io/tx/{txId}` |
| Tron | trx | 728126428 | — |

Wallet types: `ethereum` (all EVM chains) and `solana`. No Tron wallet.

Use `""` for native token contract (ETH, SOL, BNB, etc.). All amounts are **human-readable** (e.g. `0.01` = 0.01 USDT), not wei/lamports.

## Common Stablecoins

| Chain | USDT | USDC |
|-------|------|------|
| Ethereum | `0xdAC17F958D2ee523a2206206994597C13D831ec7` | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| BNB Chain | `0x55d398326f99059fF775485246999027B3197955` | `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d` |
| Base | `0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Arbitrum | `0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9` | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |
| Polygon | `0xc2132D05D31c914a87C6611C10748AEb04B58e8F` | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| Solana | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |

## Failure Handling

| Error | Fix |
|-------|-----|
| "insufficient balance" | Check `purr wallet balance`, fund wallet first |
| "no route found" | No liquidity on this chain for the pair |
| "slippage exceeded" | Increase slippage or reduce amount |
| "approval failed" | ERC-20 approval reverted, check token contract |
| Cross-chain minimum $10 | Amount below cross-chain threshold |
| Gasless not available | Amount below ~$5 USD, use `user_gas` instead |
| makeOrder expired | Steps 6-7-8 took >60s, re-run from confirm |
| `error_code: 80000` | Wrong contract address, verify with `token-info` |
| `40001: Demo trading failed` | Usually insufficient balance — check balance first |
| Tron swap requested | Tron is **not supported** — no Tron wallet available. Suggest an alternative chain |
