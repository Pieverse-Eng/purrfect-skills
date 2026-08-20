# Lista Vaults With OWS

Use this file when an OWS wallet should deposit, redeem, or withdraw through
`lista-vaults`.

## Flow

1. Use Lista discovery normally.
2. Build the Lista write steps without `--execute`.
3. Show the vault, token, amount, wallet, chain, and generated steps.
4. After user confirmation, execute the steps with OWS.

## Discover Vaults And Balances

```bash
purr lista list-vaults --zone <classic|alpha|aster>
OWS_PASSPHRASE="ows_key_..." ows fund balance --wallet <ows-wallet> --chain bsc
```

Use the OWS EVM address as `--wallet` for Lista commands.

## Deposit

```bash
purr lista deposit \
  --vault <vault-address> \
  --amount-wei <underlying-amount-wei> \
  --token <underlying-token-address> \
  --wallet <ows-evm-address> \
  --chain-id 56 \
  > /tmp/lista-deposit.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/lista-deposit.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <bsc-rpc>
```

The deposit builder includes token approval when needed.

## Redeem

```bash
purr lista redeem \
  --vault <vault-address> \
  --shares-wei <share-amount-wei> \
  --wallet <ows-evm-address> \
  --chain-id 56 \
  > /tmp/lista-redeem.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/lista-redeem.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <bsc-rpc>
```

## Withdraw

```bash
purr lista withdraw \
  --vault <vault-address> \
  --amount-wei <underlying-amount-wei> \
  --wallet <ows-evm-address> \
  --chain-id 56 \
  > /tmp/lista-withdraw.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/lista-withdraw.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <bsc-rpc>
```

Do not add `--execute` to `purr lista` in OWS flows.
