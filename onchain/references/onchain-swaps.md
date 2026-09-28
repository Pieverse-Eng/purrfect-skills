# Onchain Swaps

Use `purr wallet uniswap` to quote, buy, sell, or swap tokens on Robinhood Chain
(4663), Arc Mainnet (5042), and Soneium (1868) through the hosted wallet. This includes stock/ETF
tokens, memecoins, and other ERC-20 tokens with a supported route. The command
quotes by default; `--execute` submits a transaction after user confirmation.

Sui swaps use a different command, `purr wallet sui-swap` (Cetus aggregator);
see [Sui](#sui). The shared workflow's quote → confirm → execute steps apply
to it as well.

Follow the shared workflow below and the selected chain's section:
[Robinhood Chain](#robinhood-chain), [Arc Mainnet](#arc-mainnet), [Soneium](#soneium),
or [Sui](#sui).

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
purr wallet uniswap --from <ticker_or_address> --to <ticker_or_address> --amount <decimal_amount> --chain <robinhood|arc|soneium> [--slippage <percent>] [--min-amount-out <raw_amount>] [--dedup-key <key>] [--execute]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--from <ticker_or_address>` | Required | Source asset. Use a registered ticker on the selected chain or its exact token contract address. |
| `--to <ticker_or_address>` | Required | Destination asset. Accepts the same ticker or contract-address forms as `--from`, including memecoin contracts. |
| `--amount <decimal_amount>` | Required | Human-readable source-token amount, such as `0.003` ETH or `5` USDG; not wei/base units. |
| `--chain <name>` / `--chain-id <id>` | Recommended | Robinhood (`4663`, default), Arc (`5042`), or Soneium (`1868`). Use either form. |
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

## Soneium

- **Chain:** `--chain soneium` or `--chain-id 1868`. Requires CLI and Platform
  versions with Soneium support.
- **Tokens:** `ETH` selects native ETH. `WETH` resolves to
  `0x4200000000000000000000000000000000000006` (18 decimals). `USDC.e`
  resolves to bridged USDC at `0xbA9986D2381edf1DA03B0B9c1f8b00dc4AacC369`
  (6 decimals). For other tokens, resolve and use their exact Soneium contract
  address. Do not reuse token addresses from a different chain.
- **Gas:** reserve native ETH for approvals and swaps.
- **Explorer:** `https://soneium.blockscout.com/tx/<tx_hash>`.
- **Execution:** ordinary sends use TEE signing and Platform RPC broadcasting,
  as on Arc. Runtime-guarded on-demand sends require provider-native Soneium
  send/replay support. A quote does not prove that guarded execution is enabled.
  Report unsupported-send or policy rejections;
  do not bypass them with raw signing, alternative credentials, or RPC sends.
- **Campaign scope:** Startale vault deposits and JPYSC are separate integrations.
  Do not present a token transfer or swap as completion of a vault deposit task.

Replace `<TOKEN_CA>` with the selected token's Soneium contract address and
`<MIN_OUT_RAW>` with the confirmed quote's `minimumToAmount` string.

```bash
# Quote native ETH -> ERC-20
purr wallet uniswap --chain soneium --from ETH --to <TOKEN_CA> --amount 0.001 --slippage 0.5

# Execute only after confirmation, preserving the output floor
purr wallet uniswap --chain soneium --from ETH --to <TOKEN_CA> --amount 0.001 --slippage 0.5 --min-amount-out <MIN_OUT_RAW> --execute

# Quote ERC-20 -> native ETH
purr wallet uniswap --chain-id 1868 --from <TOKEN_CA> --to ETH --amount 1
```

## Sui

- **Command:** `purr wallet sui-swap`, not `uniswap`. Sui mainnet only, through
  the Cetus aggregator. The platform builds and checks the swap, and the TEE
  signs and broadcasts it.
- **Coins:** `SUI`, `USDC`, or a full coin type `0x<package>::<module>::<NAME>`
  (module and type names are case-sensitive). See the Sui coin table in
  SKILL.md. Do not guess a coin type from a symbol.
- **Gas:** keep SUI for gas, including when swapping USDC or another coin.
- **Explorer:** `https://suiscan.xyz/mainnet/tx/<hash>`.
- **Fees:** some routes pass through Aftermath pools, which charge a small
  protocol fee (0.05%). Part of it goes to a third-party address, so it shows
  up in the transaction's balance changes. This is expected.

```bash
purr wallet sui-swap --from <SUI|USDC|coin_type> --to <SUI|USDC|coin_type> --amount <decimal_amount> [--slippage <percent>] [--min-amount-out <raw_amount>] [--idempotency-key <key>] [--execute]
```

| Parameter | Required? | Description |
| --- | --- | --- |
| `--from` / `--to` | Required | `SUI`, `USDC`, or a full coin type. |
| `--amount <decimal_amount>` | Required | Human-readable input amount, such as `0.5` SUI; not base units. |
| `--slippage <percent>` | Optional | Slippage percentage: `0.5` means 0.5% (default 0.5, at most 50, up to two decimals). |
| `--min-amount-out <raw_amount>` | Optional | Minimum output in raw output-coin base units. When executing, pass the confirmed quote's `minAmountOutBaseUnits` string to preserve its output floor. Do not pass `minAmountOut`, which is in whole-coin units. |
| `--idempotency-key <key>` | Optional | Resumes an earlier send. Pass only the key a previous result or error reported (`operationId` / `idempotencyKey`). |
| `--execute` | Optional | Executes the confirmed swap. Omit for quote-only mode. |

Replace `<MIN_OUT_RAW>` with the confirmed quote's `minAmountOutBaseUnits` string.

```bash
# Quote SUI -> USDC
purr wallet sui-swap --from SUI --to USDC --amount 0.5 --slippage 0.5

# Execute only after confirmation, preserving the output floor
purr wallet sui-swap --from SUI --to USDC --amount 0.5 --slippage 0.5 --min-amount-out <MIN_OUT_RAW> --execute

# Any coin by full coin type
purr wallet sui-swap --from SUI --to 0x...::module::NAME --amount 0.2
```

**Quote:** show `estimatedAmountOut`, `minAmountOut` and the route. The quote
also returns `minAmountOutBaseUnits` for `--min-amount-out`.

**Result:** `--execute` returns once the swap is confirmed. Report `hash`, the
explorer link, and `amountOut` (the actual output received, formatted).
`amountOut` is null only if the fullnode had not reported the transaction yet.
For `POLICY_DEFERRED`, `SUI_SUBMISSION_UNKNOWN`, `stale_chain_state` and
policy denials, follow the [Sui retry and error rules](raw-address-transfers.md#sui).
Swap-specific errors:

| Error | Meaning / Action |
| --- | --- |
| `quote_below_minimum` | The fresh route is below the confirmed floor; get a new quote and confirm it again. |
| `unsupported_coin` / `Unknown Sui coin` | The coin could not be identified; ask for its exact full coin type. |
| `no_route` / `router_unavailable` | No usable Cetus route right now (`router_unavailable` may succeed on retry). |

## Quote Response

The CLI prints one JSON object. Relevant `uniswap` quote fields are listed
below; for Sui, see [Sui](#sui).

| Field | Meaning |
| --- | --- |
| `chainId`, `fromToken`, `toToken` | Chain and exact token identities, using the representation described in the chain's section. |
| `fromAmount`, `fromAmountBaseUnits` | Human-readable input and raw input amount. |
| `estimatedToAmountFormatted` | Estimated output-token quantity. |
| `minimumToAmountFormatted`, `minimumToAmount` | Human-readable and raw minimum output. |
| `quoteSource` | `official` — Platform uses the Uniswap Trading API. |

## Execution Results

`--execute` submits the swap, then checks its receipt for up to 60 seconds;
allow command time for both. The compact result contains `status`, `chainId`,
`hash`, `explorerUrl`, and, when available, actual `input` / `output` and `gas`.
Include the hash and explorer link in the reply, then use this table:

| `status` | Report / action |
| --- | --- |
| `success` | Included successfully onchain; report the actual amounts below. Inclusion does not guarantee finality. |
| `reverted` | Reverted; no fill. |
| `pending` / `unknown` | Submitted, confirmation pending/unavailable. Preserve the hash and stop. |
| No `status` (older CLI) | Hash proves submission only; use read-only checks before claiming success. |

Use `input` / `output` (`tokenAddress`, `amount`) for actual quantities. Amounts
are already formatted decimal strings. Report only quantities present in the result;
unavailable quantities are omitted. Follow `warnings` / `reason` when present.
Arc native USDC is already de-duplicated and labeled
`native` with symbol `USDC`; other tokens retain their CA. `gas` (`amount`,
`symbol`) is the separate execution fee, excluding approval gas and separate
rollup fees. `recipient` appears when explicitly supplied.

Do not automatically follow this result with curl, Python decoding, or a balance
refresh. Use [read-only chain checks](read-only-chain-checks.md) for the older-CLI
case above, uncertain execution errors, or explicit follow-up requests. Never
repeat `--execute` to query status; resolve an uncertain submission before retrying.

## Shared Errors

| Error Message | Meaning / Action |
| --- | --- |
| `Unknown token ...` | The ticker is absent from the CLI registry. Resolve and use the exact contract address on the selected chain. |
| `purr wallet uniswap supports ... only` | Select a supported chain; Soneium requires a CLI version with chain 1868 support. |
| `No quotes available` / `No route found` | Report that the current router found no usable route for this pair and amount; do not claim the token has no market. |
| `Latest Uniswap quote is below minAmountOut` | Preserve the confirmed floor; obtain a new quote for confirmation rather than silently lowering it. |
| Insufficient funds or gas | Check source-token and native gas balances before retrying, following the chain's balance and gas rules. |
