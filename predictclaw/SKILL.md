---
name: predictclaw
description: Predict.fun skill with a PolyClaw-style CLI for markets, wallet funding, trading, positions, and hedging.
metadata: {"openclaw":{"emoji":"🔮","homepage":"https://predict.fun","requires":{"bins":["uv","node"]},"install":[{"id":"uv-brew","kind":"brew","formula":"uv","bins":["uv"],"label":"Install uv (brew)"},{"id":"node-runtime","kind":"brew","formula":"node","bins":["node"],"label":"Install Node.js (brew)"}]}}
---

# PredictClaw

PredictClaw is the predict.fun-native skill for browsing markets, checking wallet readiness, viewing funding guidance, withdrawing funds, placing buys, inspecting positions, and scanning hedge opportunities.

## When to use

- `markets trending` — discover trending predict.fun markets.
- `markets search <query>` — search markets.
- `market <id>` — show a single market.
- `wallet status` — wallet mode, balances, and readiness.
- `wallet deposit` — manual top-up guidance and asset roles.
- `wallet withdraw usdt|bnb <amount> <to>` — withdraw USDT or BNB to an external address (`eoa` only for now).
- `buy <market_id> YES|NO <amount>` — place a predict.fun order (`eoa` only for now).
- `positions` / `position <id>` — inspect tracked and remote positions.
- `hedge scan` / `hedge analyze <id1> <id2>` — find and analyze hedge relationships.

## Install

### ClawHub / packaged install

```bash
clawhub install predictclaw
cd ~/.openclaw/skills/predictclaw
uv sync
cd {baseDir}/node && npm install
cp template.env .env
```

The installed skill directory `~/.openclaw/skills/predictclaw` is the only canonical user config root. In OpenClaw manifests and examples, this same installed path may appear as `{baseDir}`. Any repository checkout or workspace copy is a development-only artifact, not a user config root.

### Manual install

1. Copy or symlink this repository into `~/.openclaw/skills/predictclaw/`
2. From the installed skill directory, run:

```bash
cd {baseDir} && uv sync
cd {baseDir}/node && npm install
cd {baseDir} && cp template.env .env
```

## Main flow

1. Choose a mode first (`read-only`, `eoa`, `predict-account`, or internal `mandated-vault`).
2. Copy the matching template to `.env` and fill only that mode's required fields.
3. Verify with `cd {baseDir} && uv run python scripts/predictclaw.py --help` and `cd {baseDir} && uv run python scripts/predictclaw.py markets trending`.
4. For signer-backed flows, use `wallet status --json` before `buy`, `wallet withdraw`, or vault operations. `buy` and `wallet withdraw` are currently available for `eoa`; `predict-account` fails closed until controlled Kernel execute lands.

`wallet status` requires signer configuration. For `read-only`, start with `markets trending` or `market <id> --json`.

## Modes and configuration keys

PredictClaw's runtime validator enforces per-mode requirements. The frontmatter intentionally does not gate prompt inclusion on an env allowlist: `PREDICT_WALLET_MODE` selects the contract, and the validator rejects missing mode-specific fields at execution time.

- `read-only` — browsing only. Uses `PREDICT_ENV`, `PREDICT_WALLET_MODE`, and `PREDICT_API_KEY` for mainnet reads.
- `eoa` — platform-wallet signer trading. Uses `PREDICT_WALLET_MODE=eoa`, `WALLET_API_URL`, `WALLET_API_TOKEN`, `INSTANCE_ID`, optional `WALLET_CHAIN_ID`.
- `predict-account` — Predict Account auth and read-only status are available now; `buy` and `wallet withdraw` fail closed with `unsupported-predict-account-execution` until the platform `/wallet/execute` controlled Kernel path lands. Uses `PREDICT_ACCOUNT_ADDRESS`, `WALLET_API_URL`, `WALLET_API_TOKEN`, `INSTANCE_ID`. This path is an explicit paired dependency on platform PR #2030 (`messageEncoding: "hex"`) and must not fall back to raw keys or MCP.
- `predict-account + vault` — overlay funding route `vault-to-predict-account`. Funding/status are available; Predict Account `buy`/`wallet withdraw` remain fail closed until controlled Kernel execute lands. Also uses `ERC_MANDATED_VAULT_ADDRESS`, `ERC_MANDATED_FACTORY_ADDRESS`, `ERC_MANDATED_VAULT_ASSET_ADDRESS`, `ERC_MANDATED_VAULT_NAME`, `ERC_MANDATED_VAULT_SYMBOL`, `ERC_MANDATED_VAULT_AUTHORITY`, `ERC_MANDATED_VAULT_SALT`, `ERC_MANDATED_CONTRACT_VERSION`, and `ERC_MANDATED_CHAIN_ID`.
- pure `mandated-vault` — internal bootstrap/control-plane path. It is not a standalone trading mode and still returns `unsupported-in-mandated-vault-v1` for `buy`, `positions`, and `hedge` flows.

The full env matrix and copy-paste examples live in `references/configuration.md`.

Older docs used `skills.entries.predictclaw.env`; treat that as a host-specific config surface, not the canonical PredictClaw config.

## Vault bootstrap

`wallet bootstrap-vault --json` is preview-only. `--confirm` plans with the bundled `@erc-mandated/sdk` helper, then broadcasts the returned transaction request through the platform wallet API. The command currently returns a `submitted` status plus a manual env block; it does not wait for a receipt and does not auto-edit `.env`.

The bundled SDK helper only prepares plans and encodes data. The platform wallet API holds signing/approval/broadcast authority, and the vault contract policy authorizes what the vault can actually execute. If the predicted vault is still undeployed, PredictClaw surfaces preparation details and `manual-only` guidance without broadcasting.

## Safety boundaries

- Platform wallet boundary: the default Purrfect path never reads or exports raw private keys. All signatures, approvals, and broadcasts go through the instance-scoped platform wallet API.
- ERC-20 approval is bounded: `buy` checks the current USDT allowance and issues a bounded approval for the requested order amount only when needed; an existing sufficient allowance is left untouched.
- Predict Account signing is an explicit paired dependency on platform PR #2030 and must not fall back to raw keys or MCP.
- Vault bootstrap does not claim deployment before a receipt or code gate. Present `submitted + manual env block`, not "deployed/backfilled".
- Predict Account `buy` and `wallet withdraw` fail closed with `unsupported-predict-account-execution` until the platform `/wallet/execute` controlled Kernel path lands; overlay funding/status guidance remains available.
