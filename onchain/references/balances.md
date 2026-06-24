# Balances

Use balances to inspect native coin or token holdings on a specific chain. Add
`--token` for ERC-20 or SPL token balances.

## Workflow

1. Identify the wallet family: EVM or Solana.
2. Identify the chain.
3. Identify whether the user wants the native token or a specific token.
4. For native EVM balances, include `--chain-type ethereum` with `--chain-id`.
5. Run the matching balance command.
6. Return the balance, token symbol, chain, and wallet address if present.

## Syntax

```bash
purr wallet balance [--chain-type <ethereum|solana>] [--chain-id <chain_id>] [--token <ticker_or_address>]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--chain-type <ethereum|solana>` | Required for Solana and native EVM balances | Selects the wallet family. Use `ethereum` for native EVM balances when a Solana wallet also exists; use `solana` for Solana balances. |
| `--chain-id <chain_id>` | Required for EVM | Selects the EVM chain by numeric chain ID, such as `56` for BNB Smart Chain or `8453` for Base. |
| `--token <ticker_or_address>` | Optional | Selects a token balance instead of the native coin. Accepts a known ticker such as `USDT` or `USDC`, or a raw token contract/mint address. |

## Commands

```bash
purr wallet balance --chain-type ethereum --chain-id 56                    # native BNB on BSC
purr wallet balance --chain-type ethereum --chain-id 8453                  # native ETH on Base
purr wallet balance --token USDT --chain-id 56                             # USDT on BSC
purr wallet balance --token USDC --chain-id 8453                           # USDC on Base
purr wallet balance --chain-type ethereum --chain-id 196                   # native OKB on X Layer
purr wallet balance --token USDT0 --chain-id 196                           # USDT0 on X Layer
purr wallet balance --token USDC --chain-id 196                            # USDC on X Layer
purr wallet balance --token USDG --chain-id 196                            # USDG on X Layer
purr wallet balance --chain-type solana                                    # native SOL
purr wallet balance --chain-type solana --token USDC                       # USDC on Solana
```

## Response Shape

Success prints one JSON object to stdout:

```json
{
  "address": "0x... or base58...",
  "chainId": 56,
  "chainType": "ethereum",
  "balance": "1000000000000000000",
  "balanceFormatted": "1.0",
  "currency": "BNB",
  "symbol": "BNB",
  "decimals": 18,
  "tokenAddress": "0x..."
}
```

Token fields vary by native coin or token query. Native balances may omit
`tokenAddress`.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Unsupported chain_type. Supported: ...` | The requested `--chain-type` is not supported. |
| `Unsupported chain_id. Supported: ...` | The requested EVM `--chain-id` is not supported. |
| `Multiple wallets exist. Specify chain_type query parameter (ethereum or solana).` | The wallet family is ambiguous. For native EVM balances, add `--chain-type ethereum`; for Solana balances, add `--chain-type solana`. |
| `No wallet found. Use \`purr wallet address\` first to create one.` | No wallet exists yet for the selected chain family. |
| `Token balance query failed: ...` | Token balance lookup failed on the selected chain. |
| `Balance query failed: ...` | Native balance lookup failed on the selected chain. |
| `Unknown token ...` or `No token registry ...` | The ticker could not be resolved locally; use a supported ticker or raw token address. |
