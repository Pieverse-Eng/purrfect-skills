# OpenSea With OWS

Use this file when an OWS wallet should sign or execute OpenSea payloads.

## Transaction Execution

Use OpenSea vendor skills to prepare fulfillment, transaction, or action JSON.
Then run `purr opensea` without `--execute` and execute the emitted steps with
OWS:

```bash
purr opensea buy \
  --wallet <ows-evm-address> \
  --fulfillment-file <fulfillment.json> \
  > /tmp/opensea-buy.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/opensea-buy.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <chain-rpc>
```

The same pattern applies to:

```bash
purr opensea sell \
  --wallet <ows-evm-address> \
  --fulfillment-file <fulfillment.json> \
  > /tmp/opensea-sell.json

purr opensea tx \
  --wallet <ows-evm-address> \
  --chain-id <chain-id> \
  --tx-file <tx.json> \
  > /tmp/opensea-tx.json

purr opensea actions \
  --wallet <ows-evm-address> \
  --chain-id <chain-id> \
  --actions-file <actions.json> \
  > /tmp/opensea-actions.json
```

If `purr opensea actions` returns `signatureRequests`, sign those requests
first. Do not execute only the transaction steps from a mixed transaction plus
signature action payload.

## Order, Payment, And Typed Data Signatures

Use OWS for EIP-712 typed data:

```bash
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet <ows-wallet> \
  --chain eip155:<chain-id> \
  --message "typed-data" \
  --typed-data "$(cat /tmp/opensea-typed-data.json)" \
  --json
```

Use this for OpenSea listing signatures, offer signatures, x402/EIP-3009
payment typed data, and typed data items returned in `signatureRequests`.
Include `types.EIP712Domain` in the typed-data JSON before calling OWS.

## Auth Or SIWE Message Signatures

```bash
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet <ows-wallet> \
  --chain eip155:<chain-id> \
  --message "$(cat /tmp/opensea-message.txt)" \
  --json
```

Return the signature exactly as OWS reports it. Stop if the OpenSea payload
expects a signer that is not the OWS EVM address.
