# Typed Order Commands

Use these commands instead of constructing Hyperliquid order, modify, or
cancel payloads. The CLI constructs the venue request and rejects missing,
duplicate, unknown, conflicting, positional, or invalid arguments before it
sends a platform request.

Raw `order` and `modify` commands are removed. `cancel` and
`cancel-by-cloid` do not accept `--body-json` or `--body-file`. There is no
typed batch-order, batch-modify, or batch-cancel fallback.

## Select the Command

| Intent | Command | Venue grouping |
| --- | --- | --- |
| Place one ordinary limit or reduce-only order | `limit-order` | `na` |
| Place an entry with attached TP and SL | `bracket-order` | `normalTpsl` |
| Add one stop-loss for an existing position | `stop-loss` | `positionTpsl` |
| Add one take-profit for an existing position | `take-profit` | `positionTpsl` |
| Add both TP and SL for an existing position | `protect-position` | `positionTpsl` |
| Replace an open ordinary limit order | `modify-limit-order` | Preserves the chosen order type |
| Replace an open stop-loss | `modify-stop-loss` | Trigger order |
| Replace an open take-profit | `modify-take-profit` | Trigger order |

A user request for a stop-loss or take-profit requires a trigger command. Do
not translate it into `limit-order`. Use `limit-order --reduce-only true` only
when the user actually wants an ordinary resting or market-style exit order.

## Place Orders

### Ordinary limit order

```bash
purr hyperliquid limit-order \
  --asset <asset-id> \
  --side buy|sell \
  --size <asset-size> \
  --price <price> \
  --tif Gtc|Ioc|Alo|FrontendMarket \
  --reduce-only true|false \
  [--cloid <cloid>]
```

`--size` is in asset units, not USD. Resolve `assetId` and `szDecimals` with
`symbol`; do not infer either one.

`FrontendMarket` is market-style execution with an explicit protection price,
not an unbounded market order. Treat `--price` as the user-confirmed worst
execution boundary. For a buy it should be above the current executable price;
for a sell it should be below. If the user has not approved that boundary, do
not invent one.

### Entry with attached TP/SL

```bash
purr hyperliquid bracket-order \
  --asset <asset-id> \
  --side buy|sell \
  --size <asset-size> \
  --entry-price <price> \
  --entry-tif Gtc|Ioc|Alo|FrontendMarket \
  --take-profit-price <trigger> \
  --stop-loss-price <trigger> \
  --execution market|limit \
  [--take-profit-worst-price <price>] \
  [--stop-loss-worst-price <price>] \
  [--take-profit-limit-price <price>] \
  [--stop-loss-limit-price <price>] \
  [--cloid <entry-cloid>]
```

This submits an entry followed by fixed-size, reduce-only TP and SL children
using `normalTpsl`. Their size does not adjust with later position changes.
`--cloid` applies to the entry. After submission, use
`orders --kind frontend` to identify the entry and child OIDs.

For a long entry, confirm that TP is above the intended entry/current market
and SL is below it. For a short entry, confirm the reverse. A merely valid
`TP > SL` or `TP < SL` relationship is not enough if either trigger would fire
immediately.

### Existing-position protection

```bash
purr hyperliquid stop-loss \
  --asset <asset-id> \
  --position-side long|short \
  --size <current-position-size> \
  --trigger-price <trigger> \
  --execution market|limit \
  [--worst-price <price>] \
  [--limit-price <price>] \
  [--cloid <cloid>]

purr hyperliquid take-profit \
  --asset <asset-id> \
  --position-side long|short \
  --size <current-position-size> \
  --trigger-price <trigger> \
  --execution market|limit \
  [--worst-price <price>] \
  [--limit-price <price>] \
  [--cloid <cloid>]

purr hyperliquid protect-position \
  --asset <asset-id> \
  --position-side long|short \
  --size <current-position-size> \
  --take-profit-price <trigger> \
  --stop-loss-price <trigger> \
  --execution market \
  --take-profit-worst-price <price> \
  --stop-loss-worst-price <price>
```

These commands create reduce-only `positionTpsl` orders. Unlike
`normalTpsl`, their size adjusts proportionally when the position size changes.
Before using them, read `state --kind perp [--dex <dex>]` and verify the exact
asset, position side, and absolute current position size. A position has no
OID.

For full-position protection, pass the full current position size. For a
proportional partial TP/SL, pass the user-confirmed portion of the current
position and explain that its absolute size will scale with later position
changes. These commands cannot promise a fixed absolute partial-close size;
if that is the user's requirement, report that the typed CLI does not expose
that conditional-order behavior and do not fall back to a raw payload. Never
copy size from an old entry order or assume the position is unchanged.

`protect-position` currently supports market execution only. Use the
individual trigger commands when limit execution is required.

## Trigger and Execution Prices

The trigger and the executable order price are different:

- `--trigger-price`, `--take-profit-price`, and `--stop-loss-price` are trigger
  prices.
- Market trigger execution requires an explicit `--worst-price`, or the
  matching `--take-profit-worst-price` and `--stop-loss-worst-price`.
- When closing a long, every market-trigger worst price must be strictly below
  its trigger.
- When closing a short, every market-trigger worst price must be strictly
  above its trigger.
- Never set the worst price equal to the trigger. A gap or price jump could
  otherwise leave the protection unable to execute.
- Limit trigger execution requires `--limit-price`, or the paired
  `--take-profit-limit-price` and `--stop-loss-limit-price`. Do not also pass a
  worst-price option.

For an existing long, a normal TP is above the current market and a normal SL
is below it. For an existing short, the reverse applies. If a requested trigger
is already crossed or would fire immediately, stop and ask the user instead of
silently changing it.

Do not invent an automatic slippage percentage. The final confirmation must
show every trigger and worst/limit execution price.

## Modify Open Orders

```bash
purr hyperliquid modify-limit-order \
  --oid <oid-or-cloid> \
  --asset <asset-id> \
  --side buy|sell \
  --size <asset-size> \
  --price <price> \
  --tif Gtc|Ioc|Alo|FrontendMarket \
  --reduce-only true|false \
  [--cloid <replacement-cloid>]

purr hyperliquid modify-stop-loss \
  --oid <oid-or-cloid> \
  --asset <asset-id> \
  --position-side long|short \
  --size <asset-size> \
  --trigger-price <trigger> \
  --execution market|limit \
  [--worst-price <price>] \
  [--limit-price <price>] \
  [--cloid <replacement-cloid>]

purr hyperliquid modify-take-profit \
  --oid <oid-or-cloid> \
  --asset <asset-id> \
  --position-side long|short \
  --size <asset-size> \
  --trigger-price <trigger> \
  --execution market|limit \
  [--worst-price <price>] \
  [--limit-price <price>] \
  [--cloid <replacement-cloid>]
```

A modify command replaces the complete open order; it is not a partial patch.
Read the current order first and provide every required field. `--oid` selects
the target and accepts a numeric OID or a cloid. Optional `--cloid` is the
client ID on the replacement order, not the target selector.

Neither `bracket-order` nor `protect-position` can be modified as one group.
For a bracket, modify its still-open entry with `modify-limit-order`. For both
commands, modify each open TP/SL child with its matching modify command;
`protect-position` has no entry order.

Use the frontend order's `isPositionTpsl` field to preserve sizing semantics.
For a position TP/SL, re-read live position state and preserve the user's
protected proportion. For a normal bracket child, preserve its fixed child
size. Never convert between fixed and proportional protection silently.

Once an entry order is filled, it is historical and cannot be modified. Manage
the resulting position by creating or modifying its open protection orders.
For a partially filled entry, the OID controls only the unfilled remainder;
the filled amount is already a position.

## Find and Verify Order IDs

```bash
purr hyperliquid orders --kind frontend [--dex <dex>]
purr hyperliquid orders --kind open [--dex <dex>]
purr hyperliquid orders --kind historical
purr hyperliquid fills [--start-time <ms>]
purr hyperliquid order-status --oid <oid-or-cloid>
```

- Use `frontend` to identify current entry and TP/SL child OIDs.
- Use `open` for the basic current open-order list.
- Use `historical` or `fills` to locate an already filled or cancelled entry.
- Use `order-status` to verify one known numeric OID or cloid.
- `state` identifies positions, but positions do not have order IDs.

Never select an order using only coin, side, or conversational context when
multiple candidates can exist. Verify the exact open order and its type before
modifying or cancelling it.

## Cancel

```bash
purr hyperliquid cancel --asset <asset-id> --oid <numeric-oid>
purr hyperliquid cancel-by-cloid --asset <asset-id> --cloid <cloid>
```

`cancel` accepts a numeric OID only. Use `cancel-by-cloid` for a cloid. Confirm
the asset and exact open order before execution. The typed CLI does not expose
batch or fast-cancel bodies.

## Validation Failure

All named options require explicit values. A CLI validation error means no
platform request was sent. Surface the error and do not silently delete an
option, guess a missing value, change the order type, or fall back to a raw
payload. If the corrected order parameters differ from the confirmed action,
show the complete corrected action and obtain confirmation again.
