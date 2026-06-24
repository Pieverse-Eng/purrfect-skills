# Setup And Policy

## First-Time API Key Access Setup

1. If no API key is available, generate a strong owner passphrase with a
   CSPRNG, show it to the user exactly once, and stop until the user confirms it
   has been saved.
2. Use the owner passphrase only for provisioning policy-constrained API-key
   access. Pass it through stdin for owner commands; do not put it in command
   arguments or write it to disk.
3. Create or select a wallet with owner passphrase stdin:
   ```bash
   printf '%s\n%s\n' "$OWNER_PASSPHRASE" "$OWNER_PASSPHRASE" |
     ows wallet create --name "ows-treasury"
   ```
4. Inspect addresses and supported chains:
   `ows wallet list` and `ows wallet info`.
5. Write a policy JSON using CAIP-2 chain IDs, such as `eip155:8453` for Base
   or `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` for Solana mainnet.
6. Register the policy:
   `ows policy create --file <policy.json>`.
7. Create an API key scoped to the wallet and policy with owner passphrase
   stdin:
   ```bash
   printf '%s\n' "$OWNER_PASSPHRASE" |
     ows key create --name "api-access" --wallet ows-treasury --policy <policy-id>
   ```
8. Save the raw `ows_key_...` token shown once, then clear the owner passphrase
   from shell variables.
9. Use the API token through `OWS_PASSPHRASE="ows_key_..."` for signing,
   payment, and other wallet-scoped operations.

## Owner Wallet Setup

Use this section for provisioning API-key access or when asked to create or
manage the underlying wallet. Wallet setup precedes policy and API key
creation.

Generate the owner passphrase before wallet creation:

```bash
OWNER_PASSPHRASE="$(openssl rand -base64 48)"
```

Show the generated owner passphrase to the user exactly once and ask them to
confirm it has been saved before continuing. Keep it only in session memory.

Create a wallet by piping the generated passphrase twice for the create and
confirm prompts:

```bash
printf '%s\n%s\n' "$OWNER_PASSPHRASE" "$OWNER_PASSPHRASE" |
  ows wallet create --name "ows-treasury"
```

Use 24 words when the user asks for a stronger mnemonic:

```bash
printf '%s\n%s\n' "$OWNER_PASSPHRASE" "$OWNER_PASSPHRASE" |
  ows wallet create --name "ows-treasury" --words 24
```

Only add `--show-mnemonic` when the user explicitly asks to display the backup
phrase and confirms the secret exposure.

Inspect wallets and chain support:

```bash
ows wallet list
ows wallet info
```

Import and export are sensitive. Confirm first, then prefer stdin or environment
variables for imported secrets:

```bash
echo "<mnemonic words>" | ows wallet import --name "imported" --mnemonic
echo "<private-key-hex>" | ows wallet import --name "from-evm" --private-key
echo "<private-key-hex>" | ows wallet import --name "from-sol" --private-key --chain solana
ows wallet export --wallet "ows-treasury"
```

Rename or delete wallets only after confirmation:

```bash
ows wallet rename --wallet "ows-treasury" --new-name "ops-treasury"
ows wallet delete --wallet "ops-treasury" --confirm
```

## Policy Engine

OWS has two access modes:

| Caller | Credential | Policy behavior |
|---|---|---|
| Owner | wallet passphrase | full access; policies are not evaluated |
| API key | `ows_key_...` token | all policies attached to the API key are evaluated |

Policies attach to API keys, not directly to wallets. An API key is scoped to
one or more wallets and one or more policies. All attached policies must allow
the request. Denials and policy failures fail closed before wallet key material
is decrypted.

Declarative rules include:

- `allowed_chains`: allow only listed CAIP-2 chain IDs
- `expires_at`: allow only before an ISO-8601 timestamp
- `allowed_typed_data_contracts`: allow EIP-712 typed data only for listed
  `domain.verifyingContract` addresses

Custom executable policies receive a `PolicyContext` JSON object on stdin and
must write one JSON object to stdout:

```json
{ "allow": true }
```

or:

```json
{ "allow": false, "reason": "Daily spending limit exceeded" }
```

Executable policy errors, invalid JSON, missing executables, non-zero exits, and
timeouts are denials.

## Policy And Key Commands

Create a simple Base-only policy:

```json
{
  "id": "base-only",
  "name": "Base only",
  "version": 1,
  "created_at": "2026-03-22T00:00:00Z",
  "rules": [
    { "type": "allowed_chains", "chain_ids": ["eip155:8453"] },
    { "type": "expires_at", "timestamp": "2026-12-31T23:59:59Z" }
  ],
  "action": "deny"
}
```

Create a Solana-only policy by using the Solana CAIP-2 ID:

```json
{
  "id": "solana-only",
  "name": "Solana only",
  "version": 1,
  "created_at": "2026-06-24T00:00:00Z",
  "rules": [
    {
      "type": "allowed_chains",
      "chain_ids": ["solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp"]
    },
    { "type": "expires_at", "timestamp": "2026-12-31T23:59:59Z" }
  ],
  "action": "deny"
}
```

Register and inspect policies:

```bash
ows policy create --file base-only.json
ows policy list
ows policy show --id base-only
ows policy delete --id base-only --confirm
```

Create and use an API key:

```bash
printf '%s\n' "$OWNER_PASSPHRASE" |
  ows key create --name "api-access" --wallet ows-treasury --policy base-only
unset OWNER_PASSPHRASE
OWS_PASSPHRASE="ows_key_..." ows sign tx --wallet ows-treasury --chain base --tx "0x02f8..." --json
ows key list
ows key revoke --id <key-id> --confirm
```

The raw `ows_key_...` token is shown once at creation time. Redact it in chat
unless the user explicitly asks to display it.

Use policies as the primary guardrail. If wallet access is requested and no
policy exists, propose a minimal policy first, commonly:

- `allowed_chains` for the target CAIP-2 chain IDs
- `expires_at` for time-bounded access
- `allowed_typed_data_contracts` for EIP-712 contract allowlists when relevant

Then complete setup with `ows policy create` and owner-passphrase stdin for
`ows key create`. After the API key exists, clear the owner passphrase and run
wallet operations with `OWS_PASSPHRASE="ows_key_..."`.

## Revocation

1. List API keys with `ows key list`.
2. Revoke the selected API key with `ows key revoke --id <key-id> --confirm`.
3. Treat the old `ows_key_...` token as invalid after revocation.

## Recovery, Import, And Export

1. Confirm the user really wants a secret-bearing operation.
2. Prefer stdin or environment variables over command-line arguments for secrets.
3. Run import, export, or derive.
4. Redact secrets from summaries unless the user explicitly requested display.
