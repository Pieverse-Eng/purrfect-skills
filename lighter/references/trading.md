# Trading — orders, cancel, modify, leverage, margin

`order`, `place-orders`, `bracket-order`, `cancel`, `cancel-all`, `modify`, `update-leverage`,
and `update-margin` are account-changing. Follow the Confirmation Contract in
`SKILL.md`.

`order-preview` is non-mutating: it only computes. No execution confirmation.

Trading integration must be enabled and `account.status` should be `ready`
before writes. Complete
[Transaction Fee Authorization](../SKILL.md#transaction-fee-authorization)
first when required.

## Inspect orders and activity

```bash
purr lighter orders            # same as active-orders
purr lighter active-orders     # live working orders only
purr lighter inactive-orders   # completed / inactive — not returned by orders
purr lighter trades [--market <SYM> --market-type <t>] [--limit <n>]
purr lighter positions
purr lighter limits
```

**`orders` ≡ `active-orders`.** Neither is a full history. Use `inactive-orders`
and `trades` for past activity. Large `order-index` values are decimal integer
strings (may exceed JS safe integer range) — pass them through unchanged as
strings.

## Place an order

```bash
purr lighter order \
  (--market-id <id> | --market <symbol> --market-type perp|spot) \
  --side buy|sell \
  --size <amount> \
  --price <price> \
  [--type limit|market|stopLoss|stopLossLimit|takeProfit|takeProfitLimit|twap] \
  [--time-in-force ioc|gtt|postOnly] \
  [--reduce-only true|false] \
  [--trigger-price <price>] \
  [--client-order-index <n>] \
  [non-IOC only: --expires-in <duration> | --expires-at <iso> | --order-expiry <unix-ms>]
```

`place-orders` takes the same flags and submits **one** order via `/orders`. It
is not a multi-leg batch. For independent orders, issue separate confirmed
commands. For an entry with attached TP/SL, use the linked group below.

### Price is required — including market orders

`order` / `place-orders` require a positive `price` for every order type. For
`market` orders, price is the **worst acceptable fill** (slippage bound):

- Buy market → highest price you accept
- Sell market → lowest price you accept

Derive it from the book for the **exact size**:

```bash
purr lighter order-book-depth --market <SYM> --market-type <t> --limit 100
```

1. Walk cumulative depth on the hit side.
2. Compute projected VWAP and the worst level reached.
3. If depth cannot fill the size, stop and ask the user to resize.
4. If the user gave no slippage tolerance, present touch / VWAP / worst level
   and ask for an exact cap. **Never invent a default buffer.**
5. Put the bound and bps distance from touch and VWAP in the confirmation.

Never describe the bound as “the price you will pay” — it is the worst price
you tolerate.

### Size and precision

Use `sizeDecimals`, `priceDecimals` and `limits` from the platform tools when
they returned the market; otherwise resolve it:

```bash
purr lighter market --market <SYM> --market-type <t>
```

Round size and price to market decimals. Decimal / range errors mean fix inputs,
not blind retry:

- `LIGHTER_DECIMAL_INVALID` / `LIGHTER_DECIMAL_PRECISION_UNSUPPORTED`
- `LIGHTER_AMOUNT_OUT_OF_RANGE` / `LIGHTER_PRICE_OUT_OF_RANGE`

`1000`-prefixed markets are per-1000 units of the underlying (see
[symbols.md](symbols.md)).

### Time in force and expiry

| Order type | Default TIF |
| --- | --- |
| `market`, `stopLoss`, `takeProfit` | `ioc` |
| `limit`, `stopLossLimit`, `takeProfitLimit`, `twap`, or omitted type | `gtt` |

Constraints:

- Market and stop-loss/take-profit (non-limit) require `ioc`
- `twap` requires `gtt`
- IOC **market** and **limit** orders reject all expiry flags
- Expiry flags are mutually exclusive: `--expires-in` | `--expires-at` |
  `--order-expiry`
- `--expires-in` units: `ms|s|m|h|d|w` (for example `30m`, `24h`, `7d`)
- `--expires-at` must include `Z` or an explicit offset
- Explicit expiry must be in the future and ≤ **30 days**

`postOnly` rejects takes — use only when the user wants maker-only.

### Order preview

Body-only (flags above are **not** accepted on this command):

```bash
purr lighter order-preview --body-json '{"marketId":12,"side":"buy","type":"limit","size":"1","price":"100"}'
```

Never present a preview result as a live order.

## Entry with attached TP/SL

Use `bracket-order` for a non-reduce-only perpetual entry with linked-size,
opposite-side, reduce-only SL-limit and TP-limit exits. Resolve market precision,
inspect positions, and confirm the complete group under the Confirmation Contract.

```bash
purr lighter bracket-order \
  --market <SYM> --market-type perp \
  --side buy|sell --size <size> --price <entry-limit> \
  --stop-loss-trigger <trigger> --stop-loss-price <limit> \
  --take-profit-trigger <trigger> --take-profit-price <limit> \
  --expires-in <duration>
```

For Market/IOC entry, replace `--price` with `--type market --slippage-bps <bps>`
(integer, 0–9999). Obtain explicit slippage approval; the gateway bounds a fresh
quote. Unfilled quantity is canceled.

- For buys: SL trigger < entry < TP trigger; exit limits ≤ triggers. Reverse
  for sells. Market quote and bound must both fit between triggers. Never invent buffers.
- Explicit expiry applies to both exits and any GTT entry, regardless of fill
  time. Stop-limit exits can trigger without filling.
- Submit once; never substitute standalone orders or an unprotected entry.
  If unsupported, stop.
- Keep request/transaction IDs. Verify fills, linked protection, parameters, and
  expiry; distinguish pending, partial, and filled states. Recheck after position
  changes and reconcile uncertain submissions before retrying.

## Cancel and modify

```bash
purr lighter cancel (--market-id <id> | --market <SYM> --market-type <t>) --order-index <id>
purr lighter cancel-all [--time-in-force immediate|scheduled|abortScheduled] [--time <unix-ms>]
purr lighter modify (--market-id <id> | --market <SYM> --market-type <t>) \
  --order-index <id> --size <amount> --price <price> [--trigger-price <price>]
```

- Refresh `active-orders` before cancel/modify; do not invent order indexes.
- Pass large indexes as exact decimal strings.
- Confirm each cancel/modify (or a clearly enumerated cancel-all).

## Read the write result

`order`, `place-orders`, `cancel` and `modify` answer after Lighter has
executed the transaction (a wait of up to about 2 s), not on submission.
`status: succeeded` only means the submission was accepted. Report from
`executionStatus`, `orderStatus` and `executionError`:

| Response | Meaning | Report |
| --- | --- | --- |
| `executionStatus: succeeded`, `orderStatus: open` or `pending` | The order is working (`pending`: a trigger order waiting) | Placed. Keep `orderIndex` (an exact string) for cancel/modify |
| `executionStatus: succeeded`, `orderStatus: filled` | Filled | Filled; take amounts from `trades` |
| `executionStatus: succeeded`, `orderStatus: canceled-*` | Part filled, the rest cancelled | Partial fill; take amounts from `trades` |
| `executionStatus: failed`, `orderStatus: canceled-*` | The matching engine cancelled it unfilled | Not placed, and why: `canceled-post-only` (would have taken), `canceled-not-enough-liquidity` (IOC with nothing to match), `canceled-invalid-balance`, `canceled-margin-not-allowed`, `canceled-too-much-slippage`, ... |
| `executionStatus: succeeded` on `cancel` / `modify` | Lighter applied it | Cancelled / modified |
| `executionStatus: pending` or `unknown` | Not executed within the wait | No outcome yet: `purr lighter request-status --request-id <actionRequestId>`, then `active-orders` |
| Error `LIGHTER_TRANSACTION_FAILED` | Lighter executed the transaction and refused it | Nothing changed; see [errors.md](errors.md) |

`cancel-all`, `bracket-order`, `update-leverage` and `update-margin` still
answer on submission: verify them with orders and positions.

## Leverage and margin

```bash
purr lighter update-leverage \
  (--market-id <id> | --market <SYM> --market-type perp) \
  (--leverage <n> | --initial-margin-fraction <n>) \
  [--margin-mode cross|isolated]

purr lighter update-margin \
  (--market-id <id> | --market <SYM> --market-type perp) \
  --amount <amount> --direction add|remove
```

- Leverage path is **perp only**. Pass either `--leverage` or
  `--initial-margin-fraction`.
- Omitting `--margin-mode` applies `cross`; that is CLI behavior, not the
  user's choice. When the user has not chosen cross or isolated, ask, and pass
  the chosen `--margin-mode` explicitly.
- Margin `amount` is a positive decimal string; direction is `add` or `remove`.
- Prefer one combined confirmation when a leverage change immediately precedes
  its order (see Confirmation Contract). Execute leverage first.

## Suggested order workflow

Silent preparation:

1. Readiness `enable`, `open_account` and `approve_fee` steps: when complete,
   skip `status`, `account` and `partner-fee-status`; otherwise run them, enable
   (confirmed), open or wait, and obtain fee consent then
   `approve-partner-fee` (confirmed).
2. Market precision and limits from the platform tools (or `market`), then
   `order-book-depth` and `positions` / `balances`.
3. User confirmation with full parameters.
4. `order` (or leverage then `order`).
5. Report from `executionStatus` / `orderStatus` (see
   [Read the write result](#read-the-write-result)) and verify amounts with
   `active-orders` / `trades` / `positions` — never claim a fill from `status:
   succeeded` alone. Report results and links following
   [Result Reporting](../SKILL.md#result-reporting).

## Idempotency and recovery

The CLI does **not** send client idempotency keys. The platform assigns
operation ids for writes. After timeout or `LIGHTER_SUBMIT_UNKNOWN`:

```bash
purr lighter requests --limit 10
purr lighter request-status --request-id <id>
purr lighter active-orders
purr lighter positions
```

Do not resubmit the same order to “fix” an unknown. See [errors.md](errors.md).
