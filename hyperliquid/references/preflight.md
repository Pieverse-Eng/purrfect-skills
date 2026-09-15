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
| `disable` | Turn off Hyperliquid Trading; confirm first. Platform checks positions, orders, and balances |
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
| `enabled: false` | Explain that Hyperliquid Trading is off. Confirm → `enable`. Do not enable silently |
| Error | Report and stop; do not assume enabled |

```bash
purr hyperliquid enable
purr hyperliquid disable
```

- `enable` / `disable` require confirmation (see Confirmation Contract in
  `SKILL.md`).
- `disable` fails with `HYPERLIQUID_TRADING_DISABLE_BLOCKED` when the platform
  reports blocking positions, orders, or balances. Show `blockers`, clear only
  what they list, then confirm disable again. Do not recompute the disable rule
  from balances.
- Prefer `snapshot` for a quick portfolio overview once trading is enabled; use
  `state` for exact collateral and position details needed to trade.

## Select Checks by Operation

Execute writes only under the Confirmation Contract in [SKILL.md](../SKILL.md).
Use the narrowest reads that establish the requested operation's prerequisites.

| Operation | Checks |
| --- | --- |
| Gateway account read/write | Integration status; confirm enabling if required |
| Account-wide balance, allocation, or funding plan | Account identity and all-DEX state; wallet checks when wallet funds affect the plan |
| Open/increase a position or buy spot | Target collateral, current exposure, market constraints, executable quote, and order fee status |
| Close/reduce or protect a position | Live position side/size, applicable market constraints, quote, and order fee status |
| Modify an order | Exact open order/status, replacement constraints; live position if position-sized |
| Cancel an order | Exact open order/status |
| Deposit or withdraw | Identity, source funds, destination, fees and settlement checks from [deposit-withdraw.md](deposit-withdraw.md) |
| Transfer collateral | Source available funds and destination ledger from [collateral.md](collateral.md) |
| Change account mode | Current abstraction and the confirmed target mode |
| Disable trading | All-DEX balances and relevant open orders/exposure |

### Account-Wide Funds

Run `purr hyperliquid account` for identity and
`purr hyperliquid state --all-dexs` for the account-wide view. It discovers all
perp DEXs and reads spot once. Inspect each `perps` entry (`dex`, `state`)
and the separate `spot` state. Check `complete` and `errors`; failed reads
are unknown, never zero.

For order readiness, use the target DEX's available collateral and margin
usage. Identify funds in other ledgers and any required transfer separately.
Do not add unlike currencies or treat account equity as available collateral.
For a targeted refresh use `state --kind perp --dex <dex>`, omitting
`--dex` for default perps. Follow the main agent's additional preflight
requirements when supplied.

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
| `approval_required` | Request separate standing fee approval using the consent prompt in `SKILL.md`, then run `approve-builder-fee` and verify |
| Error or unknown value | Stop and report it; do not place an order as a status probe |

After authorization, verify status and continue to the order confirmation.
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

When wallet funds affect allocation or an on-chain transfer is needed, read
wallet identity, Arbitrum USDC, and native ETH gas:

```bash
purr wallet address --chain-type ethereum
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
purr wallet balance --chain-type ethereum --chain-id 42161
```

Omitting `--token` reads native ETH. Verify wallet identity against
`purr hyperliquid account` and sufficient token/gas balances before transfers.
Report missing or unverified prerequisites in funding instructions.

Sending USDC to the wallet does not credit Hyperliquid automatically.
A separate authorized `deposit` moves it to default perp collateral; a
further transfer may be needed for spot or a builder dex. Explain these
steps and give the wallet address, Arbitrum One USDC, and native ETH gas
requirement when funding is needed. The deposit minimum applies to the
Hyperliquid deposit, not to receiving tokens in the wallet.

See [deposit-withdraw.md](deposit-withdraw.md) for execution and settlement.
