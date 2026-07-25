# Trading — orders, cancel, modify, leverage, margin

Every command here is account-changing and needs the Confirmation Contract in
`SKILL.md` first. There is **no fee-authorization step on Lighter**.

## Placing an order

```bash
purr lighter order \
  --market SOL --market-type perp \
  --side buy|sell \
  --size <amount> \
  --price <price> \
  [--type limit|market|stopLoss|stopLossLimit|takeProfit|takeProfitLimit|twap] \
  [--time-in-force ioc|gtt|postOnly] \
  [--reduce-only true|false] \
  [--trigger-price <price>] \
  [--client-order-index <n>] \
  [non-IOC only: --expires-in 30m | --expires-at <iso> | --order-expiry <unix-ms>]
```

`place-orders` takes the same flags and posts to the batch endpoint.

`order-preview` is body-only — it does **not** accept the flags above:

```bash
purr lighter order-preview --body-json '{"marketId":12,"side":"buy","type":"limit","size":"1","price":"100"}'
purr lighter order-preview --body-file <path>
```

### `--price` is required on EVERY order, including market orders

This is the single most dangerous thing to get wrong on Lighter. The platform
schema requires a positive `price` for all order types. For a market order it is
the **worst acceptable fill price** — a slippage bound, not a hint.

- **Buy market:** the highest price you accept. Too low → no fill.
  Absurdly high → you accept an awful fill.
- **Sell market:** the lowest price you accept.

Derive it from the live book and show the user your reasoning:

```bash
purr lighter order-book-depth --market SOL --market-type perp --limit 50
```

A defensible default is the far touch plus a small buffer (for a buy: best ask
× 1.0x–1.02x depending on depth and volatility). State the bound and the implied
slippage in the confirmation. Never submit a market order with a price you did
not derive from the current book, and never describe it to the user as "the
price you will pay" — it is the worst price you would tolerate.

### Size and precision

Read the market first and respect its decimals:

```bash
purr lighter market --market SOL --market-type perp
```

`LIGHTER_DECIMAL_INVALID` / `LIGHTER_DECIMAL_PRECISION_UNSUPPORTED` mean your
size or price has more precision than the market accepts — re-round, do not
retry unchanged. `LIGHTER_AMOUNT_OUT_OF_RANGE` / `LIGHTER_PRICE_OUT_OF_RANGE`
mean the value is outside venue limits, not a rounding problem.

Remember `1000`-prefixed markets are per-1000 tokens ([symbols.md](symbols.md)).

### Time in force, and the IOC trap

`--time-in-force` is `ioc`, `gtt`, or `postOnly`. **The default depends on the
order type:** `market`, `stopLoss`, and `takeProfit` default to `ioc`;
everything else defaults to `gtt`. When `--type` is omitted the order type is
`limit`.

**An IOC `market` or `limit` order rejects every expiry flag.** Passing
`--expires-in`, `--expires-at`, or `--order-expiry` on one — including a
*default*-IOC market order where you never typed `--time-in-force` — is an
error. Set an expiry only on a non-IOC order.

The three expiry flags are mutually exclusive with each other:

- `--expires-in` — integer + unit, e.g. `30m`, `24h`, `7d` (`ms|s|m|h|d|w`)
- `--expires-at` — ISO-8601 that **must** carry `Z` or an explicit UTC offset;
  a bare local timestamp is rejected
- `--order-expiry` — raw unix milliseconds

`postOnly` rejects an order that would take liquidity — appropriate when the
user explicitly wants to make, not take.

### Trigger orders

`stopLoss`, `stopLossLimit`, `takeProfit`, and `takeProfitLimit` use
`--trigger-price`. The `*Limit` variants also honour `--price` as the limit;
the plain variants execute at market once triggered, so `--price` remains the
slippage bound. Confirm both numbers explicitly with the user.

`--reduce-only true` is the correct flag for closing or trimming a position —
it cannot flip you to the opposite side. Prefer it whenever the user's intent is
"close" or "reduce".

`--price-protection` is an advanced pass-through flag accepted on most write
commands and forwarded to the venue. Leave it unset unless the user explicitly
asks for it; do not present it as a substitute for a correctly derived
`--price` bound.

## Cancel

```bash
purr lighter cancel --market SOL --market-type perp --order-index <id>
purr lighter cancel-all [--time-in-force immediate|scheduled|abortScheduled] [--time <unix-ms>]
```

Get `--order-index` from `active-orders`, never from memory of a submit
response. `cancel-all` is blunt — list what is open and confirm the full set
before running it. `scheduled` requires `--time`; `abortScheduled` cancels a
previously scheduled cancel.

## Modify

```bash
purr lighter modify --market SOL --market-type perp --order-index <id> \
  --size <amount> --price <price> [--trigger-price <price>]
```

Both `--size` and `--price` are required — modify replaces them, so re-send the
values you want even if only one is changing. Confirm the before/after.
`--trigger-price` is accepted here too, for trigger orders.

## Leverage

```bash
purr lighter update-leverage --market SOL --market-type perp \
  (--leverage <1-100> | --initial-margin-fraction <1-65535>) [--margin-mode cross|isolated]
```

Perp only. `--leverage` and `--initial-margin-fraction` are two ways to express
the same thing — pass one. `--margin-mode` defaults to `cross`; state which mode
you are setting in the confirmation, because switching cross↔isolated changes
the liquidation profile of an existing position.

Raising leverage on an open position moves the liquidation price against the
user. Say so before confirming.

## Margin

```bash
purr lighter update-margin --market SOL --market-type perp --amount <amount> --direction add|remove
```

Isolated-margin adjustment. `remove` reduces the buffer and moves liquidation
closer — quote the current position and margin before confirming.

## After submitting

A submit response is not a fill. Verify with:

```bash
purr lighter active-orders     # still resting?
purr lighter inactive-orders   # filled or cancelled?
purr lighter trades            # actual executions
purr lighter positions         # net effect
```

If the submit timed out or returned `LIGHTER_SUBMIT_UNKNOWN`, **do not
resubmit** — reconcile first. See [errors.md](errors.md).
