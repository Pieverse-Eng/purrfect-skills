# Buy / Sell

Use normal buy/sell when the user wants to trade a four.meme token through its
native four.meme quote-token route.

## Workflow

1. Run `purr wallet address --chain-type ethereum` to get the user's EVM wallet.
2. Run `purr wallet balance --chain-type ethereum --chain-id 56` to check BSC
   native BNB balance for gas before asking for remaining token details.
3. For buys, identify whether the user is specifying quote-token spend
   (`--funds`) or target token amount (`--amount`).
4. For sells, identify the token amount to sell and check the sell-token
   balance with `purr wallet balance --token <token> --chain-id 56`.
5. Show token, wallet, amount, and action. Ask for confirmation before
   `--execute`.
6. Run the matching command with `--execute`.
7. Report the transaction result, including hash or status, then re-check
   balances if useful.

Stay in normal buy/sell routing when the user asks for a normal four.meme
trade. Use BNB bridge commands only when the user specifically needs to enter
or exit a non-BNB raised-token launch with BNB. Do not present
`buy-with-bnb` or `sell-for-bnb` commands as alternatives during a normal
buy/sell flow. If the raised-token route is uncertain, ask a neutral
clarifying question or run discovery/status first; show bridge commands only
after the user chooses the bridge flow or discovery proves it is required.

## Syntax

```bash
purr fourmeme buy --token <0x_token> --wallet <0x_wallet> [--funds <quote_amount> | --amount <token_amount>] --execute
purr fourmeme sell --token <0x_token> --wallet <0x_wallet> --amount <token_amount> --execute
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--token <0x_token>` | Required | four.meme token contract address on BSC. |
| `--wallet <0x_wallet>` | Required | User's EVM wallet address. |
| `--funds <quote_amount>` | Required for buy when `--amount` is omitted | Human-readable quote-token amount to spend. |
| `--amount <token_amount>` | Required for sell; optional buy mode | Human-readable token amount. For buy, this is the desired token amount. For sell, this is the amount to sell. |
| `--slippage <decimal>` | Optional | Slippage for buy/sell quote bounds. |
| `--execute` | Required for user-facing execution | Builds, signs, and broadcasts through the wallet execution flow. |

## Commands

```bash
purr fourmeme buy --token 0xToken --wallet 0xWallet --funds 0.1 --execute
purr fourmeme buy --token 0xToken --wallet 0xWallet --amount 1000 --execute
purr fourmeme sell --token 0xToken --wallet 0xWallet --amount 1000 --execute
```

## Routing Notes

`purr fourmeme buy|sell` detects:

- V1 vs V2
- X Mode
- TaxToken
- AntiSniper
- agent-created flags

Use the CLI routing instead of manually selecting contract methods. Approvals
are conditional when needed.

V1 sells do not have native on-chain min-out enforcement. The CLI still computes
quote bounds for labels and V2 `minFunds` where available.

## Response Shape

Success prints the wallet execution result, including transaction hash or step
execution details:

```json
{
  "hash": "0x...",
  "chainId": 56,
  "status": "success"
}
```

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Missing required argument: --token` | Token address is missing. |
| `Missing required argument: --wallet` | Wallet address is missing. |
| `Missing required argument: --amount` | Sell amount is missing. |
| `Invalid address` | Token or wallet address is invalid. |
| `insufficient native gas balance` | Wallet lacks BNB for gas. |
| `insufficient token balance` | Wallet lacks the token being sold. |
| `contract execution reverted` | Token trading may be disabled, the amount is invalid, or the chain state rejected the route. |
| `Failed to execute EVM transaction` | Wallet execution failed; report the exact upstream error. |
