# Trading

Order lifecycle through `purr hyperliquid`. Inspect status freely. Confirm
every action that changes orders, positions, or leverage. Always resolve
`assetId` first — see
[order-wire-format.md](order-wire-format.md) for the raw order JSON schema.

Trading integration must be enabled first (see
[preflight.md](preflight.md)). Exchange commands fail with
`HYPERLIQUID_TRADING_DISABLED` when it is off.

## Inspect Orders and Fills

```bash
purr hyperliquid orders [--kind open|frontend|historical] [--dex <dex>]
purr hyperliquid fills [--start-time <ms>] [--end-time <ms>] [--aggregate-by-time true|false] [--reversed true|false]
purr hyperliquid order-status --oid <oid-or-cloid>
```

| Command | Purpose |
| --- | --- |
| `orders` | Open / frontend / historical orders; `--kind` defaults to `open` |
| `fills` | User fills; with `--start-time` uses time-range API; without it returns recent fills |
| `order-status` | Status for a numeric oid or cloid (`0x` + exactly 32 hex chars) |

Notes:

- `--dex` on `orders` applies to `open` and `frontend` only. `historical`
  ignores `--dex`.
- For `fills`, `--start-time` is required when `--end-time` or `--reversed` is
  set. `--aggregate-by-time` and `--reversed` accept `true`/`false` (also
  `1`/`0`/`yes`/`no`).

## Change Orders and Leverage

```bash
purr hyperliquid order --body-json '<json>'        # or --body-file <path>
purr hyperliquid modify --body-json '<json>'
purr hyperliquid cancel --body-json '<json>'
purr hyperliquid cancel-by-cloid --body-json '<json>'
purr hyperliquid update-leverage --asset <asset-id> --is-cross true|false --leverage <1-50>
purr hyperliquid schedule-cancel [--time <ms>]
```

Pass **either** `--body-json` or `--body-file`, never both. Prefer compact
`--body-json` for an ordinary single action. Reserve `--body-file` for large
batches at a known writable workspace path; never write these payloads under
`/tmp` with file-writing tools.

## Place Order Workflow

Run preparatory queries silently. Do not tell the user that checks are starting
or list the internal execution plan. The first message should be a required fee
or collateral confirmation, an actionable ambiguity/error, or the final trade
confirmation that includes any leverage change.

0. Ensure trading is enabled (`status`; confirm → `enable` if needed).

1. Resolve the market:

```bash
purr hyperliquid symbol --coin <coin> [--dex <dex>]
```

2. Check collateral and positions. For a non-default dex, query both the
   default account and the resolved target dex:

```bash
purr hyperliquid state --kind both
purr hyperliquid state --kind both --dex <target-dex>
```

Use the target dex's `withdrawable` / available collateral when deciding
whether the order is funded. Never count default perp collateral as available
to a non-default dex.

3. For **every** order (perpetual or spot), check fee authorization before any
   account-changing preparation or order confirmation:

```bash
purr hyperliquid builder-fee-status
```

Follow **Order Fee Preflight** in [preflight.md](preflight.md) if the result
is `approval_required`.

4. Before leverage or order submission, estimate required margin from the
   intended size, current price, and leverage. For a non-default dex, if the
   target dex lacks enough collateral but the default account has enough,
   confirm a `send-asset` transfer, execute it, and re-read both balances. If
   total free collateral is insufficient, stop and report the shortfall. Do
   not submit an order to test whether collateral is sufficient.

5. If leverage must change, include it in the final trade confirmation rather
   than asking separately. Fee or collateral confirmation does not authorize
   leverage:

```bash
purr hyperliquid update-leverage --asset <assetId> --is-cross true --leverage 5
```

6. Optional: refresh price context:

```bash
purr hyperliquid prices [--dex <dex>]
purr hyperliquid l2 --coin <canonical-coin>
```

7. Build the complete wire-format body in memory using `assetId` and
   `szDecimals` (see [order-wire-format.md](order-wire-format.md)). Validate
   that an order request contains the top-level `orders` array and `grouping`
   before asking for confirmation. Do not mix perpetual and spot assets in one
   batch.

8. Confirm with the user: market, side, size, price/TIF or trigger, reduce-only,
   leverage/margin mode if changed, approximate notional. State clearly that
   the confirmed workflow will set leverage first and then submit the order.

9. After yes, if leverage is changing, run `update-leverage` first. Continue
   only when it succeeds; otherwise report the error and do not submit the
   order. Then place the already confirmed order:

```bash
purr hyperliquid update-leverage --asset <assetId> --is-cross <true|false> --leverage <n>
purr hyperliquid order --body-json '{"orders":[{"a":0,"b":true,"p":"3000","s":"0.01","r":false,"t":{"limit":{"tif":"Ioc"}}}],"grouping":"na"}'
```

Skip `update-leverage` when no change is needed. Replace every example value
with the already confirmed leverage and order. Do not expose payload
construction, file writes, validation retries, or CLI invocation to the user.

10. Reconcile. Prefer `orders --kind open` first. Use `order-status` only when
   you have an oid from the submit `response` or from the open-order list (or a
   cloid you set on the order). Order results may also include `replayed: true`
   when the platform returned a prior identical request — treat as already
   submitted, do not re-send.

```bash
purr hyperliquid orders --kind open [--dex <dex>]
purr hyperliquid order-status --oid <oid-or-cloid>
purr hyperliquid state --kind perp [--dex <dex>]
```

Do not report a fill unless status, fills, or state shows it.

## Cancel / Modify Workflow

1. List open orders if the user did not supply oid/cloid:

```bash
purr hyperliquid orders --kind open [--dex <dex>]
```

2. Build cancel or modify JSON (see wire format doc).
3. Confirm → run `cancel`, `cancel-by-cloid`, or `modify`.
4. Re-list open orders or `order-status`.

## Leverage

```bash
purr hyperliquid update-leverage --asset 0 --is-cross true --leverage 10
```

- `--asset` is the same `assetId` from symbol resolution.
- `--is-cross true` = cross margin; `false` = isolated.
- `--leverage` integer `1`–`50`.
- Confirm before running. If the venue rejects leverage changes with open
  positions, report the error and stop.

## Dead-Man Switch

```bash
purr hyperliquid schedule-cancel --time <unix-ms>
purr hyperliquid schedule-cancel
```

- With `--time <unix-ms>`: schedule a venue cancel-all at that time (dead-man).
- Without `--time`: send `{}`, which clears any existing scheduled cancel (does
  **not** schedule a new one).

Confirm which of those two the user wants before running.

## Confirmation Summary Template

```text
Action: place order | modify | cancel | update leverage | …
Market: <coin> (assetId=<n>)
Side / size / price (or amount): …
TIF or trigger: …
Reduce-only: yes|no
Leverage / margin (if set): …
Collateral notes: …
Network: Hyperliquid mainnet

Do you want to execute this Hyperliquid action with these parameters? (Yes/No)
```

## Safety

- Never invent `assetId`, price ticks, or size decimals.
- Prefer reduce-only (`r: true`) when the user asks to close or reduce a
  position without flipping.
- Stop on insufficient margin; show `state` and funding options instead of
  retrying larger risk.
- After `HYPERLIQUID_API_PARTIAL_SUCCESS`, reconcile with order and state
  checks; do not resubmit the same batch blindly.
- Never mix perpetual and spot orders in one request.
