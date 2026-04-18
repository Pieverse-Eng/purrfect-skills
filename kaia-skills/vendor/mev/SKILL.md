---
name: mev
description: KIP-249 MEV Auction system on Kaia — slot-based backrun auction with hidden bidding. Use when developers ask about MEV on Kaia, searcher strategies, or the auction system. NOT like Ethereum's PBS/Flashbots.
disable-model-invocation: true
user-invocable: false
---

# MEV Auction (KIP-249) — Slot-Based Auction on Kaia

Kaia's MEV system is fundamentally different from Ethereum's PBS/Flashbots model. Do NOT apply Ethereum MEV assumptions to Kaia.

---

## How It Works

### Core Concept: Slot-Based Adjacency

If a target transaction is at index **i** in the block, the winning backrun is placed at **i+1**. This is enforced at the protocol level.

### Auction Flow

```
1. Searcher deposits KAIA in AuctionDepositVault (covers bid + gas)
       ↓
2. Searcher identifies backrun opportunity on a target tx
       ↓
3. Searcher submits hidden bid to off-chain Auctioneer
   (includes: targetTxHash, bid amount, backrun calldata)
       ↓
4. Auctioneer selects highest valid bid per block
       ↓
5. Auctioneer sends winning bid to block proposer
       ↓
6. Proposer crafts BidTx (signed by proposer, not searcher)
       ↓
7. Block includes: [..., targetTx(i), BidTx(i+1), ...]
       ↓
8. AuctionEntryPoint executes atomically:
   - Collects bid payment from searcher deposit
   - Executes backrun logic
   - Refunds gas to proposer
       ↓
9. Bid fees → AuctionFeeVault (governance-controlled distribution)
```

---

## Key Rules

- **Hidden bidding** — searchers submit bids privately to Auctioneer
- **One winning bid per searcher per block**
- **Early deadline** — proposer enforces tx cutoff to allow auction time
- **If target tx not in block** → backrun tx is dropped
- **If target tx reverts** → BidTx is discarded (no balance loss for proposer)
- **If target tx succeeds** → bid is paid regardless of backrun execution result
- **Deposit cooldown** — prevents immediate withdrawal after bidding

---

## Contracts

### Mainnet

| Contract            | Address                                      |
| ------------------- | -------------------------------------------- |
| AuctionEntryPoint   | `0xFc5c1C92d8DE06F7143f71FeA209e04042dcff82` |
| AuctionDepositVault | `0x0E66b62273Cc99BC519DD4dD0C0Cf689dd7b9876` |
| AuctionFeeVault     | `0x303BB9c9FF4Aa656ac4c8e9f99F8E4C133FDa665` |

### Kairos Testnet

| Contract            | Address                                      |
| ------------------- | -------------------------------------------- |
| AuctionEntryPoint   | `0x2fF66A8b9f133ca4774bEAd723b8a92fA1e28480` |
| AuctionDepositVault | `0x2A168bCdeB9006eC6E71f44B7686c9a9863C1FBc` |
| AuctionFeeVault     | `0xE4e7d880786c53b6EA6cfA848Eb3a05eE97b2aCC` |

---

## BidTx Parameters

```
BidDetails:
  target_tx_hash    # Hash of the target transaction
  block_num         # Target block number
  sender            # Searcher address (must have deposit)
  nonce             # Searcher's nonce in AuctionEntryPoint
  to_addr           # Target address of backrun logic
  call_gas_limit    # Gas limit for backrun (max: 10,000,000)
  call_data         # Backrun calldata (max: 64KB)
  bid_amount        # Bid in kei
  from_signature    # EIP-712 signed by searcher
  auc_signature     # EIP-191 signed by auctioneer
```

---

## vs Ethereum MEV

| Aspect           | Kaia KIP-249                 | Ethereum PBS/Flashbots      |
| ---------------- | ---------------------------- | --------------------------- |
| Auction type     | Slot-based backrun only      | Full block building         |
| Adjacency        | Enforced (i, i+1)            | Builder discretion          |
| Bidding          | Hidden, off-chain Auctioneer | MEV-Boost relay             |
| Who builds       | Proposer (original)          | Separate builder            |
| Deposit required | Yes (AuctionDepositVault)    | No                          |
| Fee destination  | Governance-controlled vault  | Proposer directly           |
| Scope            | Backrun only                 | Frontrun, backrun, sandwich |
