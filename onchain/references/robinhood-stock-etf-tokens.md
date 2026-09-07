# Robinhood Stock/ETF Tokens

Use this reference when a user asks for trading Robinhood stock/ETF tokens,
including quoting, buying, selling, or swapping them on Robinhood Chain, looking
up Robinhood Chain stock token or tokenized ETF contract addresses, or checking
balances for one of those assets.

These addresses are for Robinhood Chain only.

## Chain

| Chain | Chain ID | Explorer |
| --- | ---: | --- |
| Robinhood Chain | 4663 | `https://robinhoodchain.blockscout.com` |

## Usage Notes

- Treat these as token contract references for Robinhood Chain, not stock
  trading advice.
- Use only the listed Robinhood Chain addresses; the same ticker on another
  address or chain is not canonical.
- The current `purr` CLI resolves these tickers on `--chain-id 4663` /
  `--chain robinhood` for balance, transfer, and `wallet uniswap` commands.
- Use raw addresses only when a tool path requires an address.

## Swap Workflow

Use `purr wallet uniswap` to quote or execute Robinhood Chain AMM swaps for
these stock/ETF tokens. The command quotes by default. Add `--execute` only
after the user confirms the quote.

1. Identify the source asset the wallet holds: native `ETH`, `WETH`, `USDG`,
   or one of the listed stock/ETF tokens.
2. Identify the target stock/ETF ticker from the tables below.
3. Run the quote command without `--execute`.
4. Show the estimated shares/tokenized shares, minimum shares/tokenized shares,
   route, and source amount to the user. The quote output is still an ERC-20
   token amount and can be fractional.
5. If the user confirms, rerun the same command with `--execute`.
6. Return the transaction hash, Robinhood Chain explorer link
   (`https://robinhoodchain.blockscout.com/tx/<tx_hash>`), and final token/ETH
   balance when execution succeeds.

## Swap Syntax

```bash
purr wallet uniswap --from <ticker_or_address> --to <ticker_or_address> --amount <decimal_amount> [--chain robinhood|--chain-id 4663] [--execute]
```

## Swap Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--from <ticker_or_address>` | Required | Source asset. Use `ETH`, `WETH`, `USDG`, a stock/ETF ticker, or a raw Robinhood Chain token address. |
| `--to <ticker_or_address>` | Required | Destination asset. Use `ETH`, `WETH`, `USDG`, a stock/ETF ticker, or a raw Robinhood Chain token address. |
| `--amount <decimal_amount>` | Required | Human-readable source amount, not wei/base units. For example, `5` USDG, `0.003` ETH, or `0.03` SPCX. |
| `--chain robinhood` | Recommended | Selects Robinhood Chain by alias. Use `--chain-id 4663` if an explicit numeric chain ID is preferred. |
| `--execute` | Optional | Executes the swap. Omit this flag for quote-only mode. |
| `--slippage <percent>` | Optional | Overrides backend default slippage. `0.5` means 0.5%; `1` means 1%. |
| `--min-amount-out <raw_amount>` | Optional | Advanced protection. Raw base-unit minimum output, usually not needed because execute requotes and applies slippage. |
| `--dedup-key <key>` | Optional | Advanced idempotency key. Omit for normal use so identical accidental reruns can be deduped by the backend. |

## Swap Commands

```bash
purr wallet uniswap --from USDG --to SPCX --amount 5 --chain robinhood          # quote 5 USDG -> SPCX
purr wallet uniswap --from USDG --to SPCX --amount 5 --chain robinhood --execute # execute after user confirmation
purr wallet uniswap --from ETH --to SPCX --amount 0.003 --chain robinhood       # quote native ETH -> SPCX
purr wallet uniswap --from SPCX --to ETH --amount 0.03 --chain robinhood        # quote SPCX -> native ETH
purr wallet uniswap --from SPCX --to ETH --amount 0.03 --chain robinhood --execute
purr wallet uniswap --from USDG --to SPY --amount 10 --chain-id 4663            # quote 10 USDG -> SPY
purr wallet uniswap --from SPCX --to AAPL --amount 0.01 --chain robinhood       # quote stock-to-stock via USDG
```

## Swap Response Shape

Quote mode prints one JSON object to stdout:

```json
{
  "provider": "uniswap",
  "chainId": 4663,
  "chainType": "ethereum",
  "from": "0x...",
  "fromToken": "0x0000000000000000000000000000000000000000",
  "toToken": "0x4a0E65A3EcceC6dBe60AE065F2e7bb85Fae35eEa",
  "fromAmount": "0.003",
  "fromAmountBaseUnits": "3000000000000000",
  "estimatedToAmountFormatted": "0.031",
  "minimumToAmountFormatted": "0.030845",
  "minimumToAmount": "30845000000000000",
  "quoteSource": "amm",
  "ammRoute": {
    "protocol": "router",
    "steps": []
  }
}
```

Execute mode returns the same quote fields plus transaction fields:

```json
{
  "mode": "transaction",
  "hash": "0x...",
  "transactionId": "..."
}
```

## Swap Response Errors

| Error Message | Meaning |
| --- | --- |
| `Unknown token ...` | The ticker is not in the local registry for Robinhood Chain. Use a supported ticker from this file or a raw address. |
| `purr wallet uniswap currently supports Robinhood Chain only` | The command was called with a chain other than Robinhood Chain. Use `--chain robinhood` or `--chain-id 4663`. |
| `Latest Uniswap quote is below minAmountOut` | The quote moved below the requested minimum before execution. Requote and ask the user to confirm again. |
| `Insufficient balance` | The wallet does not have enough source asset or native ETH for gas. |
| `No route found` | No AMM route is currently available for the requested pair/amount. |

## Stock Tokens

| Ticker | Name | Token Address |
| --- | --- | --- |
| AAPL | Apple | `0xaF3D76f1834A1d425780943C99Ea8A608f8a93f9` |
| AMD | AMD | `0x86923f96303D656E4aa86D9d42D1e57ad2023fdC` |
| AMZN | Amazon | `0x12f190a9F9d7D37a250758b26824B97CE941bF54` |
| BABA | Alibaba | `0xad25Ac6C84D497db898fa1E8387bf6Af3532a1c4` |
| BE | Bloom Energy | `0x822CC93fFD030293E9842c30BBD678F530701867` |
| COIN | Coinbase | `0x6330D8C3178a418788dF01a47479c0ce7CCF450b` |
| CRCL | Circle Internet Group | `0xdF0992E440dD0be65BD8439b609d6D4366bf1CB5` |
| CRWV | CoreWeave | `0x5f10A1C971B69e47e059e1dC91901B59b3fB49C3` |
| GOOGL | Alphabet Class A | `0x2e0847E8910a9732eB3fb1bb4b70a580ADAD4FE3` |
| INTC | Intel | `0xc72b96e0E48ecd4DC75E1e45396e26300BC39681` |
| META | Meta Platforms | `0xc0D6457C16Cc70d6790Dd43521C899C87ce02f35` |
| MSFT | Microsoft | `0xe93237C50D904957Cf27E7B1133b510C669c2e74` |
| MU | Micron Technology | `0xfF080c8ce2E5feadaCa0Da81314Ae59D232d4afD` |
| NVDA | NVIDIA | `0xd0601CE157Db5bdC3162BbaC2a2C8aF5320D9EEC` |
| ORCL | Oracle | `0xb0992820E760d836549ba69BC7598b4af75dEE03` |
| PLTR | Palantir Technologies | `0x894E1EC2D74FFE5AEF8Dc8A9e84686acCB964F2A` |
| SNDK | Sandisk Corporation | `0xB90A19fF0Af67f7779afF50A882A9CfF42446400` |
| SPCX | Space Exploration Technologies Corp | `0x4a0E65A3EcceC6dBe60AE065F2e7bb85Fae35eEa` |
| TSLA | Tesla | `0x322F0929c4625eD5bAd873c95208D54E1c003b2d` |
| USAR | USA Rare Earth | `0xd917B029C761D264c6A312BBbcDA868658eF86a6` |

## Tokenized ETFs

| Ticker | Name | Token Address |
| --- | --- | --- |
| QQQ | Invesco QQQ | `0xD5f3879160bc7c32ebb4dC785F8a4F505888de68` |
| SGOV | iShares 0-3 Month Treasury Bond ETF | `0x92FD66527192E3e61d4DDd13322Aa222DE86F9B5` |
| SLV | iShares Silver Trust | `0x411eFb0E7f985935DAec3D4C3ebaEa0d0AD7D89f` |
| SPY | SPDR S&P 500 ETF Trust | `0x117cc2133c37B721F49dE2A7a74833232B3B4C0C` |
| USO | United States Oil Fund | `0xa30FA36Db767ad9eD3f7a60fC79526fB4d56D344` |

## Examples

```bash
purr wallet balance --chain-id 4663 --token NVDA
purr wallet balance --chain-id 4663 --token SPY
purr wallet balance --chain-id 4663 --token 0xd0601CE157Db5bdC3162BbaC2a2C8aF5320D9EEC  # raw NVDA address
```
