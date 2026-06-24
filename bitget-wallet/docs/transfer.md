# Transfer (Token Transfer) Domain Knowledge

This document describes the **Transfer flow** for on-chain token transfers via the ToB Transfer API (`ms-user-go`). The server handles transaction construction, broadcasting, and on-chain status tracking. Use `purr bitget transfer-execute` for supported EVM makeTransferOrder + platform-wallet signing + submitTransferOrder.

**MUST read this file before calling any transfer API** (`purr bitget transfer-execute` or `get-transfer-order`).

## Flow Overview

| Step | Interface / Script | Description |
|------|--------------------|-------------|
| 0 | `batch-v2` | **Pre-check**: verify sender has enough token balance and (if not gasless) enough native gas |
| 1+2+3 | **`purr bitget transfer-execute`** | makeTransferOrder + platform-wallet sign + submitTransferOrder in one run |
| 4 | `get-transfer-order` | Poll order status until SUCCESS or FAILED |

### EVM Transfer Execution

Use `purr bitget transfer-execute` for supported EVM transfers. It creates the
transfer order, checks the platform signer matches `--from-address`, signs with
the platform wallet, and submits immediately.

```bash
# EVM token transfer (standard)
purr bitget transfer-execute \
  --chain eth \
  --contract 0xdAC17F958D2ee523a2206206994597C13D831ec7 \
  --from-address 0xAbC... --to-address 0xDeF... \
  --amount 100

# EVM gasless transfer
purr bitget transfer-execute \
  --chain base \
  --contract 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --from-address 0xAbC... --to-address 0xDeF... \
  --amount 50 --gasless true
```

Solana transfers, Solana gasless partial-sign, Social Login Wallet flows, Tron
execution, and Morph AltFee source signing are out of scope.

## Pre-Transfer Checks

Before any transfer, the agent **must**:

1. **Balance check**: Run `batch-v2` to verify sender has enough token balance for the transfer amount.
2. **Gas check** (if not gasless): Verify native token balance is sufficient for gas fees.
3. **estimateRevert guard**: `purr bitget transfer-execute` checks `data.estimateRevert` and aborts if `true` (insufficient balance, contract revert, etc.).

```bash
python3 scripts/bitget-wallet-agent-api.py batch-v2 \
  --chain <chain> --address <sender> --contract "" --contract <tokenContract>
```

## Gasless Transfer

Gasless mode allows token transfers without holding native gas tokens (ETH, SOL, BNB, etc.). Gas fees are paid from the user's stablecoin balance (USDT/USDC).

### How to Enable

Pass `--gasless true` to `purr bitget transfer-execute`. The API parameter `noGas=true` is sent automatically.

### Supported Chains and Pay Tokens

| Chain | USDT | USDC |
|-------|------|------|
| eth | `0xdAC17F958D2ee523a2206206994597C13D831ec7` | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| bnb | `0x55d398326f99059fF775485246999027B3197955` | `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d` |
| base | `0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| arbitrum | `0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9` | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |
| matic | `0xc2132D05D31c914a87C6611C10748AEb04B58e8F` | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| morph | `0xe7cd86e13AC4309349F30B3435a9d337750fC82D` | `0xCfb1186F4e93D60E60a8bDd997427D1F33bc372B` |
| sol | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |

### Token Selection

- **Automatic** (default): Server selects the best pay token from the whitelist (sufficient balance + stable price).
- **Manual**: Pass `--gasless-pay-token <contract>` to specify a particular token.

### Gasless Response Fields

When gasless is available, `data.noGas` contains:

| Field | Description |
|-------|-------------|
| `available` | `true` if gasless is active |
| `payToken` | Contract address of the selected pay token |
| `payTokenSymbol` | Symbol (e.g. "USDC") |
| `payAmount` | Gas fee amount deducted from token balance |
| `payTokenPriceUsd` | Current USD price of pay token |
| `need7702Auth` | EVM only: `true` if first-time 7702 binding needed |
| `acceptableTokens` | Full whitelist of eligible pay tokens |

### Gasless Unavailable — Explicit Fallback

When `--gasless true` is requested but gasless is not available (chain not supported, amount below threshold, no eligible pay token with sufficient balance), `purr bitget transfer-execute` **does not silently fall back** to a standard transfer.

Instead, it stops and reports that Bitget did not mark gasless as available. Ask
the user whether they want to retry without gasless.

**Scenarios where gasless is not available:**
- The chain is not in the gasless whitelist
- Transfer amount (USD value) is below the threshold
- No pay token has sufficient balance or queryable price
- `noGas` was not requested

**Agent rule:** If the script aborts due to gasless unavailable, inform the user and ask whether they want to retry without `--gasless` (standard transfer). Do NOT automatically retry.

### EIP-7702 Override

> **DANGER: High-impact account-level change.** Overwriting an existing EIP-7702 binding is permanent and cannot be undone. The previous third-party binding will be lost.

If the sender address is already bound to a third-party EIP-7702 contract, gasless will fail with **error code 30108**. To proceed:

1. Inform the user: *"Your address has an existing third-party EIP-7702 binding. Gasless transfer requires replacing it. This is permanent."*
2. Only after explicit user confirmation, re-run with `--override-7702 true`.

The response `noGas.warn` will contain a warning message — **always display it to the user**.

**Agent rule:** NEVER pass `--override-7702` without first explaining the risk and obtaining explicit user confirmation ("yes, override my existing 7702 binding").

## Execution Source Types

The `source.type` field determines whether `purr bitget transfer-execute` can
execute the transfer:

| source.type | Signing Method | Applicable Chains |
|-------------|---------------|-------------------|
| `evm_legacy` | Supported by `purr bitget transfer-execute` | bnb |
| `evm_1559` | Supported by `purr bitget transfer-execute` | eth, base, arbitrum, matic, morph |
| `evm_7702` | Supported by `purr bitget transfer-execute`; signs `msgToSign[].hash`, returns `JSON.stringify(msgs)` | EVM gasless |
| `evm_morph_altfee` | Out of scope | morph AltFee |
| `sol_raw` | Out of scope | sol standard |
| `sol_partial` | Out of scope | sol gasless |

### EVM 7702 Detail

`purr bitget transfer-execute` handles EVM 7702 source data internally.
Do not manually sign or submit `source.evm7702.msgToSign`.

The `source.evm7702.msgToSign` array can contain 1-2 items:

1. **`msgType=auth`** (first-time only): Authorization to bind 7702 contract. Sign `hash` with ECDSA secp256k1 (`unsafe_sign_hash`).
2. **`msgType=call`**: Transfer execution call. Sign `hash` with eth_sign (`unsafe_sign_hash`).

The CLI fills each item's `sig` field and submits the required payload.

Both auth + call signing and the transfer itself are bundled into **one on-chain transaction** (EIP-7702 Type-4 tx) by the server.

### Solana Partial Signing

Solana partial signing is out of scope for this packaged skill.

For gasless Solana transfers:
1. Server constructs the transaction with a feePayer (gas account) and pre-signs slot 0
2. `source.sol.rawTx` contains the base58 partial-signed transaction
3. Client adds user signature to slot 1 (Ed25519 partial-sign)
4. The fully-signed transaction is submitted

**blockhash expiry**: Solana `recentBlockhash` expires after ~60 seconds (~150 slots).

## Morph AltFee

When `chain=morph` and the response contains both `source` (evm_1559) and `altFeeSource` (evm_morph_altfee), two gas payment options exist:

| Option | Source Field | Gas Payment |
|--------|-------------|-------------|
| Standard | `source` (evm_1559) | ETH |
| AltFee | `altFeeSource` (evm_morph_altfee) | USDT/USDC/BGB |

**AltFee token contracts (Morph mainnet, chainId=2818):**

| feeTokenID | Symbol | Contract |
|-----------|--------|----------|
| 1 | USDT | `0xc7D67A9CBB121B3B0b9c053Dd9F469523243379A` |
| 2 | USDC | `0xE34C91815d7FC18A9E2148bcD4241D0a5848b693` |
| 3 | BGB | `0x55d1F1879969bDbb9960d269974564C58dbc3238` |

The response `altFee.feeTokenID` indicates which token was selected by the server. The `altFee` object also includes `feeTokenContract`, `feeTokenSymbol`, `feeTokenDecimal`, and `feeTokenPrice`.

`purr bitget transfer-execute` uses the standard `source` when it is `evm_1559`.
Morph AltFee signing is out of scope.

## Chain-Specific Notes

### EVM (eth/bnb/base/arbitrum/matic/morph)
- **Native token transfer**: `contract=""`, `source.evm.to` = receiver, `source.evm.data="0x"`
- **Token transfer**: `contract` = ERC-20 address, `source.evm.to` = contract, `data` = `transfer(address,uint256)` calldata
- **EIP-1559** (eth/base/arbitrum/matic/morph): `fee.eip1559` is non-null
- **L2 chains** (base/arbitrum/morph): `fee.l1FeeMax` is non-empty (L1 calldata fee)
- **Gasless**: Only for token transfers (`contract` must be non-empty; native token gasless is not supported)

### Solana (sol)
- **Native SOL transfer**: `contract=""`
- **SPL Token transfer**: `contract` = SPL Token Mint address
- **Fee units**: `fee.stdPriPrice` (lamports/CU), `fee.stdPriLimit` (compute unit limit)
- **blockhash expiry**: ~60 seconds. Solana signing is out of scope here.

### Memo Field
The `--memo` parameter is passed through to `ms_chain` for on-chain inclusion. Chain support varies — not all chains support memo. Pass `""` or omit for no memo.

## Order Status

| Status | Description | txid |
|--------|-------------|------|
| `PENDING` | Order created, not yet broadcast | — |
| `PROCESSING` | Transaction broadcast, awaiting chain confirmation | present |
| `SUCCESS` | Transaction confirmed on-chain | present |
| `FAILED` | Transaction failed (broadcast failure, chain revert, etc.) | may be present |

- Status comes from real-time chain query, not database cache
- Gasless orders may have `txid` in format `getgas_task_xxx` (gas-account task ID, not final chain hash)
- When `orderStatus=FAILED`, the `failReason` field contains the failure description
- `gasAccountData` in the API response is for server internal use; clients should ignore it
- Poll `get-transfer-order` until terminal status (SUCCESS/FAILED)

## Error Codes

| Code | Description | Action |
|------|-------------|--------|
| 0 | Success | — |
| 30101 | Missing or invalid parameters | Check request params; `msg` contains the missing field |
| 30102 | Unsupported chain | Verify chain code |
| 30103 | Insufficient balance | Top up or enable gasless |
| 30104 | estimateRevert (predicted failure) | Do not proceed; investigate root cause |
| 30105 | orderId not found | Check orderId or re-create order |
| 30106 | Order already submitted | Do not resubmit; orderId is single-use |
| 30107 | Invalid gasless signature (7702 auth failed) | Retry through `purr bitget transfer-execute`; do not construct signatures manually |
| 30108 | Third-party 7702 binding exists, override7702=false | Prompt user, re-request with `--override-7702` |
| 30201 | ms_chain service error | Retry; `msg` has details |
| 30202 | gas-account service unavailable | Fall back to standard transfer |
| 30500 | Internal error | Contact backend; `msg` has details |

## Timing Constraints

- **EVM orderId**: No hard expiry, but nonce may be consumed. Recommend submit within **10 minutes**.
- **Solana blockhash**: Expires in ~**60 seconds**. Solana signing is out of scope here.
- **orderId is single-use**: Once submitted successfully, the same orderId cannot be resubmitted.
