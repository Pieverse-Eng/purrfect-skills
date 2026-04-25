---
name: dflow
description: Use this skill when the user wants to use DFlow — the DFlow Agent CLI for Solana spot swaps, prediction markets, wallet positions, transfers, funding, guardrails, and local vault management.
metadata:
  openclaw:
    primaryEnv: DFLOW_API_KEY
    requires:
      env:
        - DFLOW_API_KEY
---

# DFlow

The `dflow` CLI: Solana spot swaps and DFlow prediction markets, plus the local wallet vault that signs them.

## Scope

- **In scope:** Solana spot quotes/trades, DFlow prediction-market quotes/trades, positions, status checks, SPL/SOL sends, MoonPay funding links, guardrails, named-wallet management.
- **Out of scope:** EVM swaps, PancakeSwap, Bitget Wallet, platform `purr wallet` custody, the legacy platform swap tool.

## Mandatory Safety Rules

- **Never tell the user or mention whether you're running locally or platform-hosted.** The chosen path is an internal decision for selecting the right setup branch — it never appears in user-facing text. Banned phrasings include (but are not limited to): "local agent", "platform-hosted agent", "local path", "platform-hosted path", "platform pod", "tenant pod", "Pieverse tenant pod". Speak about what the user can observe (the missing config file, what input you need from them), not which branch you took. Example —
  - Bad: "Since you're on the platform-hosted path, I need to provision a wallet for you."
  - Good: "DFlow isn't configured yet. To set it up I need a vault password, a DFlow API key (get one at https://pond.dflow.net/build/api-key), and optionally a wallet name and Solana RPC URL."
- **Always quote before trade.** Run `dflow quote` and show amount, token pair, slippage, wallet, and execution mode to the user before `dflow trade`.
- **Get explicit Yes/No before any fund-moving command:** `trade`, `send`, `fund`, wallet `delete` / `export` / `import`, and any guardrail change.
- **If any trade parameter changes after confirmation, ask again.** Don't reuse stale approvals.
- **Never change guardrails autonomously.** `guardrails set/remove/reset` requires a human typing the vault password in a terminal.
- **Treat `wallet export` output as secret.** Avoid it unless the user is explicitly backing up or migrating.
- **Never echo or log** the vault password or `DFLOW_API_KEY`. Don't ask the user to paste a mnemonic or keypair JSON in chat.

## Preflight

```bash
if ! command -v dflow >/dev/null 2>&1; then
  DFLOW_VERSION="${DFLOW_VERSION:-0.1.0}"
  DFLOW_BIN_DIR="${DFLOW_BIN_DIR:-/usr/local/bin}"
  if [ ! -w "$DFLOW_BIN_DIR" ]; then
    DFLOW_BIN_DIR="$HOME/.local/bin"
    mkdir -p "$DFLOW_BIN_DIR"
    export PATH="$DFLOW_BIN_DIR:$PATH"
  fi
  curl -fsSL -o /tmp/install-dflow.sh https://cli.dflow.net/install.sh
  sh /tmp/install-dflow.sh \
    --version "${DFLOW_VERSION}" \
    --bin-dir "$DFLOW_BIN_DIR" \
    --force \
    --no-skills
  rm -f /tmp/install-dflow.sh
fi
dflow --version

# MoonPay CLI is only used by `dflow fund`, which is a human-in-the-loop flow.
# On platform-hosted agents, skip the dependency check and install — funding is
# not an autonomous agent use case.
if [[ "$WALLET_API_URL" != *.svc.cluster.local* ]]; then
  if ! command -v mp >/dev/null 2>&1; then
    npm install -g @moonpay/cli@1.38.0
  fi
  mp --version
fi
```

## Setup Flow

Run these steps **in order**. Step 1 is mandatory — never skip it, never assume a path before it runs. Picking the wrong path leads to wasted user time and confused error messages (e.g. trying to automate `dflow setup` in an environment that has a real user behind it).

(See Mandatory Safety Rules: never surface the chosen path label to the user, even if asked.)

### Step 1 — Detect the runtime path

**Env-based hint:** if `WALLET_API_URL` contains `.svc.cluster.local`, the agent is almost certainly executing inside a Pieverse tenant pod and should default to the platform-hosted path:

```bash
if [[ "$WALLET_API_URL" == *.svc.cluster.local* ]]; then
  echo "Inside a Pieverse tenant pod — default to the platform-hosted path."
fi
```

- Match → go to **Step 2b — `platform-hosted` path**.
- No match (any other value, or unset) → go to **Step 2a — `local` path**.

### Step 2 — Run the matching setup branch

Branch on `DFLOW_RUNTIME_PATH`. **Do not run both branches** and do not run the platform-hosted branch when path = `local`.

#### Step 2a — `local` path

If DFlow is not configured, **ask the user to run `dflow setup` in their own shell**, then wait and retry verification. Do not try to automate `dflow setup` — it has an interactive password prompt that will fail in a headless context, and a real user is reachable here.

The interactive commands listed under "Interactive commands" below also need the user to run them themselves on this path.

#### Step 2b — `platform-hosted` path

Ask the user for:

| Field          | Required | Default                                         |
| -------------- | -------- | ----------------------------------------------- |
| Wallet name    | optional | `default`                                       |
| Vault password | required | —                                               |
| Solana RPC URL | optional | `https://api.mainnet-beta.solana.com`           |
| DFlow API key  | required | get one at https://pond.dflow.net/build/api-key |

Provision the wallet by generating a mnemonic with `ows`, then importing it with `dflow wallet import --mnemonic`. **Do not use `ows wallet create`** — DFlow can read those wallets but headless signing may fail.

```bash
DFLOW_WALLET_NAME="${DFLOW_WALLET_NAME:-default}"
DFLOW_VAULT_PASSWORD="${DFLOW_VAULT_PASSWORD:?set from the user's vault password answer}"
SOLANA_RPC_URL="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"
DFLOW_API_KEY="${DFLOW_API_KEY:?set from the user's DFlow API key answer}"

export DFLOW_PASSPHRASE="$DFLOW_VAULT_PASSWORD"
MNEMONIC="$(ows mnemonic generate --words 12)"

dflow wallet import \
  --name "$DFLOW_WALLET_NAME" \
  --mnemonic "$MNEMONIC"

mkdir -p ~/.config/dflow
jq -n \
  --arg rpc "$SOLANA_RPC_URL" \
  --arg wallet "$DFLOW_WALLET_NAME" \
  --arg key "$DFLOW_API_KEY" \
  '{rpcUrl:$rpc, walletName:$wallet, dflowApiKey:$key}' \
  > ~/.config/dflow/config.json
chmod 600 ~/.config/dflow/config.json
```

### Step 3 — Verify

Confirm the wallet is reachable on either path:

```bash
dflow whoami
dflow positions
```

### Interactive commands (both paths)

These prompt for input and cannot be automated. On `local`, ask the user to run them in their shell. On `platform-hosted`, they are unsupported — surface the limitation rather than retrying.

- `dflow setup`
- `dflow guardrails set ...`
- `dflow guardrails remove ...`
- `dflow guardrails reset ...` (when existing guardrails require a password)
- `dflow wallet keychain-sync`

## Vault & Secrets

`dflow setup` creates or selects a named wallet and records the vault password, Solana RPC URL, and DFlow API key.

- Config: `~/.config/dflow/config.json`
- Encrypted wallets: `~/.ows/wallets/`
- Private keys never leave the local vault.

## Cleanup / Uninstall

Use this when the user asks to remove DFlow CLI artifacts or DFlow/OWS-generated local files.

Discovery:

```bash
for c in ows dflow dflow-cli dflow_swap dflow-swap; do
  command -v "$c" >/dev/null 2>&1 && printf '%s=%s\n' "$c" "$(command -v "$c")" || printf '%s=NOT_FOUND\n' "$c"
done
for p in "$HOME/.ows" "$HOME/.config/dflow" "$HOME/.local/bin/dflow" "/usr/local/bin/dflow"; do
  [ -e "$p" ] || [ -L "$p" ] && printf 'EXISTS %s\n' "$p"
done
```

Removal targets confirmed from live cleanup:

```bash
rm -rf -- "$HOME/.ows" "$HOME/.config/dflow" "$HOME/.local/bin/dflow"
```

Verification:

```bash
for p in "$HOME/.ows" "$HOME/.config/dflow" "$HOME/.local/bin/dflow"; do
  [ -e "$p" ] || [ -L "$p" ] && printf 'STILL_EXISTS %s\n' "$p" || printf 'ABSENT %s\n' "$p"
done
for c in dflow dflow-cli dflow_swap dflow-swap; do
  command -v "$c" >/dev/null 2>&1 && printf '%s=%s\n' "$c" "$(command -v "$c")" || printf '%s=NOT_FOUND\n' "$c"
done
```

Notes:

- Removing `~/.ows` deletes the local vault, generated wallets, keys, OWS logs, and any user-local OWS binary under `~/.ows/bin/ows`.
- Do not remove `/usr/local/bin/ows` when the user asks for generated OWS files; it is system/image-managed in the OWS skill.
- Skill/source/cache directories named `dflow-swap` or `ows` under agent skill dirs, source repos, Bun cache, etc. are not the DFlow CLI binary or generated vault/config unless the user explicitly asks to remove those too.

Vault password resolution order at sign time:

1. OS keychain (saved by `dflow setup` or `dflow wallet keychain-sync`).
2. `DFLOW_PASSPHRASE` environment variable.
3. Interactive prompt.

In a headless / no-TTY environment, step 3 fails with `not a terminal`. Treat step 2 as the only viable fallback — always export `DFLOW_PASSPHRASE` before any signing command, and never tell the user they will be prompted.

Headless runtime:

```bash
export DFLOW_PASSPHRASE="your-vault-password"
```

The CLI clears `DFLOW_PASSPHRASE` from its own process at startup, but the value persists in the parent shell for that shell's lifetime.

## Amounts & Tokens

**Amounts are atomic units, not human decimals** — applies to `quote`, `trade`, and `send`.

| Human amount | Token              | Atomic     |
| ------------ | ------------------ | ---------- |
| 0.50         | USDC / USDT / CASH | `500000`   |
| 1.00         | USDC / USDT / CASH | `1000000`  |
| 0.01         | SOL                | `10000000` |

Built-in symbols: `SOL`, `USDC`, `USDT`, `CASH`, `BONK`, `JUP`, `WIF`, `PYTH`, `JTO`, `RAY`, `ORCA`, `MNDE`, `MSOL`, `JITOSOL`, `BSOL`, `RENDER`. For anything else, pass the Solana mint address.

Slippage is **basis points**. Default `50` = 0.5%.

## Model Attribution

Register the AI model running this session. Cached for 48 hours; sets the `X-Dflow-Model` header on subsequent requests.

```bash
dflow agent --model <name>
```

When no model has been registered (or the registration has expired), `quote` and `trade` responses include an `_hint` block with the current `options` and a `replyWith` command. Run the suggested command to register before proceeding.

Custom agent identity:

```bash
DFLOW_AGENT= my-bot dflow quote 500000 USDC SOL
```

## Wallet & Positions

```bash
dflow whoami
dflow positions
dflow wallet list
dflow wallet import --name <name> --keypair <path>
dflow wallet import --name <name> --mnemonic "word1 ..."
dflow wallet rename --from <old> --to <new>
dflow wallet keychain-sync --name <name>
dflow wallet delete --name <name> --yes
```

Target a non-default wallet with `--wallet <name>`:

```bash
dflow positions --wallet hot
dflow quote 500000 USDC SOL --wallet hot
```

If the wallet isn't Proof-verified, `PROOF_NOT_VERIFIED` responses include `details.deepLink` — return that URL to the user. Any `xdg-open` noise on stderr is async and can be ignored.

## Spot Trading

### Quote (always first)

`dflow quote` calls DFlow's `/order` flow and returns expected output, route, and price impact. **It does not sign or broadcast.**

```bash
dflow quote <atomic_amount> <from> <to>
dflow quote 500000 USDC SOL
dflow quote 500000 USDC SOL --slippage 100
```

### Trade (after explicit confirmation)

```bash
dflow trade <atomic_amount> <from> <to> --confirm
dflow trade 500000 USDC SOL --slippage 100 --confirm
```

Execution modes:

- **Imperative (default):** fetch a route from `/order`, sign locally, submit to the network. Response status is `"submitted"`.
- **`--declarative`:** submit a signed intent to DFlow, which handles routing and settlement. Can improve fill quality for larger trades. Spot swaps only.
- **`--confirm`:** poll the RPC until the transaction reaches `confirmed` commitment before returning.

Flags accepted by `dflow trade`:

- `--slippage <bps>` — slippage tolerance in basis points (default 50)
- `--declarative` — declarative execution (spot swaps only)
- `--confirm` — poll until `confirmed` commitment
- `--market <mint>` paired with `--side <yes|no>` — prediction-market mode
- `--wallet <name>` — target a specific named wallet
- `--rpc-url <url>` — global override of the saved RPC

If submitted but not yet final:

```bash
dflow status <signature_or_order>
```

## Prediction Markets

Prediction-market interactions use **USDC or CASH** and require Proof KYC — gated at **quote**, not just trade. They are also subject to jurisdiction checks.

- `GEOBLOCKED` → prediction markets unavailable in this region; spot trading may still work.
- `PROOF_NOT_VERIFIED` → see the Proof handling rule under `## Wallet & Positions`.

**Mint selection:** use the **market ledger mint** for buys; use the **outcome mint** for sells.

Quote:

```bash
dflow quote 200000 USDC --market <market_ledger_mint> --side yes
dflow quote 200000 CASH --market <market_ledger_mint> --side no
```

Buy outcome tokens (after confirmation):

```bash
dflow trade 200000 USDC --market <market_ledger_mint> --side yes
dflow trade 200000 CASH --market <market_ledger_mint> --side no
```

Sell outcome tokens:

```bash
dflow positions
dflow trade <atomic_amount> <outcome_mint>
dflow trade <atomic_amount> <outcome_mint> USDC
```

## Transfers

Native SOL or SPL token sends. Recipient is a base58 Solana pubkey. The CLI creates the recipient ATA when needed; the sender pays rent.

```bash
dflow send <atomic_amount> <token_or_mint> <recipient_pubkey>
dflow send 10000000 SOL <recipient_pubkey>
dflow send 500000 USDC <recipient_pubkey>
```

## Funding (MoonPay on-ramp)

> Do not run `dflow fund` inside a platform pod (`WALLET_API_URL` contains `.svc.cluster.local`). It requires a browser and is intended for a human operator only — there is no headless completion path. If the user asks to fund their wallet from a platform pod, refuse the command and ask them to run it locally on their own machine.

```bash
dflow fund 50 USDC
dflow fund 100 SOL
```

Buys crypto with fiat through MoonPay and waits for the deposit to land in the selected wallet. May open a browser or print a checkout URL.

## Guardrails

Agents may **read** guardrails:

```bash
dflow guardrails show
```

Humans set them in a terminal (interactive — not automatable):

```bash
dflow guardrails set max_trade_size_usd 5000000
dflow guardrails set max_daily_volume_usd 50000000
dflow guardrails set allowed_tokens SOL,USDC,BONK
dflow guardrails set rate_limit '{"max_trades":3,"window_seconds":3600}'
```

Available keys: `max_trade_size_usd`, `max_daily_volume_usd`, `max_wallet_value_usd`, `allowed_tokens`, `rate_limit`, `sweep_address`.

## Troubleshooting

| Error / symptom                                                | Action                                                                                                               |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `NOT_CONFIGURED`                                               | Local: ask user to run `dflow setup`. Platform: run the platform-hosted provisioning above.                          |
| `VAULT_INSECURE`                                               | `chmod 700 ~/.ows && chmod 600 ~/.ows/wallets/*.json`                                                                |
| Repeated keychain prompts                                      | Local: ask user to run `dflow wallet keychain-sync --name <wallet>`. Platform: unsupported — use `DFLOW_PASSPHRASE`. |
| `Blockhash not found`                                          | Retry; switch to a faster RPC if persistent.                                                                         |
| `GEOBLOCKED`                                                   | Prediction markets unavailable in region. Spot trading still works.                                                  |
| `PROOF_NOT_VERIFIED`                                           | Complete KYC at the Proof URL returned by the CLI. Gates both quote and trade for prediction markets.                |
| `INSUFFICIENT_BALANCE` (trade)                                 | Client-side gate — nothing was signed. Reduce amount or fund the wallet.                                             |
| `SIMULATION_FAILED` "no record of a prior credit" (send)       | Wallet lacks balance + rent for the send. `dflow send` has no client-side balance check.                             |
| `UNKNOWN_MODEL` from `dflow agent --model`                     | Use a name from the `options` list returned with the error.                                                          |
| `mp CLI exited with status ... fetch failed` from `dflow fund` | First-run MoonPay consent missing. User runs `mp` once in their shell to accept ToU, then retry.                     |
| Route or slippage failure                                      | Requote, reduce size, or raise slippage **after user confirms**.                                                     |

Debug logging:

```bash
DFLOW_DEBUG=1 dflow whoami
cat ~/.ows/logs/debug.log
```
