---
name: dflow-platform-fees
description: Collect a builder fee on DFlow trades via `platformFeeBps` or `platformFeeScale`. Use when the user asks how to take a cut, add a builder fee, or what `platformFeeBps` / `platformFeeScale` means. Do NOT use to run the trade itself.
disable-model-invocation: true
user-invocable: false
---

# DFlow Platform Fees

Builder→user fee on a DFlow trade, paid to a builder-controlled token account
on success. Put these fields in `--params-json` on `purr dflow order`.

## Two models

### Fixed — `platformFeeBps`

Flat bps (1 bps = 0.01%). Works on **spot and PM**. The only option for spot.

### Dynamic — `platformFeeScale` (PM outcome tokens only)

```
fee = k * p * (1 - p) * c
```

- `k` = `platformFeeScale`, 3-decimal (`50` → 0.050)
- `p` = all-in price, 0–1
- `c` = contract size
- Paid in the settlement mint (USDC or CASH)

Peaks at `p = 0.5`, zero at 0 and 1, **nothing at redemption** (`p = 1`).
Not available on spot.

Example: `k = 50`, 100 YES at `p = 0.40` →
`0.050 * 0.40 * 0.60 * 100 = 1.20` USDC.

## Parameters

- `platformFeeBps` — fixed fee in bps
- `platformFeeScale` — dynamic coefficient, PM only
- `platformFeeMode` — `outputMint` (default) or `inputMint`
- `feeAccount` — existing SPL token account that receives the fee. DFlow
  will not create it.

| Trade type | Allowed `platformFeeMode` |
|---|---|
| Spot | `inputMint` or `outputMint` |
| PM outcome-token trades | Always settlement mint, regardless of what you pass |

One ATA per collected token, owned by the builder, already created. PM fees
need a USDC or CASH ATA.

## Missing pieces

1. Spot, PM, or both — scopes the model.
2. Rate — bps or `k`.
3. Collection token(s) and whether the matching ATA already exists.

## Gotchas

- Do not set `platformFeeBps` unless you are actually collecting. A declared
  but unused fee still eats slippage budget.
- Dynamic fees are 0 at redemption. There is no "cut on redeem" knob.
- `platformFeeScale` is not valid on spot.
- On PM, `platformFeeMode: "inputMint"` does not collect in the input token.
- Failed / cancelled trades charge no fee.

These are not DFlow's own PM trading fees (the
`roundup(0.07 × c × p × (1 − p))` schedule). Do not mix them.

## Sibling skills

- `dflow-spot-trading` — base spot order; layer these params on top
- `dflow-kalshi-trading` — base PM order; layer these params on top
