---
name: fee-delegation
description: Kaia's protocol-native fee delegation system. Use when building gasless UX, implementing gas sponsorship, or working with fee-delegated transactions.
disable-model-invocation: true
user-invocable: false
---

# Fee Delegation — Protocol-Native Gas Sponsorship

Fee delegation is Kaia's killer feature. A third party pays gas fees for the user **at the protocol level** — no smart contracts needed.

**NOT ERC-4337.** No bundlers, no paymasters, no UserOperations. Two signatures, one transaction.

---

## How It Works

1. Sender creates a fee-delegated transaction type
2. Sender signs → **sender's signature** (authorizes the action)
3. Transaction sent to fee payer (off-chain coordination)
4. Fee payer signs → **fee payer's signature** (authorizes gas payment)
5. Transaction submitted with **both signatures**
6. Gas deducted from **fee payer's account**, not sender's

---

## Full vs Partial Fee Delegation

| Type        | Fee Payer Covers        | Tx Type Suffix             |
| ----------- | ----------------------- | -------------------------- |
| **Full**    | 100% of gas             | `FeeDelegated...`          |
| **Partial** | Specified ratio (1-99%) | `FeeDelegated...WithRatio` |

Partial delegation uses a `feeRatio` parameter. Example: `feeRatio: 70` → fee payer pays 70%, sender pays 30%.

---

## Fee-Delegated Transaction Types

**Full delegation:**

1. `TxTypeFeeDelegatedValueTransfer`
2. `TxTypeFeeDelegatedValueTransferMemo`
3. `TxTypeFeeDelegatedSmartContractDeploy`
4. `TxTypeFeeDelegatedSmartContractExecution`
5. `TxTypeFeeDelegatedAccountUpdate`
6. `TxTypeFeeDelegatedCancel`

**Partial delegation (WithRatio):**
7–12. Same as above with `WithRatio` suffix

---

## Code Example (ethers-ext)

```javascript
const { Wallet, JsonRpcProvider } = require("@kaiachain/ethers-ext/v6");

// Sender creates and signs
const sender = new Wallet(senderPrivKey, provider);
const tx = {
  type: TxType.FeeDelegatedValueTransfer,
  to: recipientAddr,
  value: parseKaia("1"),
  from: sender.address,
};
const senderTx = await sender.signTransaction(tx);

// Fee payer signs and sends
const feePayer = new Wallet(feePayerPrivKey, provider);
const sentTx = await feePayer.sendTransactionAsFeePayer(senderTx);
```

---

## Use Cases

- **User onboarding** — new users with no KAIA
- **dApp-sponsored transactions** — app pays gas for users
- **B2B gas services** — enterprise gas payment
- **Subsidized UX** — partial delegation for gradual transition

## Also See

- [Gas Abstraction](../gas-abstraction/SKILL.md) — pay gas with ERC-20 tokens (KIP-247)
