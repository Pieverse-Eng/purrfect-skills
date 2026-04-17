---
name: transactions
description: Kaia transaction types — far more than Ethereum's 3 types. Use when working with Kaia-specific transaction types or understanding the tx type system.
disable-model-invocation: true
user-invocable: false
---

# Transaction Types — Kaia

Kaia has **20+ transaction types** vs Ethereum's 3 (legacy, EIP-2930, EIP-1559). Each operation has dedicated types optimized for gas and functionality.

## Transaction Type Matrix

| Category                   | Basic                        | Fee Delegated         | Partial Fee Delegated |
| -------------------------- | ---------------------------- | --------------------- | --------------------- |
| **Legacy**                 | TxTypeLegacyTransaction      | —                     | —                     |
| **ValueTransfer**          | TxTypeValueTransfer          | TxTypeFeeDelegated... | ...WithRatio          |
| **ValueTransferMemo**      | TxTypeValueTransferMemo      | TxTypeFeeDelegated... | ...WithRatio          |
| **SmartContractDeploy**    | TxTypeSmartContractDeploy    | TxTypeFeeDelegated... | ...WithRatio          |
| **SmartContractExecution** | TxTypeSmartContractExecution | TxTypeFeeDelegated... | ...WithRatio          |
| **AccountUpdate**          | TxTypeAccountUpdate          | TxTypeFeeDelegated... | ...WithRatio          |
| **Cancel**                 | TxTypeCancel                 | TxTypeFeeDelegated... | ...WithRatio          |

Ethereum-compatible types (Type 0, 1, 2) are also fully supported.

## Key Differences from Ethereum

- **`from` field is explicit** — required in all Kaia tx types because addresses are decoupled from keys
- **Fee delegation variants** — every tx type has full + partial fee delegation versions
- **AccountUpdate** — unique to Kaia, changes the account's key(s)
- **Cancel** — explicitly cancels a pending tx by nonce
- **ValueTransferMemo** — value transfer with attached data (separate from contract execution)

## Signature Validation

Because Kaia decouples keys from addresses, signature validation uses the **AccountKey** associated with the `from` address, not the address derivation. The `from` field is crucial.

For fee-delegated transactions, **two signatures** are validated:

1. Sender's signature (from sender's AccountKey)
2. Fee payer's signature (from fee payer's AccountKey, specifically RoleFeePayer if role-based)
