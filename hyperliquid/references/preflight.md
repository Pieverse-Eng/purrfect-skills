# Preflight / Account

Use these commands before trading, funding, or explaining balances.

## Commands

```bash
purr hyperliquid account
purr hyperliquid state [--kind perp|spot|both] [--dex <dex>]
purr hyperliquid builder-fee-status
purr hyperliquid abstraction
purr hyperliquid set-abstraction --mode disabled|unifiedAccount|portfolioMargin
```

| Command | Purpose |
| --- | --- |
| `account` | Hyperliquid account address, network, and wallet metadata |
| `state` | Perp margin/positions and/or spot balances for that address |
| `builder-fee-status` | Whether the fixed 0.05% transaction fee is authorized for perpetual orders |
| `abstraction` | Current Hyperliquid account mode (`default`, `disabled`, `unifiedAccount`, `portfolioMargin`) |
| `set-abstraction` | Set account mode to `disabled`, `unifiedAccount`, or `portfolioMargin`; confirm first |

## Workflow

Run these checks silently. Do not announce that preflight, market resolution,
or balance inspection is starting, and do not narrate the remaining steps.

1. Run `purr hyperliquid account` to show the Hyperliquid account address.
2. Run `purr hyperliquid state --kind both` for a full collateral and position
   snapshot. Use `--kind perp` or `--kind spot` when only one side is needed.
3. When the user targets a builder dex (for example equity perps on `xyz`),
   also run `state --kind both --dex xyz` (or the relevant dex name).
4. Before confirming any perpetual order or changing leverage/collateral for
   it, run `builder-fee-status` and follow **Perpetual Fee Preflight** below. Do
   not run it for a confirmed spot market.
5. Check `abstraction` when the user asks about Standard / unified / portfolio
   margin mode. Only call `set-abstraction` after confirmation.

## Perpetual Fee Preflight

First establish that the intended order is perpetual. A resolved symbol with
`spotPairId` is spot; when the market type is unclear, inspect
`purr hyperliquid markets --kind perp` and `--kind spot` rather than guessing.

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
confirmation. The authorization itself does not submit or fill an order. Spot
orders skip this check because they do not use this authorization.

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
