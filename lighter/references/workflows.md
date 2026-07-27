# Typical workflows

End-to-end recipes. Follow the Confirmation Contract in `SKILL.md` for every
account-changing step. Prepare silently; surface decisions, confirmations,
results, and blocking errors only.

## Shared gates

At the start of any exchange workflow:

```bash
purr lighter status
# if disabled: explain → confirm → enable
purr lighter account
```

If `account.status` is not `ready`, follow first-open or wait paths before
promising a trade.

For every order path: after the account is ready, run
`purr lighter partner-fee-status` and complete 0.05% transaction fee consent
when required.

## A. First open and fund

1. Integration + readiness:

```bash
purr lighter status
purr lighter account
purr lighter deposit-networks
purr wallet balance --chain-type ethereum --chain-id <source> --token USDC
purr wallet balance --chain-type ethereum --chain-id <source>   # native gas on source chain
```

2. If `account_opening_required`, confirm initial amount and chain (enough USDC
   **and** gas) → open:

```bash
purr lighter open-account --amount 25 --source-chain-id 8453
```

3. Poll until ready. **Do not** start a second open/deposit while opening.
   Re-run the same `open-account` **only** if the response has
   `nextAction: "resume_account_opening"`. On policy deferred, observe
   `deposits` only — never re-run to unstick.

```bash
purr lighter account
purr lighter deposits --limit 5
```

4. Summarize L1 address, account status, remaining source-chain USDC and gas.
   If `depositTxHash` / `approvalTxHash` are present, add source-chain explorer
   links (see Explorer Links in `SKILL.md`), not the Lighter logs URL.

## B. Add funds after open

1. Confirm account is `ready`.
2. Check `deposit-networks` minimum, source-chain **USDC**, and **native gas**.
3. Confirm amount + chain → deposit:

```bash
purr lighter deposit --amount 50 --source-chain-id 42161
```

4. Track `deposit-status` / `deposits` until credited; then `balances`. Do not
   re-run deposit on policy deferred or unknown — observe the same request.
   Link any L1 `depositTxHash` / `approvalTxHash` with the source-chain
   explorer for that `sourceChainId`.

## C. Crypto perp open (example: long SOL)

1. Gates: `status`, `account` ready, `partner-fee-status`.
2. Resolve market and book:

```bash
purr lighter market --market SOL --market-type perp
purr lighter order-book-depth --market SOL --market-type perp --limit 100
purr lighter positions
purr lighter balances
```

3. If leverage must change, include it in the trade confirmation (or confirm
   separately), then:

```bash
purr lighter update-leverage --market SOL --market-type perp --leverage 5 --margin-mode cross
```

4. Confirm side, size, price (worst acceptable for market), TIF → order:

```bash
purr lighter order --market SOL --market-type perp --side buy --type market \
  --size 1 --price <worst-acceptable>
```

5. Verify:

```bash
purr lighter active-orders
purr lighter positions
purr lighter trades --market SOL --market-type perp --limit 5
```

If the order (or leverage) response has `txHash`, include
`https://app.lighter.xyz/explorer/logs/<txHash>` in the result summary.

## D. Spot buy (example: LIT)

1. Gates + fee status.
2. Resolve **spot** explicitly (LIT also has a perp):

```bash
purr lighter market --market LIT --market-type spot
purr lighter order-book-depth --market LIT --market-type spot --limit 100
purr lighter balances
```

3. Confirm → order with `--market-type spot`.
4. Verify balances and trades.

## E. Close / reduce position

1. Read `positions` and `active-orders`.
2. Prefer reduce-only for the close:

```bash
purr lighter order --market SOL --market-type perp --side sell --type market \
  --size <position-size> --price <worst-acceptable> --reduce-only true
```

3. Verify positions are flat; cancel leftover orders if needed. Include the
   Lighter explorer link when `txHash` is present.

## F. Cancel working orders

```bash
purr lighter active-orders
# confirm each cancel or cancel-all
purr lighter cancel --market SOL --market-type perp --order-index <id>
# or
purr lighter cancel-all
```

## G. Secure withdraw to Ethereum

1. `withdrawal-delay`, `balances`, destination is the TEE Ethereum address.
2. Preview:

```bash
purr lighter withdraw --amount 10
```

3. Confirm amount ≥ 1 USDC and delay expectations → execute:

```bash
purr lighter withdraw --amount 10 --yes
```

4. Track `request-status`; do not claim arrival from submit alone.

## H. Fast withdraw to Arbitrum

1. Preview fee and net:

```bash
purr lighter fast-withdraw --amount 10
```

2. Confirm amount (must leave ≥ 4 USDC after fee) and that destination is
   Arbitrum. Re-quote risk: execute re-fetches fee.

```bash
purr lighter fast-withdraw --amount 10 --yes
```

3. Reconcile via `requests` / balances.

## I. Market ambiguity

If resolve fails with `LIGHTER_MARKET_AMBIGUOUS`:

1. List candidates (symbol, type, market id).
2. Ask which market the user means.
3. Continue with that type/id; do not guess.

## J. Unknown write outcome

After timeout or `LIGHTER_SUBMIT_UNKNOWN`:

```bash
purr lighter requests --limit 10
purr lighter request-status --request-id <id>
purr lighter active-orders
purr lighter positions
purr lighter deposits --limit 5
```

Report what is known. Only re-issue a write after the user confirms a new
action and reconciliation shows the prior one did not apply.
