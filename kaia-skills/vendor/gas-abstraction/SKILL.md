---
name: gas-abstraction
description: KIP-247 Gasless Transaction — pay gas fees with ERC-20 tokens on Kaia without holding any KAIA. Use when developers ask about gasless UX, token-based gas payment, or onboarding users who only have bridged stablecoins.
disable-model-invocation: true
user-invocable: false
---

# Gas Abstraction (KIP-247) — Pay Gas with ERC-20 Tokens

Users who bridge assets to Kaia often have USDT/USDC but **zero KAIA for gas**. KIP-247 solves this at the protocol level.

**This is NOT ERC-4337.** No bundlers, no UserOperations. The block proposer handles everything natively.

---

## How It Works

1. User has ERC-20 tokens (e.g., USDT) but no KAIA
2. User creates two transactions with 0 gas balance:
   - **GaslessApproveTx** — approves GaslessSwapRouter to spend tokens
   - **GaslessSwapTx** — calls `swapForGas(token, amountIn, minAmountOut, amountRepay, deadline)`
3. Block proposer detects the GaslessTx pattern
4. Proposer injects a **LendTx** (type `0x7802`) — transfers KAIA to user
5. User's approve + swap execute using the lent KAIA
6. GaslessSwapRouter swaps ERC-20 → KAIA via DEX, repays proposer
7. Surplus goes to user (minus commission)

**All atomic. All in one block. User never needs to acquire KAIA first.**

---

## Key Contract: GaslessSwapRouter

| Network | Address                                      |
| ------- | -------------------------------------------- |
| Mainnet | `0xCf658F786bf4AC62D66d70Dd26B5c1395dA22c63` |
| Kairos  | `0x4b41783732810b731569E4d944F59372F411BEa2` |

### Interface

```solidity
function swapForGas(
    address token,     // whitelisted ERC-20
    uint256 amountIn,  // tokens to swap
    uint256 minAmountOut, // minimum KAIA output
    uint256 amountRepay,  // exact amount to repay proposer
    uint256 deadline   // tx deadline
) external;

function getSupportedTokens() external view returns (address[] memory);
function getAmountIn(address token, uint amountOut) external view returns (uint amountIn);
```

### Repayment Calculation

```
amountRepay = V1 + V2 + V3
  V1 = LendTx fee       = SwapTx.GasPrice × 21000
  V2 = ApproveTx fee     (if approve tx exists)
  V3 = SwapTx fee
```

The proposer is made whole. The user gets any surplus from the swap.

---

## Constraints

- Only **whitelisted tokens** are supported (contract owner manages whitelist)
- Only **single-hop swaps** through predetermined DEX contracts
- GaslessApproveTx MUST be followed by GaslessSwapTx from the same sender
- GaslessSwapTx CAN exist alone (if token is already approved)

---

## vs Ethereum Approaches

| Feature                  | Kaia KIP-247                      | Ethereum ERC-4337                   |
| ------------------------ | --------------------------------- | ----------------------------------- |
| Level                    | Protocol-native                   | Smart contract layer                |
| Who pays                 | Block proposer lends, gets repaid | Paymaster contract                  |
| Complexity               | 2 txs (approve + swap)            | UserOperation + Bundler + Paymaster |
| Token support            | Whitelisted ERC-20s               | Paymaster-defined                   |
| User needs native token? | No                                | No                                  |
| Requires special wallet? | No                                | Smart contract wallet               |

---

## When to Use

- **User onboarding** from other chains (bridged USDT/USDC, no KAIA)
- **First-time transactions** for new Kaia users
- Combined with fee delegation for full gasless UX
