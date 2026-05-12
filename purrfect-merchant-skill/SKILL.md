---
name: purrfect-merchant-skill
description: >
  Operate a Pieverse A2A merchant: products, USDT/stablecoin payments, loyalty
  rewards, customer tracking. For shops, point-of-sale, and any Maolongxia
  ecosystem merchant — pod-hosted or self-hosted.
when_to_use: >
  Triggers on: setting up a shop or PoS to accept USDT or stablecoin payments,
  onboarding a merchant on a Pieverse tenant pod or self-hosted host, managing
  a product catalog or menu with prices, configuring loyalty programs or
  reward rules (e.g. "buy 10 get discount"), checking customer wallet history
  or coupons, generating wallet QR codes, troubleshooting payment settlement
  or reconciliation issues with the Credentials Provider (CP), running an A2A
  commerce payment server, or any HTTP 402 / A2A settlement flow on the
  Maolongxia / Pieverse stack. Covers boba shops, milk tea shops, food stalls,
  jewelry vendors — any small vendor accepting crypto.
  Do NOT use for: generic web dev or CI/CD, non-Pieverse payment integrations
  like Stripe / Binance Pay, platform admin actions (instance provisioning,
  shopId allocation, wallet binding — those live in the Pieverse platform
  admin docs), or anything that operates across multiple merchants.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - mcp__purrfect-merchant__*
metadata:
  openclaw:
    os: [linux, darwin]
    emoji: 🛍️
    requires:
      bins: [node]
  hermes:
    tags:
      - Merchant
      - Pieverse
      - Payments
      - A2A-Commerce
      - Crypto
      - USDT
      - Stablecoin
      - Loyalty
      - Coupons
      - LIFF
      - MCP
      - Maolongxia
    related_skills: []
---

# Purrfect Merchant

A merchant operations skill for turning a small vendor into a Pieverse A2A
merchant with membership tracking and loyalty rewards. The agent that uses
this skill is **the merchant's own agent** — it lives alongside one merchant
and acts on that merchant's behalf. It is not a platform-admin tool and has
no view of other merchants.

Discoverable from any agent framework:

- **Claude Code** — discovered via this SKILL.md
- **OpenClaw / ClawHub** — same SKILL.md with `metadata.openclaw` block
- **A2A-compatible agents** (Hermes, etc.) — `GET /.well-known/agent.json` on the HTTP server
- **MCP hosts** — `node src/mcp.js` exposes all operations as MCP tools via stdio JSON-RPC

This skill operates through three surfaces:
**CLI** (`node src/index.js`), **HTTP API** (`/buy`, `/.well-known/agent.json`),
and **MCP tools** (`purrfect_product_*`, `purrfect_customer_*`, etc.).

## Data Locality (read first)

All merchant state — products, customers, coupons, reward rules, orders,
payment events, profile, loyalty cursors — **lives in the in-pod (or
in-host) SQLite at `data/merchant.db`**. There is no platform-side
authoritative copy. There is no sync job. There is no admin API to mutate
these from outside.

If the agent finds itself reaching for a "platform API" to add a product or
update a reward, the routing is wrong — the answer is always the local CLI
or MCP tool. The only outbound calls this skill makes to the Pieverse
platform are the Pieverse A2A settlement call (`POST /v1/payments/settle`,
on paid Pieverse `/buy` retries), the OKX x402 merchant-payment helper calls
(`POST /v1/instances/:id/merchant-payments/okx-x402/*`, for orders whose
`paymentMethod` is `okx-x402`), and the SDK event-feed pull
(`GET /v1/payments/events`, owned by the loyalty reconciler process). These
are runtime dependencies, not configuration surfaces.

## Step 0: Confirm Where You're Running

The skill runs in two shapes. Both use the same CLI and MCP tools — the
difference is who supplies the public URL, the merchant wallet, and the
Pieverse API key.

1. **In-pod** — a tenant pod (Pieverse-managed, OpenClaw, Hermes) where the
   operator injects merchant config via env (`MERCHANT_WALLET`, `LIFF_ID`,
   `MERCHANT_SHOP_ID`, etc.) and the public URL is platform-served at
   `https://purr.pieverse.io/m/<shopId>/...`. The agent should not be
   asking the user for these — they are already there.
2. **Self-hosted** — the user runs `node src/index.js` on their own host
   (laptop, VPS, container they bought). The agent must collect a wallet
   address, a Pieverse API key, and a public HTTPS URL before doing
   anything else (see "Setup and Operation → Initial Setup").

### Detection

Run these checks in order; take the first match.

**Signal 1 (best): your own active tool list.**
If your tool list includes any `purrfect_*` MCP tool — `purrfect_product_list`,
`purrfect_customer_get`, `purrfect_order_create`, etc. — the skill's MCP
server is wired into your runtime. Use those tools for CRUD. (You can
confirm without side effects by calling `purrfect_product_list` or
`purrfect_profile_get` once.)

**Signal 2: skill source + SQLite reachable from disk.**
If you reach the skill via shell rather than MCP, probe the filesystem:

```bash
# Look for the skill source in conventional locations.
for skill_root in . /app /opt/skill /opt/purrfect-merchant-skill; do
  if [[ -f "$skill_root/src/db.js" && -f "$skill_root/src/index.js" ]]; then
    found_skill_root="$skill_root"
    break
  fi
done

# Resolve the SQLite path the skill would actually use
# (src/index.js:51-52 reads $MERCHANT_DB or falls back to data/merchant.db).
db_path="${MERCHANT_DB:-${found_skill_root:-.}/data/merchant.db}"

# Either the DB already exists, or its directory is writable so the skill
# can create it on first run.
if [[ -n "$found_skill_root" ]] \
   && { [[ -f "$db_path" ]] || [[ -w "$(dirname "$db_path")" ]]; }; then
  echo "skill at $found_skill_root, DB at $db_path"
fi
```

If signals 1 or 2 succeed, you can drive the skill. To distinguish in-pod
from self-hosted, look for the operator-injected env: `INSTANCE_ID`,
`MERCHANT_SHOP_ID`, or `MERCHANT_PUBLIC_CP_URL` are set inside Pieverse
pods and absent on a self-hosted host. The distinction only matters for
**setup** — in-pod skips initial setup because the platform did it; the
day-to-day CLI/MCP commands are identical.

### Out of scope: platform admin actions

This skill does not provision instances, allocate `shopId`, bind wallets,
toggle the merchant feature flag, or enable LIFF. Those are platform-admin
actions and live in the Pieverse platform's own admin docs and runbooks.
If a request looks like "create an instance for a new merchant", "give
this merchant a shop ID", or "POST `/v1/instances/:id/merchant`", the
agent reading this skill is not the right agent.

### Out of scope: forwarding from outside

The skill never receives platform-side admin webhooks or merchant routing
requests. The platform finds this merchant via its own `shopId →
instanceId` mapping (`instance.config.merchant.shopId` in platform
Postgres) and proxies traffic to the pod's HTTP server (`/buy`, `/api/*`,
`/liff/*`). Once traffic lands at the pod, this skill handles it.

## Quick Start

### In-pod (Pieverse / OpenClaw / Hermes)

The platform injects merchant config (`MERCHANT_WALLET`, `LIFF_ID`,
`MERCHANT_SHOP_ID`) into the pod, and `start-*.sh` already starts the
HTTP server. As the merchant agent, you mostly drive day-to-day operations
through MCP tools:

```
purrfect_product_add        # add a menu item
purrfect_order_create       # create an order to charge a customer
purrfect_recent_payments    # answer "最近有付款吗"
purrfect_sales_today        # answer "今天卖了多少"
```

If the loyalty reconciler isn't running, start it as a sidecar:

```bash
node examples/loyalty-reconciler.js &
```

### Self-hosted

```bash
npm install
node src/index.js setup "<shop name>" <0xWallet> <pieverse-api-key>
node src/index.js product add "Coffee" 5000000000000000000
node src/index.js qr                                  # data/merchant-qr.png
node src/index.js serve                               # HTTP on :3000
node examples/loyalty-reconciler.js                   # async reconciler sidecar
```

You also need a public HTTPS URL pointing at port 3000 (Cloudflare Tunnel,
Tailscale Funnel, or any reverse proxy with TLS — see Setup and Operation
§1 for options).

## Quick Reference

| Action | CLI | MCP tool |
|---|---|---|
| Add / update / remove product | `node src/index.js product {add,update,remove}` | `purrfect_product_{add,update,remove}` |
| List products | `node src/index.js product list` | `purrfect_product_list` |
| Create order | — | `purrfect_order_create` (`paymentMethod` defaults to `pieverse-a2a`; use `okx-x402` for X Layer OKX orders) |
| Look up order | `curl /order/<code>` | `purrfect_order_get` |
| List customers + spend | `node src/index.js customer list` | `purrfect_customer_list` |
| Recent payments | — | `purrfect_recent_payments` |
| Today's / week's / all-time sales | — | `purrfect_sales_{today,week,summary}` |
| Add reward rule | `node src/index.js reward add ...` | `purrfect_reward_add` |
| List / redeem coupon | `node src/index.js coupon {list,redeem}` | `purrfect_coupon_{list,redeem}` |
| Generate QR (wallet or LIFF) | `node src/index.js qr` | `purrfect_qr_generate` |
| Reconcile failed settlements | `node src/index.js reconcile {list,resolve}` | — |
| Inspect event cursor health | — | `purrfect_event_cursor_status` |

Detailed flag/argument docs are under **Setup and Operation** below.

## When to Use This Skill

Activate this skill when the user or agent wants to:

- Set up a merchant shop to accept crypto payments
- Add, update, or manage products with prices in stablecoins
- Generate a QR code for their public merchant endpoint
- Accept payments via the Pieverse A2A Commerce Protocol
- Track customer purchases and membership by wallet address
- Create loyalty reward rules (e.g., "after 10 purchases, get 1U off")
- View or manage coupons
- Check failed settlements for reconciliation

## When NOT to Use

- **Generic web dev / CI/CD / general programming** — this skill is purely about merchant operations.
- **Non-Pieverse payment integrations** — Stripe, Binance Pay, PayPal, etc. live in their own SDKs.
- **Platform admin actions** — provisioning instances, allocating `shopId`, binding wallets, toggling the merchant feature flag, enabling LIFF. Those are platform-admin actions and live in the Pieverse platform's own admin docs.
- **Cross-merchant operations** — aggregating across shops, querying multiple merchants. The skill agent only sees its own merchant's SQLite.
- **Customer-side flows** — buying, scanning, paying. This skill is the seller side; customer agents read the public agent card and 402 challenge.

## Prerequisites & Runtime

**Runtime** — Node.js ≥ 22 (ESM). Runs in a Pieverse tenant pod, an
OpenClaw / Hermes harness, or a self-hosted Linux/macOS host. Container
images (`packages/container/Dockerfile` in the platform monorepo) bundle
the skill at `/app/upstream-merchant-skill`; self-hosted users `git
clone` and `npm install`.

**Runtime dependencies** (auto-installed via `npm install`):

- `@pieverseio/merchant-sdk` — A2A event-feed subscription
- `better-sqlite3` — local SQLite (WAL mode, all amounts stored as TEXT)
- `hono` + `@hono/node-server` — HTTP server
- `qrcode` — QR PNG generation
- `jose` — LIFF ID-token verification (cached JWKS)
- `zod` — `/api/*` request-body schema validation

**Discovery surfaces this skill exposes:**

- **A2A agent card** — `GET /.well-known/agent.json` returns the
  `AgentCard` JSON (`@pieverse-eng/shared` schema, `protocol: a2a/1.0`).
  Customer agents discover the merchant via this endpoint. The card is
  rendered by `src/agent-card.js` from local SQLite + config.
- **MCP server** — `node src/mcp.js` over stdio JSON-RPC, exposing 24
  `purrfect_*` tools. Auto-spawned for OpenClaw + Claude Code via the
  `.mcp.json` at repo root; for Hermes, merge the snippet in `hermes.yaml`
  into `~/.hermes/config.yaml`.
- **HTTP API** — `GET /buy`, `GET /order/:code`, `POST /api/orders`,
  `GET /api/catalog`, `GET /api/profile`, plus the `/liff/*` static
  bundle. See **Agent Integration** below for full details.

**External dependencies**: Pieverse A2A orders call
`POST /v1/payments/settle` from `src/handlers/settle.js` on paid `/buy`
retries, and OKX x402 orders call
`POST /v1/instances/:id/merchant-payments/okx-x402/*` from
`src/handlers/okx-x402.js`. The CP/platform base URL defaults to
`https://purr.pieverse.io`.

## Async Event Reconciliation

The skill's HTTP server settles each `/buy` synchronously, but a separate
**reconciler** process consumes the Pieverse event feed (`GET
/v1/payments/events`) so settled payments still land in the local
`event_inbox` even if the synchronous flow was interrupted (deploy, crash,
network blip). `merchant.subscribe()` from `@pieverseio/merchant-sdk@0.2.1`
owns polling, retry/backoff, and a cursor stored in the local SQLite.

This repo ships a runnable reference at `examples/loyalty-reconciler.js`:

```bash
node examples/loyalty-reconciler.js
```

Run it as a sidecar process alongside the HTTP server (same host, same
SQLite file). Handlers are idempotent — replayed events and already-recorded
credentials are skipped, so running the reconciler in parallel with the
synchronous `/buy` flow is safe and recommended.

## Setup and Operation

### 1. Initial Setup

**Ask the user for these three inputs before running anything. Do not proceed until you have all three.**

1. **Public HTTPS URL** — the URL customer agents will hit. If the user doesn't
   have one yet, offer them concrete options (see "Getting a public HTTPS URL"
   below) and let them pick. `http://localhost:3000` is **dev only** —
   external buyer agents should reject non-TLS 402 endpoints in production.
2. **Merchant wallet address** — the EVM address that receives payments.
   0x-prefixed, 40 hex chars.
3. **Pieverse API key** — the bearer key the skill uses to call
   `POST /v1/payments/settle`. Obtain from the Pieverse onboarding flow at
   `purr.pieverse.io/agent-onboard.md`. Store securely; the skill writes it to
   `data/config.json` with `0o600` permissions.

**Getting a public HTTPS URL** — offer the user 2–3 of these and let them pick:

| Option                        | Notes                                                                                                                      |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Cloudflare Tunnel**         | Production-grade, free tier, automatic TLS, no open ports. `cloudflared tunnel --url http://localhost:3000`. Good default. |
| **Tailscale Funnel**          | Similar to Cloudflare Tunnel, requires a Tailscale account. `tailscale funnel 3000`.                                       |
| **ngrok**                     | Dev/testing only. Free-tier URLs rotate and are rate-limited. Not for production.                                          |
| **VPS + Caddy**               | Run the Node process on a VPS, front it with Caddy for automatic Let's Encrypt TLS. Needs a domain.                        |
| **VPS + nginx + certbot**     | Same pattern, manual TLS renewal. Needs a domain.                                                                          |
| **Fly.io / Railway / Render** | Managed platforms with HTTPS out of the box. Deploy from git.                                                              |

Once you have all three inputs, run:

```bash
cd <project-dir>
npm install
node src/index.js setup "<shop-name>" <wallet-address> <pieverse-api-key>
```

This creates `data/config.json` with merchant wallet, API key, and defaults (USDT on BSC chain 56). Environment variables override config values:

| Variable           | Purpose                                                     |
| ------------------ | ----------------------------------------------------------- |
| `MERCHANT_WALLET`  | On-chain wallet address                                     |
| `PIEVERSE_API_KEY` | Credentials Provider API key                                |
| `PIEVERSE_CP_URL`  | Pieverse API base URL (default: `https://purr.pieverse.io`) |
| `TOKEN_ADDRESS`    | Token contract (default: USDT BSC)                          |
| `CHAIN_ID`         | Blockchain (default: 56)                                    |
| `PORT`             | HTTP server port (default: 3000)                            |
| `PUBLIC_URL`       | Public HTTPS base URL for non-platform merchants            |
| `RATE_LIMIT`       | Max requests/min per IP (default: 60)                       |
| `LOG_LEVEL`        | Logging verbosity: error/warn/info/debug                    |

> **Naming note — CP base URL.** `PIEVERSE_CP_URL` (this skill's env var),
> `MERCHANT_PUBLIC_CP_URL` (the platform operator's injected env var inside
> tenant pods), `cpBaseUrl` (the `@pieverseio/merchant-sdk` constructor arg),
> and the `payment.settleUrl` field on the agent card all refer to the same
> thing: the **Pieverse CP base URL** (default `https://purr.pieverse.io`).
> Self-hosted merchants running the `cp-service` standalone peer implementation
> point all of them at their own CP instead.

### 2. Product Management

Add products before accepting payments. Prices are in token base units (e.g., 1 USDT = 1000000000000000000 with 18 decimals):

```bash
node src/index.js product add "Matcha Latte" 5000000000000000000
node src/index.js product add "Boba Tea" 4000000000000000000
node src/index.js product list              # human-readable table
node src/index.js product list --json       # JSON array for programmatic use
node src/index.js product update 1 "Matcha Latte" 6000000000000000000
node src/index.js product remove 2
```

Prices must be non-negative integers. The skill validates input and rejects non-numeric values.

Product names are treated as the merchant-facing identity for menu items.
Before adding a product, list the catalog and compare names after trimming
whitespace and ignoring case. If the same product name already exists, do
not add another row and do not silently change the price. Ask the merchant
whether they want to update the existing product, including the existing
product id/name/price and the proposed new name/price. Only after the
merchant confirms should you call `purrfect_product_update` (or
`node src/index.js product update <id> ...`). If `purrfect_product_add`
returns `PRODUCT_NAME_CONFLICT`, treat that as this exact confirmation step.

### 3. QR Code Generation

Generate a printable QR code of the merchant's public endpoint:

```bash
node src/index.js qr                       # saves to data/merchant-qr.png
node src/index.js qr /path/to/output.png   # custom path
```

### 4. Start the Payment Server

Launch the HTTP server to accept A2A payments:

```bash
node src/index.js serve
```

The server exposes these endpoints:

- `GET /health` — health check with shop name
- `GET /.well-known/agent.json` — A2A discovery for customer agents
- `GET /buy?product=<id>&wallet=<customer-wallet>` — issues HTTP 402 Pieverse A2A payment challenge
- `GET /buy?order=<code>&wallet=<customer-wallet>` — pays a merchant-created Pieverse A2A order
- `GET /buy?order=<code>` — for an order created with `paymentMethod: "okx-x402"`, returns an OKX x402 `PAYMENT-REQUIRED` header. Retrying the same URL with `PAYMENT-SIGNATURE` settles through platform's OKX service.
- `GET /buy` (no params) — returns product listing

**Payment flow (what happens automatically):**

1. Customer's agent hits `GET /buy?product=1&wallet=0xCustomer...`
2. Skill returns HTTP 402 with Pieverse A2A challenge JSON containing amount, token, chain, recipient, and a `challengeId`
3. If the customer has an active coupon, the amount is automatically reduced
4. Customer's agent authorizes via the Credentials Provider and retries the same merchant `GET /buy` request with `X-Pieverse-Payment: pt_live_*`
5. Skill calls `POST /v1/payments/settle` on the Pieverse API (`https://purr.pieverse.io`) with `http_response` proof (content digest, status code, timestamp)
6. Skill verifies the settlement receipt matches the challenge amount, token, chain, and merchant wallet
7. On CP success, the skill **atomically** in one SQLite transaction:
   - Logs the payment record
   - Updates customer stats (payment count, total spent)
   - Evaluates all reward rules
   - Issues a coupon if any threshold is crossed
   - Redeems the applied coupon (if one was auto-applied)
8. Returns a JSON summary from the retried `GET /buy` request

For OKX x402 orders, the order stores `paymentMethod: "okx-x402"` locally.
Do not put `rail` or `paymentMethod` into the `buyUrl`; route selection comes
from the order row. The first `/buy?order=<code>` call asks platform to build
the `PAYMENT-REQUIRED` header; the retry with `PAYMENT-SIGNATURE` asks platform
to settle through OKX broker and then records the local payment/order as paid.

**If CP succeeds but the DB write fails**, the settlement is recorded in a `failed_settlements` table for manual reconciliation. The payment is not silently lost.

### 5. Loyalty Rewards

Set up threshold-based rules that automatically issue coupons:

```bash
# After 10 payments, issue a coupon worth 1 USDT
node src/index.js reward add payment_count 10 1000000000000000000

# After spending 50 USDT total, issue a coupon worth 5 USDT
node src/index.js reward add total_spent 50000000000000000000 5000000000000000000

node src/index.js reward list
node src/index.js reward remove <id>
```

**How rewards work:**

- Each rule fires **exactly once** per customer per rule (enforced by DB UNIQUE constraint)
- When a customer's stats cross a threshold after a payment, a coupon is created
- Active coupons are **auto-applied** to the next 402 challenge for that customer
- Applied coupons enter `pending_redemption` state to prevent concurrent use
- On settlement, the coupon is redeemed; on challenge expiry, it reverts to `active`

### 6. Customer & Coupon Management

```bash
node src/index.js customer list                  # all customers with summary stats
node src/index.js customer 0xWalletAddress       # detail + payment history
node src/index.js coupon list                    # all coupons
node src/index.js coupon list 0xWalletAddress    # coupons for specific customer
node src/index.js coupon redeem <id>             # manually redeem a coupon
```

### 7. Reconciliation

Check for settlements that succeeded at the CP but failed locally:

```bash
node src/index.js reconcile list
node src/index.js reconcile resolve <id>
```

### 8. Async Event Reconciliation

See the "Async Event Reconciliation" section above. Run it as a sidecar
alongside the HTTP server — same SQLite, idempotent handlers, no
double-counting.

### All Commands Support `--json`

Append `--json` to any command for structured JSON output suitable for agents and scripts:

```bash
node src/index.js product list --json
node src/index.js customer list --json
node src/index.js reconcile list --json
```

## Agent Behavior Guidelines

When representing the merchant, follow these behaviors to make event visibility feel natural.

### Start of each conversation

Call `purrfect_unacked_events` as one of the first actions. If the result is non-empty, lead with a short summary, for example:

> 顺便告诉您，自上次对话后有 2 笔新付款，总计 240 USDT。要查看详情吗？

Only mention this if there are actually unacked events.

### When the merchant asks "最近有付款吗" / "recent payments" / similar

Call `purrfect_recent_payments`. Default `limit=10`. The tool auto-acknowledges returned events, so subsequent calls will not re-surface the same entries unless they matter to the new question. When `matchedOrder` is present, use the order code and description to summarize the payment in merchant-friendly terms.

### When the merchant wants to create or manage an order

Use `purrfect_order_create` for requests like "建个订单" or "收 12 USDT 的抹茶拿铁". Return the short code and order QR/payment URL. For the红包 OKX flow, pass `paymentMethod: "okx-x402"` and return the plain `buyUrl`; do not append route-selection query parameters. Use `purrfect_order_get` for "这个订单付了吗", `purrfect_order_list` for queues, and `purrfect_order_cancel` only when the merchant clearly wants to void a pending order.

### When the merchant wants to add menu/catalog items

Use `purrfect_product_list` first when adding items from a menu, photo, or
onboarding conversation. If a normalized duplicate name already exists
(case-insensitive, trimmed), stop and ask the merchant to confirm whether
the existing item should be updated. Do not infer consent from a repeated
menu upload, OCR retry, or similar-looking name. After confirmation, use
`purrfect_product_update` with the existing product id; otherwise leave the
existing product unchanged.

### When the merchant asks about sales

Use `purrfect_sales_today` for "今天卖了多少", `purrfect_sales_week` for recent trend questions, and `purrfect_sales_summary` for all-time totals or top customers/items. These reports use UTC day boundaries and local SQLite payment rows.

### When the merchant suspects missing events

Phrases like "顾客说付了但我没看到", "why didn't X go through", "事件好像没同步":

1. Call `purrfect_event_cursor_status` first. The tool returns `cursor`, `lastEventAt`, `unackedCount`, and `processedEventCount` from the local inbox. If `cursor` is null or `lastEventAt` looks much older than expected, the `examples/loyalty-reconciler.js` subscriber process may not be running or may be misconfigured — suggest the merchant check that the subscriber is live against the same SQLite file.
2. Once cursor health looks reasonable, call `purrfect_events` with whatever filter the customer can provide (`credential_id` if known, or a time window via `since`). The SDK owns poll scheduling, retry, and backoff, so there is nothing else for the skill to report beyond cursor health.

### Privacy

Do not include full customer wallet addresses or credential IDs in summary text when responding to the merchant. Summarize by count and amount. Surface raw identifiers only when the merchant specifically asks for them.

## Key Technical Details

- **Runtime:** Node.js 22+ ESM, 4 runtime deps (better-sqlite3, hono, qrcode, @pieverseio/merchant-sdk)
- **Database:** SQLite via better-sqlite3 with WAL mode, all amounts stored as TEXT, arithmetic via BigInt
- **HTTP:** Hono + @hono/node-server (14 KB, zero native HTTP deps)
- **Event subscription:** `@pieverseio/merchant-sdk@0.2.1` for `merchant.subscribe()` — the SDK owns polling, retry/backoff, cursor-ordered delivery, and `hasMore` draining. The skill's HTTP server does NOT run a built-in subscriber; `examples/loyalty-reconciler.js` is the runnable entrypoint that feeds the shared SQLite event inbox.
- **Rate limiting:** Sliding window per IP on /buy (configurable via RATE_LIMIT)
- **Logging:** Structured JSON to stdout/stderr for settlement events
- **Graceful shutdown:** SIGTERM/SIGINT closes DB and server cleanly
- **Security:** Wallet address validation (0x + 40 hex), config file 0o600 permissions, 15s fetch timeout on CP calls, settlement receipt validation, payment dedup via UNIQUE constraint on challenge_id

## Agent Integration

### A2A Discovery

When the HTTP server is running, any A2A-compatible agent can discover this merchant:

```
GET http://localhost:3000/.well-known/agent.json
```

Returns the agent card with skill definitions, input schemas, endpoints, and the Pieverse A2A extension URI. (The `localhost:3000` URL above is **dev only**; production merchants expose the card under their public HTTPS `PUBLIC_URL`.)

> **Source of truth for agent-card fields.** The locked field values —
> `version: "1.0"`, `payment.protocol: "pieverse-a2a-402"`, the `capabilities`
> block, and the `merchant` / `products` shapes — are defined in the
> `AgentCard` type exported by `@pieverse-eng/shared` and consumed by
> `@pieverseio/merchant-sdk@0.2.1`. Treat the SDK as authoritative: when the
> SDK bumps, re-read its `AgentCard` type before changing the card builder
> here so this skill and the SDK don't drift.

### MCP Tools

Connect any MCP host to the merchant's tools via stdio:

```bash
node src/mcp.js
```

Available MCP tools (24):

- `purrfect_product_add` — Add a product to the merchant catalog
- `purrfect_product_list` — List all products in the merchant catalog
- `purrfect_product_update` — Update a product name and/or price
- `purrfect_product_remove` — Remove a product from the catalog
- `purrfect_customer_list` — List all known customers with summary stats (total payments, total spent)
- `purrfect_customer_get` — Get customer details and payment history by wallet address
- `purrfect_reward_add` — Add a reward rule that issues coupons on thresholds
- `purrfect_reward_list` — List all reward rules
- `purrfect_reward_remove` — Deactivate a reward rule by ID
- `purrfect_coupon_list` — List coupons, optionally filtered by wallet address
- `purrfect_coupon_redeem` — Manually redeem a coupon by ID
- `purrfect_qr_generate` — Generate a QR code PNG encoding the merchant wallet address for walk-in payments
- `purrfect_order_create` — Create a pending order with amount, optional description, expiry, code, payment URL, and optional `paymentMethod` (`pieverse-a2a` or `okx-x402`)
- `purrfect_order_list` — List orders by status (`pending`, `paid`, `expired`, `cancelled`, or `all`)
- `purrfect_order_get` — Get one order by code, including linked payment context when paid
- `purrfect_order_cancel` — Cancel a pending order by code
- `purrfect_order_code_qr` — Generate a QR code PNG for the order payment URL
- `purrfect_recent_payments` — List recent settled payments from the local event inbox. Use when merchant asks "最近有付款吗" or "刚才谁付的钱". Auto-acknowledges by default.
- `purrfect_events` — Query the local event inbox with filters. Use for specific lookups like "credential xxx 的事件". Never auto-acknowledges.
- `purrfect_unacked_events` — List events the merchant has not yet seen. Call at the start of each conversation.
- `purrfect_event_cursor_status` — Report merchant event subscription cursor and local inbox health. Use first when the merchant suspects a missing payment.
- `purrfect_sales_today` — Summarize today's UTC sales totals, customers, order count, and top items
- `purrfect_sales_week` — Summarize the last 7 UTC days with daily breakdowns and totals
- `purrfect_sales_summary` — Summarize all-time sales with top customers, top items, and top orders

### Registering the MCP server

The repo ships ready-to-use config snippets at its root:

- **`.mcp.json`** — auto-discovered by **OpenClaw** and **Claude Code** when
  the skill is loaded. No extra registration needed for these two.
- **`hermes.yaml`** — merge into your `~/.hermes/config.yaml` under
  `mcp_servers:` (Hermes does not auto-spawn from skill frontmatter).
  After restart, tools surface as `mcp_purrfect-merchant_*`.

Claude Code users who prefer a global registration over per-project
discovery can add the same JSON to `~/.claude/settings.json` instead.

## File Layout

```
src/
├── index.js          CLI entrypoint (argv parsing, --json flag)
├── mcp.js            MCP server (stdio JSON-RPC, 24 tools)
├── agent-card.js     A2A agent card builder
├── server.js         Hono app with /buy, /health, /.well-known/agent.json + rate limiter
├── db.js             SQLite connection + migration runner
├── config.js         Config file + env var overrides
├── products.js       Product CRUD with input validation
├── qr.js             QR code PNG generation
├── customers.js      Customer upsert + payment history
├── rewards.js        Reward rules, coupon issuance/redemption, pending state
├── event-reconciler.js  Idempotent SDK event handler (loyalty + inbox record) used by examples/loyalty-reconciler.js
├── event-inbox.js    Phase A/B: migration-backed event_inbox table + MCP query helpers (recordEventInbox, listRecentPayments, listEvents, listUnackedEvents, acknowledgeEvents, getEventCursorStatus)
├── orders.js         Phase B: order CRUD, code generation, expiry, credential linking, paid-state helpers
├── sales.js          Phase C: UTC sales analytics over local payments and matched orders
├── logger.js         Structured JSON logging (zero deps)
├── ratelimit.js      Sliding window rate limiter (zero deps)
├── handlers/
│   ├── challenge.js  GET /buy → HTTP 402 challenge + coupon auto-apply + order payment branch
│   ├── order.js      GET /order/:code order details for customer agents
│   └── settle.js     CP settlement helpers + atomic post-processing + recovery
└── migrations/
    ├── 001_initial.sql
    ├── 002_payment_challenge_unique.sql
    ├── 003_failed_settlements.sql
    ├── 004_coupon_pending_status.sql
    ├── 005_payment_event_subscription.sql  # event_cursors + processed_payment_events (owned by event-reconciler.js)
    ├── 006_event_inbox.sql                  # Phase A: event_inbox table for MCP visibility
    └── 007_orders.sql                       # Phase B: orders + payment/event attribution columns
```

## Testing

```bash
npm test    # runs all tests
```

Covers: schema constraints, product CRUD, QR generation, full A2A payment flow (including CP errors 409/410/500/unreachable and DB failure recovery), customer tracking, reward thresholds, coupon lifecycle with pending_redemption, double-issuance prevention, wallet validation, payment dedup, logging, rate limiting, end-to-end integration, and CLI with --json output.
