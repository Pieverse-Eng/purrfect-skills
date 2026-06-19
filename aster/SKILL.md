---
name: aster
description: Aster futures API,market data,trading,account,deposits
metadata:
  openclaw:
    primaryEnv: ASTER_USER_WALLET
---

# Aster DEX (Perpetual Futures)

Interact with Aster DEX for perpetual futures trading. Authenticated API calls are signed by the authorized Aster Pro API wallet.

## Scope

- In scope: Futures market data, trading, account management, futures↔spot transfers, on-chain Aster deposits via `purr aster deposit`
- Out of scope: On-chain withdrawals, spot trading execution, account creation (user must already have an Aster futures account)

## Credentials

The user must provide the main Aster login wallet address. Ask the user directly if you don't have it:

| Credential | Description |
|------------|-------------|
| **User wallet address** | The main wallet the user logged into Aster with |

If the user hasn't set up Aster yet, they need to:
1. Open an Aster futures account at asterdex.com
2. Run `purr wallet address --chain-type ethereum --chain-id 56` to get the Pieverse agent EVM wallet address
3. In Aster API Management → Pro API, authorize that address as an API wallet with the needed permissions
4. Provide the main Aster login wallet address

Once you have the user wallet address, pass it to `purr aster api` via `--user`. The CLI derives the signer from the Pieverse managed wallet automatically. Use `--signer <API_WALLET_ADDRESS>` only when you want to assert the expected signer during debugging.

## Assistant Behavior

- For authenticated Aster API requests, ask for the main Aster login wallet only when missing. Do not ask the user for an API wallet signer or a private key.
- Omit `--signer` in normal `purr aster api` commands. The CLI derives the signer from the Pieverse managed wallet; use `--signer` only as a debugging assertion.
- For trade, transfer, deposit execution, and any other write action, show the concrete action details and ask for explicit confirmation before broadcasting or sending the signed request.
- If Pro API authorization is missing, tell the user to authorize the Pieverse agent EVM wallet from `purr wallet address --chain-type ethereum --chain-id 56`; Aster may return `-1000 No agent found` until that wallet is authorized for the provided `--user` account.

## How Authentication Works — IMPORTANT

**Always use `purr aster api` for ALL authenticated calls.** It builds the signing payload, asks the Pieverse managed wallet to sign as the authorized Aster API wallet, and calls fapi.asterdex.com in one shot. One command, done.

**DO NOT** use the vendor's `aster_api.py build-sign-request` / `signed-request` 2-step flow, ask for the Pieverse wallet private key, or attempt manual signing. Those exist in the vendor directory as reference but `purr` replaces them entirely with a simpler workflow. Ignore `vendor/futures-auth/SKILL.md` for implementation — use it only if you need to understand the protocol for debugging.

## Runtime Requirements

- `python3` is available in the instance runtime
- The vendor client is at `./skills/aster/vendor/aster_api.py` (market data only)
- `purr` CLI is at `/usr/local/bin/purr` (authenticated calls)

## Read Path — Market Data (No Auth)

Use the vendor client directly for public data:

```bash
cd ./skills/aster/vendor
python3 aster_api.py ticker --symbol BTCUSDT
python3 aster_api.py ticker-24hr --symbol BTCUSDT
python3 aster_api.py depth --symbol BTCUSDT --limit 5
python3 aster_api.py klines --symbol BTCUSDT --interval 1h --limit 10
python3 aster_api.py premium-index --symbol BTCUSDT
python3 aster_api.py funding-rate --symbol BTCUSDT
python3 aster_api.py funding-info --symbol BTCUSDT
python3 aster_api.py trades --symbol BTCUSDT --limit 20
python3 aster_api.py exchange-info
python3 aster_api.py server-time
python3 aster_api.py book-ticker --symbol BTCUSDT
```

See `vendor/futures-market-data/SKILL.md` for full endpoint reference.

## Write Path — Authenticated API Calls

Use `purr aster api` for ALL authenticated endpoints. It handles signing automatically:

```bash
purr aster api --endpoint /fapi/v3/balance \
  --user <USER_WALLET>
```

For endpoints with extra params, add them as flags:

```bash
purr aster api --method POST --endpoint /fapi/v3/order \
  --user <USER_WALLET> \
  --symbol BTCUSDT --side BUY --type LIMIT \
  --quantity 0.001 --price 50000 --timeInForce GTC
```

Returns raw JSON from fapi.asterdex.com.

## Deposit Path — On-chain Deposits

Use `vendor/deposit-fund/reference.md` for the full deposit workflow. Deposits use `purr aster deposit`, not `purr aster api`. Run the command without `--execute` first to preview the generated steps.

Preview first:

```bash
purr aster deposit \
  --token <token_ticker_or_address> \
  --amount-wei <amount_wei> \
  --wallet <wallet_address> \
  --chain-id <1|56|42161>
```

Show the token, raw amount, funding wallet, source chain, broker ID, and any approval step. Ask for explicit confirmation before execution.

After confirmation, rerun the same command with `--execute`:

```bash
purr aster deposit \
  --token <token_ticker_or_address> \
  --amount-wei <amount_wei> \
  --wallet <wallet_address> \
  --chain-id <1|56|42161> \
  --execute
```

## Execution Flow — Check Account Balance

```bash
purr aster api --endpoint /fapi/v3/balance \
  --user <USER_WALLET>
```

## Execution Flow — Place Order

1. Get price: `cd ./skills/aster/vendor && python3 aster_api.py ticker --symbol BTCUSDT`
2. Show order details and ask for confirmation
3. Place order:
```bash
purr aster api --method POST --endpoint /fapi/v3/order \
  --user <USER_WALLET> \
  --symbol BTCUSDT --side BUY --type LIMIT \
  --quantity 0.001 --price 50000 --timeInForce GTC
```
4. Parse response and confirm fill

## Execution Flow — Set Leverage

```bash
purr aster api --method POST --endpoint /fapi/v3/leverage \
  --user <USER_WALLET> \
  --symbol BTCUSDT --leverage 10
```

## Execution Flow — Cancel Order

```bash
purr aster api --method DELETE --endpoint /fapi/v3/order \
  --user <USER_WALLET> \
  --symbol BTCUSDT --orderId 123456
```

## Execution Flow — Query Positions

```bash
purr aster api --endpoint /fapi/v3/positionRisk \
  --user <USER_WALLET> \
  --symbol BTCUSDT
```

## Execution Flow — Futures↔Spot Transfer

```bash
purr aster api --method POST --endpoint /fapi/v3/asset/wallet/transfer \
  --user <USER_WALLET> \
  --amount 10 --asset USDT --clientTranId <unique-id> --kindType FUTURE_SPOT
```

`kindType`: `FUTURE_SPOT` (futures→spot) or `SPOT_FUTURE` (spot→futures). `clientTranId` must be unique per transfer.

## Order Types

| Type | Required Params |
|------|----------------|
| LIMIT | timeInForce, quantity, price |
| MARKET | quantity |
| STOP | quantity, price, stopPrice |
| STOP_MARKET | stopPrice |
| TAKE_PROFIT | quantity, price, stopPrice |
| TAKE_PROFIT_MARKET | stopPrice |
| TRAILING_STOP_MARKET | callbackRate (0.1-5) |

## Confirmation Contract (Mandatory)

Before ANY order execution, show:
- Symbol, Side (BUY/SELL), Type, Quantity, Price (if applicable), Leverage

Then ask: `Do you want to place this order? (Yes/No)`

## Parameter Rules

- All param values MUST be strings (e.g. `"10"` not `10`)
- Symbol: uppercase, no separator (e.g. `"BTCUSDT"`)
- Quantity/Price: string decimals (e.g. `"0.001"`, `"50000.00"`)

## Vendor Skills Reference

The vendor directory contains API endpoint documentation. Use these as reference for endpoint params and response shapes — but always call endpoints through `purr aster api`, never through the vendor's `build-sign-request`/`signed-request` flow.

| Skill | Purpose |
|-------|---------|
| `vendor/futures-market-data/` | Public REST endpoints (no auth) — use `aster_api.py` directly |
| `vendor/futures-account/` | Balance, positions, leverage, margin endpoint reference |
| `vendor/futures-trading/` | Order placement, cancellation, query endpoint reference |
| `vendor/futures-errors/` | Error codes, rate limits, retry logic |
| `vendor/futures-auth/` | Signing protocol reference (DO NOT implement — `purr` handles this) |
| `vendor/futures-websocket/` | Futures websocket stream reference |
| `vendor/spot-market-data/` | Spot public market data endpoint reference |
| `vendor/spot-account/` | Spot account endpoint reference |
| `vendor/spot-trading/` | Spot order placement, cancellation, query endpoint reference |
| `vendor/spot-auth/` | Spot signing protocol reference |
| `vendor/spot-errors/` | Spot error codes, rate limits, retry logic |
| `vendor/spot-websocket/` | Spot websocket stream reference |
| `vendor/deposit-fund/` | Aster deposit workflow reference |

These folders are reference material. Do not claim `purr` supports spot or
websocket execution commands unless that CLI surface exists.

## Failure Handling

- `-1000 No agent found`: The Pieverse managed wallet is not authorized for the `--user` Aster account, or the wrong main wallet address was used
- `-1021 INVALID_TIMESTAMP`: Server time drift — use `python3 aster_api.py server-time` to check
- `-1022 INVALID_SIGNATURE`: Signing format error — verify credentials are correct
- `-2019 MARGIN_NOT_SUFFICIENT`: Not enough margin
- `-4047/-4048 MARGIN_TYPE_ERROR`: Cannot change margin with open positions/orders
