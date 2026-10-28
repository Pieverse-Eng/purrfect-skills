# Native perpetual trading

Use only the installed `purr injective` business commands and the current Agent.
This candidate executes USDC perpetuals on the existing default subaccount. It
does not expose Spot writes, account opening, bridging or arbitrary messages.

## Prepare the exact action

1. Use the platform's exact native market hash/product. Read `readiness
   --market-id HASH` for capabilities, ticks, mark, INJ gas and spendable margin.
   Reuse current per-turn facts; do not reread the whole portfolio or catalog.
2. For order/close/protection/replace/batch cancellation/margin, read `management
   --market-id HASH` at Review. It provides the same snapshot's readiness,
   position, full order inventory, gas and `stateHash`. Never reuse a view after
   changing Agent or wallet. Missing/incomplete facts block a write.
3. Create a JSON review file containing exactly `stateHash` and
   `cancelOrderHashes`. Choose hashes explicitly from the observed inventory.
   Show these cancellations in the user's review. Do not silently cancel exits
   or opening orders, guess a hash, or copy a cancellation set from an old view.
4. Build the command without `--execute` to obtain a local business draft. Check
   decimal strings, tick alignment and total message gas. Ask confirmation of
   this unchanged body, then submit it once with the execution flags below.

| Action | Command and required business flags |
| --- | --- |
| Open | `order --kind limit\|market --side buy\|sell --quantity Q --price P --margin M` |
| Close/reduce | `close --side buy\|sell --quantity Q --price WORST` (opposite the current position) |
| Cancel one | `cancel --order-hash HASH` |
| Replace regular order | `replace --order-hash HASH --quantity Q --price P --margin M --reduce-only true\|false --review-file FILE` |
| Paired TP/SL | `protection --quantity Q --stop-loss-kind market\|limit --stop-loss-trigger P --stop-loss-price WORST_OR_LIMIT --take-profit-kind market\|limit --take-profit-trigger P --take-profit-price WORST_OR_LIMIT --review-file FILE` |
| One protection leg | The same `protection` command with only that leg's three flags |
| Cancel selected | `cancel-batch --review-file FILE` |
| Adjust margin | `margin --direction add\|remove --amount USDC --review-file FILE` |

All commands require `--market-id HASH --max-fee-inj MAXIMUM`. Use the current
review file for order/close too when exits exist. A margin review has an empty
cancellation set. `price` on market/close/protective-market commands is the
explicit worst acceptable execution price, not a fresh unlimited market order.
Ask for a slippage bound if not already authorized; compute exact tick-aligned
values without binary-float rounding or a guessed tick. Do not raise a gas ceiling
silently. A multi-message transaction needs a reviewed total ceiling.

Execution adds `--wallet-generation CURRENT_GENERATION --idempotency-key
ORIGINAL_KEY --execute true`. The platform derives identity, sequence, signer,
native messages and broadcast. The CLI never signs or directly connects to RPC.

## Position and protection boundaries

- Protection uses zero-margin reduce-only native legs in **one** business
  request. Do not submit TP and SL as independent replayable requests.
- Review every replaced existing exit, including unknown external conditionals.
  Unknown role stays unknown; native numeric SL is 3/4 and TP is 5/6, not the
  numbering used by Lighter. Do not label a generic conditional TP or SL.
- Cancel pending opening orders separately, confirm their outcome and refresh
  before adding/replacing exits. Do not append an unreviewed cleanup.
- Reduce-only quantity must fit the currently observed position; a replacement
  may not increase the reducible remaining size. Refresh after fills/side changes.
- A successful protection receipt proves inclusion, not that a trigger has
  fired. Verify native order and fill observations. On close/reopen, verify that
  old protection has been removed before treating a new position as protected.
- Native batches contain at most 32 messages. Do not silently split an approved
  action; ask for the next bounded reviewed action after the first outcome is known.

For 202, timeout or unknown receipt, stop new actions and follow the original
request as described in [errors](errors.md). Only a verified, approved and still
unbroadcast policy hold permits one identical original-key resume POST. A new
key or replacement body is not recovery.
