# Morph With OWS

Use this file when an OWS wallet should perform Morph EVM workflows.

## Transfer

Replace `purr wallet transfer` with the EVM builder plus OWS execution:

```bash
purr evm transfer \
  --to <recipient> \
  --amount-wei <wei> \
  --chain-id 2818 \
  > /tmp/morph-transfer.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/morph-transfer.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <morph-rpc>
```

For ERC-20 transfers, add `--token <token-address>`.

## DEX, Bridge, And Raw Calldata

When a Morph tool returns calldata, build an approval if needed, then build the
raw call. Use the exact router, calldata, value, and gas limit from the Morph
flow:

```bash
purr evm approve \
  --token <token> \
  --spender <spender> \
  --amount <wei-or-max> \
  --chain-id 2818 \
  > /tmp/morph-approve.json

purr evm raw \
  --to <router-or-contract> \
  --data <0x-calldata> \
  --value <0x-wei> \
  --gas-limit 500000 \
  --chain-id 2818 \
  > /tmp/morph-call.json

jq -s '{steps:(.[0].steps + .[1].steps)}' \
  /tmp/morph-approve.json /tmp/morph-call.json \
  > /tmp/morph-steps.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/morph-steps.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <morph-rpc>
```

If no approval is needed, execute only the raw-call file.

## Identity And Contract Calls

Replace `purr wallet abi-call` with:

```bash
purr evm abi-call \
  --to <contract> \
  --signature '<function-signature>' \
  --args '<json-array>' \
  --chain-id 2818 \
  > /tmp/morph-abi-call.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/morph-abi-call.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <morph-rpc>
```

## Script Boundaries

Do not run Morph scripts that call platform wallet endpoints as an OWS signing
path. Scripts that POST to `/wallet/sign-transaction`, `/wallet/sign-typed-data`,
or `/wallet/execute` must first be changed or wrapped to output unsigned
transactions, typed data, or `steps` JSON. If that payload is not available,
stop and say OWS cannot safely take over the script yet.
