---
name: ows
description: Open Wallet Standard — local wallet management, policy-gated signing, and API key access. Manages the ~/.ows/ vault.
---

# OWS (Open Wallet Standard)

Local wallet custody via the `ows` CLI. Keys never leave the pod — encrypted at rest with AES-256-GCM, decrypted only during signing, zeroed immediately after.

## Rules

- **The `ows` CLI is preinstalled in the container image** at `/usr/local/bin/ows`. If `ows --version` fails, this is a deployment bug — report it instead of attempting to install.
- **Do not run `ows update`** inside pods — the binary is image-managed.
- **Always ask the user for confirmation before any write operation** — wallet creation, deletion, renaming, import, signing, transaction broadcast, key creation/revocation, and policy creation/deletion.
- **All signing must use an API key token** (`ows_key_...`). This is agent mode — the agent should never have the passphrase, only a scoped token.
- Secrets are supplied via `OWS_PASSPHRASE` env var: `OWS_PASSPHRASE="..." ows ...`
- The vault passphrase used for creating wallet is always empty string since it's agent mode.
- **Do NOT use `ows wallet export`** — it requires an interactive terminal which is not available.
- Always pass `--json` to signing commands for structured output.
- **Chain names:** use specific names (`ethereum`, `base`, `arbitrum`, `optimism`, `polygon`, `bsc`, `avalanche`, `plasma`, `etherlink`) or CAIP-2 (`eip155:8453`). The legacy alias `--chain evm` still works but emits a deprecation warning — prefer `ethereum` explicitly.

## Setup Flow (first-time agent onboarding)

Run these in order. Every step asks for user confirmation before it writes.

### 1. Create (or import) a wallet

```bash
# Fresh wallet:
ows wallet create --name "<wallet-name>"
#   --words 24        optional, defaults to 12
#   Passphrase prompt: press ENTER twice (empty string) — agent-mode convention
#   (container isolation is the at-rest security boundary, not the passphrase)

# Or import from existing mnemonic:
OWS_MNEMONIC="word1 word2 ..." ows wallet import --name "<wallet-name>" --mnemonic
#   Same passphrase rule: empty string on the prompt

# Or import from private key (need --chain to pick curve: ethereum=secp256k1, solana=ed25519):
OWS_PRIVATE_KEY="0x..." ows wallet import --name "<wallet-name>" --private-key --chain ethereum
#   Same passphrase rule: empty string on the prompt
```

Verify with `ows wallet list` — the wallet should show a derived address per chain family (`eip155:1`, `solana:...`, `bitcoin:...`, etc.).

### 2. Create a policy (REQUIRED for agent-mode signing)

Policies are a **default-deny allowlist**. Without a policy attached, the key CANNOT sign anything. Write a policy that matches the chains you want to let the agent touch.

```bash
cat > /tmp/policy.json <<'EOF'
{
  "version": 1,
  "name": "evm-mainnets",
  "rules": [
    {
      "type": "allowed_chains",
      "chain_ids": ["eip155:1", "eip155:56", "eip155:8453", "eip155:42161", "eip155:10", "eip155:137", "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp"]
    }
  ]
}
EOF
ows policy create --file /tmp/policy.json
# → prints the policy ID (UUID); capture it for step 3
```

Chain IDs must be CAIP-2 (`eip155:<chainId>` / `solana:<genesis-hash>`). `ows policy list` to review, `ows policy show --id <uuid>` for details.

### 3. Create an API key bound to the wallet + policy

```bash
ows key create \
  --name "agent-key" \
  --wallet <wallet-name> \
  --policy <policy-id-from-step-2> \
  --expires-at "2027-01-01T00:00:00Z"
# → prints `ows_key_...` token ONCE. Save it immediately to .env / secrets store.
```

`--wallet` and `--policy` are **repeatable** — attach multiple wallets or policies if needed (AND semantics: every attached policy must allow the operation).

### 4. Hand the token to the agent and sign-test

```bash
export OWS_PASSPHRASE="ows_key_..."
ows sign message --wallet <wallet-name> --chain ethereum --message "test" --json
# → {"recovery_id": 28, "signature": "..."}
```

If you see `policy denied: ...`, the policy in step 2 doesn't cover the chain/operation — amend the policy JSON and re-run `policy create` (policies are immutable once created; create a new one and re-attach).

### 5. (Optional) verify the key scope before real signing

```bash
ows key list
# Shows each key with its attached Wallets + Policies
```

Agent is now ready. All subsequent signing calls reuse `$OWS_PASSPHRASE` — never embed the raw passphrase / mnemonic / private key in the agent's environment. `OWS_PASSPHRASE` can be set once per shell with `export`, or prefixed inline for single commands. Both are correct — the value is always the `ows_key_...` token.

## Wallet Management

### Create wallet

```bash
ows wallet create --name "my-wallet"
# --words 24        (default: 12)
# --show-mnemonic   (prints mnemonic — DANGEROUS, only for backup)
```

### List wallets

```bash
ows wallet list
```

### Vault info

```bash
ows wallet info
```

### Rename wallet

```bash
ows wallet rename --wallet "my-wallet" --new-name "new-name"
```

### Delete wallet

```bash
ows wallet delete --wallet "my-wallet" --confirm
```

### Import wallet

```bash
# From mnemonic (reads from OWS_MNEMONIC env or stdin)
ows wallet import --name "imported" --mnemonic
# --index <N>       account index (default: 0)

# From private key (reads from OWS_PRIVATE_KEY env or stdin)
ows wallet import --name "imported" --private-key --chain ethereum
# --chain required for private key import (determines curve)
```

## Signing

Supply API key token via `OWS_PASSPHRASE` env. Always use `--json`.

### Sign message

```bash
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet my-wallet \
  --chain ethereum \
  --message "hello" \
  --json
# --encoding hex     (default: utf8)
# --index <N>        account index (default: 0)
```

### Sign EIP-712 typed data

```bash
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet my-wallet \
  --chain ethereum \
  --message "" \
  --typed-data '{"types":{...},"primaryType":"...","domain":{...},"message":{...}}' \
  --json
```

### Sign transaction

```bash
OWS_PASSPHRASE="ows_key_..." ows sign tx \
  --wallet my-wallet \
  --chain ethereum \
  --tx <hex-encoded-unsigned-tx> \
  --json
```

### Sign and broadcast

```bash
OWS_PASSPHRASE="ows_key_..." ows sign send-tx \
  --wallet my-wallet \
  --chain ethereum \
  --tx <hex-encoded-unsigned-tx> \
  --json
# --rpc-url <url>    override default RPC
```

## Policy Management

Policies gate what API keys can do. AND semantics — all policies on a key must allow the operation.

### Create policy

```bash
ows policy create --file /tmp/policy.json
```

Policy JSON:

```json
{
  "id": "<uuid>",
  "version": 1,
  "name": "evm-only",
  "created_at": "2026-04-01T00:00:00Z",
  "rules": [
    {
      "type": "allowed_chains",
      "chain_ids": ["eip155:1", "eip155:56", "eip155:8453"]
    }
  ],
  "action": "deny"
}
```

Rule types: `allowed_chains` (CAIP-2 chain IDs), `expires_at` (ISO-8601), custom executable.

### List / show / delete

```bash
ows policy list
ows policy show --id <uuid>
ows policy delete --id <uuid> --confirm
```

## API Key Management

### Create key

```bash
ows key create \
  --name "agent-key" \
  --wallet <wallet-name-or-id> \
  --policy <policy-id>
# --wallet and --policy are repeatable for multiple wallets/policies
# --expires-at "2026-12-31T23:59:59Z"
# Token shown once — save it immediately
```

### List / revoke

```bash
ows key list
ows key revoke --id <uuid> --confirm
```

## Mnemonic

```bash
ows mnemonic generate
# --words 24    (default: 12)

ows mnemonic derive --chain ethereum
# Reads mnemonic from OWS_MNEMONIC env or stdin
# --chain omitted = derive all chains
# --index <N>    account index (default: 0)
```

## Balance Query (universal — preferred)

**`ows fund balance` has two limitations**: (1) returns **tokens only**, no native gas coin; (2) allowlist is restricted to MoonPay-tracked chains (`ethereum` / `base` / `bsc` / `polygon` / `arbitrum` / `optimism` / `solana`) — non-listed chains like Morph / Tempo / Hyperliquid fail with `UnsupportedChain`.

For **any chain (including Morph) + native coin + token balances in a single call**, use the Bitget Wallet vendor's `batch-v2` as the canonical balance checker:

```bash
python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 \
  --chain <bnb|eth|base|arbitrum|solana|morph|...> \
  --address <ows-evm-or-solana-addr> \
  --contract <token-addr-or-empty>
```

Returns JSON `data[0].list` keyed by contract address. Key `""` = native coin (BNB / ETH / SOL / ...); specific addresses = ERC-20 / SPL tokens.

Chain identifiers accepted: `bnb` (or `bsc`) / `eth` (or `ethereum`) / `base` / `arbitrum` / `optimism` / `polygon` / `solana` / `morph` / `avalanche` / `tron` / many more. This is the single balance tool that works across every chain OWS signs on.

Requires the `bitget-wallet` skill to be present (preinstalled in every tenant pod alongside `ows`).

## Fund (MoonPay on-ramp — limited scope)

```bash
ows fund balance --wallet my-wallet
# --chain base    (default: base)
# ⚠ tokens only, no native; limited to MoonPay allowlist. Prefer batch-v2 above.

ows fund deposit --wallet my-wallet
# --chain base    (default: base)
# --token USDC    (default: USDC)
```

## Pay (x402)

```bash
OWS_PASSPHRASE="ows_key_..." ows pay request --wallet my-wallet https://api.example.com/resource
# --method GET     (default: GET)
# --body '{...}'   request body JSON

ows pay discover
# --query "weather"
# --limit 100
# --offset 0
```

## Configuration

```bash
ows config show
```

## Supported Chains

`--chain` accepts a specific chain name, CAIP-2 ID, or bare EVM chain ID (e.g. `ethereum`, `eip155:8453`, or `8453`).

| Family  | Chain names (`--chain` value)                                                                    | CAIP-2 example                            |
| ------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------- |
| EVM     | Friendly names: `ethereum`, `base`, `arbitrum`, `optimism`, `polygon`, `bsc`, `avalanche`, `plasma`, `etherlink`. CAIP-2 only (no friendly alias in CLI v1.2.4): Tempo, Hyperliquid. | `eip155:1`, `eip155:8453`, `eip155:4217` (tempo), `eip155:999` (hyperliquid), … |
| Solana  | `solana`                                                                                         | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` |
| Bitcoin | `bitcoin`                                                                                        | `bip122:000000000019d6689c085ae165831e93` |
| Other   | `cosmos`, `tron`, `ton`, `sui`, `filecoin`, `spark`, `xrpl`                                      | `cosmos:cosmoshub-4`, `tron:mainnet`, …   |

## Vault

`~/.ows/` — `wallets/`, `keys/`, `policies/`, `config.json`, `logs/audit.jsonl`. Backed up to GCS automatically.

## Per-Skill Integration Guide

This section contains OWS-specific execution notes for every skill that supports it.

**Routing rule:** `onchain` is the top-level skill. When the user explicitly names OWS (e.g. "using OWS", "via my OWS vault"), read this guide for the specific downstream skill being requested. Downstream skill files do NOT mention OWS — all OWS logic lives here.

**Pre-check for every OWS flow:** If `ows wallet list` returns no wallet, ask the user to create one first (`ows wallet create --name ...`) — do NOT auto-create.

---

### pancake

**Pattern:** `purr ows-execute` (drop `--execute`, capture steps JSON).

**Address:** `ows wallet list` → `eip155:1` line.

**Balance:** `python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain bnb --address <addr> --contract <token-addr-or-empty>`.

**Notes:**
- Most `purr pancake` commands accept `--wallet <addr>` (swap, add/remove-liquidity, v3-mint, v3-collect, v3-stake/unstake/harvest).
- Farm / syrup commands do NOT: `stake / unstake / harvest` (pass `--pid`), `syrup-stake / syrup-unstake` (pass `--pool-address`), `v3-increase / v3-decrease` (pass `--token-id`).
- `allowance_lt` conditional auto-skips redundant approvals at broadcast time.

**Flow:**
```
1. ADDR=$(ows wallet list | awk '/eip155:1/ {print $NF; exit}')
2. python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain bnb --address $ADDR --contract <token-addr-or-empty>
3. Vendor planner discovery (unchanged)
4. purr pancake <command> [--wallet $ADDR] [args] > /tmp/pancake_steps.json
5. purr ows-execute --steps-file /tmp/pancake_steps.json --ows-wallet <name>
6. Re-run step 2
```

---

### morph

**Patterns:**
- **Transfer:** `purr ows-wallet build-transfer` → `ows sign send-tx`
- **DEX / abi-call:** drop `--execute` → `purr ows-execute`

**Address:** `ows wallet list` → `eip155:1` line.

**Balance:**
- Universal: `python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain morph --address <addr> --contract <token-addr-or-empty>`.
- Alternative native-only: `python3 morph_api.py balance --address <addr>`.

**Critical constraints:**
- `ows sign send-tx` **MUST** include `--rpc-url https://rpc.morph.network` for Morph (`eip155:2818`).
- Native ETH transfers need `--gas-limit 100000` on `build-transfer`.
- Bulbaswap router calls need `--gas-limit 500000` on `purr evm raw`.
- Bulbaswap returns **different router addresses per quote** — re-approve each time.

**Flows:**

*Transfer:*
```
1. ADDR=$(ows wallet list | awk '/eip155:1/ {print $NF; exit}')
2. python3 morph_api.py balance --address $ADDR
3. purr ows-wallet build-transfer --ows-wallet <name> --to 0x... --amount 0.01 --chain-id 2818 --gas-limit 100000 [--token USDT] > /tmp/tx.json
4. ows sign send-tx --chain eip155:2818 --wallet <name> --rpc-url https://rpc.morph.network --tx $(jq -r .unsignedTxHex /tmp/tx.json) --json
5. python3 morph_api.py tx-receipt --hash <tx_hash>
```

*DEX Swap — ETH → ERC20:*
```
1. python3 morph_api.py dex-quote ... --recipient 0xAddr
2. VALUE_HEX=$(python3 -c "from decimal import Decimal; print(hex(int(Decimal('<value>') * 10**18)))")
3. purr evm raw --to <methodParameters.to> --data <calldata> --value $VALUE_HEX --chain-id 2818 --gas-limit 500000 > /tmp/swap.json
4. purr ows-execute --steps-file /tmp/swap.json --ows-wallet <name>
```

*DEX Swap — ERC20 → anything (with approval):*
```
1. python3 morph_api.py dex-quote ... --recipient 0xAddr
2. python3 morph_api.py dex-allowance --token USDT --owner 0xAddr --spender <methodParameters.to>
3. purr evm approve --token USDT --spender <methodParameters.to> --amount max --chain-id 2818 > /tmp/approve.json
4. purr evm raw --to <methodParameters.to> --data <calldata> --value 0x0 --chain-id 2818 --gas-limit 500000 > /tmp/swap.json
5. jq -s '{steps: (.[0].steps + .[1].steps)}' /tmp/approve.json /tmp/swap.json > /tmp/combined.json
6. purr ows-execute --steps-file /tmp/combined.json --ows-wallet <name>
```

*Agent Identity (EIP-8004):*
```
1. IDENTITY=0x8004A169FB4a3325136EB29fA0ceB6D2e539a432
   NAME_HEX=0x$(printf 'MorphBot' | xxd -p | tr -d '\n')
2. cat > /tmp/register_args.json <<'EOF'
["https://example.com/agent.json",[["name","$NAME_HEX"]]]
EOF
   purr evm abi-call --to "$IDENTITY" --signature 'register(string,(string,bytes)[])' --args "$(cat /tmp/register_args.json)" --chain-id 2818 > /tmp/step.json
3. purr ows-execute --steps-file /tmp/step.json --ows-wallet <name>
```

> **Helper scripts stay on the default path:** `eip7702.py`, `altfee_send.py`, `agent_set_wallet.py`, `x402_pay.py`, `bridge_swap.py` use special tx types or gasless EIP-712 flows that OWS CLI doesn't handle.

---

### kraken

**Pattern:** `purr ows-wallet build-transfer` → `ows sign send-tx` (deposit only).

**Address:** `ows wallet list` → `eip155:1` line (EVM) or `solana:*` line (Solana).

**Balance:** `python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain <bnb|eth|base|solana> --address <addr> --contract <token-addr-or-empty>`.

**Notes:**
- Step 1 (get Kraken deposit address) and Step 3 (monitor status) are unchanged.
- Only Step 2 (the actual on-chain send) switches to OWS.
- For native tokens (BNB, ETH, SOL), **omit `--token`**.
- For ERC-20 / SPL, pass `--token <ticker_or_address>`.
- EVM tx pins nonce + gas; Solana pins recent blockhash (~60s). Check `meta.staleAfter` — if expired, re-run `build-transfer`.

**Flow:**
```
# EVM deposit example (BNB / ETH / USDT / USDC):
purr ows-wallet build-transfer --ows-wallet <name> --to <kraken-deposit-address> --amount 0.01 --chain-id 56 [--token USDT] > /tmp/tx.json
TX_HEX=$(jq -r .unsignedTxHex /tmp/tx.json)
CHAIN=$(jq -r .chain /tmp/tx.json)
OWS_PASSPHRASE="ows_key_..." ows sign send-tx --chain "$CHAIN" --wallet <name> --tx "$TX_HEX" --json

# Solana SOL deposit:
purr ows-wallet build-transfer --ows-wallet <name> --chain-type solana --to <kraken-deposit-address> --amount 0.5 > /tmp/tx.json
OWS_PASSPHRASE="ows_key_..." ows sign send-tx --chain solana --wallet <name> --tx "$(jq -r .unsignedTxHex /tmp/tx.json)" --json

# Solana SPL deposit (USDC):
purr ows-wallet build-transfer --ows-wallet <name> --chain-type solana --to <kraken-deposit-address> --amount 100 --token USDC > /tmp/tx.json
OWS_PASSPHRASE="ows_key_..." ows sign send-tx --chain solana --wallet <name> --tx "$(jq -r .unsignedTxHex /tmp/tx.json)" --json
```

---

### bitget-wallet

**Pattern:** `purr ows-wallet sign-transaction` replaces `purr wallet sign-transaction`.

**Address:** `ows wallet list` → `eip155:1` line (EVM) or named Solana wallet.

**Balance:** `python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain <bnb|eth|base|arbitrum|solana|morph|...> --address <addr> --contract <token-addr-or-empty>`.

**Critical constraints:**
- **Must use `--feature user_gas`** during the `confirm` step. OWS cannot sign gasPayMaster `eth_sign` raw digests.
- If `recommendFeatures` from quote does not include `user_gas`, tell the user OWS doesn't support gasless mode for this swap.

**Flow:**

> The numbers below correspond to the standard 10-step swap flow in `bitget-wallet/SKILL.md`; only step 7 changes.

```
1. ADDR=$(ows wallet list | awk '/eip155:1/ {print $NF; exit}')   # EVM example
2. python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain <chain> --address $ADDR --contract <token-addr-or-empty>
3. check-swap-token
4. quote
5. confirm --feature user_gas
6. make-order > /tmp/bgw_order.json
7. OWS_PASSPHRASE="ows_key_..." purr ows-wallet sign-transaction --ows-wallet <name> --txs-json-file /tmp/bgw_order.json > /tmp/bgw_signed.json
8. send --json-file /tmp/bgw_signed.json
9. get-order-details
10. python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2
```

**Support matrix:**
| Mode | OWS support |
|------|-------------|
| EVM `user_gas` swap | Yes |
| RWA stock trading | Yes |
| Solana swap | Yes |
| EVM gasless (`--feature no_gas`) | No |
| Tron swap | No |

---

### fourmeme

**Patterns:**
- **Buy / Sell / Create-token:** drop `--execute` → `purr ows-execute`
- **Login challenge:** `ows sign message` replaces `purr wallet sign`

**Address:** `ows wallet list` → `eip155:1` line.

**Balance:** `python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain bnb --address <addr> --contract <token-addr-or-empty>`.

**Critical constraints:**
- `purr fourmeme create-token` **without `--execute` still performs off-chain setup** (login, image upload, API call) before returning the on-chain step JSON. It is NOT a dry-run.
- The raw `ows` CLI only accepts the API token via `$OWS_PASSPHRASE` env — there is no `--ows-token` flag on `ows sign message`.

**Flows:**

*Buy / Sell:*
```
# Default:
purr fourmeme buy --token 0xToken --wallet 0xWallet --funds 0.1 --execute

# OWS:
ADDR=$(ows wallet list | awk '/eip155:1/ {print $NF; exit}')
python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain bnb --address $ADDR --contract <token-addr-or-empty>
purr fourmeme buy --token 0xToken --wallet $ADDR --funds 0.1 > /tmp/fm_steps.json
OWS_PASSPHRASE="ows_key_..." purr ows-execute --steps-file /tmp/fm_steps.json --ows-wallet <name>
re-run python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2
```

*Create Token:*
```
# 1. Login challenge (unchanged)
purr fourmeme login-challenge --wallet $ADDR

# 2. Sign with OWS
OWS_PASSPHRASE="ows_key_..." ows sign message --wallet <name> --chain ethereum --message "You are sign in Meme <nonce>" --json
# Write signature to /tmp/fourmeme_login_signature.txt

# 3. Build create-token (no --execute)
purr fourmeme create-token --wallet $ADDR --login-nonce <nonce> --login-signature-file /tmp/fourmeme_login_signature.txt ... > /tmp/fm_steps.json

# 4. Execute
OWS_PASSPHRASE="ows_key_..." purr ows-execute --steps-file /tmp/fm_steps.json --ows-wallet <name>
```

**Failure modes:**
| Error | Fix |
|-------|-----|
| `wallet not found: '<name>'` | Check spelling with `ows wallet list` |
| `policy denied: chain eip155:56` | Policy missing BSC — create one with `eip155:56` |
| `Signature for this request is not valid` | Nonce expired. Re-run `login-challenge`, re-sign with `ows sign message`, retry once. |
| `Step N ... reverted on-chain` | Check partial results — earlier steps (e.g. approve) may have already succeeded. Never blindly retry the full sequence. |

---

### lista-vaults

**Pattern:** `purr ows-execute` (drop `--execute` from deposit / redeem / withdraw).

**Address:** `ows wallet list` → `eip155:1` line.

**Balance:** `python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain bnb --address <addr> --contract <deposit-token-addr-or-empty>`.

**Flow:**
```
# Default:
purr lista deposit --vault 0x... --amount-wei ... --token 0x... --wallet 0x... --chain-id 56 --execute

# OWS:
ADDR=$(ows wallet list | awk '/eip155:1/ {print $NF; exit}')
python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain bnb --address $ADDR --contract <deposit-token-addr-or-empty>
purr lista deposit --vault 0x... --amount-wei ... --token 0x... --wallet $ADDR --chain-id 56 > /tmp/lista_steps.json
OWS_PASSPHRASE="ows_key_..." purr ows-execute --steps-file /tmp/lista_steps.json --ows-wallet <name>
re-run python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2
```

Same pattern for `redeem` and `withdraw`.

**Failure modes:**
| Error | Fix |
|-------|-----|
| `Step 0 (Approve token for Lista vault) reverted` | Inspect on bscscan. Some tokens reject large approvals. |
| `Step 1 (Lista vault deposit) reverted` | Vault paused or at capacity. Approve already succeeded — DO NOT re-run the full sequence (would double-approve). |

---

### opensea

**Pattern:** `purr ows-execute` (drop `--execute` from buy / sell).

**Address:** `ows wallet list` → `eip155:1` line.

**Balance:** `python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain <eth|base|polygon|arbitrum|optimism> --address <addr> --contract <token-addr-or-empty>`.

**Notes:**
- Vendor reads (listing discovery, fulfillment JSON fetching) are unchanged.
- `--wallet` passed to `purr opensea buy/sell` must match the OWS `eip155:1` address.
- `allowance_lt` auto-skips redundant ERC-20 approvals.

**Flows:**

*Buy NFT:*
```
1. Vendor workflow — find listing, write fulfillment JSON to /tmp/fulfillment.json
2. ADDR=$(ows wallet list | awk '/eip155:1/ {print $NF; exit}')
3. python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain <listing-chain> --address $ADDR --contract ""
4. purr opensea buy --wallet $ADDR --fulfillment-file /tmp/fulfillment.json > /tmp/buy_steps.json
5. purr ows-execute --steps-file /tmp/buy_steps.json --ows-wallet <name>
```

*Sell NFT / Accept Offer:*
```
1. Vendor workflow — find offer, write fulfillment JSON to /tmp/fulfillment.json
2. ADDR=$(ows wallet list | awk '/eip155:1/ {print $NF; exit}')
3. purr opensea sell --wallet $ADDR --fulfillment-file /tmp/fulfillment.json > /tmp/sell_steps.json
4. purr ows-execute --steps-file /tmp/sell_steps.json --ows-wallet <name>
```

---

### dflow-swap

**Pattern:** `purr dflow-ows swap` (single command — quote → sign → broadcast → confirm).

**Address:** `ows wallet list` → named Solana wallet address.

**Balance:** `python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain solana --address <addr> --contract <mint-or-empty>`.

**Notes:**
- `purr dflow-ows swap` runs entirely inside the pod, signing locally with OWS.
- Default RPC is `https://api.mainnet-beta.solana.com`. Override with `$SOLANA_RPC_URL` or `--rpc-url`.

**Flow:**
```
1. Confirm Solana address from `ows wallet list`
2. python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain solana --address <ows-solana-addr> --contract <mint-or-empty>
3. OWS_PASSPHRASE="ows_key_..." purr dflow-ows swap --from-token <mint> --to-token <mint> --amount <human-readable> --ows-wallet <name> --slippage 0.01
4. Re-run python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2
```

**Failure modes:**
| Error | Fix |
|-------|-----|
| `policy denied: chain solana` | Policy missing Solana — create one with `solana` chain |
| `Simulation failed: Attempt to debit an account but found no record of a prior credit` | Wallet has no SOL or no input token. Fund first. |
| `Solana tx confirmation timed out` | Tx may still confirm later — check explorer with returned `hash` before retrying. |

---

### binance-connect

**Pattern:** address-only substitution. No on-chain write originates from this skill — Binance delivers crypto directly.

**Address:** `ows wallet list` → pick address matching `--network`:
- `BSC` / `ETH` / `BASE` → `eip155:*` address
- `SOL` → `solana:*` address

**Balance confirmation:** `python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain <bnb|eth|base|solana> --address <addr> --contract <token-addr-or-empty>`.

**Notes:**
- Steps 2–5 (`quote`, `buy`, checkout URL, `status`) are **identical** to the default path.
- Only Steps 1 (get address) and 6 (confirm balance) change.
- Do NOT use `ows fund balance` — it excludes native coins and has a narrower chain allowlist.

**Flow:**
```
# Default Step 1: wallet_address with chain_type "ethereum"
# OWS Step 1:
ADDR=$(ows wallet list | awk '/eip155:1/ {print $NF; exit}')   # for BSC/ETH/BASE
# or: ows wallet list | awk '/solana:/ {print $NF; exit}'       # for SOL

# Steps 2-5 unchanged

# Default Step 6: wallet_balance
# OWS Step 6:
python3 skills/bitget-wallet/vendor/bitget-wallet-agent-api.py batch-v2 --chain <bnb|eth|base|solana> --address $ADDR --contract <token-addr-or-empty>
```
