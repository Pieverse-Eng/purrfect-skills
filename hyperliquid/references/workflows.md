# Trading Workflows

This is the execution sequence for trade cards and order management.
Authorization follows [SKILL.md](../SKILL.md#confirmation-contract).
Funding-only requests use [deposit-withdraw.md](deposit-withdraw.md);
internal transfers use [collateral.md](collateral.md).

## Prepare Before Confirmation

Apply these checks to the requested operation. Opening or increasing a
position needs funding and sizing checks; closing, protecting, modifying,
and cancelling use the live position/order checks in their sections below.

1. Read [preflight.md](preflight.md) and select the relevant checks.
   For allocation or funding decisions, establish available collateral and
   identify any required deposit or transfer.
2. Read [market-data.md](market-data.md). Resolve each exact market and retain
   `coin`, `assetId`, `szDecimals`, dex, supported margin mode, and fresh
   executable price context. Use current market metadata for constraints.
3. Read [order-commands.md](order-commands.md) for order parameters,
   quantity calculation, price boundaries, and precision. For leverage changes,
   also read [trading.md](trading.md#leverage). Derive size from the requested
   budget or live position/order as appropriate, and verify applicable constraints.
4. If funds must move, read the relevant deposit/transfer reference now.
   Prepare source, destination, amount, fee scope, and command syntax along
   with leverage and entry/protection commands. Batch independent reads.
5. Present the concrete parameters, funding requirements, and execution
   boundaries under the Confirmation Contract. Follow the main agent's
   allocation and presentation rules when provided.

If required data is unavailable, mark readiness unverified and resolve the
gap before dependent writes. Verify command syntax from the reference or
CLI help rather than trial orders.

## Execute the Confirmed Plan

Refresh the state and quotes relevant to the operation, and revalidate
parameters affected by those changes. Apply the Confirmation Contract to
any parameter changes.

Apply the Confirmation Contract before each account-changing step.
Perform the required steps in dependency order:

1. Confirm and enable trading if necessary.
2. Deposit wallet USDC if needed; verify credited default perp collateral.
3. Transfer to spot or the selected builder dex if needed; verify that ledger.
4. Complete any disclosed standing fee approval and verify its status.
5. Confirm leverage/margin mode with the order, then set it; stop if it fails.
6. Submit the prepared typed order with its required protection.
7. Verify actual positions, open entries, and every protection leg with the
   inspection commands in [trading.md](trading.md).

Fee approval must precede orders; if account initialization prevents approval
earlier, complete the authorized deposit first. Skip already satisfied steps.
Reuse verified command parameters and resolve any new errors through
[errors.md](errors.md). Reconcile uncertain/partial results before continuing.

For HIP-3 markets, only the target dex's available collateral funds an order.
Spot entries require spot funds. Verify transferred collateral before
dependent orders.

## Open a Position

Select `limit-order` for an ordinary limit or bounded market-style entry;
select `bracket-order` for an entry with attached TP/SL.
Use the exact syntax and sizing rules in
[order-commands.md](order-commands.md#place-orders).

For long positions, TP is above and SL below the intended entry; reverse for
shorts. Confirm trigger execution mode and worst/limit prices. Store entry
and child OIDs. A resting entry is pending, not a filled position.

## Protect an Existing Position

Read the actual non-zero position side and size from fresh perp state.
Use `protect-position` for paired market protection, or `stop-loss` /
`take-profit` for an individual trigger. Read the position-sizing semantics
in [order-commands.md](order-commands.md): position TP/SL scales with the live
position, unlike a fixed-size bracket child.

Stop if a proposed trigger is already crossed. Apply fee preflight and
confirm the triggers and execution boundaries. Verify the new child OIDs
with frontend orders; the historical entry OID is not the protection target.

## Modify an Order

Read frontend orders and exact status using [trading.md](trading.md).
Identify the still-open target, its type, and `isPositionTpsl`.
Reconstruct the full replacement using the field mapping and
`--always-place` rules in [order-commands.md](order-commands.md).
Modify commands are replacements, not partial patches.

Use current `sz`, not `origSz`, for ordinary orders/fixed-size children;
refresh live position state for position-sized TP/SL. Confirm all replacement
fields and any always-place duplicate-order risk. Modify each protection leg
by its own OID, then verify. A filled entry cannot be modified.

## Close or Reduce

Read the live position, resolve the market, and apply fee preflight.
Use the opposite side with `limit-order --reduce-only true`, sized to the
confirmed reduction. There is no `close-position` command; market-style
execution still needs its disclosed worst-price boundary.

Verify the remaining position and inspect protection orders. Handle leftover
orders only within the authorized scope; do not claim flat from submission.

## Cancel an Order

Locate the exact open OID/cloid and confirm its target under the
Confirmation Contract. Use the cancel commands in [trading.md](trading.md),
then verify status. A filled historical entry cannot be cancelled.

## Disable Trading

Read all-DEX balances and each relevant dex's open orders. Positive default,
builder-dex, or spot balances (including dust), positions, and orders can
block disable. Use reported blockers from [preflight.md](preflight.md).

Prepare any needed closes, cancellations, spot conversions, collateral
consolidation, and withdrawal under the Confirmation Contract. Use the same
workflows/references above, verify they completed, then disable. Report
unmovable dust or other blockers instead of retrying in a loop.
