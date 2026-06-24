# Operations

## API-Key Signing

1. Set the wallet with `--wallet <wallet>` or `OWS_WALLET=<wallet>`.
2. Set the API token with `OWS_PASSPHRASE="ows_key_..."`.
3. Show the exact command and get confirmation.
4. Run a signing command, for example:
   ```bash
   OWS_PASSPHRASE="ows_key_..." ows sign message \
     --wallet ows-treasury \
     --chain base \
     --message "hello" \
     --json
   ```
5. If policy denies the action, report the CLI error exactly and do not retry
   with owner passphrase.

## Signing Commands

Sign messages:

```bash
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet "ows-treasury" --chain ethereum --message "hello" --json
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet "ows-treasury" --chain solana --message "hello" --json
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet "ows-treasury" --chain bitcoin --message "hello" --json
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet "ows-treasury" --chain 8453 --message "hello" --json
```

Sign EIP-712 typed data on EVM chains:

```bash
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet "ows-treasury" \
  --chain base \
  --message "typed-data" \
  --typed-data '<typed-data-json>' \
  --json
```

For OWS CLI typed-data signing, include `types.EIP712Domain` in the JSON. Some
typed-data libraries omit it, but the OWS CLI rejects those payloads.

Sign raw transaction bytes:

```bash
OWS_PASSPHRASE="ows_key_..." ows sign tx \
  --wallet "ows-treasury" --chain ethereum --tx "0x02f8..." --json
OWS_PASSPHRASE="ows_key_..." ows sign tx \
  --wallet "ows-treasury" --chain solana --tx "deadbeef..." --json
```

Sign and broadcast a transaction:

```bash
OWS_PASSPHRASE="ows_key_..." ows sign send-tx \
  --wallet "ows-treasury" --chain base --tx "0x02f8..." --json
OWS_PASSPHRASE="ows_key_..." ows sign send-tx \
  --wallet "ows-treasury" --chain base --tx "0x02f8..." \
  --rpc-url "<rpc-url>" --json
OWS_PASSPHRASE="ows_key_..." ows sign send-tx \
  --wallet "ows-treasury" --chain solana --tx "0x0100..." \
  --rpc-url "<solana-rpc-url>" --json
```

`--chain` may be a supported chain alias, a CAIP-2 ID such as `eip155:8453`,
or a bare EVM chain ID such as `8453`. Passphrases and API tokens are supplied
through `OWS_PASSPHRASE` or an interactive prompt, not a `--passphrase` flag.
Use `--index <n>` for non-default accounts.

## Purr OWS Transfer And Execute Helpers

Use these only when the user asks to operate an OWS wallet through Purr CLI or
when a Purr workflow already produced executable steps. Show the exact command
and get confirmation before signing or broadcasting.

The Purr wrappers still use local OWS custody and policy checks:

```bash
OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/steps.json \
  --ows-wallet "ows-treasury"
```

### Solana Native Or SPL Transfer

Build the unsigned Solana transfer, then execute the emitted JSON object:

```bash
purr ows-wallet build-transfer \
  --ows-wallet "ows-treasury" \
  --to "<solana-recipient>" \
  --amount "0.01" \
  --chain-type solana \
  --rpc-url "<solana-rpc-url>" \
  > /tmp/solana-transfer.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/solana-transfer.json \
  --ows-wallet "ows-treasury" \
  --rpc-url "<same-solana-rpc-url>"
```

For SPL tokens, add `--token <mint>` and optionally `--decimals <n>` to
`purr ows-wallet build-transfer`.

Keep the build and execute RPC URLs the same. If Solana returns
`BlockhashNotFound`, rebuild the transaction to get a fresh blockhash and retry
once only after user confirmation. If the chain reports insufficient funds,
account not found, policy denial, or another broadcast error, report it exactly.

### Solana Swap Or Vendor Transaction

Purr does not discover Solana swap routes. Use the swap provider or upstream
tool to build an unsigned transaction, then execute it with an explicit Solana
marker:

```json
{
  "steps": [
    {
      "chain": "solana",
      "serializedTransaction": "<base58-serialized-transaction>",
      "label": "swap"
    }
  ]
}
```

Then run:

```bash
OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/solana-swap.json \
  --ows-wallet "ows-treasury" \
  --rpc-url "<solana-rpc-url>"
```

Use `serializedTransaction` for base58 payloads. Use `unsignedTxHex` or
`serializedTx` for hex payloads. When `unsignedTxHex` is used, include an
explicit Solana marker such as `chain: "solana"`, `chainType: "solana"`, or
`chainId: 501`; do not rely on `unsignedTxHex` alone.

### EVM Steps

`purr ows-execute` executes EVM `TxStep[]` arrays. The file must contain
`{ "steps": [...] }` or an array of steps with matching numeric `chainId`
values:

```json
{
  "steps": [
    {
      "to": "0x3333333333333333333333333333333333333333",
      "data": "0x",
      "value": "0x0",
      "chainId": 8453,
      "label": "example"
    }
  ]
}
```

Then run:

```bash
OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/evm-steps.json \
  --ows-wallet "ows-treasury" \
  --rpc-url "<evm-rpc-url>"
```

Do not pass a single EVM `purr ows-wallet build-transfer` output object to
`purr ows-execute`. For EVM build-transfer output, use the `nextStep` command
from the JSON or run `ows sign send-tx --chain eip155:<chain-id> --tx
<unsignedTxHex>`.

## Funding, Balance, And x402

Check balances:

```bash
OWS_PASSPHRASE="ows_key_..." ows fund balance --wallet "ows-treasury" --chain base
```

Create a funding deposit:

```bash
OWS_PASSPHRASE="ows_key_..." ows fund deposit --wallet "ows-treasury" --chain base
OWS_PASSPHRASE="ows_key_..." ows fund deposit --wallet "ows-treasury" --chain base --token USDC
```

Discover x402 services:

```bash
ows pay discover
ows pay discover --query "weather"
ows pay discover --limit 20 --offset 100
```

Make an x402-capable HTTP request:

```bash
OWS_PASSPHRASE="ows_key_..." ows pay request "https://api.example.com/data" --wallet "ows-treasury"
OWS_PASSPHRASE="ows_key_..." ows pay request \
  "https://api.example.com/submit" \
  --wallet "ows-treasury" \
  --method POST \
  --body '{"query":"test"}'
```

Explain that `ows pay request` may sign an EIP-3009 USDC authorization and retry
the request with a payment header when the server returns HTTP 402.

## Mnemonics

Generate a mnemonic:

```bash
ows mnemonic generate --words 24
```

Derive an address from a mnemonic. The mnemonic is read from `OWS_MNEMONIC` or
stdin:

```bash
echo "<mnemonic words>" | ows mnemonic derive --chain ethereum
echo "<mnemonic words>" | ows mnemonic derive
echo "<mnemonic words>" | ows mnemonic derive --chain base --index 1
```

Mnemonic commands expose root wallet material. Require confirmation and redact
the phrase unless the user explicitly requests display.

## x402 Payment Workflow

1. Discover services with `ows pay discover`.
2. Show payment target, method, body, and wallet.
3. Confirm with the user.
4. Run `OWS_PASSPHRASE="ows_key_..." ows pay request "<url>" --wallet "<wallet>"`.
5. Summarize HTTP status, payment status, response body, and errors.
