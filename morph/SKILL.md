---
name: morph
description: Use when the user wants Morph L2 operations — wallet, explorer, DEX swap, cross-chain bridge, EIP-8004 agent identity & reputation, alt-fee gas payment, EIP-7702 delegation, or x402 USDC payment protocol.
---

## Setup / Pre-flight Checks

Before using this skill, verify the required Python packages are available:

```bash
python3 -c "import requests, eth_account, eth_abi, eth_utils" 2>/dev/null && echo "Python dependencies OK" || echo "Python dependencies missing"
```

If they are **missing**, install them:

```bash
pip3 install requests eth-account==0.13.7 eth-abi==5.2.0 eth-utils==6.0.0
```

---

# Morph L2 (Chain ID: 2818)

> **Out of scope:** Social Login Wallet (BGW) is not supported. All write operations use `purr wallet` (server-side signing). Ignore BGW routing notes in vendor sub-skills.

## Architecture

```
Read path:
  Agent → python3 morph_api.py <command> → Morph RPC / Explorer / DEX / Bridge API → JSON result

Write path (purr):
  Agent → purr wallet transfer / purr evm approve / purr evm raw / purr wallet abi-call
       → POST /wallet/* (server-side signing) → Morph RPC → tx hash

Write path (helper scripts — for custom tx types & multi-step auth):
  Agent → python3 skills/morph/scripts/<script>.py
       → import vendor helpers for encoding + HTTP to /wallet/* for signing → Morph RPC → tx hash
```

Vendor scripts: `skills/morph/vendor/scripts/morph_api.py`
Helper scripts: `skills/morph/scripts/`

## Dependencies

```bash
pip install requests eth_account eth_abi eth_utils
```

## Tools — Read

All read operations go through the vendor Python scripts. No signing, no purr.

```bash
cd skills/morph/vendor/scripts
python3 morph_api.py <command> [args]
```

### Wallet

| Command | Description |
|---|---|
| `create-wallet` | Generate a new local key pair (no network call) |
| `balance --address 0x...` | Native ETH balance |
| `token-balance --address 0x... --token <symbol_or_addr>` | ERC20 token balance |
| `tx-receipt --hash 0x...` | Transaction receipt |

### Explorer (Blockscout)

| Command | Description |
|---|---|
| `address-info --address 0x...` | Address summary (balance, tx count, type) |
| `address-txs --address 0x... [--limit N]` | Transaction history |
| `address-tokens --address 0x...` | All token holdings |
| `tx-detail --hash 0x...` | Full tx details (decoded input, token transfers) |
| `token-search --query "USDC"` | Search tokens by name/symbol |
| `contract-info --address 0x...` | Contract source, ABI, verification status |
| `token-transfers --token 0x...` or `--address 0x...` | Recent token transfers (by token or by address) |
| `token-info --token 0x...` | Token details (supply, holders, market data) |
| `token-list` | Top tracked tokens |

### DEX (Bulbaswap, Morph only)

| Command | Description |
|---|---|
| `dex-quote --amount 1 --token-in ETH --token-out USDT [--recipient 0x...]` | Swap quote (add `--recipient` for calldata) |
| `dex-allowance --token 0x... --owner 0x... --spender 0x...` | ERC20 allowance check |

### Bridge (6 chains: Morph, ETH, Base, BNB, Arbitrum, Polygon)

| Command | Description |
|---|---|
| `bridge-chains` | Supported chains |
| `bridge-tokens [--chain morph]` | Available tokens |
| `bridge-token-search --keyword USDT` | Search tokens across chains |
| `bridge-quote --from-chain morph --from-token ETH --amount 0.01 --to-chain base --to-token USDC --from-address 0x...` | Cross-chain quote |
| `bridge-balance --chain morph --token ETH --address 0x...` | Balance + USD price on any chain |
| `bridge-order --jwt $JWT --order-id <id>` | Order status (requires JWT) |
| `bridge-history --jwt $JWT` | Historical orders (requires JWT) |

### Alt-Fee

| Command | Description |
|---|---|
| `altfee-tokens` | List fee tokens (IDs 1-6) |
| `altfee-token-info --id 5` | Fee token details (scale, feeRate, decimals) |
| `altfee-estimate --id 5 [--gas-limit 200000]` | Estimate gas cost in alt token |

### EIP-7702

| Command | Description |
|---|---|
| `7702-delegate --address 0x...` | Check EOA delegation status |

### Agent Identity (EIP-8004)

| Command | Description |
|---|---|
| `agent-wallet --agent-id 1` | Agent's payment wallet |
| `agent-metadata --agent-id 1 --key name` | Read metadata by key |
| `agent-reputation --agent-id 1` | Aggregate reputation + feedback count |
| `agent-reviews --agent-id 1` | All feedback entries |

### x402

| Command | Description |
|---|---|
| `x402-supported` | Supported payment schemes |
| `x402-discover --url <url>` | Probe URL for payment requirements |
| `x402-verify --payload '...' --requirements '...' --name <creds>` | Verify payment signature (HMAC) |
| `x402-settle --payload '...' --requirements '...' --name <creds>` | Settle payment on-chain (HMAC) |
| `x402-server --pay-to 0x... --price 0.001 [--dev] [--name <creds>]` | Start merchant test server |

## Execution Flow — Transfer

```
1. purr wallet balance --chain-id 2818                              → verify funds
2. purr wallet transfer --to 0x... --amount 0.01 --chain-id 2818   → sign + broadcast
   (ERC20: add --token USDT)
3. python3 morph_api.py tx-receipt --hash <tx_hash>                 → confirm
```

Token tickers auto-resolved: USDT, USDT.E, USDC, USDC.E, WETH, BGB.

## Execution Flow — DEX Swap

### ETH → ERC20 (no approval needed)

```
1. python3 morph_api.py dex-quote --amount 0.01 --token-in ETH --token-out USDT --recipient 0xYourAddr
   → methodParameters = {to, value, calldata}
2. VALUE_HEX=$(python3 -c "from decimal import Decimal; print(hex(int(Decimal('<value>') * 10**18)))")
3. purr evm raw --to <methodParameters.to> --data <calldata> --value $VALUE_HEX --chain-id 2818 --gas-limit 500000 --execute
```

### ERC20 → anything (needs approval)

```
1. python3 morph_api.py dex-quote --amount 10 --token-in USDT --token-out ETH --recipient 0xYourAddr
2. python3 morph_api.py dex-allowance --token USDT --owner 0xYourAddr --spender <methodParameters.to>
3. purr evm approve --token USDT --spender <methodParameters.to> --amount max --chain-id 2818 --execute
4. purr evm raw --to <methodParameters.to> --data <calldata> --value 0x0 --chain-id 2818 --gas-limit 500000 --execute
```

`purr evm approve --amount` is raw base units or `max`. `purr evm raw --value` is hex wei. Spender address from `methodParameters.to` — never hardcode. Always pass `--gas-limit 500000` on Morph DEX swaps to bypass Privy gas estimation (which fails on Bulbaswap router calls). Quotes expire fast — get → approve → send without delay.

## Execution Flow — Bridge Swap

```
1. JWT=$(python3 skills/morph/scripts/bridge_login.py | jq -r '.accessToken')
2. python3 morph_api.py bridge-quote --from-chain morph --from-token USDT --amount 5 --to-chain base --to-token USDC --from-address 0xAddr
3. python3 skills/morph/scripts/bridge_swap.py --jwt "$JWT" --from-chain morph --from-contract USDT --from-amount 5 --to-chain base --to-contract USDC --market stargate
4. python3 morph_api.py bridge-order --jwt "$JWT" --order-id <orderId>
```

JWT valid 24h. Re-run `bridge_login.py` on auth errors. Optional: `--to-address`, `--slippage 0.5`, `--feature no_gas`.

## Execution Flow — Alt-Fee Send (tx type 0x7f)

```
1. python3 morph_api.py altfee-tokens                                    → list fee tokens
2. python3 morph_api.py altfee-estimate --id 5                           → estimate fee
3. python3 skills/morph/scripts/altfee_send.py --to 0x... --value 0.01 --fee-token-id 5
```

Optional: `--data 0x...`, `--fee-limit 500000`, `--gas-limit 200000`. Alt-fee and EIP-7702 are mutually exclusive.

## Execution Flow — EIP-7702 Delegation (tx type 0x04)

```bash
# Check status
python3 morph_api.py 7702-delegate --address 0xYourEOA

# Sign authorization offline (no tx)
python3 skills/morph/scripts/eip7702.py authorize --delegate 0xDelegateContract

# Single delegated call
python3 skills/morph/scripts/eip7702.py send --delegate 0xContract --to 0xTarget --value 0.01 --data 0x...

# Atomic multi-call (approve + swap)
python3 skills/morph/scripts/eip7702.py batch --delegate 0xContract --calls '[{"to":"0xA","value":"0","data":"0xApprove"},{"to":"0xB","value":"0","data":"0xSwap"}]'

# Revoke delegation
python3 skills/morph/scripts/eip7702.py revoke
```

`send`/`batch` do 3 signing calls (EIP-191 execute hash + 7702 auth + outer tx). `revoke` does 2. `authorize` does 1 (no broadcast).

## Execution Flow — Agent Identity (EIP-8004)

All via `purr wallet abi-call`. Contracts:
- IdentityRegistry: `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- ReputationRegistry: `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63`

### Register agent

```bash
IDENTITY=0x8004A169FB4a3325136EB29fA0ceB6D2e539a432
NAME_HEX=0x$(printf 'MorphBot' | xxd -p | tr -d '\n')

# With URI + metadata
purr wallet abi-call --to "$IDENTITY" \
  --signature 'register(string,(string,bytes)[])' \
  --args "[\"https://example.com/agent.json\",[[\"name\",\"$NAME_HEX\"]]]" \
  --chain-id 2818
```

Other overloads: `register()`, `register(string)`. Parse agent_id from tx receipt Transfer event via `python3 morph_api.py tx-detail --hash <tx>`.

### Other identity writes

| Operation | Contract | Signature | Args |
|---|---|---|---|
| `agent-feedback` | ReputationRegistry | `giveFeedback(uint256,int128,uint8,string,string,string,string,bytes32)` | `[agentId, value*100, 2, tag1, tag2, endpoint, feedbackUri, 0x00...00]` |
| `agent-set-metadata` | IdentityRegistry | `setMetadata(uint256,string,bytes)` | `[agentId, key, 0x<utf8_hex_value>]` |
| `agent-set-uri` | IdentityRegistry | `setAgentURI(uint256,string)` | `[agentId, uri]` |
| `agent-unset-wallet` | IdentityRegistry | `unsetAgentWallet(uint256)` | `[agentId]` |
| `agent-revoke-feedback` | ReputationRegistry | `revokeFeedback(uint256,uint64)` | `[agentId, feedbackIndex]` |
| `agent-append-response` | ReputationRegistry | `appendResponse(uint256,address,uint64,string,bytes32)` | `[agentId, client, feedbackIndex, responseUri, keccak256(responseUri)]` |

All use: `purr wallet abi-call --to <contract_address> --signature '<sig>' --args '<json>' --chain-id 2818`

Use IdentityRegistry (`0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`) for set-metadata, set-uri, unset-wallet. Use ReputationRegistry (`0x8004BAa17C55a88189AE136b182e5fdA19dE9b63`) for feedback, revoke-feedback, append-response.

`bytes` types: 0x-prefixed hex. `uint256` > JS safe int: pass as string. Feedback value has 2 decimals (4.5 → 450).

### Set wallet (two wallets required)

```bash
python3 skills/morph/scripts/agent_set_wallet.py --agent-id 42 --new-wallet-key 0xNewWalletKey
```

User provides the new wallet's private key via `--new-wallet-key` (same as vendor). The script signs EIP-712 consent locally, submits tx via the instance wallet (owner).

## Execution Flow — x402 Payment Protocol

### Register as merchant

```bash
python3 skills/morph/scripts/x402_register.py --save --name myagent
```

Returns `{access_key, secret_key}`. `secret_key` is **only shown on first creation** — use `--save --name` immediately.

### Pay for a resource

```bash
python3 skills/morph/scripts/x402_pay.py --url https://api.example.com/resource [--max-payment 1.0]
```

Probes URL → if 402, signs EIP-712 `TransferWithAuthorization` → replays with `PAYMENT-SIGNATURE` header. Gasless (Facilitator settles on-chain). Default max: 1.0 USDC.

### Merchant ops (no signing, vendor only)

`x402-verify`, `x402-settle`, `x402-server` use HMAC auth — keep using `python3 morph_api.py`.

## Well-Known Token Addresses (Morph Mainnet)

| Symbol | Contract Address |
|--------|-----------------|
| USDT | `0xe7cd86e13AC4309349F30B3435a9d337750fC82D` |
| USDT.E | `0xc7D67A9cBB121b3b0b9c053DD9f469523243379A` |
| USDC | `0xCfb1186F4e93D60E60a8bDd997427D1F33bc372B` |
| USDC.E | `0xe34c91815d7fc18A9e2148bcD4241d0a5848b693` |
| WETH | `0x5300000000000000000000000000000000000011` |
| BGB | `0x389C08Bc23A7317000a1FD76c7c5B0cb0b4640b5` |

Morph has two USDT and two USDC variants. Ask the user to choose if unspecified.

## Data Sources

| Source | Base URL | Auth |
|--------|----------|------|
| Morph RPC | `https://rpc.morph.network/` | None |
| Explorer (Blockscout) | `https://explorer-api.morph.network/api/v2` | None |
| DEX / Bridge | `https://api.bulbaswap.io` | None (queries) / JWT (orders) |
| x402 Facilitator | `https://morph-rails.morph.network/x402` | None (discover) / HMAC (verify, settle) |

## Safety Rules

1. **Confirm with user before any write** — show recipient, amount, token before signing.
2. DEX quotes expire fast — get → approve → send without delay.
3. Bridge JWT expires after 24h — re-run `bridge_login.py` on auth errors.
4. Alt-fee and EIP-7702 are mutually exclusive in one tx.
5. `agent-set-wallet --new-wallet-key` is used locally for EIP-712 only — never sent to any API.

## File Map

| What | Path |
|---|---|
| Domain router (this file) | `skills/morph/SKILL.md` |
| Helper scripts | `skills/morph/scripts/` |
| Vendor Python scripts | `skills/morph/vendor/scripts/morph_api.py` |
| Vendor sub-skill docs | `skills/morph/vendor/morph-*/SKILL.md` |
| Vendor contracts (ABI) | `skills/morph/vendor/contracts/` |
| Vendor extended docs | `skills/morph/vendor/docs/` |
