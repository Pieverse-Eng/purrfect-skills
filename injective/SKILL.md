---
name: injective
description: Use when querying or trading Injective perpetuals, managing native orders or protection, or requesting and accepting Injective RFQ quotes.
version: 1.1.0
---

# Injective

Use `purr injective` for Injective mainnet markets and the current Agent's account. Platform credentials select the instance and wallet; never
request a private key, import another wallet, or select an arbitrary address.

Check installed capability once before the first query:

```sh
purr injective --help
```

Requires purr CLI v0.2.70 or a later release with the Injective group. If the
group is unknown, report that the installed CLI needs an upgrade. Backend capability errors
are separate; see [errors](references/errors.md).

| Request | Read first |
| --- | --- |
| Markets, exact market, depth, recent trades or candles | [Market data](references/market-data.md) |
| Balances, positions, open orders, order history or fills | [Account](references/account.md) |
| Open/close, cancel, replace, margin or TP/SL | [Native trading](references/trading.md) |
| RFQ comparison, contract authorization, acceptance or revocation | [RFQ](references/rfq.md) |
| Missing capability, unavailable data, stale data or pagination error | [Errors](references/errors.md) |

Market discovery belongs to `discover_markets`; use its exact Injective market
hash and product when available. Same labels do not establish identical assets.
Keep exact denoms, decimal strings, source times, completeness and opaque cursors.
Explain null as unknown and stale as historical. Only a successful fresh empty
collection establishes no rows within that query's coverage.

## Execution capability and confirmation

Reads ship in CLI v0.2.70. Native writes require the later CLI candidate containing
`readiness`, `management`, `protection` and `rfq` plus enabled backend routes.
Inspect installed help; never invent a released minimum version. If an installed
command is missing or readiness disables the action, report the blocker and stop.
Do not bypass it with wallet raw transactions, direct SDK/REST writes or an MCP.
Spot reads remain supported; this execution candidate is USDC perpetuals only.

Follow the relevant reference before acting. Produce the local business draft
first (the default, with no HTTP), and summarize market, side, size, margin,
worst/limit/trigger prices, explicitly affected order hashes, USDC fee allowance
and the INJ gas ceiling. Ask for confirmation of that unchanged action before
adding `--execute true`, current `--wallet-generation` and one original
`--idempotency-key`. Initial intent to trade does not approve a later changed
quote, price, size, fee, cancellation scope or contract authorization.
An already explicit instruction approving those exact parameters is sufficient;
do not ask again for the same unchanged action.

RFQ authorization is a separate action with separate consent because it grants
broad contract permissions. Never combine an authorization and a later quote
acceptance into an automatic sequence. A policy hold is still pending; a
submitted transaction is still not a fill. Unknown results must recover the
original request, never retry with a new key. See [errors](references/errors.md).

Reads require no confirmation, account opening or INJ gas. The account is the
existing wallet's default subaccount 0. Transactions require user-funded
native INJ; the platform does not sponsor gas. Wallet funding alone does not
establish available margin or execution permission.
