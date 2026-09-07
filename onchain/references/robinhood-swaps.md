# Robinhood Chain Token Swaps

Use `purr wallet uniswap` to quote, buy, sell, or swap Robinhood Chain tokens
through the hosted wallet. This includes stock/ETF tokens, memecoins, and other
ERC-20 tokens with a supported route. The command quotes by default;
`--execute` submits a transaction after user confirmation.

## Select the assets

- Always specify `--chain robinhood` or `--chain-id 4663`.
- Use `ETH` for native ETH, or registered tickers such as `WETH` and `USDG`.
- For stock/ETF ticker lookup, use the
  [stock/ETF address directory](robinhood-stock-etf-tokens.md).
- For other tokens, use the exact Robinhood Chain contract address in
  `--from` or `--to`. A token does not need to appear in the stock directory
  or CLI ticker registry to be quoted by address.
- If the caller supplies only an unregistered token name, resolve its contract
  on Robinhood Chain or ask for the address if ambiguous. Do not substitute a
  same-name token or an address on another chain.

## Quote and execute

1. Identify the input token, output token, and source-token amount. Check input
   funds and native ETH for gas using the [balance commands](balances.md).
2. Quote without `--execute`. `--amount` is in source-token units: `0.003`
   ETH means 0.003 ETH, not $0.003 or wei.
3. Show the chain, token identities (including an unregistered token's contract),
   input amount, estimated output, minimum output, and slippage for confirmation.
   Use token quantities for generic assets; do not label memecoin output as shares.
4. After confirmation of those concrete parameters, execute with the same assets,
   amount, chain, and slippage. Pass the quote's raw `minimumToAmount` through
   `--min-amount-out` to preserve the confirmed output floor. Execution requotes;
   if the constraints cannot be met, present a new quote for confirmation.
   An already confirmed matching trade card does not need a second confirmation.
5. Return the transaction hash and explorer link:
   `https://robinhoodchain.blockscout.com/tx/<tx_hash>`.
   A returned hash means submission; check the receipt through
   [read-only chain checks](read-only-chain-checks.md) before reporting success.
   Report updated balances after confirmation onchain. For an uncertain execution
   result, check transaction status before retrying.

## Commands

Replace `<TOKEN_CA>` with the selected token's exact contract address and
`<MIN_OUT_RAW>` with the quote's `minimumToAmount` string.

```bash
# Native ETH -> an arbitrary Robinhood Chain token: quote
purr wallet uniswap --from ETH --to <TOKEN_CA> --amount 0.003 --chain robinhood --slippage 0.5

# Execute only after confirmation of this quote
purr wallet uniswap --from ETH --to <TOKEN_CA> --amount 0.003 --chain robinhood --slippage 0.5 --min-amount-out <MIN_OUT_RAW> --execute

# Sell a held token for native ETH: quote
purr wallet uniswap --from <TOKEN_CA> --to ETH --amount 100 --chain robinhood

# USDG -> a token identified by contract: quote
purr wallet uniswap --from USDG --to <TOKEN_CA> --amount 5 --chain-id 4663

# Registered stock tickers use the same workflow
purr wallet uniswap --from USDG --to SPCX --amount 5 --chain robinhood
purr wallet uniswap --from SPCX --to AAPL --amount 0.01 --chain robinhood
```

`--slippage` is a percentage (`0.5` = 0.5%), not basis points. Omit it to use
the backend default. `--min-amount-out` uses raw output-token base units, unlike
the human-readable input `--amount`. Keep it as a string from the quote.
`--dedup-key` is optional; normally omit it to retain automatic deduplication.
Do not change it merely to bypass a duplicate-execution response.

## Read the result

The CLI prints one JSON object. Relevant quote fields are:

| Field | Meaning |
| --- | --- |
| `chainId`, `fromToken`, `toToken` | Chain and exact token identities; native ETH uses the zero address. |
| `fromAmount`, `fromAmountBaseUnits` | Human-readable input and raw input amount. |
| `estimatedToAmountFormatted` | Estimated output-token quantity. |
| `minimumToAmountFormatted`, `minimumToAmount` | Human-readable and raw minimum output. |
| `quoteSource` | `official` for the Uniswap API, or `amm` for the local AMM fallback. |

Execute results additionally include `mode: "transaction"`, `hash`, and
`transactionId`. Display amounts actually returned; do not invent missing fields.

## Route availability and errors

The backend tries the official Uniswap API first when configured. If no usable
official quote or swap plan is available, it tries local AMM routing. The local
V4 pool index currently covers a predefined token set and can miss other tokens;
this restriction does not filter official API routes. Token-address acceptance
or a successful quote does not guarantee that execution will succeed.

| Result/error | Action |
| --- | --- |
| `Unknown token ...` | The ticker is absent from the CLI registry. Resolve and use the exact Robinhood Chain contract address. |
| `purr wallet uniswap currently supports Robinhood Chain only` | Use `--chain robinhood` or `--chain-id 4663`. |
| `No quotes available` / `No route found` | Report that the current router found no usable route for this pair and amount; do not claim the token has no market. |
| `Latest Uniswap quote is below minAmountOut` | Preserve the confirmed floor; obtain a new quote for confirmation rather than silently lowering it. |
| Insufficient funds or gas | Check source-token and native ETH balances before retrying. |
