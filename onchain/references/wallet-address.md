# Wallet Address

Use this section when the user needs their wallet address. Choose EVM for
EVM-compatible chains such as BSC, Ethereum, Base, Arbitrum, Optimism, and
Polygon. Choose Solana for Solana.

## Workflow

1. Identify whether the user wants an EVM address or Solana address.
2. Run the matching command.
3. Return the address and, for EVM, mention that it works across EVM chains.

## Syntax

```bash
purr wallet address [--chain-type <ethereum|solana>] [--chain-id <chain_id>]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--chain-type <ethereum|solana>` | Optional, recommended | Selects the wallet family. Use `ethereum` for the EVM address and `solana` for the Solana address. |
| `--chain-id <chain_id>` | Optional | Passes a numeric EVM chain ID to the wallet API when needed. For normal address checks, prefer `--chain-type`. |

## Commands

```bash
purr wallet address --chain-type ethereum # EVM wallet address
purr wallet address --chain-type solana   # Solana wallet address
```

## Response Shape

Success prints one JSON object to stdout:

```json
{
  "address": "0x... or base58...",
  "chainId": 56,
  "chainType": "ethereum",
  "createdNow": false
}
```

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Unsupported chain type. Supported: ...` | The requested `--chain-type` is not supported. |
| `Unsupported chain. Supported: ...` | The requested EVM `--chain-id` is not supported. |
| `User not found`, `Wallet provider state invalid`, `Wallet service error`, or `Internal server error` | Auth, instance, provider, or wallet service failure. |
