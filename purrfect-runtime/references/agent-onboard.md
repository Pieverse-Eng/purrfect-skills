# PurrfectClaw Onboarding

You are onboarding to PurrfectClaw, an on-chain execution platform. After completing these steps you will have:

- A TEE-secured wallet (private keys never leave the secure enclave)
- The `purr` CLI for wallet operations, on-chain execution, and DeFi commands
- Platform skills for DeFi operations (swaps, lending, token creation)

**API base URL:** `https://purr.pieverse.io` | **This doc:** `https://purr.pieverse.io/agent-onboard.md`

Follow every step in order. Do not skip or reorder.

---

## Step 1: Authenticate

Choose an authentication method based on your use case:

| | API Key | Social Login |
|---|---|---|
| **Human needed?** | No | Yes — human approves via OAuth |
| **Auth type** | Static key (`pcp_live_*`) | JWT access token + refresh token |
| **Token validity** | Permanent (until revoked) | Access: 1 hour, Refresh: 7 days |
| **Resources tied to** | Agent ID | User account |
| **Best for** | Autonomous agents | Agents with a human owner who wants identity-based access |

**If the user does not specify an authentication method, default to Option A (API Key).**

### Option A: API Key (Default — recommended for autonomous agents)

Send a POST request to register. No authentication required. Remote agents must
receive a `.pie` handle during registration, so use the helper below instead of
a one-shot `curl`: it sends both `name` and a handle candidate, retries names or
handles that are blocked by policy, and backs off if the handle proof signer is
temporarily unavailable.

```bash
AGENT_NAME="${AGENT_NAME:-YOUR_AGENT_NAME}"

normalize_handle() {
  node - "$1" <<'NODE'
const input = (process.argv[2] || 'remote-agent').trim().toLowerCase().replace(/\.pie$/u, '')
const chars = []
let previousHyphen = false
for (const char of input) {
  const code = char.charCodeAt(0)
  const out =
    (code >= 97 && code <= 122) || (code >= 48 && code <= 57) ? char : '-'
  if (out === '-') {
    if (chars.length === 0 || previousHyphen) continue
    previousHyphen = true
  } else {
    previousHyphen = false
  }
  chars.push(out)
  if (chars.length >= 30) break
}
while (chars[chars.length - 1] === '-') chars.pop()
let handle = chars.join('')
if (handle.length < 5) handle = `agent-${handle || 'remote'}`
console.log(handle.slice(0, 30).replace(/-+$/u, ''))
NODE
}

register_remote_agent() {
  for attempt in 1 2 3 4 5 6; do
    suffix=""
    if [ "$attempt" -gt 1 ]; then
      suffix="-$(openssl rand -hex 3 2>/dev/null || date +%s)"
    fi
    name="${AGENT_NAME}${suffix}"
    handle="$(normalize_handle "$name")"
    payload="$(node - "$name" "$handle" <<'NODE'
console.log(JSON.stringify({
  name: process.argv[2],
  handle: process.argv[3],
  chainType: 'ethereum'
}))
NODE
)"

    tmp="$(mktemp)"
    status="$(curl -sS -o "$tmp" -w "%{http_code}" -X POST "https://purr.pieverse.io/v1/agents/register" \
      -H "Content-Type: application/json" \
      -d "$payload")"
    body="$(cat "$tmp")"
    rm -f "$tmp"

    code="$(BODY="$body" node <<'NODE'
try {
  const body = JSON.parse(process.env.BODY || '{}')
  console.log(body.code || body.error || '')
} catch {
  console.log('')
}
NODE
)"

    if [ "$status" = "200" ]; then
      if ! BODY="$body" node <<'NODE'
const body = JSON.parse(process.env.BODY || '{}')
const d = body.data || {}
if (!d.agentId || !d.apiKey || !d.wallet || !d.handle || !d.renderedHandle) {
  console.error('registration response missing required identity fields')
  process.exit(1)
}
NODE
      then
        echo "$body" >&2
        return 1
      fi
      echo "$body"
      return 0
    fi

    case "$code" in
      AGENT_NAME_TAKEN|HANDLE_TAKEN|handle_already_taken|handle_reserved|invalid_handle)
        continue
        ;;
      HANDLE_CLAIM_RETRYABLE)
        sleep "$attempt"
        continue
        ;;
      *)
        echo "$body" >&2
        return 1
        ;;
    esac
  done

  echo "registration failed after retries" >&2
  return 1
}

REGISTER_RESPONSE="$(register_remote_agent)"
printf '%s\n' "$REGISTER_RESPONSE"
```

Replace `YOUR_AGENT_NAME` with a unique name (e.g. your hostname or agent identifier).
If the name is already taken, the API returns `409` with:

```json
{ "ok": false, "error": "Agent name already exists", "code": "AGENT_NAME_TAKEN" }
```

The helper retries with a random suffix for name/handle conflicts or policy
blocks. If you are calling the API manually, retry with a different `name` and
`handle`, for example by appending a hostname, environment, or random suffix.

The response contains the values you need. **Save the `apiKey` immediately — it is shown only once.**
Only continue if the response includes `apiKey`, `wallet`, `handle`, and
`renderedHandle`.

```json
{
  "ok": true,
  "data": {
    "agentId": "...",
    "apiKey": "pcp_live_...",
    "handle": "your-agent",
    "renderedHandle": "your-agent.pie",
    "walletProvisioned": true,
    "wallet": { "address": "0x...", "chainId": 56, "chainType": "ethereum" }
  }
}
```

If handle proof signing is temporarily unavailable, registration fails without
returning an API key:

```json
{
  "ok": false,
  "error": "handle_claim_retryable",
  "code": "HANDLE_CLAIM_RETRYABLE"
}
```

In that case, wait briefly and run the registration helper again. Do not write
credentials to disk from a failed registration response.

Write the credentials to `~/.purrfectclaw/.env`:

```bash
if ! ENV_EXPORTS="$(REGISTER_RESPONSE="$REGISTER_RESPONSE" node <<'NODE'
const body = JSON.parse(process.env.REGISTER_RESPONSE || '{}')
const d = body.data || {}
if (!d.agentId || !d.apiKey || !d.wallet?.address || !d.handle || !d.renderedHandle) {
  console.error('Refusing to write env: registration response is missing required identity fields')
  process.exit(1)
}
function out(name, value) {
  console.log(`${name}=${JSON.stringify(String(value))}`)
}
out('AGENT_ID', d.agentId)
out('API_KEY', d.apiKey)
out('INSTANCE_ID', d.agentId)
out('WALLET_ADDRESS', d.wallet.address)
out('PIE_HANDLE', d.handle)
out('PIE_NAME', d.renderedHandle)
NODE
)"; then
  return 1 2>/dev/null || exit 1
fi
eval "$ENV_EXPORTS"

mkdir -p ~/.purrfectclaw
cat > ~/.purrfectclaw/.env << ENVEOF
AGENT_ID=$AGENT_ID
API_KEY=$API_KEY                            # Your static API key (pcp_live_*)
AUTH_TOKEN=$API_KEY                         # Used by Steps 2-4
WALLET_API_URL=https://purr.pieverse.io
WALLET_API_TOKEN=$API_KEY
INSTANCE_ID=$INSTANCE_ID
WALLET_ADDRESS=$WALLET_ADDRESS
PIE_HANDLE=$PIE_HANDLE
PIE_NAME=$PIE_NAME
ENVEOF
```

Source it for subsequent steps:

```bash
source ~/.purrfectclaw/.env
```

### Option B: Social Login (For agents with a human owner who wants identity-based access)

Instead of an API Key, you can authenticate via Google using the device flow. This gives you a JWT access token bound to a user identity rather than a static API key. Resources (instances, wallets) are tied to the user, not the API key.

**Step B1: Initiate the device flow**

```bash
curl -sf -X POST "https://purr.pieverse.io/v1/auth/device" \
  -H "Content-Type: application/json"
```

Response:

```json
{
  "ok": true,
  "data": {
    "deviceCode": "...",
    "loginUrl": "https://purr.pieverse.io/v1/auth/sso?device_code=...",
    "expiresIn": 600,
    "interval": 5
  }
}
```

**Step B2: Show the login URL to your owner**

Display the `loginUrl` to the owner (e.g., print it, open a browser, or send it via chat). The owner clicks the link, signs in with Google, and sees a success page.

**Step B3: Poll for the result**

Poll every 5 seconds until the owner completes login:

```bash
curl -sf -X POST "https://purr.pieverse.io/v1/auth/device/token" \
  -H "Content-Type: application/json" \
  -d '{"deviceCode": "<deviceCode from step B1>", "chainType": "ethereum"}'
```

While the owner hasn't logged in yet, you'll get HTTP 428:

```json
{ "ok": false, "error": "authorization_pending" }
```

Once the owner completes login, you'll receive everything in one response:

```json
{
  "ok": true,
  "data": {
    "accessToken": "eyJ...",
    "instanceId": "...",
    "user": { "id": "...", "email": "...", "name": "..." },
    "wallet": { "address": "0x...", "chainId": 56, "chainType": "ethereum" }
  }
}
```

**Write the credentials to `~/.purrfectclaw/.env`:**

```bash
mkdir -p ~/.purrfectclaw
cat > ~/.purrfectclaw/.env << 'ENVEOF'
ACCESS_TOKEN=<accessToken from response>    # Your JWT access token (expires in 1h)
REFRESH_TOKEN=<refreshToken from response>  # Use POST /v1/auth/refresh to renew
AUTH_TOKEN=$ACCESS_TOKEN                    # Used by Steps 2-4
INSTANCE_ID=<instanceId from response>
WALLET_ADDRESS=<wallet.address from response>
WALLET_API_URL=https://purr.pieverse.io
WALLET_API_TOKEN=<accessToken from response>
INSTANCE_ID=<instanceId from response>
ENVEOF
```

> **Note:** Access tokens expire after 1 hour. Use `POST /v1/auth/refresh` with your refresh token to get a new access token without re-authenticating.

### Source credentials

Whichever option you chose, source the credentials for subsequent steps:

```bash
source ~/.purrfectclaw/.env
```

> **In the following steps, `$AUTH_TOKEN` refers to whichever token you received — your API Key (`pcp_live_*`) or JWT access token.** If you used Option A, `$AUTH_TOKEN` is your `API_KEY`. If you used Option B, it is your `ACCESS_TOKEN`.

---

## Step 2: Download skills

Download all platform skills as a single bundle:

```bash
mkdir -p ~/.purrfectclaw/skills
curl -sf "https://purr.pieverse.io/v1/skills/bundle" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -o /tmp/skills-bundle.tar.gz
tar xzf /tmp/skills-bundle.tar.gz -C ~/.purrfectclaw/skills
```

---

## Step 3: Install purr CLI and configure

### 3a. Install purr

Install the purr CLI from GitHub Releases:

```bash
curl -fsSL https://raw.githubusercontent.com/Pieverse-Eng/purr-cli/main/install.sh | bash
```

This installs the `purr` binary to `~/.purrfectclaw/bin/purr` and prints PATH instructions if needed.

To pin a specific version:

```bash
curl -fsSL https://raw.githubusercontent.com/Pieverse-Eng/purr-cli/main/install.sh | PURR_VERSION=v0.2.2 bash
```

Verify:

```bash
purr version
```

### 3b. Configure purr credentials

The purr CLI needs three values to connect to the platform. You can set them via environment variables (already in `~/.purrfectclaw/.env` from Step 1) or via the config command:

```bash
purr config set api-url "https://purr.pieverse.io"
purr config set api-token "$AUTH_TOKEN"
purr config set instance-id "$INSTANCE_ID"
```

> **Note:** Environment variables (`WALLET_API_URL`, `WALLET_API_TOKEN`, `INSTANCE_ID`) take precedence over the config file. If you sourced `~/.purrfectclaw/.env` in Step 1, purr is already configured.

Verify credentials:

```bash
purr config list
```

### 3c. Add purr to PATH

```bash
# Append to shell profile (skip if already present)
grep -q '.purrfectclaw/bin' ~/.zshrc 2>/dev/null || \
  echo 'export PATH="$HOME/.purrfectclaw/bin:$PATH"' >> ~/.zshrc
```

### 3d. Register skills with OpenClaw (OpenClaw-hosted agents only)

> **Skip this step if you are running a standalone agent without an OpenClaw gateway.**

If your agent runs inside an OpenClaw-hosted pod, register the skills directory so the gateway can discover them:

```bash
# Read current value (may be empty or already have entries)
CURRENT=$(openclaw config get skills.load.extraDirs 2>/dev/null)

# Merge: append our path if not already present
MERGED=$(node -e "
const cur = (() => { try { return JSON.parse('${CURRENT:-[]}'); } catch { return []; } })();
const p = '~/.purrfectclaw/skills';
if (cur.indexOf(p) === -1) cur.push(p);
console.log(JSON.stringify(cur));
")

openclaw config set skills.load.extraDirs "$MERGED"
```

---

## Step 4: Verify

Test that purr CLI is working:

```bash
purr wallet address --chain-type ethereum
# Expected: returns JSON with your 0x wallet address
```

If registration returned `walletProvisioned=false`, this verification step is
also the recovery step: it will create the wallet on demand through the API.

### OpenClaw-hosted agents only

> **Skip this section if you are running a standalone agent.**

Restart the gateway to load the new skills, then verify:

```bash
openclaw gateway restart

# Skills should include PurrfectClaw skills (onchain, pancake, etc.)
openclaw skills list
```

---

## What you now have

### purr CLI commands

| Command | What it does |
|---------|-------------|
| `purr wallet address` | Get your wallet address |
| `purr wallet balance` | Check native or token balance |
| `purr wallet transfer` | Transfer tokens (native or ERC-20) |
| `purr wallet sign` | Sign a message |
| `purr wallet sign-typed-data` | Sign EIP-712 typed data |
| `purr execute` | Execute transaction steps from a file |
| `purr pancake swap --execute` | Swap tokens via PancakeSwap |
| `purr bitget swap --execute` | Multi-chain EVM swaps via Bitget |
| `purr lista deposit --execute` | Deposit into Lista DAO vaults |
| `purr lista list-vaults` | List available Lista vaults |
| `purr fourmeme buy --execute` | Buy tokens on Four.meme |

### Skills (from platform)

Skills are operational instructions loaded into your agent's context. They tell the agent how to route and execute on-chain operations. The `onchain` skill is the orchestrator — it dispatches to the correct skill for each intent (swap, lend, bridge, etc.).

### Credentials (in `~/.purrfectclaw/.env`)

| Variable | Purpose |
|----------|---------|
| `AGENT_ID` | Your agent's unique ID |
| `API_KEY` | Platform auth key — Option A (`pcp_live_*`) |
| `ACCESS_TOKEN` | JWT access token — Option B (expires in 1h) |
| `AUTH_TOKEN` | Unified token alias used by Steps 2-4 (set to `$API_KEY` or `$ACCESS_TOKEN`) |
| `WALLET_ADDRESS` | Your provisioned wallet address |
| `WALLET_API_URL` | API base URL for purr CLI |
| `WALLET_API_TOKEN` | Auth token for purr CLI |
| `INSTANCE_ID` | Instance ID for purr CLI |

---

## Troubleshooting

- **Skills not showing (OpenClaw-hosted only)**: Run `openclaw skills list` and check for PurrfectClaw skills. If missing, verify `~/.purrfectclaw/skills/` has subdirectories with `SKILL.md` files and that you ran Step 3d.
- **Skills not found (standalone agents)**: Verify `~/.purrfectclaw/skills/` has subdirectories with `SKILL.md` files. Re-run the skill bundle download from Step 2 if empty.
- **purr not found**: Ensure `~/.purrfectclaw/bin` is in PATH. Run `source ~/.zshrc` or start a new shell. Re-run the install script if the binary is missing.
- **purr auth errors**: Run `purr config list` to verify credentials are set. Check that `WALLET_API_URL`, `WALLET_API_TOKEN`, and `INSTANCE_ID` are configured via env vars or `purr config set`.
- **"wallet not found" errors**: Run `purr wallet address --chain-type ethereum` or call `POST /v1/instances/$AGENT_ID/wallet/ensure` to create the wallet. If it fails, verify your auth token is valid and the wallet backend is reachable.
- **Agent registration returns `409 Agent name already exists`**: Retry with a different `name`. Names must be globally unique when provided.
