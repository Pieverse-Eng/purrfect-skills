# Trading

Use the parameterized `purr hyperliquid` commands for the complete order
lifecycle. Inspect status freely; confirm every action that changes orders,
positions, or leverage. Read [order-commands.md](order-commands.md) before
placing, protecting, modifying, or cancelling orders.

Trading integration must be enabled first (see
[preflight.md](preflight.md)). Exchange commands fail with
`HYPERLIQUID_TRADING_DISABLED` when it is off.

## Inspect Orders, Fills, and Positions

```bash
purr hyperliquid state [--kind perp|spot|both] [--dex <dex>]
purr hyperliquid orders [--kind open|frontend|historical] [--dex <dex>]
purr hyperliquid fills [--start-time <ms>] [--end-time <ms>] [--aggregate-by-time true|false] [--reversed true|false]
purr hyperliquid order-status --oid <oid-or-cloid>
```

| Command | Purpose |
| --- | --- |
| `state` | Current positions and balances; positions do not have OIDs |
| `orders --kind frontend` | Current open orders with frontend TP/SL relationship fields and child OIDs |
| `orders --kind open` | Basic current open-order list; `open` is the default |
| `orders --kind historical` | Filled, cancelled, and other historical orders |
| `fills` | Recent or time-ranged fills, including their source order IDs |
| `order-status` | Exact status for one numeric OID or cloid |

`--dex` on `orders` applies to `open` and `frontend` only. Historical orders
are account-wide. For `fills`, `--start-time` is required when `--end-time` or
`--reversed` is provided.

An open entry order and a resulting position are different objects:

- An unfilled entry remains open and may be modified or cancelled by OID.
- A filled entry is historical and cannot be modified. Its result is a
  position, which has no OID.
- For a partially filled entry, its OID controls only the open remainder. The
  filled amount must be managed as a position.
- Add protection to an existing position with `stop-loss`, `take-profit`, or
  `protect-position`. Modify existing protection by its open child OID.

## Place Order Workflow

Run preparatory queries silently. The first user-facing message should be a
required fee/collateral confirmation, an actionable ambiguity/error, or the
final trade confirmation.

1. Ensure trading is enabled (`status`; confirm then `enable` if needed).

2. Resolve the exact market:

```bash
purr hyperliquid symbol --coin <coin> [--dex <dex>]
```

Use its canonical `coin`, `assetId`, and `szDecimals`. If resolution is
ambiguous, present the candidates and wait for the user's selection.

3. Check positions and collateral. For a non-default dex, query both accounts:

```bash
purr hyperliquid state --kind both
purr hyperliquid state --kind both --dex <target-dex>
```

Only the target dex's available collateral funds its order.

4. Before every order-placement command, check fee authorization:

```bash
purr hyperliquid builder-fee-status
```

Follow **Order Fee Preflight** in [preflight.md](preflight.md) when approval is
required. Do this before leverage or collateral changes for the order.

5. Check price context, required margin, size precision, and trigger direction:

```bash
purr hyperliquid prices [--dex <dex>]
purr hyperliquid l2 --coin <canonical-coin>
```

Do not submit an order to discover whether collateral is sufficient. If a
builder dex is short and the default account can fund it, confirm
`send-asset` separately and re-read both states.

6. Select the command by intent:

- Ordinary limit, reduce-only exit, or explicitly bounded FrontendMarket:
  `limit-order`.
- New entry with attached TP and SL: `bracket-order`.
- Existing position with one trigger: `stop-loss` or `take-profit`.
- Existing position with both triggers: `protect-position`.

Never represent a requested stop-loss or take-profit as a plain
`limit-order`. For market trigger execution, require and confirm the explicit
worst price described in [order-commands.md](order-commands.md).

7. If leverage must change, include it in the same final trade confirmation:

```bash
purr hyperliquid update-leverage \
  --asset <asset-id> \
  --is-cross true|false \
  --leverage <1-50>
```

8. Confirm the complete action: market and `assetId`, side/position side, asset
size, entry/limit price and TIF, every trigger, every worst/limit execution
price, reduce-only behavior, approximate notional, and leverage/margin change.
For `bracket-order` or `protect-position`, one confirmation covers the legs
because they are one CLI action, but every leg must appear in the summary.

9. After confirmation, apply a confirmed leverage change first. Place the
already confirmed typed order only if leverage succeeds. Do not alter arguments
in response to a validation error.

10. Reconcile:

```bash
purr hyperliquid orders --kind frontend [--dex <dex>]
purr hyperliquid order-status --oid <oid-or-cloid>
purr hyperliquid fills
purr hyperliquid state --kind perp [--dex <dex>]
```

Use OIDs returned by submission or found in the order lists. A result may
contain `replayed: true` when the platform returns a prior identical request;
treat it as already submitted and do not resend. Do not claim a fill until
status, fills, or state proves it.

## Protect an Existing Position

1. Resolve the market and read current perp state.
2. Verify the actual non-zero position side and absolute current size.
3. Read current price context. Stop if a proposed trigger is already crossed
   or would fire immediately.
4. Run fee preflight.
5. Confirm the position, size, TP/SL triggers, execution mode, and
   worst/limit prices.
6. Submit `protect-position` for paired market protection or the matching
   individual trigger command.
7. Use `orders --kind frontend` to capture and verify each new child OID.

The historical entry OID is useful for audit only; it is not needed to add
position protection.

## Modify Workflow

1. Find the exact open target:

```bash
purr hyperliquid orders --kind frontend [--dex <dex>]
purr hyperliquid order-status --oid <oid-or-cloid>
```

2. Confirm that it is still open and identify whether it is an ordinary limit,
   stop-loss, or take-profit. Do not infer the target from coin alone.
3. Reconstruct the complete replacement order from the current order plus the
   requested change. Modify commands are not partial patches.
4. Confirm the exact target OID and all replacement fields.
5. Run the matching `modify-limit-order`, `modify-stop-loss`, or
   `modify-take-profit`.
6. Re-read `frontend` orders or `order-status`.

If the entry has filled, stop trying to modify it. Create or modify protection
for the resulting position instead.

## Cancel Workflow

1. Find and verify the exact open order as above.
2. Confirm the market, asset ID, order type, and numeric OID or cloid.
3. Run one typed cancel:

```bash
purr hyperliquid cancel --asset <asset-id> --oid <numeric-oid>
purr hyperliquid cancel-by-cloid --asset <asset-id> --cloid <cloid>
```

4. Re-list open/frontend orders or query `order-status`.

The CLI does not expose raw, batch, or fast-cancel payloads.

## Leverage

```bash
purr hyperliquid update-leverage --asset <asset-id> --is-cross true|false --leverage <1-50>
```

- `--asset` is the resolved `assetId`.
- `--is-cross true` means cross margin; `false` means isolated.
- Confirm before running.
- If the venue rejects a change with open exposure, report it and stop.

## Dead-Man Switch

```bash
purr hyperliquid schedule-cancel --time <unix-ms>
purr hyperliquid schedule-cancel
```

With `--time`, schedule a venue cancel-all. Without it, clear the existing
schedule; it does not schedule a new one. Confirm which action the user wants.

## Confirmation Summary

```text
Action: place | protect | modify | cancel | update leverage | …
Market: <coin> (assetId=<n>)
Target OID/cloid (modify/cancel): …
Side / position side / size: …
Entry or limit price and TIF: …
TP/SL trigger and worst/limit execution prices: …
Reduce-only behavior: …
Leverage / margin (if changed): …
Collateral notes: …
Network: Hyperliquid mainnet

Do you want to execute this Hyperliquid action with these parameters? (Yes/No)
```

Omit irrelevant fields, but never omit a field that controls order execution.

## Safety

- Never invent asset IDs, OIDs, price ticks, size precision, or missing order
  fields.
- Never switch between plain limit and trigger commands to work around an
  error.
- Use reduce-only for a requested close/reduction so the order cannot flip the
  position.
- Stop on insufficient margin and show funding or size choices.
- After partial success or an unknown submission outcome, reconcile before any
  retry. Do not resubmit the entire multi-leg action blindly.
- Do not mix perpetual and spot legs in one request.
