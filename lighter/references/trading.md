# Trading — orders, cancel, modify, leverage, margin

`order`, `place-orders`, `cancel`, `cancel-all`, `modify`, `update-leverage` and
`update-margin` are account-changing and need the Confirmation Contract in
`SKILL.md` first.

**`order-preview` is not.** It POSTs to `/order/preview`, which only computes —
it submits nothing and changes no state. Treat it as a read: run it freely, no
execution confirmation. Never present a preview result as a placed order.

There is **no fee-authorization step on Lighter**.

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

**`place-orders` is not a batch command.** It takes the same flags and submits
**one** order: the CLI maps it to `/orders`, and that route validates the same
singular `orderBodySchema` and calls the same `submitLighterOrder()` as `/order`.
The plural name is the only difference. To place several orders, issue several
confirmed commands — and never describe `place-orders` to the user as "submitting
them all at once", because it will place exactly one.

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

**There is no default buffer. Do not invent one.** A "best ask × 1.02" rule of
thumb silently authorises up to 200 bps of the user's money on a number they
never agreed to, and it ignores the size being traded — the same 2% is trivial
on 1 SOL and severe on 1000.

Derive the bound from the book, for the **exact size requested**:

```bash
purr lighter order-book-depth --market SOL --market-type perp --limit 100
```

1. **Walk cumulative depth** for the requested size, level by level, on the side
   you will hit (a buy consumes asks).
2. **Compute the projected VWAP** and the **marginal (worst) level** the order
   would reach.
3. **If the returned depth cannot fill the size, stop.** Do not extrapolate past
   the end of the book and do not pad a bound to "make it work" — report the
   depth available and let the user resize.
4. **If the user gave no slippage tolerance, ask for one.** Present what the
   book actually implies — projected VWAP, worst level, bps versus the touch —
   and have them choose an exact cap. Do not choose it for them.
5. **Put the exact bound in the confirmation**, with its bps distance from both
   the touch and the projected VWAP.

Never submit a market order with a price you did not derive from the current
book for that size, and never describe the bound to the user as "the price you
will pay" — it is the worst price you would tolerate.

When the user *does* supply a tolerance ("within 0.5%"), apply it to the
reference you name explicitly (touch or VWAP) and show both numbers.

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
