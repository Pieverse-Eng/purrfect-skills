---
name: binance
description: Use binance-cli for Binance Spot, Futures (USD-S), and Convert. Requires auth.
metadata:
  version: 1.2.0
  author: Binance
  pieverse:
    marketSearch: true
    tradeReady:
      env:
        - [BINANCE_API_KEY, BINANCE_SECRET_KEY]
  openclaw:
    requires:
      bins:
        - binance-cli
    install:
      - kind: node
        package: '@binance/binance-cli'
        bins: [binance-cli]
        label: Install binance-cli (npm)
license: MIT
---

# Binance

Use `binance-cli` for Binance Spot, Futures (USD-S), and Convert. Requires auth.

## Market Search

For a host-provided read-only market-search request, use this section directly.
Do not load a reference skill. Binance Market Search covers Spot and USDⓈ-M
USDT perpetual futures.

- Public market data does not require credentials. Run one
  `binance-cli` command per tool call, without pipes, redirects, variables,
  command substitution, or command chaining.
- Derive a short canonical base ticker. For Spot, verify the exact candidate
  with `binance-cli spot ticker-price --symbol <BASE><QUOTE>`. For a USDT
  perpetual, use
  `binance-cli futures-usds symbol-price-ticker --symbol <BASE>USDT`.
- For a stock or tokenized-equity Spot request, do not conclude that Binance
  has no listing from a failed lookup of `<TICKER><QUOTE>`. Run
  `binance-cli spot exchange-info --symbol-status TRADING` once to read the
  live Spot catalog. The result can be retained or truncated; search its exact
  result handle with `read_tool_result` using the canonical ticker and issuer
  name. Inspect matching `symbol`, `baseAsset`, `quoteAsset`, `status`, and
  Spot trading permission fields. Binance stock-token base assets may add a
  venue-specific marker such as a trailing `B`; treat that only as a candidate
  hint and verify the underlying from Binance-provided metadata.
- Accept a candidate only when the command returns a JSON object whose `symbol`
  exactly equals the requested symbol and whose `price` is numeric. Plain-text
  `Invalid symbol.`, an error response, or a different symbol is not a listing,
  regardless of the process exit code.
- Do not run an unfiltered catalog except for the stock Spot discovery case
  above. In particular, do not run
  `binance-cli futures-usds exchange-information` or
  `binance-cli futures-usds futures-tradfi-perps-contract` for market search.
  Never shell-filter a complete Binance catalog or rerun it after receiving a
  retained result handle.
- After verifying a Spot pair, retrieve exactly the bounded candle windows
  needed by the host:
  - `binance-cli spot klines --symbol <SYMBOL> --interval 15m --limit 20`
  - `binance-cli spot klines --symbol <SYMBOL> --interval 1h --limit 20`
  - `binance-cli spot klines --symbol <SYMBOL> --interval 4h --limit 20`
- After verifying a perpetual, retrieve:
  - `binance-cli futures-usds kline-candlestick-data --symbol <SYMBOL> --interval 15m --limit 20`
  - `binance-cli futures-usds kline-candlestick-data --symbol <SYMBOL> --interval 1h --limit 20`
  - `binance-cli futures-usds kline-candlestick-data --symbol <SYMBOL> --interval 4h --limit 20`
- Return the venue-provided latest candle as the final element. Do not infer
  candles or listing identity from a different symbol.

### Market Cost

- Retrieve bounded Spot depth with
  `binance-cli spot depth --symbol <SYMBOL> --limit 100`, or USDT-perpetual
  depth with
  `binance-cli futures-usds order-book --symbol <SYMBOL> --limit 100`.
- Binance's official regular-user base taker fee is `0.1%` for Spot and
  `0.05%` for USDⓈ-M USDT futures. Pass `takerFeeBps: "10"` for Spot or
  `takerFeeBps: "5"` for the perpetual. Exclude BNB-payment discounts, VIP
  rates, referral rebates, and promotional pair discounts.
- Fee sources: `https://www.binance.com/en/fee/trading` and
  `https://www.binance.com/en/fee/futureFee`. Pass
  `additionalFeeBps: "0"`.
- Spot and linear USDⓈ-M book sizes are base-asset quantities; pass
  `baseSizePerUnit: "1"` only after the exact symbol and product have been
  verified.

> **PREREQUISITE:** Read [`auth.md`](./references/auth.md) for auth, global flags, and security rules.

## Helper Commands

| Command | Description |
|---------|-------------|
| [`algo`](./references/algo.md) | Algo Trading |
| [`alpha`](./references/alpha.md) | Alpha |
| [`c2c`](./references/c2c.md) | C2C |
| [`convert`](./references/convert.md) | Convert |
| [`copy-trading`](./references/copy-trading.md) | Copy Trading |
| [`crypto-loan`](./references/crypto-loan.md) | Crypto Loan |
| [`derivatives-options`](./references/derivatives-options.md) | Derivatives Trading (Options) |
| [`derivatives-portfolio-margin`](./references/derivatives-portfolio-margin.md) | Derivatives Trading (Portfolio Margin) |
| [`derivatives-portfolio-margin-streams`](./references/derivatives-portfolio-margin-streams.md) | Derivatives Trading Streams (Portfolio Margin) |
| [`derivatives-portfolio-margin-pro`](./references/derivatives-portfolio-margin-pro.md) | Derivatives Trading (Portfolio Margin Pro) |
| [`derivatives-portfolio-margin-pro-streams`](./references/derivatives-portfolio-margin-pro-streams.md) | Derivatives Trading Streams (Portfolio Margin Pro) |
| [`dual-investment`](./references/dual-investment.md) | Dual Investment |
| [`fiat`](./references/fiat.md) | Fiat |
| [`futures-coin`](./references/futures-coin.md) | Derivatives Trading (COIN-M Futures) |
| [`futures-coin-streams`](./references/futures-coin-streams.md) | Derivatives Trading Streams (COIN-M Futures) |
| [`futures-usds`](./references/futures-usds.md) | Derivatives Trading (USDS-M Futures) |
| [`futures-usds-streams`](./references/futures-usds-streams.md) | Derivatives Trading Streams (USDS-M Futures) |
| [`gift-card`](./references/gift-card.md) | Gift Card |
| [`margin-trading`](./references/margin-trading.md) | Margin Trading |
| [`margin-trading-streams`](./references/margin-trading-streams.md) | Margin Trading Streams |
| [`mining`](./references/mining.md) | Mining |
| [`pay`](./references/pay.md) | Pay |
| [`rebate`](./references/rebate.md) | Rebate |
| [`simple-earn`](./references/simple-earn.md) | Simple Earn |
| [`spot`](./references/spot.md) | Spot Trading |
| [`spot-streams`](./references/spot-streams.md) | Spot Trading Streams |
| [`staking`](./references/staking.md) | Staking |
| [`sub-account`](./references/sub-account.md) | Sub Account |
| [`vip-loan`](./references/vip-loan.md) | VIP Loan |
| [`wallet`](./references/wallet.md) | Wallet |

## Notes

- ⚠️ **Prod transactions** — always ask user to type `CONFIRM` before executing.
- Install binance-cli using `npm install -g @binance/binance-cli`
- Use `--help` to get the list of commands and parameters.
- Use the output from both stdout and stderr.
- Append `--profile <name>` to any command to use a non-active profile.
- All authenticated endpoints accept optional `--recvWindow <ms>` (max 60 000).
- Timestamps (`startTime`, `endTime`) are Unix ms.
- For endpoints not listed in the skill, use `binance-cli request (GET|POST|PUT...) <url> [--signed]`. Any Parameters can be added to the request (e.g: `--param1 value --param2 value`).
