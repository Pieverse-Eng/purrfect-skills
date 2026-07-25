# Preflight — integration, credentials, account

Everything under the Lighter gateway requires the trading integration to be
enabled. Only `status`, `enable`, and `disable` work while it is off.

## Integration

```bash
purr lighter status      # current integration state
purr lighter enable      # account-changing — confirm first
purr lighter disable     # account-changing — confirm first
```

`status` is the correct first call whenever you are unsure. Never `enable`
silently: state what enabling does, get an explicit yes, then run it.

If any gateway command returns `LIGHTER_TRADING_DISABLED`, stop and go through
the enable flow — do not retry the original command first.

## Readiness

```bash
purr lighter sdk-status        # signer/SDK readiness
purr lighter system-status     # venue status
purr lighter system-info
purr lighter system-config
```

`LIGHTER_INITIALIZING` means the signer is still starting: wait and re-read,
do not resubmit a write.

## Credentials — the agent cannot provision these

Lighter authenticates with an account index, API key index, and API private key
held by the platform. **`purr lighter` has no command to set them** — the CLI
exposes only `status` / `enable` / `disable` for integration state.

If you see `LIGHTER_CREDENTIAL_NOT_FOUND`, `LIGHTER_CREDENTIAL_UNVERIFIED`, or
`LIGHTER_CREDENTIAL_VERIFY_FAILED`:

1. Stop. Do not attempt a workaround, and do not ask the user to paste a private
   key into chat — it must never appear in a message.
2. Tell the user the Lighter API credentials need to be configured or
   re-verified on the platform side for this instance.
3. Re-check with `purr lighter sdk-status` / `status` afterwards.

`LIGHTER_API_KEY_SLOTS_EXHAUSTED` likewise needs platform-side attention.

## Account reads (no confirmation needed)

```bash
purr lighter account          # account summary
purr lighter balances
purr lighter positions
purr lighter limits           # account limits
purr lighter pnl [--resolution 1h] [--start-timestamp <unix>] [--end-timestamp <unix>] [--count-back <n>]
purr lighter orders
purr lighter active-orders
purr lighter inactive-orders
purr lighter transactions [--offset <n>] [--limit <n>]
purr lighter transaction --tx-hash <hash>
purr lighter l1-transaction --l1-tx-hash <hash>
purr lighter requests [--limit <n>]
purr lighter request-status --request-id <id>
```

Check `balances` and `positions` before sizing any order, and `limits` before a
large one. Read commands use a 20s client timeout and are safe to retry.

## Before an order — the short checklist

1. `status` — integration enabled?
2. `market --market <SYM> --market-type <perp|spot>` — market exists, and note
   its size/price decimals.
3. `order-book-depth --market <SYM> --market-type <t>` — derive the price bound
   (mandatory for market orders; see [trading.md](trading.md)).
4. `balances` / `positions` — is there collateral for this, and does it change
   an existing position?
5. Confirm with the user, then submit.

There is **no fee-authorization step on Lighter**. Do not prompt for one.
