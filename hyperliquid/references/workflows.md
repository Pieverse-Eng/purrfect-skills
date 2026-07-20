# Typical Workflows

End-to-end recipes. Always follow the Confirmation Contract in `SKILL.md` for
actions that can change orders, positions, collateral, settings, or funds.
Use `--body-json` for ordinary single actions. Perform preparatory queries
silently and surface only decisions, confirmations, meaningful results, or
errors that change the workflow.

## Order Fee Preflight

At every marked order step (perpetual **or** spot), follow **Order Fee
Preflight** in [preflight.md](preflight.md) before any account-changing
preparation. For `HYPERLIQUID_BUILDER_FEE_APPROVAL_REQUIRED`, follow the 428
fallback in [errors.md](errors.md); never authorize or retry automatically.

## Integration Gate

At the start of any exchange workflow, ensure trading is enabled:

```bash
purr hyperliquid status
```

If `enabled` is false, explain, confirm → `enable`, then continue. Only
`status`, `enable`, and `disable` work while disabled; every other Hyperliquid
command (including `snapshot`) requires trading enabled.

## Symbol Ambiguity

This branch applies to every order workflow, not only equity perps. If `symbol`
returns `HYPERLIQUID_SYMBOL_AMBIGUOUS`, read `data.candidates` from the CLI
error. Present each candidate's `coin`, `dex`, `assetId`, and `szDecimals`, and
ask the user which market they mean. Never select one silently.

After the user chooses, use that candidate object directly for the rest of the
workflow. Do not run `symbol` again: the candidate is already a complete
resolution. Use its canonical `coin`, `assetId`, and `szDecimals` when building
the order. For state, prices, and orders, omit `--dex` when the selected
candidate has `dex: "default"`; otherwise pass `--dex <candidate.dex>`. The
later order confirmation is still required.

## A. First-Time Fund and Status

1. Integration and identity:

```bash
purr hyperliquid status
# if disabled: confirm → enable
purr hyperliquid account
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
```

2. Confirm deposit ≥ 5 USDC → deposit:

```bash
purr hyperliquid deposit --amount 25
```

3. Wait / recheck Hyperliquid balances:

```bash
purr hyperliquid state --kind both
```

4. Summarize address, Arbitrum remaining USDC, and HL perp collateral.

## B. Crypto Perp Open (Example: ETH)

1. Ensure trading enabled (`status`; enable if needed). Resolve market:

```bash
purr hyperliquid symbol --coin ETH
```

2. Check collateral:

```bash
purr hyperliquid state --kind perp
```

3. Run the **Order Fee Preflight** above.

4. If leverage must change, include it in the final trade confirmation; do not
   run it yet:

```bash
purr hyperliquid update-leverage --asset <assetId> --is-cross true --leverage 5
```

5. Price context:

```bash
purr hyperliquid prices
purr hyperliquid l2 --coin ETH
```

6. Build the complete order body with `a` = `assetId`, size within
   `szDecimals`, and the required `orders` wrapper. Present one final summary
   containing both leverage and order parameters. After confirmation, set
   leverage first; place the order only if it succeeds:

```bash
purr hyperliquid update-leverage --asset <assetId> --is-cross <true|false> --leverage <n>
purr hyperliquid order --body-json '<complete-order-json>'
```

7. Reconcile:

```bash
purr hyperliquid orders --kind open
purr hyperliquid state --kind perp
```

## C. Equity / HIP-3 Perp (Example: TSLA on `xyz`)

1. Ensure trading enabled. Resolve with dex (avoid bare ambiguous tickers when
   possible):

```bash
purr hyperliquid symbol --coin TSLA --dex xyz
# or
purr hyperliquid symbol --coin xyz:TSLA
```

2. If ambiguous, follow **Symbol Ambiguity** above. Use the selected candidate
   directly; do not resolve it again.

3. Run the **Order Fee Preflight** above before any leverage or collateral
   change for this order.

4. Optional: check account mode if the user cares about unified / portfolio
   margin (`purr hyperliquid abstraction`). Builder-dex collateral still uses
   `send-asset` / `state --dex`, not abstraction mode.

5. Ensure collateral on that dex before changing leverage or submitting an
   order:

```bash
purr hyperliquid state --kind both
purr hyperliquid state --kind both --dex xyz
```

Calculate required margin from size, current price, and leverage. Compare it
with the target dex's `withdrawable` / available collateral, not the default
account value. If the target is short and the default vault has enough,
confirm →:

```bash
purr hyperliquid send-asset --destination-dex xyz --amount <amount>
```

Re-read `state --kind both --dex xyz` and continue only after the destination
balance is sufficient.

6. Include optional leverage and the order in one final trade confirmation as
   in workflow B. After yes, set leverage first and submit the order only if
   the leverage change succeeds.

7. Optional funding context:

```bash
purr hyperliquid funding --coin xyz:TSLA --start-time <ms>
```

## D. Spot Buy

1. Ensure trading enabled. Balances:

```bash
purr hyperliquid state --kind both
```

2. If USDC is only on perp, confirm → move to spot:

```bash
purr hyperliquid usd-class-transfer --amount <amount> --to-perp false
```

3. Run the **Order Fee Preflight** above (spot orders use the same fee
   authorization as perps).

4. Resolve the spot market (`markets --kind spot` or `symbol`), build order with
   that spot `assetId`, confirm → `order`.

5. Re-check `state --kind spot` and fills/orders.

## E. Close or Reduce Position

1. Ensure trading enabled. Check the position:

```bash
purr hyperliquid state --kind perp [--dex <dex>]
```

2. Run the **Order Fee Preflight** above.

3. Prefer reduce-only opposite-side order (`r: true`) sized to the position (or
   the portion the user wants to close). Confirm → `order`.

4. Cancel resting orders first if they block the close:

```bash
purr hyperliquid orders --kind open
purr hyperliquid cancel --body-json '<complete-cancel-json>'
```

5. Verify flat or reduced:

```bash
purr hyperliquid state --kind perp
```

## F. Cancel Open Orders

```bash
purr hyperliquid orders --kind open
# confirm → cancel body with a + o, or cancel-by-cloid
purr hyperliquid cancel --body-json '<complete-cancel-json>'
purr hyperliquid orders --kind open
```

## G. Withdraw Profits

1. Free collateral:

```bash
purr hyperliquid state --kind both
```

2. Confirm amount →:

```bash
purr hyperliquid withdraw --amount <amount>
```

3. Keep the returned **`nonce`**. Do not re-submit on timeout or while status is
   pending. A successful submit is not the same as Arbitrum arrival.

4. When the user asks for settlement status (or you need to confirm arrival):

```bash
purr hyperliquid withdraw-status --nonce <nonce>
```

- `status: pending` → report still settling; do not re-run withdraw.
- `status: arrived` → report `amountUsdc`, `feeUsdc`, `txHash`; optional:

```bash
purr wallet balance --chain-type ethereum --chain-id 42161 --token USDC
```

If `nonce` was never captured, reconcile with balances only — never invent a
nonce or re-withdraw to obtain one. See [deposit-withdraw.md](deposit-withdraw.md).

## H. Research Only (No Trade)

Trading must still be **enabled** for market-data and account reads through the
gateway. If disabled, enable after confirmation first (or explain that research
via these commands requires trading on).

```bash
purr hyperliquid status
purr hyperliquid symbol --coin <coin> [--dex <dex>]
purr hyperliquid markets --kind both [--dex <dex>]
purr hyperliquid prices [--dex <dex>]
purr hyperliquid l2 --coin <coin>
purr hyperliquid candles --coin <coin> --interval 1h --start-time <ms>
purr hyperliquid funding --coin <coin> --start-time <ms>
```

Do not place orders or change the account in this path. For multi-venue
tokenized stock quotes, prefer `stock-spread`.

## I. Dead-Man Schedule Cancel

Timed safety cancel (confirm human-readable time first):

```bash
purr hyperliquid schedule-cancel --time <unix-ms>
```

Clear an existing schedule (confirm clear intent first):

```bash
purr hyperliquid schedule-cancel
```

## J. Disable Trading Integration

1. Inspect exposure:

```bash
purr hyperliquid status
purr hyperliquid snapshot
purr hyperliquid state --kind both
purr hyperliquid orders --kind open
```

2. If any open positions or open orders remain, close/cancel them first (with
   confirmations). Disable will fail while exposure remains.

3. Confirm →:

```bash
purr hyperliquid disable
```

4. On `HYPERLIQUID_TRADING_DISABLE_BLOCKED`, present blockers, clear exposure,
   and obtain a new confirmation before retrying.

## Agent Habits

- One account-changing action per confirmation.
- Check `status` before exchange work.
- Symbol resolve every new market.
- Fee preflight for every order, including spot.
- Re-read state after funding, collateral moves, and trades.
- Complete in-memory wire payloads with the required request wrapper.
