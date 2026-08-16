# Typical workflows

Follow the Confirmation Contract in `SKILL.md` for every execute. Prepare
silently. Surface only decisions, results, or errors that change the path.

## A. Find a market and quote it

Named event:

```bash
purr predict-fun search --query "<text>" --limit 10
purr predict-fun market --market-id <id>
purr predict-fun market-quote --market-id <id>
```

Latest trending (open markets, highest 24h volume):

```bash
purr predict-fun markets --status OPEN --sort VOLUME_24H_DESC --first 10
purr predict-fun market-quotes --market-ids <ids>
```

Other list mappings are in [discovery.md](discovery.md). Report title, status,
and the quote. Then stop unless the user asked to trade.

## B. First trade (MARKET BUY YES)

```bash
purr predict-fun account
purr predict-fun readiness --market-id <id>
purr predict-fun approvals --market-id <id> --operation TRADE --side BUY
```

If USDT or BNB is short, stop and use the `onchain` skill to fund chain `56`.

If approvals are missing:

```bash
purr predict-fun approval-preview --operation TRADE --market-id <id> --side BUY --amount <spend>
# confirm →
purr predict-fun approval-execute --preview-id <uuid>
# include https://bscscan.com/tx/<hash> from the response
purr predict-fun approvals --market-id <id> --operation TRADE --side BUY
```

Then the order:

```bash
purr predict-fun orderbook --market-id <id> --outcome YES
purr predict-fun order-preview --market-id <id> --outcome YES --side BUY --strategy MARKET --spend <decimal>
# confirm → execute immediately
purr predict-fun order-execute --preview-id <uuid>
purr predict-fun order --order-hash <preview.orderHash>
purr predict-fun positions --market-id <id>
```

If `order` is still `OPEN` / 0 filled and `positions` or `balances` already
moved, follow
**Verify a MARKET fill** in [trading.md](trading.md) (`matches`, `activity`,
re-read the order, `balances --market-id`).

If the book cannot fill it, `PREDICT_INSUFFICIENT_LIQUIDITY` — reduce size or
switch to LIMIT. Amount floors are in [trading.md](trading.md).

## C. LIMIT sell

```bash
purr predict-fun positions --market-id <id>
purr predict-fun orderbook --market-id <id> --outcome <YES|NO>
purr predict-fun order-preview --market-id <id> --outcome <YES|NO> --side SELL --strategy LIMIT --quantity <decimal> --price <(0,1)>
# confirm →
purr predict-fun order-execute --preview-id <uuid>
purr predict-fun order --order-hash <hash>
```

## D. Cancel open orders

```bash
purr predict-fun orders --status OPEN
purr predict-fun cancel-preview --order-hashes <hash>[,<hash>]
# confirm →
purr predict-fun cancel-execute --preview-id <uuid>
# include https://bscscan.com/tx/<hash> from the response
purr predict-fun order --order-hash <hash>
```

Use `cancel-all-preview` only when the user asked to cancel every open order.
On `PREDICT_CANCEL_ALL_REQUIRES_BATCHING`, cancel explicit pages of hashes
instead.

Use remove-from-book only when the user asks for off-chain pull and accepts
stranded-collateral risk:

```bash
purr predict-fun remove-from-book-preview --order-hashes <hash>
# confirm, including the risk →
purr predict-fun remove-from-book-execute --preview-id <uuid> --acknowledge-risk true
```

## E. Split, merge, redeem, convert

```bash
purr predict-fun position-preview --action SPLIT --market-id <id> --amount <decimal>
purr predict-fun position-preview --action MERGE --market-id <id> --amount <decimal>
purr predict-fun position-preview --action REDEEM --market-id <id> --outcome <YES|NO>
purr predict-fun position-preview --action CONVERT --category-slug <slug> --market-ids <id,id> --amount <decimal>
# each action: confirm →
purr predict-fun position-execute --preview-id <uuid>
# include https://bscscan.com/tx/<hash> from the response
purr predict-fun positions --market-id <id>
```

Approve the matching operation first when the preview warns. On a standard
market, omit `--amount` on REDEEM; pass it only when `market` shows
`isNegRisk`.

## F. Watch a book

```bash
purr predict-fun stream --topics orderbook:<id>,wallet --max-events 20 --timeout-ms 15000
```

Keep topics allowlisted and ≤ 8. Stop when you have the answer.
