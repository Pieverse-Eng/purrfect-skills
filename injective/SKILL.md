---
name: injective
description: Use when querying Injective markets or account state.
version: 1.0.0
---

# Injective

Use `purr injective` for read-only Injective mainnet markets and the current
Agent's account. Platform credentials select the instance and wallet; never
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
| Missing capability, unavailable data, stale data or pagination error | [Errors](references/errors.md) |

Market discovery belongs to `discover_markets`; use its exact Injective market
hash and product when available. Same labels do not establish identical assets.
Keep exact denoms, decimal strings, source times, completeness and opaque cursors.
Explain null as unknown and stale as historical. Only a successful fresh empty
collection establishes no rows within that query's coverage.

This phase cannot place/cancel/close orders, set protection, accept RFQs, enable
trading, deposit or withdraw. For an execution request, explain that Injective
execution is unavailable and stop. Do not bypass it with wallet raw transactions,
direct SDK/REST writes, another venue, or a new MCP server.

Reads require no confirmation, account opening or INJ gas. The account is the
existing wallet's default subaccount 0. Future transactions require user-funded
native INJ; the platform does not sponsor gas. Wallet funding alone does not
establish available margin or execution permission.
