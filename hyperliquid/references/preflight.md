# Preflight / Account

Use these commands before trading, funding, or explaining balances.

## Commands

```bash
purr hyperliquid status
purr hyperliquid snapshot
purr hyperliquid enable
purr hyperliquid disable
purr hyperliquid account
purr hyperliquid state [--kind perp|spot|both] [--dex <dex> | --all-dexs]
purr hyperliquid builder-fee-status
purr hyperliquid approve-builder-fee
purr hyperliquid abstraction
purr hyperliquid set-abstraction --mode disabled|unifiedAccount|portfolioMargin
```

| Command | Purpose |
| --- | --- |
| `status` | Whether Hyperliquid Trading is enabled for this instance (integration gate) |
| `snapshot` | Dashboard-style summary: account value, PnL, margin used, open positions, risk (requires trading enabled) |
| `enable` | Turn on Hyperliquid Trading so exchange routes work; confirm first |
| `disable` | Turn off Hyperliquid Trading; blocked while positions, orders, or funds remain |
| `account` | Hyperliquid account address, network, and wallet metadata |
| `state` | Perp margin/positions and/or spot balances for that address |
| `builder-fee-status` | Whether the fixed 0.05% transaction fee is authorized for orders |
| `abstraction` | Current Hyperliquid account mode (`default`, `disabled`, `unifiedAccount`, `portfolioMargin`) |
| `set-abstraction` | Set account mode to `disabled`, `unifiedAccount`, or `portfolioMargin`; confirm first |

## Trading Integration Gate

Gateway account reads and writes require the trading integration to be enabled.
Public `search`, `symbol`, `markets`, `l2`, and `candles` remain available without
wallet credentials; see [market-data.md](market-data.md). Authorization to
enable/disable follows [SKILL.md](../SKILL.md#confirmation-contract).

Run this check silently when starting any Hyperliquid workflow:

```bash
purr hyperliquid status
```

| Result | Action |
| --- | --- |
| `enabled: true` | Continue |
| `enabled: false` | Explain that Hyperliquid Trading is off. Verify authorization → `enable`; ask only if not covered |
| Error | Report and stop; do not assume enabled |

```bash
purr hyperliquid enable
purr hyperliquid disable
```

- `enable` / `disable` require confirmation (see Confirmation Contract in
  `SKILL.md`).
- `disable` fails with `HYPERLIQUID_TRADING_DISABLE_BLOCKED` when any default or
  builder-dex account has open positions, open orders, positive account value,
  or withdrawable funds, or when any positive spot balance or dust remains.
  Show the `blockers` payload, clear the reported exposure and funds, then
  retry only within the confirmed scope. Do not treat a rounded display
  value of zero as proof that exact dust is absent.
- Prefer `snapshot` for a quick portfolio overview once trading is enabled; use
  `state` for exact collateral and position details needed to trade.

## Workflow

Use this preflight before a trade card; execute writes only under the
Confirmation Contract in [SKILL.md](../SKILL.md).

1. Run `purr hyperliquid status`. If disabled, obtain authorization if needed
   and `enable` before gateway account commands.
2. Run `purr hyperliquid account` to show the Hyperliquid account address.
3. Run `purr hyperliquid state --all-dexs` for balance overviews and trade-card
   preflight. It discovers all perp DEXs and reads spot once. Read each entry
   in `perps` (`dex`, `state`) and the separate `spot` state. Check `complete`
   and `errors`; failed reads are unknown, never zero.
4. Use the target DEX's state for order readiness, including existing positions
   and margin usage. Report funds in other ledgers separately and identify any
   required transfer. Do not sum different collateral currencies or equate
   account equity with available collateral. For a targeted refresh, use
   `state --kind perp --dex xyz` (omit `--dex` for default perps).
5. Before confirming any order-placement command (`limit-order`,
   `bracket-order`, `stop-loss`, `take-profit`, or `protect-position`) or
   changing leverage/collateral for it, run `builder-fee-status` and follow
   **Order Fee Preflight** below.
6. For trade cards and funding, run the wallet checks below and distinguish
   wallet funds from exchange collateral.
7. Check `abstraction` when the user asks about Standard / unified / portfolio
   margin mode. Only call `set-abstraction` after confirmation.

## Order Fee Preflight

All order-placement commands (perp and spot) require the fixed additional
`0.05%` transaction fee authorization when it is not already approved.
Non-order actions skip this check.

```bash
purr hyperliquid builder-fee-status
```

Handle the result before building the final order confirmation:

| Status | Action |
| --- | --- |
| `approved` | Continue normally; do not ask for fee consent again |
| `approval_required` | Disclose the standing fee under the Confirmation Contract in `SKILL.md`; obtain consent if not already covered, then approve and verify |
| Error or unknown value | Stop and report it; do not place an order as a status probe |

After authorization, verify status and continue the covered plan.
Authorization itself does not submit or fill an order.

In user-facing text, say “additional 0.05% transaction fee,” never “builder
fee.” Command and response names may retain `builder-fee` internally.

## State Guidance

- Hyperliquid keeps **perp collateral** and **spot USDC** in separate ledgers.
- Deposits from Arbitrum credit the **perp** side first (see
  [deposit-withdraw.md](deposit-withdraw.md)).
- Open positions, free collateral, and margin usage come from perp state.
- Spot balances matter for spot orders and for `usd-class-transfer` planning.
- `--kind` defaults to `both` when omitted.
- `--all-dexs` supports `perp` or `both` and cannot be combined with `--dex`.
  Without it, `state` and `snapshot` do not provide an all-DEX balance overview.
- `--dex` applies only to the **perp** leg. Spot state is always the account’s
  spot clearinghouse (not filtered by builder dex).

## Abstraction (account mode)

- Check with `purr hyperliquid abstraction` (no confirmation). Response includes
  `abstraction` only (no separate `dexAbstraction` field).
- To change the mode, confirm first and then run:

```bash
purr hyperliquid set-abstraction --mode disabled
purr hyperliquid set-abstraction --mode unifiedAccount
purr hyperliquid set-abstraction --mode portfolioMargin
```

| Mode | Meaning (agent guidance) |
| --- | --- |
| `disabled` | Standard account mode |
| `unifiedAccount` | Unified account mode |
| `portfolioMargin` | Portfolio margin mode |

`--mode` must be exactly one of the three values above (sent as JSON
`abstraction`). Alias: `--abstraction`.

The response may also return `default` (venue default / unset presentation).
Do not pass `default` or removed modes such as
`dexAbstraction` to `set-abstraction`. Prefer leaving mode unchanged unless the
user explicitly wants a mode change.

## Wallet Funding Checks

Before a trade card or deposit, read wallet identity, Arbitrum USDC, and
native ETH gas together:

```bash
purr wallet address --chain-type ethereum
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
purr wallet balance --chain-type ethereum --chain-id 42161
```

Omitting `--token` reads native ETH; do not pass `--token ETH`.
Verify that the receiving wallet matches `purr hyperliquid account`.
A failed read is unknown, not zero. Check gas before asking for funding,
not only after a deposit fails.

Sending USDC to the wallet does not credit Hyperliquid automatically.
A separate authorized `deposit` moves it to default perp collateral; a
further transfer may be needed for spot or a builder dex. Explain these
steps and give the wallet address, Arbitrum One USDC, and native ETH gas
requirement when funding is needed. The deposit minimum applies to the
Hyperliquid deposit, not to receiving tokens in the wallet.

See [deposit-withdraw.md](deposit-withdraw.md) for execution and settlement.
