# Order Wire Format

Hyperliquid order, modify, and cancel bodies use the venue wire shape. The
platform validates this JSON strictly: only documented fields are allowed, and
unknown keys are rejected. Build it carefully; do not invent fields.

Limits: up to **100** entries in `orders` or `cancels` per request.

For ordinary single actions, pass a complete compact payload directly:

```bash
purr hyperliquid order --body-json '{"orders":[{"a":0,"b":true,"p":"100000","s":"0.001","r":false,"t":{"limit":{"tif":"Gtc"}}}],"grouping":"na"}'
```

The top-level `orders` wrapper is required. Build and validate the complete
payload before requesting confirmation. Use `--body-file` only for genuinely
large batches at a known writable workspace path; never attempt to create it
under `/tmp` with file-writing tools.

## Place Order Body

```json
{
  "orders": [
    {
      "a": 0,
      "b": true,
      "p": "100000",
      "s": "0.001",
      "r": false,
      "t": { "limit": { "tif": "Gtc" } }
    }
  ],
  "grouping": "na"
}
```

### Order fields

| Field | Type | Meaning |
| --- | --- | --- |
| `a` | integer | Asset id from `purr hyperliquid symbol` (`assetId`) |
| `b` | boolean | `true` = buy / long, `false` = sell / short |
| `p` | decimal string or number | Limit or reference price (venue tick size; do not invent extra decimals) |
| `s` | decimal string or number | Size in **asset units** (not USD); max precision = `szDecimals` |
| `r` | boolean | Reduce-only when `true` |
| `t` | object | Order type: `limit` or `trigger` |
| `c` | optional string | Client order id: `0x` + exactly **32** hex characters (34 chars total) |

Size is coin size (e.g. `0.01` ETH), not notional USD. Convert from a dollar
amount only with an explicit mid/mark price and show both to the user before
confirming.

### Limit type

```json
"t": { "limit": { "tif": "Gtc" } }
```

Allowed `tif` values: `Gtc`, `Ioc`, `Alo`, `FrontendMarket`.

- `Gtc` — good til cancel limit
- `Ioc` — immediate or cancel (aggressive / market-like when priced through book)
- `Alo` — add liquidity only
- `FrontendMarket` — venue frontend market style (use only when appropriate)

### Trigger type (TP / SL)

```json
"t": {
  "trigger": {
    "isMarket": true,
    "triggerPx": "95000",
    "tpsl": "sl"
  }
}
```

- `tpsl`: `tp` or `sl`
- `triggerPx`: trigger price
- `isMarket`: whether the triggered order is market-style

### Grouping

| Value | Meaning |
| --- | --- |
| `na` | Default / no special grouping |
| `normalTpsl` | Normal take-profit / stop-loss grouping |
| `positionTpsl` | Position TP/SL grouping |
| `{ "p": <n> }` | Position-linked grouping (`p` is a non-negative integer) |

`grouping` is optional on the request; when omitted the platform defaults to
`na`. Prefer explicit `"grouping": "na"` for simple orders.

## Examples

### Limit buy (GTC)

```json
{
  "orders": [
    {
      "a": 0,
      "b": true,
      "p": "3000",
      "s": "0.01",
      "r": false,
      "t": { "limit": { "tif": "Gtc" } }
    }
  ],
  "grouping": "na"
}
```

### Aggressive IOC sell (reduce-only close)

```json
{
  "orders": [
    {
      "a": 0,
      "b": false,
      "p": "2900",
      "s": "0.01",
      "r": true,
      "t": { "limit": { "tif": "Ioc" } }
    }
  ],
  "grouping": "na"
}
```

### With client order id

```json
{
  "orders": [
    {
      "a": 0,
      "b": true,
      "p": "3000",
      "s": "0.01",
      "r": false,
      "t": { "limit": { "tif": "Gtc" } },
      "c": "0x00000000000000000000000000000001"
    }
  ],
  "grouping": "na"
}
```

Use a unique valid cloid when the user wants cancel-by-cloid later. Do not reuse
cloids carelessly.

## Cancel Body

```json
{
  "cancels": [
    { "a": 0, "o": 123456789 }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `cancels[].a` | Asset id (integer) |
| `cancels[].o` | Order id / oid (non-negative integer only; not a cloid) |
| `f` | Optional **top-level** field; when present must be boolean `true` (fast cancel). Do not put `f` inside each cancel entry |

```bash
purr hyperliquid cancel --body-json '{"cancels":[{"a":0,"o":123456789}]}'
# optional fast cancel:
purr hyperliquid cancel --body-json '{"cancels":[{"a":0,"o":123456789}],"f":true}'
```

## Cancel By Cloid Body

```json
{
  "cancels": [
    {
      "asset": 0,
      "cloid": "0x00000000000000000000000000000001"
    }
  ]
}
```

```bash
purr hyperliquid cancel-by-cloid --body-json '{"cancels":[{"asset":0,"cloid":"0x00000000000000000000000000000001"}]}'
```

## Modify Body

```json
{
  "oid": 123456789,
  "order": {
    "a": 0,
    "b": true,
    "p": "3010",
    "s": "0.01",
    "r": false,
    "t": { "limit": { "tif": "Gtc" } }
  }
}
```

- `oid` may be a numeric oid, digit string, or cloid (`0x` + 32 hex).
- Optional `"a": true` on the modify body means always-place when supported.

```bash
purr hyperliquid modify --body-json '{"oid":123456789,"order":{"a":0,"b":true,"p":"3010","s":"0.01","r":false,"t":{"limit":{"tif":"Gtc"}}}}'
```

## Build Checklist

1. Trading integration enabled (`status`) and order fee preflight done when
   placing orders
2. `symbol` → `assetId` (`a`), `szDecimals`, canonical `coin`
3. Size string does not exceed `szDecimals`
4. Side `b` matches user intent (buy/sell)
5. Price `p` from user or recent book/mid — do not invent a “market” without a
   typed TIF/trigger
6. Set `r: true` for reduce-only closes
7. Do not mix perpetual and spot `a` values in one batch
8. Validate the complete wrapper → confirm → run with `--body-json`
9. Verify with `order-status` or `orders`

## Anti-Patterns

- Guessing `a` from “ETH is usually 0”
- Extra size decimals beyond `szDecimals`
- Claiming market orders without using an allowed `t` form
- Omitting the top-level `orders` or `cancels` wrapper
- Writing payload files under protected paths such as `/tmp`
- Pasting genuinely large batch JSON inline when a writable workspace file is safer
- Reusing the same cloid for unrelated orders
