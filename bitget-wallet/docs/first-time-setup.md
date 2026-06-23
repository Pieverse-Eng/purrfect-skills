# First-Time Setup

## Platform Wallet

For signing or execution, this skill uses the hosted Purr platform wallet through
`purr`. Do not create or import Bitget Social Login Wallets, mnemonics, private
keys, seed phrases, or key files.

Before executing a swap, RWA trade, transfer, or x402 payment, verify that `purr`
can access the platform wallet:

```bash
purr wallet address --chain-type ethereum
```

Use that returned address as the Bitget `from-address`. For swaps where the same
wallet receives the output, also use it as `to-address`.

If `purr` reports missing `WALLET_API_URL`, `WALLET_API_TOKEN`, `INSTANCE_ID`,
or config values, stop and explain that Bitget execution requires a hosted
Purr runtime or loaded platform wallet credentials.

## Query-Only Use

No platform wallet is required for read-only work such as:

- token search
- market data
- K-lines
- risk/security checks
- alpha signals
- address discovery
- RWA stock discovery
- existing order status lookups

For those tasks, use `python3 scripts/bitget-wallet-agent-api.py <command> ...`
with the matching domain document.

## Execution Preferences

Before a first execution, show the user the route or transfer details and ask for
explicit confirmation. Include:

- chain and token contracts
- amount
- wallet address
- route `market`, `protocol`, and `slippage` for swaps
- gas or gasless context
- risk warnings returned by Bitget

Do not sign, submit, pay, swap, transfer, buy, or sell until the user confirms.
