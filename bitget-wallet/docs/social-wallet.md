# Social Login Wallet

Bitget Social Login Wallet signing is out of scope for this packaged skill.

Do not use:

- `.social-wallet-secret`
- `--wallet-id`
- `social-wallet.py`
- `social_order_make_sign_send.py`
- `social_transfer_make_sign_send.py`
- Bitget TEE signing APIs

For supported EVM execution, use the hosted Purr platform wallet instead:

```bash
purr bitget order-execute ...
purr bitget transfer-execute ...
purr bitget x402-pay ...
```

For read-only Bitget API operations such as balances, quotes, market data, token
checks, RWA discovery, and order status, use:

```bash
python3 scripts/bitget-wallet-agent-api.py <command> ...
```
