---
name: addresses
description: Verified system contract addresses on Kaia mainnet and Kairos testnet. Use when you need contract addresses for Kaia system contracts. Do NOT hallucinate addresses — use only the verified addresses listed here.
disable-model-invocation: true
user-invocable: false
---

# Contract Addresses — Kaia

**NEVER guess contract addresses.** If an address isn't listed here, say you don't know it.

> Source: https://docs.kaia.io/references/contract-addresses/ + core team verified data (2026-03-16)

## Kaia Mainnet (Chain ID: 8217)

| Contract                          | Address                                      |
| --------------------------------- | -------------------------------------------- |
| AddressBook                       | `0x0000000000000000000000000000000000000400` |
| KIP-149 Registry                  | `0x0000000000000000000000000000000000000401` |
| KIP-113 SimpleBlsRegistry (proxy) | `0x3e80e75975bdb8e04B800485DD28BebeC6d97679` |
| KIP-81 GovParam                   | `0x362976Cc2Ef6751DE6bf6008e3E90e1e02deCa51` |
| KIP-226 CLRegistry                | `0x25F4044c655Fc7B23c62bbC78ceF3B4EBFb4e478` |
| KIP-247 GaslessSwapRouter         | `0xCf658F786bf4AC62D66d70Dd26B5c1395dA22c63` |
| KIP-249 AuctionEntryPoint         | `0xFc5c1C92d8DE06F7143f71FeA209e04042dcff82` |
| KIP-249 AuctionDepositVault       | `0x0E66b62273Cc99BC519DD4dD0C0Cf689dd7b9876` |
| KIP-249 AuctionFeeVault           | `0x303BB9c9FF4Aa656ac4c8e9f99F8E4C133FDa665` |
| KIP-163 PublicDelegationFactory   | `0x29C8cc53d22F79D4024ecB67DB1a09b37bCdE415` |
| Canonical WKAIA                   | `0x19Aac5f612f524B754CA7e7c41cbFa2E981A4432` |
| KIP-103 TreasuryRebalance         | `0xD5ad6D61Dd87EdabE2332607C328f5cc96aeCB95` |
| KIP-160 TreasuryRebalanceV2       | `0xa4df15717Da40077C0aD528296AdBBd046579Ee9` |
| KIP-226 CLDEXFactory              | `0x93fa0E1deE99ac4158a617a6EC79cB941bD9a39F` |
| KIP-226 CLDEXRouter               | `0x5086273d9C8a79B7d2466aaCc52a6E43E22152A5` |
| KIP-226 StakingTrackerV2          | `0xF45c37c265f148894D6d9A4c066aFaAB00557c9c` |
| Kaiabridge Bridge                 | `0x5Ff2AD57C15f7Dacb5D098d1fC82DAF482884f99` |

## Kaia Kairos Testnet (Chain ID: 1001)

| Contract                          | Address                                      |
| --------------------------------- | -------------------------------------------- |
| AddressBook                       | `0x0000000000000000000000000000000000000400` |
| KIP-149 Registry                  | `0x0000000000000000000000000000000000000401` |
| KIP-113 SimpleBlsRegistry (proxy) | `0x4BEed0651C46aE5a7CB3b7737345d2ee733789e6` |
| KIP-81 GovParam                   | `0x84214cec245d752a9f2faf355b59ddf7f58a6edb` |
| KIP-226 CLRegistry                | `0x25F4044c655Fc7B23c62bbC78ceF3B4EBFb4e478` |
| KIP-247 GaslessSwapRouter         | `0x4b41783732810b731569E4d944F59372F411BEa2` |
| KIP-249 AuctionEntryPoint         | `0x2fF66A8b9f133ca4774bEAd723b8a92fA1e28480` |
| KIP-249 AuctionDepositVault       | `0x2A168bCdeB9006eC6E71f44B7686c9a9863C1FBc` |
| KIP-249 AuctionFeeVault           | `0xE4e7d880786c53b6EA6cfA848Eb3a05eE97b2aCC` |
| KIP-163 PublicDelegationFactory   | `0x98c47c2cda854cbb025d47de72149a7ec238ec33` |
| Canonical WKAIA                   | `0x043c471bEe060e00A56CcD02c0Ca286808a5A436` |
| StakingTracker                    | `0x9b015Ab5916EE53e52Ef60f31E978b4001908c43` |

## Querying System Contracts

Use the KIP-149 Registry to look up any registered system contract:

```bash
REGISTRY="0x0000000000000000000000000000000000000401"
RPC="https://public-en.node.kaia.io"

# List all registered contract names
cast call $REGISTRY "getAllNames()(string[])" --rpc-url $RPC

# Get active address for a specific contract
cast call $REGISTRY "getActiveAddr(string)(address)" "KIP113" --rpc-url $RPC
```
