# Onchain Swaps

Use `purr wallet uniswap` to quote, buy, sell, or swap tokens on Robinhood Chain
(4663) and Arc Mainnet (5042) through the hosted wallet. This includes stock/ETF
tokens, memecoins, and other ERC-20 tokens with a supported route. The command
quotes by default; `--execute` submits a transaction after user confirmation.

Follow the shared workflow below and the selected chain's section:
[Robinhood Chain](#robinhood-chain) or [Arc Mainnet](#arc-mainnet).

## Usage Notes

- Always specify the chain using the flags in its section. Omitting it defaults
  to Robinhood.
- For tokens without a registered ticker, use the exact contract address on the
  selected chain in `--from` or `--to`. A token does not need to appear in the stock directory
  or CLI ticker registry to be quoted by address.
- If the caller supplies only an unregistered token name, resolve its contract
  on the selected chain or ask for the address if ambiguous. Do not substitute a
  same-name token or an address on another chain.

## Shared Workflow

1. Identify the input token, output token, and source-token amount. Check input
   funds and the chain's native gas balance using the [balance commands](balances.md).
   Reserve enough native currency for approval and swap gas.
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
5. Report the [execution result](#execution-results).

## Syntax

```bash
purr wallet uniswap --from <ticker_or_address> --to <ticker_or_address> --amount <decimal_amount> --chain <robinhood|arc> [--slippage <percent>] [--min-amount-out <raw_amount>] [--dedup-key <key>] [--execute]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--from <ticker_or_address>` | Required | Source asset. Use a registered ticker on the selected chain or its exact token contract address. |
| `--to <ticker_or_address>` | Required | Destination asset. Accepts the same ticker or contract-address forms as `--from`, including memecoin contracts. |
| `--amount <decimal_amount>` | Required | Human-readable source-token amount, such as `0.003` ETH or `5` USDG; not wei/base units. |
| `--chain <name>` / `--chain-id <id>` | Recommended | Robinhood (`4663`, default) or Arc (`5042`). Use either form. |
| `--slippage <percent>` | Optional | Slippage percentage: `0.5` means 0.5%, not 50%. Omit to use the backend default. |
| `--min-amount-out <raw_amount>` | Optional | Minimum output in raw output-token base units. Pass the confirmed quote's `minimumToAmount` string when executing to preserve its output floor. |
| `--dedup-key <key>` | Optional | Idempotency key. Normally omit to retain automatic deduplication; do not change it to bypass a duplicate-execution response. |
| `--execute` | Optional | Executes the confirmed swap. Omit for quote-only mode. |

## Robinhood Chain

- **Chain:** `--chain robinhood` or `--chain-id 4663`.
- **Tokens:** use `ETH` for native ETH, or registered tickers such as `WETH`
  and `USDG`. Quote responses represent native ETH with the zero address.
  For stock/ETF tickers and contract addresses, use the
  [stock/ETF address directory](robinhood-stock-etf-tokens.md).
- **Gas:** keep native ETH available, including when swapping ERC-20 tokens.
- **Explorer:** `https://robinhoodchain.blockscout.com/tx/<tx_hash>`.

### Commands

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

## Arc Mainnet

- **Chain:** `--chain arc` or `--chain-id 5042`. Requires CLI and Platform
  versions with Arc Uniswap support.
- **Tokens and units:** swap `USDC` selects the ERC-20 interface at
  `0x3600000000000000000000000000000000000000`, with **6 decimals**.
  `--amount 1` means 1 USDC. Use `USDC` or this contract address for either
  swap direction; other tokens accept their exact CA and use their own decimals.
  Do not use a native zero-address sentinel.
- **Gas:** leave USDC available for approval and swap gas.
- **RPC and explorer:** follow the
  [Arc endpoint configuration](read-only-chain-checks.md#common-rpc-endpoints)
  before reads, execution, or linking a transaction.
- **Execution restriction:** Arc swaps are unavailable on runtime-guarded
  on-demand routes.
  Report the rejection without switching credentials or bypassing the guard.

### Commands

Replace `<TOKEN_CA>` with the selected Arc token's exact contract address and
`<MIN_OUT_RAW>` with the quote's `minimumToAmount` string. When selling for USDC,
the raw output minimum uses **6 decimals**.

```bash
# Arc USDC -> a token identified by contract: quote
purr wallet uniswap --from USDC --to <TOKEN_CA> --amount 1 --chain arc

# Arc USDC -> another token: quote, then execute with the confirmed raw floor
purr wallet uniswap --from USDC --to <TOKEN_CA> --amount 1 --chain-id 5042 --slippage 0.5
purr wallet uniswap --from USDC --to <TOKEN_CA> --amount 1 --chain-id 5042 --slippage 0.5 --min-amount-out <MIN_OUT_RAW> --execute

# Sell an Arc token back to USDC (output minimum is in 6-decimal USDC units)
purr wallet uniswap --from <TOKEN_CA> --to USDC --amount 100 --chain arc
```

### Arc Errors

| Error Message | Meaning / Action |
| --- | --- |
| `Arc swaps require the USDC ERC-20 address, not a native token sentinel` | Use `--from USDC` / `--to USDC`, or the USDC ERC-20 address. |

## Quote Response

The CLI prints one JSON object. Relevant quote fields are:

| Field | Meaning |
| --- | --- |
| `chainId`, `fromToken`, `toToken` | Chain and exact token identities, using the representation described in the chain's section. |
| `fromAmount`, `fromAmountBaseUnits` | Human-readable input and raw input amount. |
| `estimatedToAmountFormatted` | Estimated output-token quantity. |
| `minimumToAmountFormatted`, `minimumToAmount` | Human-readable and raw minimum output. |
| `quoteSource` | `official` — Platform uses the Uniswap Trading API. |

## Execution Results

`--execute` submits the swap, then checks its receipt for up to 60 seconds;
allow command time for both. It returns `receipt` alongside the submission hash.
Include the hash and `receipt.explorerUrl` in the reply, then use this table:

| `receipt.status` | Report / action |
| --- | --- |
| `success` | Included successfully onchain; report the actual amounts below. Inclusion does not guarantee finality. |
| `reverted` | Reverted; no fill. |
| `pending` / `unknown` | Submitted, confirmation pending/unavailable. Preserve the hash and stop. |
| No `receipt` (older CLI) | Hash proves submission only; use read-only checks before claiming success. |

Use `receipt.actualInput` / `actualOutput` (`tokenAddress`, `amountFormatted`)
for quantities, not quote estimates. Null amounts or missing decimals remain
unavailable; follow `warnings` / `reason`. Robinhood native ETH amounts may be
unavailable even on success. Arc native USDC is already de-duplicated and labeled
`native` with 18 decimals; other tokens retain their CA. `receipt.gas` is the
separate execution fee, excluding approval gas and separate rollup fees.

Do not automatically follow this result with curl, Python decoding, or a balance
refresh. Use [read-only chain checks](read-only-chain-checks.md) for the older-CLI
case above, uncertain execution errors, or explicit follow-up requests. Never
repeat `--execute` to query status; resolve an uncertain submission before retrying.

## Shared Errors

| Error Message | Meaning / Action |
| --- | --- |
| `Unknown token ...` | The ticker is absent from the CLI registry. Resolve and use the exact contract address on the selected chain. |
| `purr wallet uniswap supports Robinhood Chain (4663) and Arc (5042) only` | Select a supported chain. |
| `No quotes available` / `No route found` | Report that the current router found no usable route for this pair and amount; do not claim the token has no market. |
| `Latest Uniswap quote is below minAmountOut` | Preserve the confirmed floor; obtain a new quote for confirmation rather than silently lowering it. |
| Insufficient funds or gas | Check source-token and native gas balances before retrying, following the chain's balance and gas rules. |
