# Wallet Signing

This packaged skill does not use local mnemonics, private keys, key files,
Bitget Social Login Wallet signing, or direct signed-payload submission.

Use the hosted Purr platform wallet through `purr`:

```bash
purr wallet address --chain-type ethereum
```

## Supported Signing Paths

| Need | Command |
|---|---|
| EVM swap or RWA execution | `purr bitget order-execute` |
| EVM token transfer or supported EVM gasless transfer | `purr bitget transfer-execute` |
| EVM x402 payment-required flow | `purr bitget x402-pay` |
| EVM EIP-3009 x402 authorization only | `purr bitget x402-sign-eip3009` |

## What `purr bitget` Does

- signs with the platform wallet, not local keys
- checks platform signer address against `--from-address` before signing
- rejects Solana partial-sign and Tron execution paths
- submits supported signed payloads through the Bitget API where required

## Out Of Scope

Stop if the user request requires:

- local private keys, mnemonics, seed phrases, or key files
- `order_sign.py`, `order_make_sign_send.py`, `transfer_make_sign_send.py`,
  `x402_pay.py`, or `key_utils.py`
- Bitget Social Login Wallet credentials or `.social-wallet-secret`
- `social-wallet.py`, `social_order_make_sign_send.py`, or
  `social_transfer_make_sign_send.py`
- Solana partial-sign, Solana x402, Tron execution, or unsupported transfer
  source types
