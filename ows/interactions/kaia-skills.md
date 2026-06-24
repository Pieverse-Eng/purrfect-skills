# Kaia Skills With OWS

Use this file when an OWS wallet should perform a Kaia or Kairos workflow from
`kaia-skills`.

## Address And Chain

Use the OWS EVM address as the wallet/caller address. Use chain ID `8217` for
Kaia mainnet and the Kairos chain ID for testnet workflows. Confirm the RPC URL
matches the step chain before broadcasting.

## Transfer

Build the unsigned step without `--execute`, then execute with OWS:

```bash
purr evm transfer \
  --to <recipient> \
  --amount-wei <wei> \
  --chain-id 8217 \
  > /tmp/kaia-transfer.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/kaia-transfer.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <kaia-rpc>
```

For token transfers, add `--token <erc20-address>` to `purr evm transfer`.

## Approval, Raw Call, And ABI Call

Use the local EVM builders that emit `steps` JSON:

```bash
purr evm approve \
  --token <token> \
  --spender <spender> \
  --amount <wei-or-max> \
  --chain-id 8217 \
  > /tmp/kaia-approve.json

purr evm raw \
  --to <contract> \
  --data <0x-calldata> \
  --value <0x-wei> \
  --gas-limit <gas-limit> \
  --chain-id 8217 \
  > /tmp/kaia-raw.json

purr evm abi-call \
  --to <contract> \
  --signature 'register(string)' \
  --args '["..."]' \
  --chain-id 8217 \
  > /tmp/kaia-abi-call.json
```

Execute the generated file after user confirmation:

```bash
OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/kaia-abi-call.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <kaia-rpc>
```

For approve + call sequences, concatenate steps before execution:

```bash
jq -s '{steps:(.[0].steps + .[1].steps)}' \
  /tmp/kaia-approve.json /tmp/kaia-raw.json \
  > /tmp/kaia-steps.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/kaia-steps.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <kaia-rpc>
```

## Message And Typed Data Signing

Replace `purr wallet sign` and `purr wallet sign-typed-data` with OWS signing:

```bash
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet <ows-wallet> \
  --chain eip155:8217 \
  --message "<message>" \
  --json

OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet <ows-wallet> \
  --chain eip155:8217 \
  --message "typed-data" \
  --typed-data "$(cat /tmp/typed-data.json)" \
  --json
```

Include `types.EIP712Domain` in EVM typed-data JSON before calling OWS.
Stop if the OWS address does not match the expected Kaia signer.
