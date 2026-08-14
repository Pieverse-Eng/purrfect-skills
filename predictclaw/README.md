# PredictClaw


PredictClaw is the predict.fun-native OpenClaw skill for browsing markets, checking wallet readiness, viewing funding guidance, withdrawing funds, placing buys, inspecting positions, and scanning hedge opportunities.

This repository packages PredictClaw as a standalone OpenClaw skill with its own CLI, runtime configuration, and tests.

PredictClaw's version source of truth is the repository-root `pyproject.toml`. When checking GitHub or building from source, use this repository root directly.

## What PredictClaw Is For

PredictClaw gives OpenClaw a predictable command surface for predict.fun workflows:

- market discovery and market detail lookup
- wallet readiness and deposit guidance
- trading through the EOA path; Predict Account currently supports auth/status only
- position journaling and query flows
- optional hedge analysis for users who enable model access

For the advanced funding route, PredictClaw supports a **Vault funding overlay** on top of the official Predict Account path. In that route, **Predict Account remains** the deposit address while Vault acts as the funding source; Predict Account order/withdraw execution still fails closed until the controlled Kernel execute path lands.

## Install

### ClawHub / packaged install

```bash
clawhub install predictclaw
cd ~/.openclaw/skills/predictclaw
uv sync
cp template.env .env
```

The installed skill directory `~/.openclaw/skills/predictclaw` is the only canonical user config root. In OpenClaw manifests and examples, this same installed path may appear as `{baseDir}`. Any repository checkout or workspace copy is a development-only artifact, not a user config root.

### Manual install

1. Copy or symlink this repository into `~/.openclaw/skills/predictclaw/`
2. From the installed skill directory, run:

```bash
cd {baseDir} && uv sync
cd {baseDir} && cp template.env .env
```

### Local repo development

From the repository root:

```bash
uv sync
uv run pytest -q
uv run python scripts/predictclaw.py --help
```

Use the repository root for development and tests only. Do not treat it as the canonical location for end-user `.env` edits or normal installed-skill CLI usage.

## How configuration actually works

PredictClaw only reads standard environment variables. The supported, tested inputs are:

- the process environment, for example `export PREDICT_ENV=testnet`
- a local `~/.openclaw/skills/predictclaw/.env` file, auto-loaded by `scripts/predictclaw.py` when present; in manifests and examples, that same installed path may appear as `{baseDir}`

If both are present, exported environment variables win and `.env` only fills missing values.

If your OpenClaw host version injects environment variables into the skill process, that also works because PredictClaw receives normal env vars either way. Older docs used `skills.entries.predictclaw.env`; treat that as a host-version-specific convenience, not the canonical PredictClaw config surface.

The SKILL frontmatter declares only the external runtimes (`uv`, `node`) needed for prompt inclusion. Mode-specific environment requirements are documented below and enforced by the runtime config validator; there is no env allowlist gate in the frontmatter.

## Mode-first onboarding (recommended)

Choose the mode first, then fill only the minimum fields for that mode.

- `read-only`
  - Use for browsing only.
  - Minimum fields: `PREDICT_ENV`, `PREDICT_WALLET_MODE`, `PREDICT_API_KEY` for mainnet reads.
- `eoa`
  - Use for platform-wallet signer trading without Predict Account overlay.
  - Minimum fields: `PREDICT_ENV`, `PREDICT_WALLET_MODE=eoa`, `PREDICT_API_KEY`, `WALLET_API_URL`, `WALLET_API_TOKEN`, `INSTANCE_ID` (plus optional `WALLET_CHAIN_ID`). The skill never reads an EOA private key in this path.
- `predict-account + ERC_MANDATED_*` (recommended funding route)
  - Use when Predict Account stays the deposit identity and Vault may fund it. Predict Account `buy`/`wallet withdraw` fail closed until controlled Kernel execute lands.
  - Ask first: **Do you already have a vault?**
  - **Have a vault** -> minimum fields: `PREDICT_ENV`, `PREDICT_WALLET_MODE=predict-account`, `PREDICT_API_KEY`, `PREDICT_ACCOUNT_ADDRESS`, `WALLET_API_URL`, `WALLET_API_TOKEN`, `INSTANCE_ID`, `ERC_MANDATED_CHAIN_ID`, `ERC_MANDATED_VAULT_ADDRESS`, optional `ERC_MANDATED_CONTRACT_VERSION`. Predict Account signing requires the paired platform `messageEncoding: "hex"` seam (platform PR #2030).
  - **Need a vault** -> deploy or redeploy a vault first with the pure `mandated-vault` bootstrap flow, then come back to overlay.
- pure `mandated-vault` (recommended governance/control-plane path)
  - Use for bootstrap, governance, and vault-only control-plane workflows.
  - Minimum fields: `PREDICT_ENV`, `PREDICT_WALLET_MODE=mandated-vault`, `PREDICT_API_KEY`, `WALLET_API_URL`, `WALLET_API_TOKEN`, `INSTANCE_ID`, `ERC_MANDATED_CHAIN_ID`. The bundled `@erc-mandated/sdk` one-shot helper prepares plans; the platform wallet API broadcasts execution.

PredictClaw never accepts raw private keys for executor/authority/bootstrap roles. Vault deployment and execution go through the platform wallet API; the bundled SDK helper only prepares plans and encoded data.
Do not treat the full derivation tuple as the primary first-step answer for overlay onboarding when the user already has a deployed vault.

## First-time setup (recommended)

1. Install the skill and run `uv sync`.
2. Pick a bootstrap file:
    - `template.env` -> secret-free local fixture bootstrap
    - `template.readonly.env` -> live read-only market reads
    - `template.eoa.env` -> platform-wallet trading
    - `template.predict-account.env` -> Predict Account auth/status
    - `template.predict-account-vault.env` -> Predict Account + vault funding/status
    - `template.mandated-vault.env` -> internal/compatibility bootstrap template
3. Copy the chosen template to `.env` inside `~/.openclaw/skills/predictclaw/`.
4. Fill only the variables required for that mode.
5. Verify the install with `uv run python scripts/predictclaw.py --help`.
6. Then run a mode-appropriate command:
   - fixture bootstrap -> `uv run python scripts/predictclaw.py markets trending`
   - live read-only -> `uv run python scripts/predictclaw.py markets trending`
   - `eoa` / `predict-account` -> `uv run python scripts/predictclaw.py wallet status --json`
   - `predict-account + vault` -> `uv run python scripts/predictclaw.py wallet status --json`

### Choose your route first

- `read-only` for browsing only.
- When the goal is to keep Predict Account as the deposit identity and let Vault only fund it, immediately choose `predict-account + ERC_MANDATED_*`.
- pure `mandated-vault` is a separate control-plane path for creating a new Vault or directly operating Vault control-plane flows.

If you want Vault funding without changing the Predict Account deposit identity, start from `template.predict-account.env`, use `PREDICT_WALLET_MODE=predict-account`, and treat that as the default answer for the "keep the official account, let Vault fund it" workflow. Predict Account `buy`/`wallet withdraw` fail closed until controlled Kernel execute lands. Do not start from pure `wallet bootstrap-vault` unless you are creating a new vault or working on the control plane directly.

For overlay onboarding, ask the vault question first:

- **Have a vault** -> provide `ERC_MANDATED_VAULT_ADDRESS`, then let PredictClaw resolve or validate the remaining vault metadata where possible.
- **Need a vault** -> deploy or redeploy a vault first with the pure `mandated-vault` bootstrap flow.

Do not treat the full derivation tuple as the primary first-step answer for overlay onboarding unless the user is explicitly on the advanced/manual recovery path.

## Bootstrap templates

- `template.env` -> safest first install; uses `test-fixture` + `read-only` so the CLI can start without secrets or network access
- `template.readonly.env` -> live market reads; mainnet market reads require PREDICT_API_KEY
- `template.eoa.env` -> EOA signer flow, pinned to mainnet with `https://api.predict.fun`
- `template.predict-account.env` -> Predict Account auth/status, pinned to mainnet with `https://api.predict.fun`
- `template.predict-account-vault.env` -> canonical user-facing template for Predict Account + vault funding/status
- `template.mandated-vault.env` -> internal/compatibility bootstrap template used during vault creation or recovery

### Recommended operating model

- For user-facing Predict Account funding/status, recommend `predict-account + vault`.
- In that model, Predict Account remains the deposit address, while Vault acts as the funding/control plane. Predict Account `buy`/`wallet withdraw` fail closed until controlled Kernel execute lands.
- `mandated-vault` is not a standalone user mode; it remains the internal/bootstrap path used when a vault still needs to be created or prepared.

## Real first-install paths

### A. CLI boots successfully

```bash
uv sync
uv run python scripts/predictclaw.py --help
```

### B. Secret-free local verification

Copy `template.env` and run:

```bash
uv run python scripts/predictclaw.py markets trending
```

This uses `test-fixture`, so it proves the skill boots and routes commands correctly without touching the live API.
Fixture mode only knows the bundled fixture market IDs (`123`, `456`, `789`, `101`, `202`). For real market IDs, switch to the live read-only template first.

### C. Live read-only market reads

Copy `template.readonly.env` to read live production markets on mainnet.

```bash
uv run python scripts/predictclaw.py markets trending
uv run python scripts/predictclaw.py market <market_id> --json
```

If mainnet reads fail with `401 unauthorized`, your `PREDICT_API_KEY` is missing or invalid.

### D. Signer-backed flows

wallet status requires signer configuration. `wallet status --json` is the right next step for `eoa` and `predict-account`, but it is not the first command to run in `read-only` mode.

### E. Mode-first minimum field rule

Do not paste the full env matrix first. Ask which mode the user is choosing, then show only the minimum fields for that mode. Add advanced authority/executor/bootstrap keys only when the selected flow actually needs vault-side execution.

## Configuration examples

The snippets below are `.env` examples. Put them in `~/.openclaw/skills/predictclaw/.env` (the same installed path sometimes shown as `{baseDir}`) or export the same names in your shell.

`OPENROUTER_API_KEY` only matters for non-fixture `hedge scan` / `hedge analyze` usage. It is not required for market, wallet, or buy flows.

### bootstrap-safe fixture mode

```dotenv
PREDICT_ENV=test-fixture
PREDICT_WALLET_MODE=read-only
```

Use this for secret-free CLI verification and local market browsing only. It does not hit the live API. Switch to `eoa`, `predict-account`, or `predict-account + vault` before using wallet or trade subcommands.

### live read-only mode

```dotenv
PREDICT_ENV=mainnet
PREDICT_WALLET_MODE=read-only
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
```

Mainnet market reads require `PREDICT_API_KEY`.

### eoa mode

The default EOA path signs through the instance-scoped platform wallet API; the skill never reads an EOA private key.

```dotenv
PREDICT_ENV=mainnet
PREDICT_WALLET_MODE=eoa
PREDICT_API_BASE_URL=https://api.predict.fun
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
WALLET_API_URL=https://YOUR_PLATFORM_WALLET_API
WALLET_API_TOKEN=YOUR_PLATFORM_WALLET_TOKEN
INSTANCE_ID=YOUR_INSTANCE_ID
WALLET_CHAIN_ID=56
```

### predict-account mode

Predict Account signing needs the paired platform `/wallet/sign` `messageEncoding: "hex"` seam (platform PR #2030). Until the controlled Kernel execute path lands, Predict Account is limited to auth and read-only status: `buy` and `wallet withdraw` fail closed with `unsupported-predict-account-execution`, and the skill must not fall back to a raw Privy key.

```dotenv
PREDICT_ENV=mainnet
PREDICT_WALLET_MODE=predict-account
PREDICT_API_BASE_URL=https://api.predict.fun
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
PREDICT_ACCOUNT_ADDRESS=0xYOUR_PREDICT_ACCOUNT
WALLET_API_URL=https://YOUR_PLATFORM_WALLET_API
WALLET_API_TOKEN=YOUR_PLATFORM_WALLET_TOKEN
INSTANCE_ID=YOUR_INSTANCE_ID
```

### predict-account + vault onboarding

The user-facing advanced mode is `predict-account + vault`, not a standalone `mandated-vault` mode.

Start from the canonical template:

```dotenv
PREDICT_ENV=mainnet
PREDICT_API_BASE_URL=https://api.predict.fun
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
PREDICT_WALLET_MODE=predict-account
PREDICT_ACCOUNT_ADDRESS=0xYOUR_PREDICT_ACCOUNT
WALLET_API_URL=https://YOUR_PLATFORM_WALLET_API
WALLET_API_TOKEN=YOUR_PLATFORM_WALLET_TOKEN
INSTANCE_ID=YOUR_INSTANCE_ID
ERC_MANDATED_VAULT_ADDRESS=0xYOUR_DEPLOYED_VAULT
ERC_MANDATED_VAULT_ASSET_ADDRESS=0xYOUR_ASSET
ERC_MANDATED_VAULT_AUTHORITY=0xYOUR_AUTHORITY
ERC_MANDATED_CONTRACT_VERSION=v0.3.0-agent-contract
ERC_MANDATED_CHAIN_ID=56
```

If you already have a vault, bind it through `ERC_MANDATED_VAULT_ADDRESS` and the related authority/asset values.

If you do not yet have a vault, use the bootstrap helper first.

### Internal bootstrap subflow (`mandated-vault`)

The older `mandated-vault` path still exists internally as the bootstrap/compatibility subflow that creates or prepares a vault before you return to the user-facing `predict-account + vault` route.

```dotenv
PREDICT_ENV=mainnet
PREDICT_API_BASE_URL=https://api.predict.fun
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
PREDICT_WALLET_MODE=mandated-vault
WALLET_API_URL=https://YOUR_PLATFORM_WALLET_API
WALLET_API_TOKEN=YOUR_PLATFORM_WALLET_TOKEN
INSTANCE_ID=YOUR_INSTANCE_ID
ERC_MANDATED_CHAIN_ID=56
```

PredictClaw uses the fixed product factory `0x6eFC613Ece5D95e4a7b69B4EddD332CeeCbb61c6`, previews the deployment first, then requires explicit confirmation before broadcast. After `--confirm`, it returns a `submitted` status plus a manual env block; it does not wait for a receipt and does not auto-edit `.env`.

On `--confirm`, PredictClaw plans with the bundled SDK helper and broadcasts the resulting transaction request through the platform wallet API.

Preview first:

```bash
uv run python scripts/predictclaw.py wallet bootstrap-vault --json
```

Confirm and broadcast:

```bash
uv run python scripts/predictclaw.py wallet bootstrap-vault --confirm --json
```

Optional bootstrap amount / funding controls:

```dotenv
ERC_MANDATED_FUNDING_MAX_AMOUNT_PER_TX=5000000000000000000
ERC_MANDATED_FUNDING_MAX_AMOUNT_PER_WINDOW=10000000000000000000
ERC_MANDATED_FUNDING_WINDOW_SECONDS=3600
```

### Internal bootstrap compatibility paths

If you intentionally need the internal bootstrap path directly, these legacy/compatibility variants still exist:

#### Explicit deployed vault

```dotenv
PREDICT_ENV=mainnet
PREDICT_API_BASE_URL=https://api.predict.fun
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
PREDICT_WALLET_MODE=mandated-vault
WALLET_API_URL=https://YOUR_PLATFORM_WALLET_API
WALLET_API_TOKEN=YOUR_PLATFORM_WALLET_TOKEN
INSTANCE_ID=YOUR_INSTANCE_ID
ERC_MANDATED_VAULT_ADDRESS=0xYOUR_DEPLOYED_VAULT
ERC_MANDATED_CHAIN_ID=56
```

Use this only when you intentionally need the internal bootstrap path to target an already deployed vault.

#### Full derivation tuple

```dotenv
PREDICT_ENV=mainnet
PREDICT_API_BASE_URL=https://api.predict.fun
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
PREDICT_WALLET_MODE=mandated-vault
ERC_MANDATED_FACTORY_ADDRESS=0xYOUR_FACTORY
ERC_MANDATED_VAULT_ASSET_ADDRESS=0xYOUR_ASSET
ERC_MANDATED_VAULT_NAME=Mandated Vault
ERC_MANDATED_VAULT_SYMBOL=MVLT
ERC_MANDATED_VAULT_AUTHORITY=0xYOUR_AUTHORITY
ERC_MANDATED_VAULT_SALT=0xYOUR_SALT
ERC_MANDATED_CONTRACT_VERSION=v0.3.0-agent-contract
ERC_MANDATED_CHAIN_ID=56
```

When the predicted vault is still undeployed, PredictClaw surfaces preparation details and `manual-only` guidance without broadcasting.

The platform wallet API is the only execution/signing authority in the default path.

### predict-account + vault overlay (recommended advanced funding route)

```dotenv
PREDICT_ENV=mainnet
PREDICT_API_BASE_URL=https://api.predict.fun
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
PREDICT_WALLET_MODE=predict-account
PREDICT_ACCOUNT_ADDRESS=0xYOUR_PREDICT_ACCOUNT
WALLET_API_URL=https://YOUR_PLATFORM_WALLET_API
WALLET_API_TOKEN=YOUR_PLATFORM_WALLET_TOKEN
INSTANCE_ID=YOUR_INSTANCE_ID
ERC_MANDATED_VAULT_ADDRESS=0xYOUR_DEPLOYED_VAULT
ERC_MANDATED_CONTRACT_VERSION=v0.3.0-agent-contract
ERC_MANDATED_CHAIN_ID=56
```

If you already have a deployed vault, this is the primary overlay path: provide `ERC_MANDATED_VAULT_ADDRESS` and let PredictClaw resolve the remaining vault metadata where possible.

If you do **not** have a vault yet, the recommended answer is to deploy or redeploy one first with the pure `mandated-vault` bootstrap flow. The full derivation tuple (`ERC_MANDATED_FACTORY_ADDRESS`, `ERC_MANDATED_VAULT_ASSET_ADDRESS`, `ERC_MANDATED_VAULT_NAME`, `ERC_MANDATED_VAULT_SYMBOL`, `ERC_MANDATED_VAULT_AUTHORITY`, and `ERC_MANDATED_VAULT_SALT`) remains available as an advanced/manual path rather than the default first step.

Only if automatic resolution fails should you manually add advanced vault metadata such as `ERC_MANDATED_VAULT_ASSET_ADDRESS` or `ERC_MANDATED_VAULT_AUTHORITY`.

Optional overlay caps:

```dotenv
ERC_MANDATED_FUNDING_MAX_AMOUNT_PER_TX=5000000000000000000
ERC_MANDATED_FUNDING_MAX_AMOUNT_PER_WINDOW=10000000000000000000
ERC_MANDATED_FUNDING_WINDOW_SECONDS=3600
```

In the overlay route, Predict Account remains the deposit account while Vault funds it through SDK-helper-backed session and asset-transfer planning. Predict Account `buy`/`wallet withdraw` still fail closed until controlled Kernel execute lands.

This is the correct route when Predict Account remains the deposit identity and Vault only supplies funds.

## Wallet Modes

PredictClaw supports four user-facing modes:

- `read-only` — browse market data only; no signer-backed wallet actions.
- `eoa` — platform-wallet signer path for wallet, trade, and funding flows (no private key in the default path).
- `predict-account` — smart-wallet auth/status path using `PREDICT_ACCOUNT_ADDRESS` plus the paired platform `messageEncoding: "hex"` seam (platform PR #2030); `buy`/`withdraw` fail closed until controlled Kernel execute lands.
- `predict-account + vault` — Predict Account remains the deposit identity while Vault acts as the advanced funding source; trading still fail closed until controlled Kernel execute lands.

### Recommended route

If the goal is to keep Predict Account as the deposit identity while Vault only funds it, use:

- `PREDICT_WALLET_MODE=predict-account`
- plus the required `ERC_MANDATED_*` overlay inputs (`predict-account + ERC_MANDATED_*`)

This is the default route for the Predict Account funding workflow. It exposes `vault-to-predict-account` semantics in `wallet status --json` and `wallet deposit --json`. Predict Account `buy`/`wallet withdraw` fail closed until controlled Kernel execute lands.

### How to answer "what address should I fund?"

- In `predict-account + vault`, the default user-facing answer is: fund the Vault deposit flow first.
- Predict Account remains the deposit identity and receives the downstream vault-driven top-up afterward.
- `wallet deposit --json` / `wallet status --json` therefore distinguish:
  - the default funding entry (`manualTopUpAddress` / `fundingAddress`) -> Vault
  - the account / recipient (`predictAccountAddress`, `tradingIdentityAddress`) -> Predict Account
- Only answer with the Predict Account deposit page when the active route is plain `predict-account` without the vault funding overlay.

### Internal bootstrap note

`mandated-vault` is an internal/bootstrap compatibility subflow, **not a standalone user mode**. It is used when PredictClaw needs to create or prepare a vault before returning to `predict-account + vault`.

The default pure bootstrap flow signs through the platform wallet API, needs deployment-fee funding, and accepts optional amount caps. PredictClaw handles the product-configured factory `0x6eFC613Ece5D95e4a7b69B4EddD332CeeCbb61c6`, previews before broadcast, requires explicit confirmation, and returns a manual env block after success.

Pure `mandated-vault` does **not** provide predict.fun trading parity. `wallet approve`, `wallet withdraw`, `buy`, `positions`, `position`, `hedge scan`, and `hedge analyze` fail closed with `unsupported-in-mandated-vault-v1`.

### Common configuration mistakes

- `read-only` is browse-only. Start with `markets ...`, not signer-backed wallet or trade commands.
- `wallet status` requires signer configuration. In `read-only`, start with `markets trending` or `market <id> --json` instead.
- `mainnet` market reads require `PREDICT_API_KEY`; missing keys fail early and invalid keys return `401 unauthorized`.
- `eoa` requires the platform wallet API (`WALLET_API_URL`, `WALLET_API_TOKEN`, `INSTANCE_ID`) and rejects Predict Account or mandated-vault inputs.
- `predict-account` requires `PREDICT_ACCOUNT_ADDRESS` plus the paired platform `messageEncoding: "hex"` seam; it must not fall back to a raw key in the default path.
- `mainnet` requires `PREDICT_API_KEY`.
- pure `mandated-vault` uses the bundled `@erc-mandated/sdk` one-shot helper for planning; the platform wallet API broadcasts execution. In overlay mode the default path is an explicit `ERC_MANDATED_VAULT_ADDRESS`, with asset and authority metadata resolved automatically where possible and only escalated to manual fields when that resolution fails.

## The bundled `@erc-mandated/sdk` helper

The default Purrfect path uses an exact-pinned `@erc-mandated/sdk` one-shot Node helper (no MCP stdio transport).

The bundled helper covers the Vault control plane:

1. **Vault prediction / preparation** — predict a vault address when only the derivation tuple is available.
2. **Vault bootstrap planning** — preview pure mandated-vault deployment through `vault_bootstrap` plan mode.
3. **Vault overlay orchestration** — expose `vault-to-predict-account` routing, funding-policy context, and session planning.
4. **Control-plane safety boundary** — if the helper is missing or unhealthy, PredictClaw surfaces a fail-closed error instead of silently guessing.

The helper is a local script, not a globally installed binary. Install its dependencies once:

```bash
cd {baseDir}/node && npm install
```

PredictClaw does not globally install packages and does not auto-edit `.env` in the default path.

The bundled SDK helper orchestrates transport and preparation; the platform wallet API holds signing/approval/broadcast authority, and the vault contract policy authorizes what the vault can actually execute.

## Command Surface

```bash
uv run python scripts/predictclaw.py markets trending
uv run python scripts/predictclaw.py markets search "election"
uv run python scripts/predictclaw.py market 123 --json
uv run python scripts/predictclaw.py wallet status --json
uv run python scripts/predictclaw.py wallet approve --json
uv run python scripts/predictclaw.py wallet deposit --json
uv run python scripts/predictclaw.py wallet bootstrap-vault --json
uv run python scripts/predictclaw.py wallet bootstrap-vault --confirm --json
uv run python scripts/predictclaw.py wallet withdraw usdt 1 0xb30741673D351135Cf96564dfD15f8e135f9C310 --json
uv run python scripts/predictclaw.py wallet withdraw bnb 0.1 0xb30741673D351135Cf96564dfD15f8e135f9C310 --json
uv run python scripts/predictclaw.py buy 123 YES 25 --json
uv run python scripts/predictclaw.py positions --json
uv run python scripts/predictclaw.py position pos-123-yes --json
uv run python scripts/predictclaw.py hedge scan --query election --json
uv run python scripts/predictclaw.py hedge analyze 101 202 --json
```

## Core workflow notes

- `wallet status` reports signer mode, funding guidance, balances, and approval readiness.
- `wallet deposit` is a funding-guidance command: in `predict-account + vault`, it shows the Vault deposit flow as the default funding entry, while still separating the Predict Account recipient / trading identity and the orchestration vault metadata.
- `wallet bootstrap-vault` is the pure mandated-vault preview / confirmation entry point.
- The default bootstrap flow uses the fixed factory `0x6eFC613Ece5D95e4a7b69B4EddD332CeeCbb61c6`; after confirmation it returns `submitted + manual env block`, not a claimed deployment.
- `wallet redeem-vault --preview --json` previews vault-share redemption and reports `redeemableNow`, `blockingReason`, and decoded contract errors such as `ERC4626ExceededMaxRedeem`.
- `wallet withdraw` validates checksum destination, positive amount, available balance, and BNB gas headroom before attempting transfer logic.
- In fixture mode, withdraw commands return deterministic placeholder transaction hashes instead of touching a chain.
- In `predict-account + ERC_MANDATED_*` overlay, `wallet status` / `wallet deposit` expose:
  - `manualTopUpAddress`
  - `tradingIdentityAddress`
  - `predictAccountAddress`
  - `tradeSignerAddress`
  - `orchestrationVaultAddress`
  - `vaultAddress`
  - `fundingRoute = vault-to-predict-account`
- Default funding now goes through the Vault deposit flow.
- Predict Account remains the deposit identity / order account; order execution is fail closed until controlled Kernel execute lands.
- The internal orchestration target remains the Predict Account, but the user-facing funding ingress is the Vault.
- Optional Vault funding-policy envs let you cap Vault→Predict transfers by per-tx amount, cumulative window amount, and window duration.
- Vault-related JSON now also surfaces `vaultAuthority`, `vaultExecutor`, `bootstrapSigner`, `allowedTokenAddresses`, and `allowedRecipients` so users and OpenClaw can reason about permissions directly.
- Those funding-policy amounts use raw token units; for BSC mainnet USDT (18 decimals), `5 U = 5000000000000000000` and `10 U = 10000000000000000000`.
- Predict Account `buy` currently fails closed with `unsupported-predict-account-execution` regardless of balance, until controlled Kernel execute lands; it does not auto-execute the vault funding leg in the current local signer context.

### Redeem preview

Use the preview-only redeem diagnostic before attempting any future exit flow:

```bash
uv run python scripts/predictclaw.py wallet redeem-vault --share-token 0x4a88c1c95d0f59ee87c3286ed23e9dcdf4cf08d7 --holder 0x7df0ba782D85B93266b595d496088ABFAc823950 --all --preview --json
```

This reads the share token, underlying asset, `maxRedeem`, `maxWithdraw`, and a simulated redeem call. The response includes `redeemableNow`, `blockingReason`, and `contractError`. The current flow is intentionally `preview-only`.

## Runtime Modes

- `test-fixture` — uses local JSON fixtures and deterministic wallet/hedge/trade behavior; ideal for development, integration tests, and secret-free first-install verification.
- `mainnet` — requires `PREDICT_API_KEY` even for market reads and should be treated as a live-trading environment.
- `testnet` — still supported only when you explicitly opt into a non-mainnet environment; it is no longer a packaged default or recommended onboarding path.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `PREDICT_STORAGE_DIR` | Local journal and position storage |
| `PREDICT_ENV` | Defaults to `mainnet` in code; `template.env` intentionally bootstraps `test-fixture`; accepted values are `mainnet`, `testnet`, or `test-fixture` |
| `PREDICT_WALLET_MODE` | Explicit mode override: `read-only`, `eoa`, `predict-account`, or `mandated-vault` |
| `PREDICT_API_BASE_URL` | Optional REST base override; packaged live templates pin this to `https://api.predict.fun`, while leaving it empty uses the env-specific default |
| `PREDICT_API_KEY` | Mainnet-authenticated predict.fun API access; required for mainnet market reads and trading |
| `WALLET_API_URL` | Platform wallet application API base URL (default signer path) |
| `WALLET_API_TOKEN` | Platform wallet bearer token (never printed or logged) |
| `INSTANCE_ID` | Platform wallet instance id |
| `WALLET_CHAIN_ID` | Optional chain id override for platform wallet sign/approve calls |
| `PREDICT_ACCOUNT_ADDRESS` | Predict Account smart-wallet address |
| `ERC_MANDATED_VAULT_ADDRESS` | Explicit deployed mandated vault address |
| `ERC_MANDATED_FACTORY_ADDRESS` | Product default factory for pure bootstrap and manual derivation override; current default is `0x6eFC613Ece5D95e4a7b69B4EddD332CeeCbb61c6` |
| `ERC_MANDATED_VAULT_ASSET_ADDRESS` | ERC-4626 asset used in mandated-vault prediction/create preparation |
| `ERC_MANDATED_VAULT_NAME` | Vault name used in mandated-vault prediction/create preparation |
| `ERC_MANDATED_VAULT_SYMBOL` | Vault symbol used in mandated-vault prediction/create preparation |
| `ERC_MANDATED_VAULT_AUTHORITY` | Authority address and create-vault `from` address for manual preparation |
| `ERC_MANDATED_VAULT_SALT` | Deterministic salt used for vault prediction/create preparation |
| `ERC_MANDATED_CONTRACT_VERSION` | Passed through to the mandated SDK helper |
| `ERC_MANDATED_CHAIN_ID` | Optional explicit chain selection for the mandated SDK helper |
| `ERC_MANDATED_ALLOWED_ADAPTERS_ROOT` | Optional 32-byte hex `allowedAdaptersRoot` used for Vault execution mandates; defaults to `0x11…11` for the current single-key MVP / PoC path |
| `ERC_MANDATED_FUNDING_MAX_AMOUNT_PER_TX` | Optional Vault→Predict funding-policy `maxAmountPerTx` in raw token units |
| `ERC_MANDATED_FUNDING_MAX_AMOUNT_PER_WINDOW` | Optional Vault→Predict funding-policy `maxAmountPerWindow` in raw token units |
| `ERC_MANDATED_FUNDING_WINDOW_SECONDS` | Optional Vault→Predict funding-policy `windowSeconds` |
| `OPENROUTER_API_KEY` | Hedge analysis model access |
| `PREDICT_MODEL` | OpenRouter model override |

## Hedge notes

- Hedge analysis uses OpenRouter over plain HTTP with a JSON-only contract.
- `OPENROUTER_API_KEY` is only required for non-fixture hedge analysis.
- Fixture mode uses deterministic keyword- and pairing-based hedge portfolios so CLI and integration tests stay secret-free.
- The current public command surface remains PolyClaw-parity plus `wallet deposit` / `wallet withdraw`; there is no public `sell` command in v1.

## Project Layout

- `scripts/predictclaw.py` — top-level CLI router
- `scripts/` — command-specific entry points
- `lib/` — config, auth, REST, wallet, funding, trade, positions, hedge, platform wallet, and mandated SDK bridge logic
- `tests/` — unit, integration, and smoke coverage for the Python skill package

## Verification Layers

```bash
# unit + command tests
uv run pytest -q

# fixture-backed end-to-end CLI checks
uv run pytest tests/integration -q

# env-gated smoke (passes or skips)
uv run pytest tests/smoke/test_testnet_smoke.py -q
```

## Safety Notes

- Do not treat fixture mode as proof of funded-wallet behavior.
- Do not assume live liquidity from docs alone.
- Keep only limited funds on automation keys.
- Withdrawal commands are public; transfer validation happens before chain interaction, but users still own the operational risk.
- `predict-account + ERC_MANDATED_*` is the recommended advanced funding route when you want Vault to fund the Predict Account; Predict Account order execution remains fail closed until controlled Kernel execute lands.
- Explicit-vs-predicted vault semantics: `ERC_MANDATED_VAULT_ADDRESS` targets an existing vault directly; otherwise PredictClaw uses the derivation tuple to ask the bundled SDK helper for the predicted vault address.
- If a predicted vault is undeployed, `wallet bootstrap-vault --json` returns preview details (`predictedVault`, transaction summary, confirmation required) without broadcasting.
- Advanced/manual derivation flows can still return create-vault preparation details with `manual-only` guidance when you intentionally stay on the manual path.
- Pure `mandated-vault` does not provide predict.fun trading parity and intentionally fails closed for unsupported paths with `unsupported-in-mandated-vault-v1`.
- Platform wallet boundary: the default Purrfect path never reads or exports raw private keys. All signatures, approvals, and broadcasts go through the instance-scoped platform wallet API.
- ERC-20 approval is bounded: the default platform-wallet path never requests an unlimited `maxUint256` allowance. `buy` checks the current USDT allowance and issues a bounded approval for the requested order amount (decimal amount with explicit `decimals=18`) only when needed; an existing sufficient allowance is left untouched. The platform `/wallet/approve` endpoint with `amount: 0` is the tightening/revocation path. Raw-key legacy overrides fail closed for `buy` because they cannot provide a bounded approval.
- Predict Account remains an explicit paired dependency on platform PR #2030 (`messageEncoding: "hex"`, EIP-191 raw-bytes seam) and must not fall back to raw keys or MCP in the default path. Until controlled Kernel execute lands, `buy` and `wallet withdraw` fail closed with `unsupported-predict-account-execution`.

## Provenance

Ported from `tabilabs/predictfunclaw` @ `9e4e8b4f75694ae7d2b015a1da445bad3ca39e09`, CC0 license retained. This repository preserves the upstream `LICENSE` and records the source commit in `PROVENANCE.md`.
