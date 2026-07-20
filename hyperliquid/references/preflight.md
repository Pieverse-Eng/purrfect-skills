# Preflight / Account

Use these commands before trading, funding, or explaining balances.

## Commands

```bash
purr hyperliquid status
purr hyperliquid snapshot
purr hyperliquid enable
purr hyperliquid disable
purr hyperliquid account
purr hyperliquid state [--kind perp|spot|both] [--dex <dex>]
purr hyperliquid builder-fee-status
purr hyperliquid abstraction
purr hyperliquid set-abstraction --mode disabled|unifiedAccount|portfolioMargin
```

| Command | Purpose |
| --- | --- |
| `status` | Whether Hyperliquid Trading is enabled for this instance (integration gate) |
| `snapshot` | Dashboard-style summary: account value, PnL, margin used, open positions, risk (requires trading enabled) |
| `enable` | Turn on Hyperliquid Trading so exchange routes work; confirm first |
| `disable` | Turn off Hyperliquid Trading; blocked while open positions or open orders exist |
| `account` | Hyperliquid account address, network, and wallet metadata |
| `state` | Perp margin/positions and/or spot balances for that address |
| `builder-fee-status` | Whether the fixed 0.05% transaction fee is authorized for orders |
| `abstraction` | Current Hyperliquid account mode (`default`, `disabled`, `unifiedAccount`, `portfolioMargin`) |
| `set-abstraction` | Set account mode to `disabled`, `unifiedAccount`, or `portfolioMargin`; confirm first |

## Trading Integration Gate

All exchange routes under the Hyperliquid gateway (`account`, `state`,
`markets`, `order`, `deposit`, `snapshot`, and the rest) require the trading
integration to be **enabled**. Only `status`, `enable`, and `disable` remain
available when trading is disabled.

Run this check silently when starting any Hyperliquid workflow:

```bash
purr hyperliquid status
```

| Result | Action |
| --- | --- |
| `enabled: true` | Continue |
| `enabled: false` | Explain that Hyperliquid Trading is off. Confirm → `enable`. Do not enable silently |
| Error | Report and stop; do not assume enabled |

```bash
purr hyperliquid enable
purr hyperliquid disable
```

- `enable` / `disable` require confirmation (see Confirmation Contract in
  `SKILL.md`).
- `disable` fails with `HYPERLIQUID_TRADING_DISABLE_BLOCKED` when any default or
  builder-dex account has open positions or open orders. Show the `blockers`
  payload, close/cancel exposure first, then retry disable only after a new
  confirmation.
- Prefer `snapshot` for a quick portfolio overview once trading is enabled; use
  `state` for exact collateral and position details needed to trade.

## Workflow

Run these checks silently. Do not announce that preflight, market resolution,
or balance inspection is starting, and do not narrate the remaining steps.

1. Run `purr hyperliquid status`. If disabled, stop for confirmation and
   `enable` before any other exchange command.
2. Run `purr hyperliquid account` to show the Hyperliquid account address.
3. Run `purr hyperliquid state --kind both` for a full collateral and position
   snapshot. Use `--kind perp` or `--kind spot` when only one side is needed.
   Optionally use `snapshot` when the user wants a high-level summary.
4. When the user targets a builder dex (for example equity perps on `xyz`),
   also run `state --kind both --dex xyz` (or the relevant dex name).
5. Before confirming **any** order (perpetual or spot) or changing
   leverage/collateral for it, run `builder-fee-status` and follow **Order Fee
   Preflight** below.
6. Check `abstraction` when the user asks about Standard / unified / portfolio
   margin mode. Only call `set-abstraction` after confirmation.

## Order Fee Preflight

All orders (perp and spot) require the fixed additional `0.05%` transaction
fee authorization when it is not already approved. Non-order actions skip this
check.

```bash
purr hyperliquid builder-fee-status
```

Handle the result before building the final order confirmation:

| Status | Action |
| --- | --- |
| `approved` | Continue normally; do not ask for fee consent again |
| `approval_required` | Briefly request authorization for the persistent additional 0.05% transaction fee using the exact consent prompt in `SKILL.md`, then run `approve-builder-fee` |
| Error or unknown value | Stop and report it; do not place an order as a status probe |

After successful authorization, continue to the ordinary order summary and
confirmation. The authorization itself does not submit or fill an order.

In user-facing text, say “additional 0.05% transaction fee,” never “builder
fee.” Command and response names may retain `builder-fee` internally.

## State Guidance

- Hyperliquid keeps **perp collateral** and **spot USDC** in separate ledgers.
- Deposits from Arbitrum credit the **perp** side first (see
  [deposit-withdraw.md](deposit-withdraw.md)).
- Open positions, free collateral, and margin usage come from perp state.
- Spot balances matter for spot orders and for `usd-class-transfer` planning.
- `--kind` defaults to `both` when omitted.
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

## Related Checks Outside Hyperliquid

For on-chain Arbitrum USDC before deposit:

```bash
purr wallet address --chain-type ethereum
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
```

Native gas on Arbitrum may also be required for the deposit transfer. If the
deposit command fails for insufficient gas or USDC, report the shortage and stop.
