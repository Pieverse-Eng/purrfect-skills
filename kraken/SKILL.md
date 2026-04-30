---
name: kraken
description: Kraken exchange — spot/xStocks/forex trading, market data, earn/staking, funding, and paper trading via the kraken CLI.
metadata:
  openclaw:
    primaryEnv: KRAKEN_API_KEY
---

## Setup / Pre-flight Checks

Before using this skill, verify the `kraken` CLI is available:

```bash
if command -v kraken &>/dev/null; then
  echo "kraken CLI is available"
else
  echo "kraken CLI is NOT available"
fi
```

If it is **not available**, install it:

```bash
curl -sL https://github.com/krakenfx/kraken-cli/releases/download/v0.2.0/kraken-cli-x86_64-unknown-linux-gnu.tar.gz \
  | tar xz --strip-components=1 -C /usr/local/bin/ \
  && chmod +x /usr/local/bin/kraken \
  && kraken --version \
  && echo "Kraken CLI installed"
```

For local development or non-x86_64 platforms, download the appropriate release from https://github.com/krakenfx/kraken-cli/releases and place the `kraken` binary on your `PATH`.

**API credentials**: `KRAKEN_API_KEY` and `KRAKEN_API_SECRET` must be set.
```bash
[ -n "${KRAKEN_API_KEY:-}" ] && [ -n "${KRAKEN_API_SECRET:-}" ] || echo "Warning: KRAKEN_API_KEY and KRAKEN_API_SECRET not set. Trading will fail."
```
If not set, ask the user to provide their Kraken API credentials. They can create keys at https://www.kraken.com/u/security/api. Do not proceed with trading operations until credentials are configured.

# Kraken Exchange

Trade crypto, tokenized stocks, and forex on Kraken via the `kraken` CLI. Supports spot trading, paper trading, earn/staking, and funding operations.

## Scope

- In scope: Spot trading (1,400+ crypto pairs), xStocks (79 tokenized US equities), forex (11 fiat pairs), earn/staking, funding (deposit/withdraw), paper trading, market data
- Futures: Supported if user provides separate futures API keys
- Out of scope: Kraken account creation (user must already have a Kraken account)

## Credentials

The user must provide two values. Ask the user directly if you don't have them:

| Credential | Env Var | Description |
|------------|---------|-------------|
| **API Key** | `KRAKEN_API_KEY` | From kraken.com Settings > API |
| **API Secret** | `KRAKEN_API_SECRET` | From kraken.com Settings > API |

For futures trading (optional, separate key pair):

| Credential | Env Var | Description |
|------------|---------|-------------|
| **Futures API Key** | `KRAKEN_FUTURES_API_KEY` | From Kraken Futures Settings > Create Key |
| **Futures API Secret** | `KRAKEN_FUTURES_API_SECRET` | From Kraken Futures Settings > Create Key |

Once you have the credentials, prefix every authenticated command with the env vars:

```bash
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" kraken <command> -o json
```

For read-only market data and paper trading commands, no credentials are needed.

## Runtime Requirements

- The `kraken` CLI must be installed and available on `PATH` (platform images have it at `/usr/local/bin/kraken`)
- For local development: install the same `kraken` CLI release, then expose it on `PATH`
- No other dependencies (single static binary)

## Output Format

Always pass `-o json` for machine-readable output. The CLI also supports `-o table` for human-readable display if the user wants formatted output.

## Error Handling

All errors return structured JSON: `{"error": "<category>", "message": "<detail>"}`.

| Error | Retryable | Action |
|-------|-----------|--------|
| `auth` | No | Check credentials |
| `rate_limit` | Yes | Wait and retry (response includes `suggestion` field) |
| `network` | Yes | Retry with backoff |
| `validation` | No | Fix input parameters |
| `api` | No | Inspect request |

## CLI Variable

All examples below use `$KRAKEN` to refer to the CLI binary:

```bash
KRAKEN=kraken
```

## Read Path — Market Data (No Auth)

```bash
# Price ticker
$KRAKEN ticker BTCUSD -o json

# OHLC candlestick data (interval: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
$KRAKEN ohlc BTCUSD --interval 60 -o json

# Order book (L2)
$KRAKEN orderbook BTCUSD --count 10 -o json

# Recent trades
$KRAKEN trades BTCUSD -o json

# Bid-ask spread history
$KRAKEN spreads BTCUSD -o json

# List all assets
$KRAKEN assets -o json

# List trading pairs (filter with --pair)
$KRAKEN pairs -o json
$KRAKEN pairs --pair BTCUSD -o json

# System status
$KRAKEN status -o json
```

## Read Path — Account (Auth Required)

```bash
# Account balance (all assets)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN balance -o json

# Extended balance (with hold amounts)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN extended-balance -o json

# Open orders
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN open-orders -o json

# Closed orders
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN closed-orders -o json

# Trade history
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN trades-history -o json

# Query specific order by txid
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN query-orders --txid <ORDER_TXID> -o json

# Open margin positions
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN positions -o json

# Ledger history
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN ledgers -o json

# Trade volume and fees
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN volume -o json
```

## Execution Flow — Spot Market Order

1. Check price: `$KRAKEN ticker <PAIR> -o json`
2. Check balance: `$KRAKEN balance -o json` (with auth env vars)
3. Show order details and ask for confirmation
4. Execute:

```bash
# Market buy — positional args: PAIR VOLUME
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order buy BTCUSD 0.001 --type market -o json

# Market sell
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order sell BTCUSD 0.001 --type market -o json
```

5. Confirm fill from response

## Execution Flow — Spot Limit Order

1. Check price and orderbook for appropriate price level
2. Show order details and ask for confirmation
3. Execute:

```bash
# Limit buy (default order type is limit)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order buy BTCUSD 0.001 --price 95000 -o json

# Limit sell
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order sell BTCUSD 0.001 --price 105000 -o json
```

## Execution Flow — Stop-Loss / Take-Profit

```bash
# Stop-loss (triggers market sell when price drops to stop price)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order sell BTCUSD 0.001 --type stop-loss --price 90000 -o json

# Take-profit (triggers market sell when price rises to take-profit price)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order sell BTCUSD 0.001 --type take-profit --price 110000 -o json

# Stop-loss-limit (triggers limit order at --price when stop hits --price2)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order sell BTCUSD 0.001 --type stop-loss-limit --price 89500 --price2 90000 -o json
```

## Execution Flow — Manage Orders

```bash
# Cancel order
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order cancel --txid <ORDER_TXID> -o json

# Cancel all open orders
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order cancel-all -o json

# Edit order (cancel+replace, preserves nothing)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order edit --txid <ORDER_TXID> BTCUSD 0.002 --price 96000 -o json

# Amend order (in-place, preserves queue priority)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order amend --txid <ORDER_TXID> BTCUSD 0.002 --price 96000 -o json

# Dead man's switch — cancel all orders after N seconds (0 to disable)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order cancel-after 60 -o json
```

## Execution Flow — xStocks (Tokenized US Equities)

xStocks are tokenized versions of US stocks and ETFs. Pairs use `x` suffix (e.g., `AAPLx/USD`).

**IMPORTANT — flag mismatch:** The `pairs` command uses `--aclass` (NOT `--asset-class`). All other commands (`ticker`, `order`) use `--asset-class`. Using the wrong flag causes a CLI error.

```bash
# List xStock pairs (note: pairs uses --aclass, not --asset-class)
$KRAKEN pairs --aclass tokenized_asset -o json

# Price
$KRAKEN ticker AAPLx/USD --asset-class tokenized_asset -o json

# Buy (market)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order buy AAPLx/USD 1 --type market --asset-class tokenized_asset -o json

# Sell (limit)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order sell AAPLx/USD 1 --price 200 --asset-class tokenized_asset -o json
```

## Execution Flow — Forex

**Same flag mismatch as xStocks:** `pairs` uses `--aclass`, other commands use `--asset-class`.

```bash
# List forex pairs (MUST use --aclass, not --asset-class)
$KRAKEN pairs --aclass forex -o json

# Price
$KRAKEN ticker EURUSD --asset-class forex -o json

# Trade
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN order buy EURUSD 100 --type market --asset-class forex -o json
```

## Execution Flow — Earn / Staking

```bash
# List earn strategies (filter by asset or lock type)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN earn strategies -o json
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN earn strategies --asset ETH -o json
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN earn strategies --lock-type flex -o json

# Current allocations
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN earn allocations -o json

# Allocate (stake) — positional args: STRATEGY_ID AMOUNT
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN earn allocate <STRATEGY_ID> 10 -o json

# Deallocate (unstake)
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN earn deallocate <STRATEGY_ID> 10 -o json

# Check allocation/deallocation status
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN earn allocate-status -o json
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN earn deallocate-status -o json
```

## Execution Flow — Funding (Deposit / Withdraw)

### Deposit (External → Kraken)

```bash
# Get deposit methods for an asset
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN deposit methods BTC -o json

# Get deposit address — positional args: ASSET METHOD
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN deposit addresses BTC Bitcoin -o json

# Check deposit status
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN deposit status -o json
```

To deposit from the instance's platform wallet to Kraken:
1. Get deposit address with the command above
2. Use `wallet_transfer` tool to send from the platform wallet to the Kraken deposit address
3. Monitor deposit status with the deposit status command

### Withdraw (Kraken → External)

```bash
# Get withdrawal methods
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN withdrawal methods BTC -o json

# Withdraw — positional args: ASSET KEY AMOUNT
# KEY is a pre-configured withdrawal address name on Kraken
KRAKEN_API_KEY="<key>" KRAKEN_API_SECRET="<secret>" \
  $KRAKEN withdraw BTC <ADDRESS_NAME> 0.01 -o json
```

## Execution Flow — Paper Trading (Safe Testing)

Paper trading uses live market prices with simulated execution. No real money. No auth required.

**Must initialize first:**

```bash
# Initialize paper account (10,000 USD default, 0.26% fee)
$KRAKEN paper init -o json

# Reset paper account (optional: override balance/currency/fee)
$KRAKEN paper reset -o json
$KRAKEN paper reset --balance 50000 --currency EUR --fee-rate 0.001 -o json
```

**Trading:**

```bash
# Paper market buy — positional args: PAIR VOLUME
$KRAKEN paper buy BTCUSD 0.001 --type market -o json

# Paper limit buy
$KRAKEN paper buy BTCUSD 0.001 --type limit --price 95000 -o json

# Paper sell
$KRAKEN paper sell BTCUSD 0.001 --type market -o json

# Paper balance
$KRAKEN paper balance -o json

# Paper open orders (limit orders waiting to fill)
$KRAKEN paper orders -o json

# Paper trade history
$KRAKEN paper history -o json

# Paper account summary with P&L
$KRAKEN paper status -o json

# Paper cancel order
$KRAKEN paper cancel <PAPER_ORDER_ID> -o json

# Paper cancel all
$KRAKEN paper cancel-all -o json
```

Paper mode simulates a 0.26% taker fee. Use it first when testing new strategies.

## Execution Flow — Futures (Optional, Separate Keys)

Requires `KRAKEN_FUTURES_API_KEY` and `KRAKEN_FUTURES_API_SECRET`.

```bash
# List futures instruments
$KRAKEN futures instruments -o json

# Futures tickers (all)
$KRAKEN futures tickers -o json

# Futures ticker (single)
$KRAKEN futures ticker PF_XBTUSD -o json

# Futures orderbook
$KRAKEN futures orderbook PF_XBTUSD -o json

# Futures account info (margin, PnL)
KRAKEN_FUTURES_API_KEY="<key>" KRAKEN_FUTURES_API_SECRET="<secret>" \
  $KRAKEN futures accounts -o json

# Futures positions
KRAKEN_FUTURES_API_KEY="<key>" KRAKEN_FUTURES_API_SECRET="<secret>" \
  $KRAKEN futures positions -o json

# Place futures order — positional args: SYMBOL SIZE
KRAKEN_FUTURES_API_KEY="<key>" KRAKEN_FUTURES_API_SECRET="<secret>" \
  $KRAKEN futures order buy PF_XBTUSD 1 --type market -o json

KRAKEN_FUTURES_API_KEY="<key>" KRAKEN_FUTURES_API_SECRET="<secret>" \
  $KRAKEN futures order sell PF_XBTUSD 1 --price 100000 -o json

# Set leverage
KRAKEN_FUTURES_API_KEY="<key>" KRAKEN_FUTURES_API_SECRET="<secret>" \
  $KRAKEN futures set-leverage PF_XBTUSD 10 -o json

# Cancel futures order
KRAKEN_FUTURES_API_KEY="<key>" KRAKEN_FUTURES_API_SECRET="<secret>" \
  $KRAKEN futures cancel --order-id <ORDER_ID> -o json

# Cancel all futures orders
KRAKEN_FUTURES_API_KEY="<key>" KRAKEN_FUTURES_API_SECRET="<secret>" \
  $KRAKEN futures cancel-all -o json

# Transfer between spot and futures wallets
KRAKEN_FUTURES_API_KEY="<key>" KRAKEN_FUTURES_API_SECRET="<secret>" \
  $KRAKEN futures transfer --from spot --to futures --amount 100 --currency USD -o json
```

## Pair Format Reference

| Asset Class | Format | Example |
|-------------|--------|---------|
| Crypto spot | `BASEQUOTE` or `BASE/QUOTE` | `BTCUSD`, `ETH/USD`, `SOLUSD` |
| xStocks | `SYMBOLx/USD` | `AAPLx/USD`, `TSLAx/USD` |
| Forex | `BASEQUOTE` | `EURUSD`, `GBPUSD` |
| Perpetual futures | `PF_BASEQUOTE` | `PF_XBTUSD`, `PF_ETHUSD` |

## Confirmation Contract (Mandatory)

Before ANY trade execution (buy, sell, allocate, deallocate, withdraw), show:

- Action (buy/sell/allocate/etc.)
- Pair or asset
- Volume/amount
- Order type (market/limit/stop-loss)
- Price (if limit/stop)
- Asset class (if non-default)

Then ask: `Do you want to execute this order? (Yes/No)`

- If user says Yes: execute.
- If user says No: do not execute; offer edit or cancel.
- If any parameter changes: ask again.

Paper trades do NOT require confirmation (no real money at risk).

## Failure Handling

| Error | Fix |
|-------|-----|
| `auth` error | Credentials are wrong — user must check API key/secret |
| `rate_limit` with suggestion | Wait as suggested, then retry |
| `validation` error | Fix input (wrong pair format, invalid volume, etc.) |
| "insufficient funds" | Check balance, deposit more first |
| "unknown pair" | Verify pair format — use `pairs` to discover valid pairs |
| "permission denied" | API key may lack required permissions (e.g., trading, withdrawal) |
| "Paper account not initialized" | Run `$KRAKEN paper init` first |
