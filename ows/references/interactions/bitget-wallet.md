# Bitget Wallet With OWS

Use this file when an OWS wallet is requested for Bitget wallet flows.

## Boundary

`purr bitget order-execute`, `purr bitget transfer-execute`, and
`purr bitget x402-pay` are platform-wallet commands. Do not use them as OWS
signing paths.

Use the OWS-scoped Bitget commands under `purr ows-wallet` instead. These
commands reuse Bitget order/transfer/payment orchestration, but sign with OWS
local custody and submit through the Bitget APIs.

## Swap And RWA

Use the `bitget-wallet` skill for Bitget discovery, risk checks, quote,
confirm, and status calls. Run its script from that skill directory or use its
absolute path:

```bash
cd /home/linwe/Developer/purrfect-skills/bitget-wallet
```

After user confirmation, execute the order with OWS:

```bash
python3 scripts/bitget-wallet-agent-api.py quote <quote-flags>
python3 scripts/bitget-wallet-agent-api.py confirm <confirm-flags>

OWS_PASSPHRASE="ows_key_..." purr ows-wallet bitget-order-execute \
  --ows-wallet <ows-wallet> \
  --order-id <order-id-from-confirm> \
  --from-chain <from-chain> \
  --from-contract <from-contract-or-empty> \
  --from-symbol <from-symbol> \
  --from-address <ows-evm-address> \
  --to-chain <to-chain> \
  --to-contract <to-contract-or-empty> \
  --to-symbol <to-symbol> \
  --to-address <ows-evm-address-or-recipient> \
  --from-amount <amount> \
  --slippage <slippage> \
  --market <market-id> \
  --protocol <protocol-id>
```

If `make-order` was already called and is still fresh, pass the prepared
response instead. Always pass `--from-address <ows-evm-address>` so the CLI
can verify the OWS signer matches the prepared order sender:

```bash
python3 scripts/bitget-wallet-agent-api.py quote <quote-flags>
python3 scripts/bitget-wallet-agent-api.py confirm <confirm-flags>
python3 scripts/bitget-wallet-agent-api.py make-order <make-order-flags> \
  > /tmp/bitget-make-order.json

OWS_PASSPHRASE="ows_key_..." purr ows-wallet bitget-order-execute \
  --ows-wallet <ows-wallet> \
  --from-address <ows-evm-address> \
  --make-order-file /tmp/bitget-make-order.json
```

Stop on Solana order payloads or Tron order payloads. OWS Bitget order
execution supports EVM `data.txs` payloads only.

## Transfers

For Bitget-managed EVM transfer orders, use the OWS-scoped transfer command:

```bash
OWS_PASSPHRASE="ows_key_..." purr ows-wallet bitget-transfer-execute \
  --ows-wallet <ows-wallet> \
  --chain <chain-code> \
  --contract <token-contract-or-empty> \
  --from-address <ows-evm-address> \
  --to-address <recipient> \
  --amount <amount>
```

If `makeTransferOrder` was already called and is still fresh, pass it with
`--transfer-order-file <file>` and still include `--from-address
<ows-evm-address>` so the CLI can verify the OWS signer before submitting.

OWS supports Bitget transfer sources `evm_legacy` and `evm_1559`. Stop on
`evm_7702`, gasless/raw-digest, Solana partial-sign, Tron, or Morph AltFee
transfer sources.

## x402 Payments

For Bitget's x402 payment envelope, use:

```bash
OWS_PASSPHRASE="ows_key_..." purr ows-wallet bitget-x402-pay \
  --ows-wallet <ows-wallet> \
  --url <url> \
  --method POST \
  --data '<json>'
```

For an EIP-3009 authorization-only request, sign the typed data directly:

```bash
OWS_PASSPHRASE="ows_key_..." purr ows-wallet bitget-x402-sign-eip3009 \
  --ows-wallet <ows-wallet> \
  --token <usdc-token> \
  --chain-id <chain-id> \
  --to <pay-to> \
  --amount <base-units>
```

Stop on Solana x402 or non-EIP-3009 asset transfer methods.
