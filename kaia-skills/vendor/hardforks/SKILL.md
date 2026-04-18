---
name: hardforks
description: Kaia hardfork history and upcoming upgrades. Use when asked about Kaia network changes, breaking changes, or upgrade timeline. Focus on Kaia-era forks (post-2024), not legacy Klaytn forks.
disable-model-invocation: true
user-invocable: false
---

# Hardforks & Upgrades — Kaia

Focus on **Kaia-era changes**. Legacy Klaytn forks (Magma, Kore, etc.) are historical — don't over-emphasize them.

> Source: https://docs.kaia.io/misc/kaia-history/ + https://github.com/kaiachain/kaia/releases

---

## Kaia Transition (v1.0.x) — Aug 2024

The fork that launched Kaia from Klaytn.

| Detail  | Value                             |
| ------- | --------------------------------- |
| Kairos  | Block #156,660,000 (Jun 13, 2024) |
| Mainnet | Block #162,900,480 (Aug 29, 2024) |

Key changes:

- **Klaytn → Kaia** rebrand at protocol level
- TreasuryRebalanceV2 + token allocation (KIP-160)
- **Transaction priority fee (tip)** introduced — KIP-162, similar to EIP-1559
- PublicDelegation + CnStakingV3 (KIP-163)
- Staking update interval → 1 block

---

## Prague (v2.0.x) — Jul 2025

Major EVM compatibility upgrade + new Kaia features.

| Detail  | Value                             |
| ------- | --------------------------------- |
| Kairos  | Block #187,930,000 (Jun 10, 2025) |
| Mainnet | Block #190,670,000 (Jul 17, 2025) |

Key changes:

- BLS12-381 precompiles (EIP-2537)
- Historical blockhash system contract (EIP-2935)
- **SetCode transaction type** — EIP-7702 / KIP-228
- Updated calldata gas price (EIP-7623 / KIP-223)
- **Consensus Liquidity** (KIP-226)
- **Gas Abstraction** — paying gas fees with tokens (KIP-247)

---

## v2.1.0 — Oct 2025 (no hardfork)

- **MEV Auction support** (KIP-249) — BidTx, Auctioneer integration
- API/storage improvements

---

## Osaka (v2.2.x) — Apr 2026 ⚠️ UPCOMING

| Detail  | Value                                 |
| ------- | ------------------------------------- |
| Kairos  | Block #209,134,000 (Feb 11, 2026)     |
| Mainnet | Block #213,333,000 (est. Apr 7, 2026) |

**⚠️ Breaking change: Contract code at address(0) will be removed.**

Key changes:

- **Blob transactions** (KIP-279, based on EIP-4844 / EIP-7594)
- BLOBHASH and BLOBBASEFEE opcodes
- Blob sidecar storage and P2P sharing
- **Address(0) conversion** from contract to EOA
- Flexible reward mechanism
- MODEXP gas repricing (EIP-7883)
- CLZ opcode (EIP-7939)
- MODEXP input upper bound (EIP-7823)

**Migration required:** If any contract depends on bytecode at address(0), it must be updated before the hardfork.

---

## Legacy Klaytn Forks (for reference only)

These are pre-Kaia forks. Don't emphasize these unless specifically asked about Klaytn history.

- **Magma** — Introduced dynamic gas fee (KIP-71)
- **Kore** — On-chain governance params (KIP-81), staking changes
- **Shanghai/Cancun** — EVM alignment with Ethereum
- **Randao** — On-chain randomness (KIP-113/114)

Full Klaytn fork history: https://docs.kaia.io/misc/klaytn-history/
