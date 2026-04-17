---
name: accounts
description: Kaia's unique account model — key-address decoupling, AccountKey types, and role-based keys. Use when working with account creation, key management, or account updates on Kaia.
disable-model-invocation: true
user-invocable: false
---

# Accounts — Kaia's Key-Address Decoupling

Unlike Ethereum, Kaia **decouples private keys from addresses**. You can change your key without changing your address. This enables key rotation, multi-sig, and role-based access — all at the protocol level.

## AccountKey Types

| Type                           | Description                                                              |
| ------------------------------ | ------------------------------------------------------------------------ |
| **AccountKeyNil**              | Empty/unset. Account retains existing key.                               |
| **AccountKeyLegacy**           | Ethereum-compatible. Address derived from key. Default for new accounts. |
| **AccountKeyPublic**           | Single key, decoupled from address. Enables key rotation.                |
| **AccountKeyFail**             | All transactions fail. Freezes the account.                              |
| **AccountKeyWeightedMultiSig** | Multiple keys with weights + threshold. Protocol-level multi-sig.        |
| **AccountKeyRoleBased**        | Different keys for different roles (see below).                          |

## Role-Based Keys

| Role                  | Index | Used For                                                 |
| --------------------- | ----- | -------------------------------------------------------- |
| **RoleTransaction**   | 0     | Signing regular transactions (transfers, contract calls) |
| **RoleAccountUpdate** | 1     | Signing account key updates only                         |
| **RoleFeePayer**      | 2     | Signing as fee payer in fee-delegated transactions       |

Each role can independently use any AccountKey type. Example: multi-sig for account updates, single key for daily transactions.

## Wallet Key Format

`0x{private key}0x{type}0x{address}`

Exists because key and address are independent — you need both stored together. Type is `00` (reserved for future types).

## Updating Account Keys

Use `TxTypeAccountUpdate` to change an account's key. This is a Kaia-specific transaction type that doesn't exist in Ethereum.

```javascript
const { Wallet, JsonRpcProvider } = require("@kaiachain/ethers-ext/v6");

const wallet = new Wallet(privateKey, provider);
const tx = {
  type: TxType.AccountUpdate,
  from: wallet.address,
  key: { type: AccountKeyType.Public, key: newPublicKey },
};
await wallet.sendTransaction(tx);
```
