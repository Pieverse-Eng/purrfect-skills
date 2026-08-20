# Aster With OWS

Use this file when an OWS wallet should authenticate to Aster or deposit into
Aster.

## Deposit

Aster deposits produce EVM steps. Build without `--execute`, then execute with
OWS:

```bash
purr aster deposit \
  --token <token-address-or-symbol> \
  --amount-wei <amount-wei> \
  --wallet <ows-evm-address> \
  --chain-id 56 \
  > /tmp/aster-deposit.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/aster-deposit.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <bsc-rpc>
```

Add `--broker <broker-id>` only when the Aster flow requires a non-default
numeric broker ID.

## API Authentication

Do not use `purr aster api` as the OWS signing path. That command signs with
the Pieverse managed wallet. For OWS, construct the Aster EIP-712 payload, sign
it with OWS, then send the authenticated FAPI request.

The OWS EVM address must already be authorized in Aster Pro API as the API
signer for the user's main Aster login wallet.

1. Build the sorted URL-encoded parameter string containing the request params,
   `timestamp`, monotonic microsecond `nonce`, `user=<main-login-wallet>`, and
   `signer=<ows-evm-address>`.
2. Build typed data:

```json
{
  "domain": {
    "name": "AsterSignTransaction",
    "version": "1",
    "chainId": 1666,
    "verifyingContract": "0x0000000000000000000000000000000000000000"
  },
  "types": {
    "EIP712Domain": [
      { "name": "name", "type": "string" },
      { "name": "version", "type": "string" },
      { "name": "chainId", "type": "uint256" },
      { "name": "verifyingContract", "type": "address" }
    ],
    "Message": [{ "name": "msg", "type": "string" }]
  },
  "primaryType": "Message",
  "message": { "msg": "<sorted-query-string-without-signature>" }
}
```

3. Sign the typed data:

```bash
OWS_PASSPHRASE="ows_key_..." ows sign message \
  --wallet <ows-wallet> \
  --chain bsc \
  --message "typed-data" \
  --typed-data "$(cat /tmp/aster-typed-data.json)" \
  --json \
  > /tmp/aster-signature.json
```

4. Add `signature=<signature>` to the signed params and call
   `https://fapi.asterdex.com<endpoint>`.

Stop on `INVALID_SIGNATURE`, `No agent found`, or signer mismatch. Do not retry
with the platform wallet.
