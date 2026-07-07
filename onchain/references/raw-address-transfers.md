# Raw Address Transfers

Use raw address transfers when the user already provides an EVM or Solana wallet
address.

## Workflow

1. Identify the raw recipient address.
2. Identify the chain, amount, and token.
3. Run the matching `purr wallet transfer` command.
4. Return the transaction result.

## Syntax

```bash
purr wallet transfer --to <address> --amount <amount> [--chain-id <chain_id>] [--chain-type <ethereum|solana>] [--token <ticker_or_address>] [--decimals <n>]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--to <address>` | Required | Recipient wallet address. Use a `0x...` address for EVM or a base58 address for Solana. |
| `--amount <amount>` | Required | Human-readable amount to send, such as `0.01`, `10`, or `100`. |
| `--chain-id <chain_id>` | Required for EVM | Numeric EVM chain ID, such as `56` for BNB Smart Chain, `143` for Monad, `8453` for Base, `196` for X Layer, or `4663` for Robinhood Chain. Not needed for Solana. |
| `--chain-type <ethereum|solana>` | Optional | Selects the chain family. Omit for EVM or set `ethereum`; use `solana` for Solana transfers. |
| `--token <ticker_or_address>` | Optional | Token to send. Omit for the native coin. Accepts a known ticker such as `USDT`, `USDC`, or `USDT0`, or a raw token contract/mint address. |
| `--decimals <n>` | Optional | Token decimals override when the token needs an explicit decimal value. |

## Commands

```bash
purr wallet transfer --to 0x... --amount 0.01 --chain-id 56                    # native BNB
purr wallet transfer --to 0x... --amount 10 --chain-id 56 --token USDT         # USDT on BSC
purr wallet transfer --to 0x... --amount 0.01 --chain-id 143                   # native MON on Monad
purr wallet transfer --to 0x... --amount 5 --chain-id 143 --token USDC         # USDC on Monad
purr wallet transfer --to 0x... --amount 5 --chain-id 8453 --token USDC        # USDC on Base
purr wallet transfer --to 0x... --amount 0.1 --chain-id 196                    # native OKB on X Layer
purr wallet transfer --to 0x... --amount 0.1 --chain-id 196 --token USDT0      # USDT0 on X Layer
purr wallet transfer --to 0x... --amount 0.1 --chain-id 196 --token USDC       # USDC on X Layer
purr wallet transfer --to 0x... --amount 0.1 --chain-id 196 --token USDG       # USDG on X Layer
purr wallet transfer --to 0x... --amount 0.01 --chain-id 4663                  # native ETH on Robinhood Chain
purr wallet transfer --to 0x... --amount 0.01 --chain-id 4663 --token 0x0Bd7D308f8E1639FAb988df18A8011f41EAcAD73 --decimals 18  # WETH on Robinhood Chain
purr wallet transfer --to 0x... --amount 1 --chain-id 4663 --token 0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168 --decimals 6       # USDG on Robinhood Chain
purr wallet transfer --to FuQPd1q... --amount 0.5 --chain-type solana          # native SOL
purr wallet transfer --to FuQPd1q... --amount 100 --chain-type solana --token USDC  # USDC on Solana
```

## Response Shape

Success prints one JSON object to stdout:

```json
{
  "from": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "to": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "amount": "10",
  "hash": "0x...",
  "chainId": 56,
  "chainType": "ethereum",
  "assetType": "erc20"
}
```

For Solana, `chainType` is `solana` and `chainId` may be omitted. `assetType` is
`native`, `erc20`, or `spl`.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `reason` such as `per_tx_cap_exceeded`, `address_not_allowlisted`, or `wallet_frozen` | Wallet policy denied the transfer. |
| `manual_approval_required` in the API body; the CLI may print `Transfer failed` | Wallet policy deferred the transfer. |
| `insufficient native gas balance` | The wallet lacks native gas for the transaction. |
| `insufficient token balance` | The wallet lacks the requested token amount. |
| `contract execution reverted` | Token contract execution reverted. |
| `chain state rejected` | The chain or signer rejected the transaction state. |
| `transaction rejected` | The signed transaction was structurally rejected. |
| `Missing required argument: --to` | Recipient address is missing. |
| `Missing required argument: --amount` | Transfer amount is missing. |
| `Missing required argument: --chain-id ...` | EVM transfer is missing `--chain-id`. |
| `Unknown token ...` or `No token registry ...` | The ticker could not be resolved locally; use a supported ticker or raw token address. |
| `Unsupported chainType. Supported: ...` or `Unsupported chainId. Supported: ...` | Requested chain family or chain ID is unsupported. |
| `Invalid EVM recipient address. wallet/transfer requires a raw 0x address; use redpackets for .pie recipients.` | EVM recipient is not a raw `0x...` address. |
| `Wallet service error` | Upstream wallet service failure without a typed response code. |
