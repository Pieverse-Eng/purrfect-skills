# CLI Reference

## Command Map

Use this map to classify requests, then confirm exact flags with command help
when needed.

| Area | Commands |
|---|---|
| Wallets | `ows wallet create`, `import`, `export`, `delete`, `rename`, `list`, `info` |
| Signing | `ows sign message`, `tx`, `send-tx` |
| Mnemonics | `ows mnemonic generate`, `derive` |
| Funding | `ows fund deposit`, `balance` |
| x402 payments | `ows pay request`, `discover` |
| Policies | `ows policy create`, `list`, `show`, `delete` |
| API keys | `ows key create`, `list`, `revoke` |
| Config | `ows config show` |
| System | `ows update`, `ows uninstall` |
| Purr OWS helpers | `purr ows-wallet build-transfer`, Bitget OWS commands, `purr ows-execute` |

Bitget OWS commands are `purr ows-wallet bitget-order-execute`,
`bitget-transfer-execute`, `bitget-x402-sign-eip3009`, and `bitget-x402-pay`.

## Inputs And Environment

Wallet arguments may also come from `OWS_WALLET` when the command supports it.
Passphrases and API tokens come from `OWS_PASSPHRASE` or an interactive prompt.
Mnemonic and private key imports read from stdin or `OWS_MNEMONIC`,
`OWS_PRIVATE_KEY`, `OWS_SECP256K1_KEY`, and `OWS_ED25519_KEY`.

Use `--index` when the user asks for a non-default account index. The default
account index is `0`.

## Supported Chains

OWS uses CAIP identifiers internally. Wallet files, policy contexts, audit logs,
and policy files should use canonical CAIP IDs, not aliases.

Supported chain families:

| Family | CAIP namespace | Example chain ID | Address shape |
|---|---|---|---|
| EVM | `eip155` | `eip155:8453` | `0x...` |
| Solana | `solana` | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` | base58 |
| Bitcoin | `bip122` | `bip122:000000000019d6689c085ae165831e93` | `bc1...` |
| Cosmos | `cosmos` | `cosmos:cosmoshub-4` | `cosmos1...` |
| Tron | `tron` | `tron:mainnet` | `T...` |
| TON | `ton` | `ton:mainnet` | `UQ...` |
| Sui | `sui` | `sui:mainnet` | `0x...` |
| XRPL | `xrpl` | `xrpl:mainnet` | `r...` |
| Spark | `spark` | `spark:mainnet` | `spark:...` |
| Filecoin | `fil` | `fil:mainnet` | `f1...` |
| Nano | `nano` | `nano:mainnet` | `nano_...` |
| NEAR | `near` | `near:mainnet` | implicit account hex |

Common CLI aliases may work in command arguments and should resolve to CAIP IDs
before processing: `ethereum`, `base`, `polygon`, `arbitrum`, `optimism`,
`bsc`, `avalanche`, `solana`, `bitcoin`, `cosmos`, `tron`, `ton`, `sui`,
`xrpl`, `spark`, `filecoin`, `nano`, `near`, and related testnet aliases.

The signing CLI may also accept bare EVM chain IDs such as `8453` for Base.

For Purr OWS Solana execution payloads, `serializedTransaction` fields are
base58. `unsignedTxHex` and `serializedTx` fields are hex. `unsignedTxHex` must
be accompanied by an explicit Solana marker before it is treated as Solana.

## Config

Show current configuration and RPC endpoints:

```bash
ows config show
```

## System Commands

Update and uninstall are supported CLI workflows, but they can alter the user's
environment or delete wallet data. Require explicit confirmation:

```bash
ows update
ows update --force
ows uninstall
ows uninstall --purge
```

Warn that `ows uninstall --purge` removes wallet data.
