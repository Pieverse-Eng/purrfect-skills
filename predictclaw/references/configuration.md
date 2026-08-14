# PredictClaw configuration

This file is the long-form configuration reference for PredictClaw. Keep the
trigger / main flow / safety boundary content in `SKILL.md`; keep mode matrices,
env tables, and copy-paste examples here.

## Config precedence

PredictClaw reads standard environment variables:

- the process environment;
- a local `~/.openclaw/skills/predictclaw/.env` file, auto-loaded by `scripts/predictclaw.py` when present.

Exported environment variables win; `.env` only fills missing values. The installed
skill directory `~/.openclaw/skills/predictclaw` is the only canonical user config
root and is represented as `{baseDir}` in install examples.

## Template selection

- `template.env` — secret-free local fixture bootstrap.
- `template.readonly.env` — live read-only market reads.
- `template.eoa.env` — platform-wallet trading.
- `template.predict-account.env` — Predict Account auth/status (paired platform seam required).
- `template.predict-account-vault.env` — Predict Account + vault funding/status.
- `template.mandated-vault.env` — internal vault bootstrap.

## Per-mode minimums

> Current availability: `eoa` is the only mode with `buy`/`wallet withdraw` execution. `predict-account` (with or without vault overlay) is auth/status only and fails closed with `unsupported-predict-account-execution` until the controlled Kernel execute path lands.

### read-only

```dotenv
PREDICT_ENV=mainnet
PREDICT_WALLET_MODE=read-only
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
```

### eoa

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

### predict-account

Predict Account signing requires the paired platform `/wallet/sign` `messageEncoding: "hex"` seam (platform PR #2030). Until the controlled Kernel execute path lands, this mode is limited to auth/status: `buy` and `wallet withdraw` fail closed with `unsupported-predict-account-execution`, and it must not fall back to a raw key.

```dotenv
PREDICT_ENV=mainnet
PREDICT_WALLET_MODE=predict-account
PREDICT_API_BASE_URL=https://api.predict.fun
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
PREDICT_ACCOUNT_ADDRESS=0xYOUR_PREDICT_ACCOUNT
WALLET_API_URL=https://YOUR_PLATFORM_WALLET_API
WALLET_API_TOKEN=YOUR_PLATFORM_WALLET_TOKEN
INSTANCE_ID=YOUR_INSTANCE_ID
WALLET_CHAIN_ID=56
```

### predict-account + vault

```dotenv
PREDICT_ENV=mainnet
PREDICT_WALLET_MODE=predict-account
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
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

If you do not have a vault yet, install the bundled helper and bootstrap it:

```bash
cd {baseDir}/node && npm install
uv run python scripts/predictclaw.py wallet bootstrap-vault --json
uv run python scripts/predictclaw.py wallet bootstrap-vault --confirm --json
```

### pure mandated-vault bootstrap

```dotenv
PREDICT_ENV=mainnet
PREDICT_WALLET_MODE=mandated-vault
PREDICT_API_KEY=YOUR_PREDICT_API_KEY
WALLET_API_URL=https://YOUR_PLATFORM_WALLET_API
WALLET_API_TOKEN=YOUR_PLATFORM_WALLET_TOKEN
INSTANCE_ID=YOUR_INSTANCE_ID
WALLET_CHAIN_ID=56
ERC_MANDATED_CHAIN_ID=56
```

When `ERC_MANDATED_VAULT_AUTHORITY` is unset, PredictClaw uses the platform
wallet signer address as the bootstrap authority. Do not provide private keys.

## Full env table

| Variable | Purpose |
| --- | --- |
| `PREDICT_STORAGE_DIR` | Local journal and position storage. |
| `PREDICT_ENV` | `mainnet`, `testnet`, or `test-fixture`. |
| `PREDICT_WALLET_MODE` | `read-only`, `eoa`, `predict-account`, or `mandated-vault`. |
| `PREDICT_API_BASE_URL` | Optional REST base override. |
| `PREDICT_API_KEY` | Mainnet-authenticated predict.fun API access. |
| `WALLET_API_URL` | Platform wallet application API base URL. |
| `WALLET_API_TOKEN` | Platform wallet bearer token (never printed or logged). |
| `INSTANCE_ID` | Platform wallet instance id. |
| `WALLET_CHAIN_ID` | Optional chain id override for platform wallet calls. |
| `PREDICT_ACCOUNT_ADDRESS` | Predict Account smart-wallet address. |
| `ERC_MANDATED_VAULT_ADDRESS` | Explicit deployed mandated vault address. |
| `ERC_MANDATED_FACTORY_ADDRESS` | Product default factory / manual derivation override. |
| `ERC_MANDATED_VAULT_ASSET_ADDRESS` | ERC-4626 asset for vault prediction/preparation. |
| `ERC_MANDATED_VAULT_NAME` | Vault name for vault prediction/preparation. |
| `ERC_MANDATED_VAULT_SYMBOL` | Vault symbol for vault prediction/preparation. |
| `ERC_MANDATED_VAULT_AUTHORITY` | Authority address; falls back to platform signer when unset. |
| `ERC_MANDATED_VAULT_SALT` | Deterministic salt for vault prediction/preparation. |
| `ERC_MANDATED_CONTRACT_VERSION` | Passed to the mandated SDK helper. |
| `ERC_MANDATED_CHAIN_ID` | Optional chain selection for the mandated SDK helper. |
| `ERC_MANDATED_ALLOWED_ADAPTERS_ROOT` | Optional 32-byte hex adapter allowlist root. |
| `ERC_MANDATED_FUNDING_MAX_AMOUNT_PER_TX` | Optional Vault→Predict per-tx cap in raw token units. |
| `ERC_MANDATED_FUNDING_MAX_AMOUNT_PER_WINDOW` | Optional Vault→Predict window cap. |
| `ERC_MANDATED_FUNDING_WINDOW_SECONDS` | Optional Vault→Predict funding window duration. |
| `OPENROUTER_API_KEY` | Optional hedge analysis model access. |
| `PREDICT_MODEL` | Optional model name for hedge analysis. |
