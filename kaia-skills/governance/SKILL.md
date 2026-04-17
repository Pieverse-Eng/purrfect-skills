---
name: governance
description: Kaia governance structure, PGT framework, and tokenomics. Use when asked about Kaia governance, validators, staking, token distribution, or the permissionless transition. Information is current as of March 2026.
disable-model-invocation: true
user-invocable: false
---

# Governance & Tokenomics — PGT Framework

Kaia is in the middle of a **major structural transition**. If your knowledge says "Kaia uses a permissioned Governance Council" — that's changing.

---

## PGT (Permissionless · Governance · Tokenomics)

A structural strategy to transform Kaia from a stable permissioned chain to a **performance-based public L1**.

### Timeline

| When         | What                                                                 |
| ------------ | -------------------------------------------------------------------- |
| Mar–Apr 2026 | GP-20/GP-21 proposals, Permissionless Phase 1                        |
| Jul 2026     | Contribution Reward (CR) system live, performance-based distribution |
| Sep 2026     | **Full Permissionless transition**                                   |

---

## GP-20: Permissionless Network Policy

Key structural changes:

1. **Validator participation opens** — anyone meeting qualifications can validate
2. **Validator ≠ GC** — roles structurally separated:
   - Validator = consensus participation (network operations)
   - GC = governance decisions (policy, direction, ecosystem)
3. **Auto GC registration** — condition-based with challenge verification (no more individual approval process)
4. **Top 50 validators** participate in consensus (by total staking amount)
5. **VRank** — validator performance evaluation system, manages eligibility

---

## GP-21: Tokenomics Reform

### Current Block Reward Structure (being reformed)

9.6 KAIA per block (~4.87% annual inflation):

- **50%** → Validators & Community
  - 20% Block Creator (Proposal Reward — **being ended**)
  - 80% Staking Reward
- **25%** → KEF (Kaia Ecosystem Fund)
- **25%** → KIF (Kaia Infrastructure Fund)

### What's Changing

**Proposal Reward (PR) → ENDED**

- Distributed uniformly regardless of contribution
- No incentive for ecosystem growth

**Contribution Reward (CR) → NEW**

- Rewards based on **measurable on-chain contribution** (TVL, economic activity)
- Unearned CR is **burned immediately** → deflationary effect
- Phased roadmap: Distribution (now) → Supply review (next) → Buyback & Burn (long-term)

### CR Operating Parameters (initial)

| Parameter                | Value                                     |
| ------------------------ | ----------------------------------------- |
| USDT deposit limit ratio | 10 KAIA : 1 USDT (based on staked amount) |
| CR Commission (min)      | 20% (adjustable per GC)                   |
| Initial TVL target       | $50M USDT                                 |
| Designated protocols     | SuperEarn, Unifi                          |
| CR reward budget         | 30M KAIA total                            |

CR requires KAIA staking + optional USDT deposit for boosting rewards.

---

## Governance Voting

- Voting on [Kaia Square](https://square.kaia.io/)
- Proposals discussed on [Governance Forum](https://govforum.kaia.io/)
- Voting rights proportional to staked KAIA with a **voting cap** (prevents majority suppression)

---

## Key Facts for Developers

- Kaia is **NOT yet permissionless** — transitioning by Sep 2026
- Current validator count is limited (GC members only) but opening up
- Token economics are shifting from "rewards for participation" to "rewards for contribution"
- If building staking/delegation UIs: account for PublicDelegation (KIP-163), CnStakingV3
- Governance params are on-chain via KIP-81 GovParam (`0x362976Cc2Ef6751DE6bf6008e3E90e1e02deCa51`)
