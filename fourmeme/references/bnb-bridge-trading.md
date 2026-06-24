# BNB Bridge Buy / Sell

Use BNB bridge commands when the four.meme launch token uses a non-BNB raised
token such as USDT, USDC, CAKE, or another supported quote token, but the user
wants to enter or exit using BNB.

## Workflow

1. Confirm the target token is a four.meme token whose quote token is not BNB.
2. Get the user's EVM wallet and check BSC BNB balance.
3. For buying, ask for the BNB amount to spend and the minimum token amount.
4. For selling, ask for token amount and minimum BNB output.
5. For `sell-for-bnb`, choose one recipient mode:
   - default wallet output
   - explicit recipient with `--to`
   - fee-sharing with `--fee-rate` and `--fee-recipient`
6. Show token, wallet, amounts, recipient or fee-sharing mode, and ask for
   confirmation before `--execute`.
7. Run the command and report the transaction result.

## Syntax

```bash
purr fourmeme buy-with-bnb --token <0x_token> --wallet <0x_wallet> --funds <bnb_amount> --min-amount <token_amount> --execute
purr fourmeme sell-for-bnb --token <0x_token> --wallet <0x_wallet> --amount <token_amount> --min-funds <bnb_amount> [--to <0x_recipient> | --fee-rate <0-500> --fee-recipient <0x_recipient>] --execute
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--token <0x_token>` | Required | four.meme token contract address on BSC. |
| `--wallet <0x_wallet>` | Required | User's EVM wallet address. |
| `--funds <bnb_amount>` | Required for `buy-with-bnb` | Human-readable BNB amount to spend. |
| `--min-amount <token_amount>` | Required for `buy-with-bnb` | Minimum token amount accepted. |
| `--amount <token_amount>` | Required for `sell-for-bnb` | Human-readable token amount to sell. |
| `--min-funds <bnb_amount>` | Required for `sell-for-bnb` | Minimum BNB output accepted. |
| `--to <0x_recipient>` | Optional | Explicit BNB recipient. Cannot be combined with fee-sharing params. |
| `--fee-rate <0-500>` | Optional | Fee-sharing rate. Requires `--fee-recipient` when greater than 0. |
| `--fee-recipient <0x_recipient>` | Optional | Fee-sharing recipient. Cannot be combined with `--to`. |
| `--execute` | Required for user-facing execution | Builds, signs, and broadcasts through the wallet execution flow. |

## Commands

```bash
purr fourmeme buy-with-bnb \
  --token 0xToken \
  --wallet 0xWallet \
  --funds 0.01 \
  --min-amount 1000 \
  --execute

purr fourmeme sell-for-bnb \
  --token 0xToken \
  --wallet 0xWallet \
  --amount 1000 \
  --min-funds 0.01 \
  --execute

purr fourmeme sell-for-bnb \
  --token 0xToken \
  --wallet 0xWallet \
  --amount 1000 \
  --min-funds 0.01 \
  --to 0xRecipient \
  --execute

purr fourmeme sell-for-bnb \
  --token 0xToken \
  --wallet 0xWallet \
  --amount 1000 \
  --min-funds 0.01 \
  --fee-rate 25 \
  --fee-recipient 0xRecipient \
  --execute
```

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
| `four.meme buy-with-bnb only supports V2 tokens` | The token is not supported by the Helper3 buy-with-BNB route. |
| `four.meme buy-with-bnb only supports tokens whose quote token is not BNB` | Use normal `buy` for BNB-quoted tokens. |
| `four.meme sell-for-bnb only supports V2 tokens` | The token is not supported by the Helper3 sell-for-BNB route. |
| `four.meme sell-for-bnb only supports tokens whose quote token is not BNB` | Use normal `sell` for BNB-quoted tokens. |
| `--to cannot be combined with --fee-rate or --fee-recipient` | Choose explicit recipient mode or fee-sharing mode, not both. |
| `--fee-rate must be an integer between 0 and 500` | Fee rate is outside the accepted range. |
| `Missing required argument: --fee-recipient` | Fee-sharing was requested with a nonzero fee rate but no recipient. |
| `insufficient native gas balance` | Wallet lacks BNB for gas or buy value. |
| `insufficient token balance` | Wallet lacks the token being sold. |
| `contract execution reverted` | The route, slippage, amount, or token state was rejected on-chain. |
