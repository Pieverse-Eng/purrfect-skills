---
name: gas
description: Kaia gas fees, costs, and unit system. Use when asked about transaction costs, gas pricing, or KAIA denominations.
disable-model-invocation: true
user-invocable: false
---

# Gas & Costs — Kaia

## Units — NOT peb/ston/KLAY

| Unit     | Value     | Equivalent                      |
| -------- | --------- | ------------------------------- |
| **kei**  | 1 kei     | Smallest unit (like wei)        |
| **Gkei** | 10^9 kei  | Like gwei — used for gas prices |
| **KAIA** | 10^18 kei | 1 KAIA                          |

**"peb" and "ston" are deprecated Klaytn names.** Use kei, Gkei, KAIA.

## Gas Fee Model

Kaia's gas pricing has evolved through multiple phases:

1. **Fixed unit price** (early Klaytn) — governance-set fixed gas price
2. **Dynamic base fee** (post-Magma, KIP-71) — adjusts based on congestion, with fee burning
3. **Priority fee/tips** (post-Kaia Transition, KIP-162) — EIP-1559-style tips added

Current model: dynamic base fee + optional priority fee. Very similar to Ethereum EIP-1559 but with Kaia-specific parameters.

## What Things Cost

KAIA transfers use 21,000 gas (same as Ethereum).

At Kaia's low gas prices, a simple transfer costs **fractions of a cent** — orders of magnitude cheaper than Ethereum mainnet.

Verify current gas price: `cast rpc eth_gasPrice --rpc-url https://public-en.node.kaia.io`

## Gas Abstraction (KIP-247)

Users can pay gas with **ERC-20 tokens** instead of KAIA. See [gas-abstraction/SKILL.md](../gas-abstraction/SKILL.md).
