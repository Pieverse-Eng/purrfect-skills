# Aster Deposit Fund

## Overview

Use `purr aster deposit` to build or execute Aster treasury deposit steps through
the Pieverse managed wallet. Do not use private-key deposit scripts, and do not
ask the user for a deposit private key.

Supported chains:

| Chain | Chain ID |
| --- | ---: |
| Ethereum | 1 |
| BNB Smart Chain | 56 |
| Arbitrum One | 42161 |

## Workflow

1. Identify the source chain.
2. Identify the deposit asset: native token, supported ticker, or raw ERC-20
   contract address.
3. Convert the requested amount to raw base units for `--amount-wei`.
4. Run `purr aster deposit` without `--execute` to inspect the generated steps.
5. Show the user the chain, token, raw amount, wallet, broker ID, and whether an
   approval step may be required.
6. Ask for explicit confirmation before broadcasting.
7. After confirmation, rerun the same command with `--execute`.
8. Return the transaction hash or hashes and execution status.

## Syntax

```bash
purr aster deposit \
  --token <token_ticker_or_address> \
  --amount-wei <amount_wei> \
  --wallet <wallet_address> \
  --chain-id <chain_id> \
  [--broker <broker_id>] \
  [--execute]
```

## Parameters

| Parameter | Required? | Description |
| --- | --- | --- |
| `--token <token_ticker_or_address>` | Required | Asset to deposit. Accepts a native token ticker such as `ETH` or `BNB`, a supported ticker resolved by `purr`, or a raw ERC-20 contract address. |
| `--amount-wei <amount_wei>` | Required | Raw base-unit amount to deposit. Do not pass a human decimal amount. |
| `--wallet <wallet_address>` | Required | User wallet address that will fund the deposit. |
| `--chain-id <chain_id>` | Required | Deposit source chain. Supported values are `1`, `56`, and `42161`. |
| `--broker <broker_id>` | Optional | Aster broker ID. Defaults to `1`. Only change it when the user explicitly provides a broker ID. |
| `--execute` | Optional | Signs and broadcasts the generated steps through the Pieverse managed wallet. Omit it to preview/build steps only. |

## Commands

```bash
purr aster deposit --token BNB --amount-wei 1000000000000000 --wallet 0x... --chain-id 56
purr aster deposit --token BNB --amount-wei 1000000000000000 --wallet 0x... --chain-id 56 --execute
purr aster deposit --token 0x... --amount-wei 1000000 --wallet 0x... --chain-id 56
purr aster deposit --token 0x... --amount-wei 1000000 --wallet 0x... --chain-id 56 --broker 1 --execute
```

## Response Shape

Without `--execute`, success prints a `TxStep[]` JSON object.

Native deposit preview:

```json
{
  "steps": [
    {
      "to": "0x128463A60784c4D3f46c23Af3f65Ed859Ba87974",
      "data": "0x...",
      "value": "0x38d7ea4c68000",
      "chainId": 56,
      "label": "Aster treasury deposit (native)"
    }
  ]
}
```

ERC-20 deposit preview usually includes an approval step followed by a deposit
step:

```json
{
  "steps": [
    {
      "to": "0xTokenAddress",
      "data": "0x...",
      "value": "0x0",
      "chainId": 56,
      "label": "Approve token for Aster treasury",
      "conditional": {
        "type": "allowance_lt",
        "token": "0xTokenAddress",
        "spender": "0x128463A60784c4D3f46c23Af3f65Ed859Ba87974",
        "amount": "1000000"
      }
    },
    {
      "to": "0x128463A60784c4D3f46c23Af3f65Ed859Ba87974",
      "data": "0x...",
      "value": "0x0",
      "chainId": 56,
      "label": "Aster treasury deposit (ERC-20)"
    }
  ]
}
```

With `--execute`, success prints the platform wallet execution result:

```json
{
  "results": [
    {
      "stepIndex": 0,
      "label": "Aster treasury deposit (native)",
      "hash": "0x...",
      "status": "success"
    }
  ],
  "from": "0x...",
  "chainId": 56,
  "chainType": "ethereum"
}
```

ERC-20 execution can return multiple results, one for approval and one for the
deposit. Conditional approval steps may be skipped when allowance is already
sufficient.

## Response Errors

| Error Message | Meaning |
| --- | --- |
| `Missing required argument: --token` | Deposit token was not provided. |
| `Missing required argument: --amount-wei` | Raw deposit amount was not provided. |
| `Missing required argument: --wallet` | Funding wallet address was not provided. |
| `Missing required argument: --chain-id` | Source chain was not provided. |
| `Unsupported chain for Aster deposit: ...` | Chain ID is not one of `1`, `56`, or `42161`. |
| `Invalid wallet` | `--wallet` is not a valid EVM address. |
| `Invalid token` | Raw ERC-20 token address is invalid. |
| `Invalid --broker` | Broker ID is not a non-negative integer. |
| `Unknown token ...` or `No token registry ...` | Ticker could not be resolved on the selected chain; use a raw token address. |
| `No steps found in JSON. Check purr output for errors.` | Execution was requested but the generated step output was empty or malformed. |
| `Wallet service error`, `transaction rejected`, or `chain state rejected` | Platform wallet, signer, or chain rejected the transaction. |
