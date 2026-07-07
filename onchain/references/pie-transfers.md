# Direct `.pie` Transfers

Use direct `.pie` transfers when the recipient is identified by a `.pie` handle
or paired Telegram account.

## Workflow

1. Identify the recipient: `.pie` handle or Telegram account.
2. Identify the chain, amount, and token.
3. Run the matching `purr .pie transfer` command.
4. Return the transaction result.

## Syntax

```bash
purr .pie transfer --pie <handle>.pie --amount <amount> --chain-id <chain_id> [--token <ticker_or_address>] [--decimals <n>] [--chain-type ethereum]
purr .pie transfer --channel telegram --account <telegram_username> --amount <amount> --chain-id <chain_id> [--token <ticker_or_address>] [--decimals <n>] [--chain-type ethereum]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--pie <handle>.pie` | Required when not using `--channel` and `--account` | Sends to the wallet for the Pie handle. Use either `--pie` or `--channel telegram --account ...`, not both. |
| `--channel telegram` | Required when not using `--pie` | Selects Telegram account lookup for the recipient. |
| `--account <telegram_username>` | Required with `--channel telegram` | The Telegram username paired to the recipient Pie identity, with or without `@`. |
| `--amount <amount>` | Required | Human-readable amount to send, such as `0.01` or `10`. |
| `--chain-id <chain_id>` | Required | Numeric EVM chain ID, such as `56` for BNB Smart Chain, `143` for Monad, `196` for X Layer, or `4663` for Robinhood Chain. |
| `--token <ticker_or_address>` | Optional | Token to send. Omit for the native coin. Accepts a known ticker such as `USDT`, or a raw token contract address. |
| `--decimals <n>` | Optional | Token decimals override when the token needs an explicit decimal value. |
| `--chain-type ethereum` | Optional | Direct `.pie` transfers currently target EVM recipients; omit this unless you need to be explicit. |

## Commands

```bash
purr .pie transfer --pie <handle>.pie --amount 0.01 --chain-id 56                         # native BNB on BSC to a Pie handle
purr .pie transfer --pie <handle>.pie --amount 10 --chain-id 56 --token USDT              # USDT on BSC to a Pie handle
purr .pie transfer --pie <handle>.pie --amount 0.01 --chain-id 143                        # native MON on Monad to a Pie handle
purr .pie transfer --pie <handle>.pie --amount 5 --chain-id 143 --token USDC              # USDC on Monad to a Pie handle
purr .pie transfer --pie <handle>.pie --amount 0.01 --chain-id 4663                       # native ETH on Robinhood Chain to a Pie handle
purr .pie transfer --pie <handle>.pie --amount 1 --chain-id 4663 --token 0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168 --decimals 6  # USDG on Robinhood Chain to a Pie handle
purr .pie transfer --channel telegram --account <username> --amount 0.01 --chain-id 56    # native BNB on BSC to a Telegram-paired Pie identity
purr .pie transfer --channel telegram --account <username> --amount 10 --chain-id 56 --token USDT # USDT on BSC to a Telegram-paired Pie identity
```

## Response Shape

Success prints one JSON object to stdout. It is the wallet transfer result plus
`pieName`:

```json
{
  "from": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "to": "0x1234567890123456789012345678901234567890",
  "amount": "10",
  "hash": "0x...",
  "chainId": 56,
  "chainType": "ethereum",
  "assetType": "erc20",
  "pieName": "alice.pie"
}
```

`assetType` is `native` for native coin transfers and `erc20` for token
transfers. Direct `.pie` transfers currently target EVM recipients.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `handle_reserved` / `Handle <handle>.pie is reserved` | The recipient handle is reserved. |
| `handle_reservation_expired` | The recipient handle reservation expired. |
| `invalid_handle` / `Handle is unavailable` | The recipient handle is blocked by handle policy. |
| `reason` such as `per_tx_cap_exceeded`, `address_not_allowlisted`, or `wallet_frozen` | Wallet policy denied the transfer. |
| `manual_approval_required` in the API body; the CLI may print `Transfer failed` | Wallet policy deferred the transfer. |
| `insufficient native gas balance` | The wallet lacks native gas for the transaction. |
| `insufficient token balance` | The wallet lacks the requested token amount. |
| `contract execution reverted` | Token contract execution reverted. |
| `chain state rejected` | The chain or signer rejected the transaction state. |
| `transaction rejected` | The signed transaction was structurally rejected. |
| `Do not pass --to; ...` | `.pie` transfers derive the recipient from `--pie` or Telegram account. |
| `purr .pie transfer currently supports only ethereum recipients` | `.pie` transfer was requested with an unsupported chain family. |
| `Use either --pie or --channel/--account, not both` | Recipient mode is ambiguous. |
| `No .pie identity found for telegram:<account>` | The Telegram account has no paired Pie identity. |
| `Missing required argument: --amount` or `Missing required argument: --chain-id ...` | Required transfer input is missing. |
| `Unknown token ...` or `No token registry ...` | The ticker could not be resolved locally; use a supported ticker or raw token address. |
| `Unsupported chainId. Supported: ...`, `Invalid EVM recipient address ...`, or `Wallet service error` | Transfer request validation or wallet service failure. |
