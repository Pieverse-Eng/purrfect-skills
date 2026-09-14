# Trading Account Commands

Command reference for orders, fills, leverage, and scheduled cancellation.
For execution order and required preparation, use [workflows.md](workflows.md).
Order placement and modification syntax lives in
[order-commands.md](order-commands.md). Authorization follows
[SKILL.md](../SKILL.md#confirmation-contract).

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

## Leverage

```bash
purr hyperliquid update-leverage --asset <asset-id> --is-cross true|false --leverage <1-50>
```

- `--asset` is the resolved `assetId`.
- `--is-cross true` means cross margin; `false` means isolated.
- Apply the Confirmation Contract in [SKILL.md](../SKILL.md).
- If the venue rejects a change with open exposure, report it and stop.

## Dead-Man Switch

```bash
purr hyperliquid schedule-cancel --time <unix-ms>
purr hyperliquid schedule-cancel
```

With `--time`, schedule a venue cancel-all. Without it, clear the existing
schedule; it does not schedule a new one. Confirm which action the user wants.

## Cancel Commands

See [order-commands.md](order-commands.md#cancel) for exact cancel syntax.
Use an exact verified open target; apply [workflows.md](workflows.md#cancel-an-order).
