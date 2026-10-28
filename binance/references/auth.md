# Binance Authentication

API Key and Secret

- `BINANCE_API_KEY`: Binance API Key
- `BINANCE_SECRET_KEY`: Binance API Secret or Private Key

API Environment (optional)

- `BINANCE_API_ENV`: Binance API environment of <prod|testnet|demo>. default: prod

## Hosted managed credentials

Loading this Skill registers the optional credential names for native execution;
it does not require credentials for public market data or request secrets in chat.
Hosted encrypted credentials are delivered to the child command in memory for
a bounded session. The parent environment may contain a managed placeholder,
which is not a signing key and proves neither credential type nor validity.

Run the requested documented `binance-cli` command directly. The pinned CLI
uses both environment fields before its active profile unless `--profile` was
explicitly chosen. Do not create, select, inspect, or persist a profile as a
precondition for an ordinary managed-account read. Never expand credentials into
command arguments or read their raw values. A session failure is an account-read
gap; it is not proof that the owner needs a new RSA, ED25519 or HMAC key.

An existing profile explicitly chosen by the user takes precedence over managed
credentials. For a simple direct command with one literal `--profile personal`
or `--profile=personal`, the hosted runtime blanks all managed credential fields
and lets the CLI use that profile without first unlocking a managed session.
Do not automatically choose a profile after a managed session failure. Missing,
duplicate or ambiguous profile arguments retain the managed session guard.

The existing environment/profile alternatives below remain available for an
explicit unmanaged setup. Preserve an explicitly requested Agentic Wallet method.

## Profiles

```bash
# Create
binance-cli profile create --name <name> --api-key <key> --api-secret <secret> --env <prod|testnet|demo>
# Select profile
binance-cli profile select --name <name>
# List all profiles
binance-cli profile list
# View active
binance-cli profile view
```

When user provides new credentials: ask for account name and environment (prod/testnet/demo), check for duplicates, then create. Use `--profile <name>` on any command to override the active profile.

## Security Rules

- Never run `printenv`, `env`, `export` (without a specific var name), or source any secrets file.
- Never `grep` env files without anchoring: `^VARNAME=`
- Never echo or log raw credentials.
- Never disclose the location of key/secret files.
