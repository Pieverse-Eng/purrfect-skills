# DFlow With OWS

Use this file when an OWS wallet should execute a DFlow Solana order.

## Order Then OWS Execution

Get an order normally, but do not use `purr dflow execute-order` or
`purr dflow order --execute`; those sign through the platform wallet.

```bash
purr dflow order \
  --input-mint <input-mint> \
  --output-mint <output-mint> \
  --amount <amount-base-units> \
  --raw \
  > /tmp/dflow-order.json
```

The order response must contain `order.transaction`, a base64 serialized Solana
transaction. Convert it to hex, wrap it as a Solana step, then execute with OWS:

```bash
TX_HEX="0x$(jq -r '.order.transaction' /tmp/dflow-order.json | base64 -d | xxd -p -c 999999)"

jq -n --arg tx "$TX_HEX" \
  '{steps:[{chain:"solana", unsignedTxHex:$tx, label:"DFlow order"}]}' \
  > /tmp/dflow-ows.json

OWS_PASSPHRASE="ows_key_..." purr ows-execute \
  --steps-file /tmp/dflow-ows.json \
  --ows-wallet <ows-wallet> \
  --rpc-url <solana-rpc>
```

If the order payload exposes a base58 serialized transaction instead, write it
as `serializedTransaction`:

```json
{
  "steps": [
    {
      "chain": "solana",
      "serializedTransaction": "<base58-serialized-transaction>",
      "label": "DFlow order"
    }
  ]
}
```

## Status

If the order response includes `orderAddress`, poll status after broadcast:

```bash
purr dflow status \
  --order-address "$(jq -r '.order.orderAddress // .order.order_address' /tmp/dflow-order.json)" \
  --poll true
```

Stop if the Solana transaction requires a signer that is not the OWS Solana
address, requires multiple missing signers, or has expired. Rebuild the order if
the blockhash or last valid block height is stale.
