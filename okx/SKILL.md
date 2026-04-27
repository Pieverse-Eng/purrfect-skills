---
name: okx
description: Use when the user wants OKX-powered token research, market data, public wallet portfolio analysis, smart-money signals, meme token scanning, security checks, DEX swaps, cross-chain bridging, DeFi investing (deposit/redeem/stake/lend), DeFi portfolio viewing, wallet operations, WebSocket market data sessions, buyer-side x402 payment, audit-log troubleshooting, gateway preflight queries, or seller-side x402 payment collection (adding a paywall to the user's own HTTP API via the `@okxweb3/x402-*` SDK).
metadata:
  {
    "openclaw":
      {
        "primaryEnv": "OKX_API_KEY",
        "requires": { "env": ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE"] },
      },
  }
---

# OKX

`okx` is the OKX domain router. It classifies user intent and dispatches to the appropriate vendor skill, or to the Seller Integration section below for paywall setup.

Vendor skills under `vendor/` use the `onchainos` CLI to interact with OKX APIs. The Seller Integration path uses the `@okxweb3/x402-*` SDK instead. No purr CLI is required.

Do not use this skill for Pieverse A2A `paymentRequired` challenges — route to the `pieverse-a2a` skill. Do not use this skill for Morph L2 x402 USDC payments (chainId 2818) — route to the `morph` skill. Use this skill only for OKX's own x402 flow (buyer-side authorization via `vendor/okx-x402-payment`, or seller-side paywall via the Seller Integration section below).

## Credentials

Runtime OKX operations (any `onchainos` command that calls the backend, and seller-SDK payment verification / settlement) require API credentials. Ask the user directly if they are not configured:

| Credential | Env var | Description |
|---|---|---|
| **API Key** | `OKX_API_KEY` | API key from the OKX Developer Portal |
| **Secret Key** | `OKX_SECRET_KEY` | Secret key paired with the API key |
| **Passphrase** | `OKX_PASSPHRASE` | Passphrase set during API key creation |

If the user hasn't set up OKX credentials yet, they need to:
1. Apply at the [OKX Developer Portal](https://web3.okx.com/onchain-os/dev-portal)
2. Create an API key and note the key, secret, and passphrase
3. Configure the three env vars above in their environment

Do not proceed with any authenticated `onchainos` command, live seller payment verification, or runtime payment flow until all three credentials are present. Repo inspection, routing, reference selection, and code scaffolding may proceed before credentials are configured.

## Scope

- Read:
  - token search, metadata, rankings, holders, clusters
  - prices, candles, address activity, wallet PnL
  - public wallet portfolio lookup by address
  - smart-money / whale / KOL signals
  - meme / trenches token scanning
  - token / DApp / tx / signature risk checks
  - OKX audit-log troubleshooting
  - OKX gateway chains / gas / gas-limit / simulate / orders
  - DeFi position viewing (per-protocol positions, portfolio overview)
  - DeFi product discovery (APY / TVL / V3 depth & price charts)
  - cross-chain bridge quote comparison and status tracking
  - WebSocket channel management (price, candle, trades, signals, meme)
- Write:
  - swap quote, approve, and execute via DEX aggregation
  - cross-chain bridge execution (Stargate / Across / Relay / Gas.zip)
  - DeFi deposit / redeem / stake / lend / borrow / repay / claim / LP add / LP remove
  - wallet lifecycle, auth, balance, send, tx history, contract call
  - buyer-side x402 payment authorization for payment-gated resources
- Build:
  - seller-side x402 payment layer — add paywall middleware to the user's own HTTP API (TypeScript / Rust / Go)

## Vendor Skills

Each vendor skill's `SKILL.md` teaches the agent the exact `onchainos` commands and parameters for that domain. Follow those instructions as-is.

| Vendor Skill | What it does |
|---|---|
| `vendor/okx-dex-token` | Token search, metadata, market cap, rankings, liquidity pools, hot tokens, holder analysis, top traders, trade history, holder cluster analysis |
| `vendor/okx-dex-market` | Real-time prices, K-line charts, index prices, wallet PnL analysis, address tracker activities |
| `vendor/okx-dex-ws` | WebSocket session management for real-time DEX data (price, candle, trades, price-info, signals, tracker, meme scanning) |
| `vendor/okx-wallet-portfolio` | Public address balance, token holdings, portfolio value |
| `vendor/okx-dex-signal` | Smart money / whale / KOL signal tracking, leaderboard rankings |
| `vendor/okx-dex-trenches` | Meme pump / trenches token scanning, dev reputation, bundle detection, aped wallets |
| `vendor/okx-security` | Token risk, DApp phishing, tx pre-execution, signature safety, approval management |
| `vendor/okx-audit-log` | Audit log export and troubleshooting guidance |
| `vendor/okx-onchain-gateway` | Gas estimation, tx simulation, broadcasting status, order tracking |
| `vendor/okx-dex-swap` | Swap quote, approve, and execute via DEX aggregation (500+ liquidity sources) |
| `vendor/okx-dex-bridge` | Cross-chain bridge — quote comparison, fee/time optimization, execution, and lifecycle status tracking across multiple bridge protocols |
| `vendor/okx-defi-invest` | DeFi investing — product discovery (APY/TVL/V3 charts), deposit, redeem, claim, stake, lend, borrow, repay, LP add/remove |
| `vendor/okx-defi-portfolio` | DeFi portfolio view — positions overview and per-protocol position detail across lending, staking, LP, and yield protocols |
| `vendor/okx-agentic-wallet` | Wallet lifecycle, auth, balance, portfolio PnL, send, tx history, contract call |
| `vendor/okx-x402-payment` | Buyer-side x402 payment authorization for payment-gated resources |

## Setup / Pre-flight Checks

Before using this skill, verify the `onchainos` CLI is available:

```bash
if command -v onchainos &>/dev/null; then
  echo "onchainos is available"
else
  echo "onchainos is NOT available"
fi
```

If it is **not available**, install it from the OKX GitHub release:

```bash
ONCHAINOS_VERSION="v2.4.1"
ONCHAINOS_TARGET=$(case "$(uname -m)" in x86_64) echo x86_64-unknown-linux-gnu ;; aarch64|arm64) echo aarch64-unknown-linux-gnu ;; i686) echo i686-unknown-linux-gnu ;; armv7l) echo armv7-unknown-linux-gnueabihf ;; *) echo "Unsupported architecture: $(uname -m)" >&2; exit 1 ;; esac)
ONCHAINOS_BINARY="onchainos-${ONCHAINOS_TARGET}"
curl -fsSL -o /tmp/onchainos "https://github.com/okx/onchainos-skills/releases/download/${ONCHAINOS_VERSION}/${ONCHAINOS_BINARY}"
curl -fsSL -o /tmp/onchainos-checksums.txt "https://github.com/okx/onchainos-skills/releases/download/${ONCHAINOS_VERSION}/checksums.txt"
ONCHAINOS_EXPECTED_SHA=$(grep "${ONCHAINOS_BINARY}" /tmp/onchainos-checksums.txt | awk '{print $1}')
ONCHAINOS_ACTUAL_SHA=$(sha256sum /tmp/onchainos | awk '{print $1}')
test -n "${ONCHAINOS_EXPECTED_SHA}" && test "${ONCHAINOS_ACTUAL_SHA}" = "${ONCHAINOS_EXPECTED_SHA}"
install -m 0755 /tmp/onchainos /usr/local/bin/onchainos
rm -f /tmp/onchainos /tmp/onchainos-checksums.txt
onchainos --version
```

---

### Pre-flight notes

The upstream vendor SKILL.md files include `onchainos` installer / updater / integrity-check steps. Use the setup check above instead, then follow the vendor SKILL.md as-is for everything else: command syntax, parameter formats, chain naming, and wallet operations.

## Supported Chains

Upstream OKX skills support: X Layer, Solana, Ethereum, Base, BSC, Arbitrum, Polygon, and 20+ additional chains depending on the specific capability.

**x402 payment chain support:**

- **Buyer** (`vendor/okx-x402-payment`): any EVM chain (`eip155:*`) returned by `onchainos wallet chains`. Non-EVM chains (Solana / Tron / Ton / Sui) are not supported.
- **Seller** (Seller Integration): **X Layer only** (`eip155:196`). OKX facilitator does not settle other networks.

## Routing

| User intent | Route to |
|---|---|
| "find token", "token metadata", "top holders", "cluster analysis", "hot tokens", "token rankings" | `vendor/okx-dex-token` |
| "price", "chart", "kline", "wallet pnl", "address activity", "index price" | `vendor/okx-dex-market` |
| "real-time price stream", "ws start", "subscribe to trades", "candle stream", "WebSocket channels" | `vendor/okx-dex-ws` |
| "check this address", "public portfolio", "wallet holdings by address", "address balance" | `vendor/okx-wallet-portfolio` |
| "smart money", "whale", "kol", "leaderboard", "top traders by PnL" | `vendor/okx-dex-signal` |
| "meme scanner", "trenches", "pump token", "dev reputation", "bundle detection" | `vendor/okx-dex-trenches` |
| "is this token safe", "scan dapp", "scan tx", "check signature risk", "approval management" | `vendor/okx-security` |
| "audit log", "okx log path", "export audit log" | `vendor/okx-audit-log` |
| "supported gateway chains", "gas price", "gas limit", "simulate tx", "track order", "broadcast status" | `vendor/okx-onchain-gateway` |
| "swap tokens", "buy tokens", "sell tokens", "trade", "get swap quote" | `vendor/okx-dex-swap` |
| "bridge tokens", "cross-chain transfer", "move assets between chains", "bridge quote", "bridge status" | `vendor/okx-dex-bridge` |
| "invest in DeFi", "earn yield", "deposit into Aave", "stake ETH on Lido", "APY", "TVL", "add liquidity", "redeem", "claim rewards", "borrow / repay" | `vendor/okx-defi-invest` |
| "check my DeFi positions", "view DeFi holdings", "my DeFi portfolio", "show staking positions", "show lending positions" | `vendor/okx-defi-portfolio` |
| "wallet balance", "wallet login", "send tokens", "tx history" | `vendor/okx-agentic-wallet` |
| "pay for 402 resource", "sign x402 payment", "payment-gated URL" (OKX x402 buyer side, not Pieverse/Morph) | `vendor/okx-x402-payment` |
| "add payment to my API", "charge per call", "monetize my endpoint", "add x402 paywall" (seller side) | **Seller Integration** section below |

## Routing Rules

- Route queries directly to the matching vendor skill — the vendor SKILL.md has the full command reference
- If a read result leads to an on-chain action, follow the vendor skill's execution flow
- For DeFi: viewing positions → `okx-defi-portfolio`; changing positions (deposit/redeem/stake/borrow/etc.) → `okx-defi-invest`
- For cross-chain movement: always `okx-dex-bridge` (not `okx-dex-swap`, which is same-chain)

## Typical Workflows

Vendor skills compose naturally in common DeFi flows.

- **Portfolio overview**: `vendor/okx-wallet-portfolio` → `vendor/okx-defi-portfolio` → `vendor/okx-dex-token` → `vendor/okx-dex-market`
- **Market research**: `vendor/okx-dex-token` → `vendor/okx-dex-market`
- **Search and buy**: `vendor/okx-dex-token` (find token) → `vendor/okx-wallet-portfolio` (check funds) → `vendor/okx-dex-swap` (execute trade)
- **Pre-flight check**: `vendor/okx-onchain-gateway` (gas / simulate / order tracking)
- **Swap and broadcast**: `vendor/okx-dex-swap` (get tx data) → sign locally → `vendor/okx-onchain-gateway` (broadcast + track)
- **Cross-chain move**: `vendor/okx-wallet-portfolio` (check source balance) → `vendor/okx-dex-bridge` (quote + execute) → `vendor/okx-dex-bridge` (status tracking)
- **Yield hunting**: `vendor/okx-defi-invest` (product discovery: APY/TVL) → `vendor/okx-security` (protocol risk check) → `vendor/okx-defi-invest` (deposit)
- **DeFi position review and action**: `vendor/okx-defi-portfolio` (see positions) → `vendor/okx-defi-invest` (redeem / claim / add liquidity)
- **Live price monitoring**: `vendor/okx-dex-ws` (subscribe price/candle/trades) → `vendor/okx-dex-swap` (act on signal)
- **Leaderboard to trade**: `vendor/okx-dex-signal` (top traders) → `vendor/okx-dex-token` (token analytics) → `vendor/okx-dex-swap` (execute)
- **Follow smart money**: `vendor/okx-dex-signal` → `vendor/okx-dex-token` → `vendor/okx-dex-market` → `vendor/okx-dex-swap`
- **Security check before trade**: `vendor/okx-security` (token / DApp / tx scan) → `vendor/okx-dex-token` (confirm details)
- **Meme research**: `vendor/okx-dex-trenches` (scanning) → `vendor/okx-dex-token` (holder clusters) → `vendor/okx-security` (risk check)
- **Full trading flow**: `vendor/okx-dex-token` (search) → `vendor/okx-dex-market` (price/chart) → `vendor/okx-wallet-portfolio` (check balance) → `vendor/okx-dex-swap` (get tx) → `vendor/okx-onchain-gateway` (simulate + broadcast + track)

## Operational Checklist

1. Verify OKX credentials are configured — if not, ask the user to set them up
2. Detect user intent
3. Match intent to the routing table above
4. Follow the vendor skill's SKILL.md for the exact `onchainos` commands, or the Seller Integration section for SDK-based paywall setup
5. Return the result directly

## Seller Integration (x402 payment collection)

Add an x402 payment layer to the user's own HTTP API using the `@okxweb3/x402-*` SDK, so buyers and AI Agents can pay per API call, settled in USDT0/USDG on X Layer (chainId 196). Covers TypeScript, Rust, and Go backends.

### Inputs to confirm or collect

For each row below: if the value is already available (in env, in earlier conversation turns, or in the project), repeat it back to the user for a one-line confirmation; if missing, ask for it. Never echo secret values back to the user; for credentials, confirm presence/status only. Do not guess, default, or fabricate.

| # | Input | Example |
|---|---|---|
| 1 | Language | TypeScript / Rust / Go |
| 2 | Brief API description | `weather query` |
| 3 | HTTP route to charge for | `GET /weather` |
| 4 | Server base URL (wherever buyers will reach it) | `http://localhost:4021` for local dev, `https://api.example.com` for production |
| 5 | Price per call | `$0.01` or `0.1 USDT` |
| 6 | Payment mode | One-time (`exact`), batch (`aggr_deferred`), or both |
| 7 | Receiving wallet on X Layer (chainId 196) | `0xb483abdb92f8061e9a3a082a4aaaa6b88c381308` |
| 8 | OKX API credentials status | `OKX_API_KEY` / `OKX_SECRET_KEY` / `OKX_PASSPHRASE` configured in the environment |

### Payment mode selection

Ask for the payment mode if the user has not specified it. Do not silently default. If the user is unsure, explain the modes and ask them to choose.

| Mode | Route scheme | Register on `eip155:196` | Use when | Notes |
|---|---|---|---|---|
| One-time payment | `exact` | TypeScript: `new ExactEvmScheme()`; Go: `exact.NewExactEvmScheme()`; Rust: `ExactEvmScheme::new()` | Normal paid API calls, higher-value resources, or requests that should have independent settlement | `syncSettle` can be used when delivery should wait for on-chain confirmation |
| Batch payment | `aggr_deferred` | TypeScript: `new AggrDeferredEvmScheme()`; Go: `deferred.NewAggrDeferredEvmScheme()`; Rust: `AggrDeferredEvmScheme::new()` | High-frequency, low-value AI agent calls, micropayments, streaming billing, or bulk API usage | Requires the OKX Agentic Wallet buyer flow; uses session-key signing; `syncSettle` is not applicable |
| Both | `exact` + `aggr_deferred` | Register both schemes and include both payment options in the route `accepts` list | Support both ordinary one-time buyers and Agentic Wallet batch buyers | Keep both options on the same protected route config |

The minimal route patterns below are TypeScript-shaped examples for scheme selection. For Go and Rust syntax, open the matching `references/SELLER-*.md` and apply the same scheme: one-time uses `exact`, batch uses `aggr_deferred`.

Minimal one-time route pattern:

```typescript
resourceServer.register("eip155:196", new ExactEvmScheme());

const routes = {
  "GET /api/data": {
    accepts: [{
      scheme: "exact",
      network: "eip155:196",
      payTo: "0xSellerWallet",
      price: "$0.01",
    }],
    description: "Premium data endpoint",
    mimeType: "application/json",
  },
};
```

Minimal batch route pattern:

```typescript
resourceServer.register("eip155:196", new AggrDeferredEvmScheme());

const routes = {
  "GET /api/data": {
    accepts: [{
      scheme: "aggr_deferred",
      network: "eip155:196",
      payTo: "0xSellerWallet",
      price: "$0.001",
    }],
    description: "Data endpoint with deferred batch settlement",
    mimeType: "application/json",
  },
};
```

Batch buyers include a session certificate in `accepted.extra.sessionCert`. Seller code should pass the payment through the SDK/facilitator flow as-is and does not need to parse that field.

### Credentials Handling

Never ask the user to paste raw API secrets into chat unless they explicitly insist.

- If the required env vars are missing, ask the user to set them in the environment:
  - `OKX_API_KEY`
  - `OKX_SECRET_KEY`
  - `OKX_PASSPHRASE`
- If the user does not have OKX credentials yet, tell them to apply through the [OKX Developer Portal](https://web3.okx.com/onchain-os/dev-portal), then add the issued values to the environment as the env vars above

### Delegation

Open the reference matching the user's language — it has the SDK surface, imports, and code patterns. Substitute the user's collected inputs into the reference's example code.

| Language | Reference |
|---|---|
| TypeScript / Node.js | [`references/SELLER-typescript.md`](references/SELLER-typescript.md) |
| Rust | [`references/SELLER-rust.md`](references/SELLER-rust.md) |
| Go | [`references/SELLER-go.md`](references/SELLER-go.md) |

The router skill is responsible only for collecting inputs and routing to the correct reference.

### Verify

After the user starts their server, confirm integration with a single unpaid request:

```bash
curl -i <base-url>/<route>
```

Expect `HTTP/1.1 402 Payment Required` with a `PAYMENT-REQUIRED` header (base64-encoded `PaymentRequired` JSON). If a 2xx comes back, the middleware is not wired correctly — revisit the reference.

### What's out of scope

- The user's business logic inside the handler
- Deployment, monitoring, scaling
- KYT / risk screening (built into OKX facilitator)

## File Map

| What | Path |
|---|---|
| OKX domain router (this file) | `okx/SKILL.md` |
| Token research | `okx/vendor/okx-dex-token/` |
| Market data | `okx/vendor/okx-dex-market/` |
| WebSocket market streams | `okx/vendor/okx-dex-ws/` |
| Public wallet portfolio | `okx/vendor/okx-wallet-portfolio/` |
| Smart money signals | `okx/vendor/okx-dex-signal/` |
| Trenches / meme scan | `okx/vendor/okx-dex-trenches/` |
| Security checks | `okx/vendor/okx-security/` |
| Audit-log troubleshooting | `okx/vendor/okx-audit-log/` |
| Gateway queries / preflight | `okx/vendor/okx-onchain-gateway/` |
| DEX swap (same-chain) | `okx/vendor/okx-dex-swap/` |
| DEX bridge (cross-chain) | `okx/vendor/okx-dex-bridge/` |
| DeFi investing | `okx/vendor/okx-defi-invest/` |
| DeFi portfolio viewing | `okx/vendor/okx-defi-portfolio/` |
| Agentic wallet | `okx/vendor/okx-agentic-wallet/` |
| Buyer-side x402 payment | `okx/vendor/okx-x402-payment/` |
| Seller-side x402 — TypeScript reference | `okx/references/SELLER-typescript.md` |
| Seller-side x402 — Rust reference | `okx/references/SELLER-rust.md` |
| Seller-side x402 — Go reference | `okx/references/SELLER-go.md` |
