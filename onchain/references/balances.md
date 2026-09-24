# Balances

Use balances to inspect native coin or token holdings on a specific chain.
`--token` accepts a ticker or contract/mint address; omit it for the native coin.

## Workflow

1. Identify the wallet family: EVM or Solana.
2. For EVM, select the chain with `--chain-id <id>` or `--chain <name>`.
3. Identify whether the user wants the native token or a specific token.
4. When querying native EVM balances with `--chain-id` and no `--token`, also
   include `--chain-type ethereum`.
5. Run the matching balance command.
6. Return the balance, token symbol, chain, and wallet address if present.

## Syntax

```bash
purr wallet balance [--chain-type <ethereum|solana>] [--chain-id <chain_id> | --chain <name>] [--token <ticker_or_address>]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--chain-type <ethereum|solana>` | Conditional | Use `solana` for Solana balances. For native EVM queries using `--chain-id` without `--token`, set `ethereum`. An EVM `--chain` alias or `--token` infers `ethereum`. |
| `--chain-id <chain_id>` / `--chain <name>` | Required for EVM (choose one) | Selects the chain by numeric ID or known alias, such as `--chain-id 5042` / `--chain arc` or `--chain-id 4663` / `--chain robinhood`. |
| `--token <ticker_or_address>` | Optional | Omit for the native coin. Accepts a known ticker such as `USDT` or `USDC`, or a raw token contract/mint address. Native tickers select the native balance. |

## Commands

```bash
purr wallet balance --chain-type ethereum --chain-id 56                    # native BNB on BSC
purr wallet balance --chain-type ethereum --chain-id 143                   # native MON on Monad
purr wallet balance --token USDC --chain-id 143                            # USDC on Monad
purr wallet balance --chain-type ethereum --chain-id 10                    # native ETH on OP Mainnet
purr wallet balance --chain-type ethereum --chain-id 130                   # native ETH on Unichain
purr wallet balance --chain-type ethereum --chain-id 8453                  # native ETH on Base
purr wallet balance --chain soneium                                      # native ETH on Soneium (1868)
purr wallet balance --chain soneium --token WETH                         # WETH on Soneium
purr wallet balance --chain-id 1868 --token <CA>                          # ERC-20 on Soneium; exact contract address
purr wallet balance --chain-type ethereum --chain-id 5042                  # native USDC on Arc (18 decimals)
purr wallet balance --chain arc --token USDC                              # native USDC; CLI with Arc ticker support
purr wallet balance --chain-id 5042 --token <CA>                           # ERC-20 on Arc; uses contract decimals
purr wallet balance --token USDT --chain-id 56                             # USDT on BSC
purr wallet balance --token USDC --chain-id 8453                           # USDC on Base
purr wallet balance --chain-type ethereum --chain-id 196                   # native OKB on X Layer
purr wallet balance --token USDT0 --chain-id 196                           # USDT0 on X Layer
purr wallet balance --token USDC --chain-id 196                            # USDC on X Layer
purr wallet balance --token USDG --chain-id 196                            # USDG on X Layer
purr wallet balance --chain-type ethereum --chain-id 4663                  # native ETH on Robinhood Chain
purr wallet balance --chain-id 4663 --token 0x0Bd7D308f8E1639FAb988df18A8011f41EAcAD73  # WETH on Robinhood Chain
purr wallet balance --chain-id 4663 --token 0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168  # USDG on Robinhood Chain
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
