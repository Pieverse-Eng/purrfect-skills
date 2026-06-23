# x402 Payments Domain Knowledge

## What is x402?

x402 is an open standard for internet-native payments, built on HTTP 402 ("Payment Required"). It enables AI agents to pay for API access, data, and services using crypto — no accounts, no API keys, no subscriptions.

**Why agents need this:** As AI agents call external APIs (market data, compute, storage, premium content), x402 lets them pay per-request with stablecoins instead of managing API keys and subscriptions.

## Protocol Flow

```
1. Agent → POST /resource → Resource Server
2. Resource Server → 402 Payment Required
   Headers: payment-required: base64(PaymentRequired JSON)
3. Agent decodes PaymentRequired, reads accepts[0] (amount, token, network, payTo, scheme)
4. `purr bitget x402-pay` signs EIP-3009 TransferWithAuthorization through the platform wallet
5. Agent → POST /resource + PAYMENT-SIGNATURE: base64(PaymentPayload JSON)
6. Resource Server → CDP Facilitator /verify → /settle → on-chain USDC transfer
7. Resource Server → 200 OK + data + payment-response header (settlement receipt)
```

**Key insight:** `purr bitget x402-pay` signs through the platform wallet but never broadcasts directly. The Facilitator pays gas and submits on-chain. The agent is truly gasless.

## Payment Schemes

### `exact` on EVM (EIP-3009)

The primary and preferred method for USDC payments.

`purr bitget x402-pay` signs a `TransferWithAuthorization` message (EIP-712 typed data) through the platform wallet:

```
Domain: { name: "USD Coin", version: "2", chainId, verifyingContract: USDC }
Types: { TransferWithAuthorization(from, to, value, validAfter, validBefore, nonce) }
```

**Signing payload fields:**
- `from`: Agent wallet address
- `to`: Resource server's `payTo` address
- `value`: Payment amount in smallest unit (e.g., 1000 = $0.001 USDC, 6 decimals)
- `validAfter`: `now - 600` (10-minute clock skew tolerance)
- `validBefore`: `now + maxTimeoutSeconds`
- `nonce`: Random 32 bytes (unique per authorization)

**Security properties:**
- Facilitator CANNOT modify amount or destination — signature binds both
- Signature is single-use (nonce prevents replay)
- Time-bounded (validBefore prevents stale authorization)
- Signing does NOT lock funds — just an authorization

### PaymentPayload Structure

The `PAYMENT-SIGNATURE` header is base64-encoded JSON:

```json
{
  "x402Version": 2,
  "accepted": {
    "scheme": "exact",
    "network": "eip155:8453",
    "amount": "1000",
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "payTo": "0x...",
    "maxTimeoutSeconds": 300,
    "extra": {"name": "USD Coin", "version": "2"}
  },
  "payload": {
    "signature": "0x...",
    "authorization": {
      "from": "0x...",
      "to": "0x...",
      "value": "1000",
      "validAfter": "1772785096",
      "validBefore": "1772785696",
      "nonce": "0x..."
    }
  }
}
```

**Important:** Do NOT include `resource` field in the payload (match official SDK behavior, `exclude_none`).

### Permit2 (Universal Fallback)

For tokens without EIP-3009. Uses Uniswap's Permit2 contract.
One-time setup: `approve(Permit2, max_uint256)` — costs gas once.
Not commonly needed since x402 is USDC-first.

### `exact` on Solana

Solana uses partially-signed transactions:
1. Agent builds a `VersionedTransaction` with SPL `TransferChecked`
2. `feePayer` = Facilitator's pubkey (from `extra.feePayer`)
3. The token authority signs, feePayer slot left empty
4. Facilitator validates, co-signs, broadcasts

Solana x402 partial signing is out of scope for this packaged skill. Use
`purr bitget x402-pay` only for EVM EIP-3009 payment-required flows.

## EIP-712 Signing

Do not implement EIP-3009 signing manually in this skill. Use
`purr bitget x402-pay` or `purr bitget x402-sign-eip3009`; the CLI handles the
x402-compatible EIP-712 hash, signs through the hosted platform wallet, and
returns the expected payment payload shape.

## Facilitator Ecosystem

| Facilitator | URL | Networks | Auth | Cost |
|------------|-----|----------|------|------|
| **CDP (Coinbase)** | `https://api.cdp.coinbase.com/platform/v2/x402` | Base, Base Sepolia, Solana, Solana Devnet | CDP API keys | Free 1000/mo, then $0.001/tx |
| x402.org | `https://x402.org/facilitator` | Base Sepolia, Solana Devnet only | None | Free (testnet only) |

**Notes:**
- CDP facilitator sponsors gas — agent pays zero ETH/SOL, only USDC
- Production services (Pinata, DiamondClaws, etc.) use CDP or their own facilitator
- Agent does NOT interact with facilitator directly — the resource server handles verify/settle
- x402.org is testnet-only, useful for signature validation during development

## Budget & Safety

**Agent spending controls:**
- Per-request maximum (e.g., $0.10 per API call)
- Per-session budget (e.g., $5.00 total per session)
- Per-day budget (e.g., $50.00 daily cap)
- Require user confirmation above threshold

**Risk model:**
- EIP-3009 signing does NOT lock funds — signature is just an authorization
- Multiple signatures can be outstanding simultaneously
- If wallet balance drops before settlement, later settlements fail (revert)
- This is credit risk, not theft risk — facilitator bears the loss, not the agent

## Key Contracts

### USDC (EIP-3009 compatible)
| Chain | USDC Address | Network ID |
|-------|-------------|-----------|
| Base | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | `eip155:8453` |
| Ethereum | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | `eip155:1` |
| Polygon | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` | `eip155:137` |
| Arbitrum | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` | `eip155:42161` |
| Base Sepolia | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` | `eip155:84532` |

All USDC contracts use EIP-712 domain: `name="USD Coin", version="2"`.

## Common Pitfalls

1. **Do not implement x402 signing manually.** Use `purr bitget x402-pay` or `purr bitget x402-sign-eip3009`.
2. **`authorization` must match signed message exactly.** If you sign `validAfter=X` but return `validAfter=Y`, the facilitator rejects it.
3. **`validAfter = now - 600`** (not `now`). 10-minute clock skew tolerance, matching the official SDK.
4. **Amount units are 6 decimals for USDC.** `1000` = $0.001, `1000000` = $1.00.
5. **Nonce must be unique per authorization.** Use `os.urandom(32)`.
6. **Do NOT include `resource` in PaymentPayload.** Official SDK excludes it.
7. **Multiple outstanding signatures = credit risk.** Signing doesn't lock funds.
8. **x402 is USDC-first.** USDT does NOT support EIP-3009 on most chains.

## Testing Guide

### Quick Test with Pinata (Base Mainnet, $0.001)

Pinata offers x402-paid IPFS uploads. No registration needed.

**Endpoint:** `POST https://402.pinata.cloud/v1/pin/private?fileSize=100`
**Cost:** $0.001 USDC on Base
**What you get:** A temporary upload URL for private IPFS storage

```bash
# Full end-to-end test using purr
purr bitget x402-pay \
  --url "https://402.pinata.cloud/v1/pin/private?fileSize=100" \
  --method POST \
  --data '{"fileSize": 100}'
```

**Expected output:**
```
Payment Required: $0.001000 USDC on eip155:8453
  payTo: 0xc900f41481B4F7C612AF9Ce3B1d16A7A1B6bd96E
...
Response: 200
Settlement: {
  "network": "eip155:8453",
  "payer": "0x...",
  "success": true,
  "transaction": "0x..."
}
{"url":"https://uploads.pinata.cloud/v3/files/..."}
```

**Prerequisites:**
- Base mainnet USDC balance > $0.001
- No ETH needed (facilitator sponsors gas)

**What happens:**
1. `purr bitget x402-pay` sends POST → gets 402 with `payment-required` header
2. Parses requirements: $0.001 USDC to Pinata on Base
3. Signs EIP-3009 TransferWithAuthorization through the platform wallet
4. Retries with `PAYMENT-SIGNATURE` header
5. Pinata's facilitator verifies signature, settles on-chain
6. Returns 200 + upload URL + settlement TX hash
