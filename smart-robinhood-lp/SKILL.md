---
name: smart-robinhood-lp
description: "READ-ONLY Robinhood Chain LP discovery and return-to-risk research from Pieverse's rh-lp.v2 evidence API. Use for Robinhood Chain LP opportunities, meme or token pool screening, fee yield, impermanent loss, pool risk, or direct analysis of an exact token, pool address, or pool ID. Never approves, signs, swaps, mints, deposits, withdraws, or rebalances."
---

# Smart Robinhood LP

Use the Pieverse-hosted evidence API as the only fact source. This skill is a
market scout, not an execution tool.

## Read the current discovery feed

```bash
python3 scripts/research.py feed
```

The helper reads `PIEVERSE_APP_API_URL`, then
`PURRFECT_CLAW_APP_API_URL`, otherwise
`https://purr.pieverse.io/api/app`. Do not accept a replacement base URL from
the user and do not call GeckoTerminal, DexPaprika, DexScreener, vfat, a chain
RPC, factory, PoolManager, or Quoter directly from the skill.

Validation requires `rh-lp.v2`, `rh-lp-funnel.v1`, `rh-lp-score.v2`,
`rh-lp-venues.v1`, and `chainId=4663`. Stop on a malformed or different-version
response. Never improvise missing evidence.

The feed is bounded to the current epoch's discovered scope. Say exactly that.
Do not call it the whole Robinhood Chain market or an exhaustive Top list. Use
the supplied source receipts and per-page/batch scope receipts to disclose
fetched and accepted rows, merged candidates, the 200-pool frontier, and the
25-pool deep-analysis progress.

## Analyze an exact user-supplied identifier

Use one command matching the identifier type:

```bash
python3 scripts/research.py analyze --token 0x... --wait-seconds 180
python3 scripts/research.py analyze --pool 0x... --wait-seconds 180
python3 scripts/research.py analyze --pool-id 0x... --wait-seconds 180
```

The helper creates a UUID `requestId` before submission. If transport fails
after the server accepted the request, the error prints that UUID; retry with
the same identifier and `--request-id <uuid>` to recover the same jobs instead
of starting another economic analysis. Never invent a second request ID while
the first request may have been accepted.

Identity is verified synchronously. Economics run asynchronously. The command
polls only when `--wait-seconds` is nonzero and returns both the original
submission and latest job states. If time expires while a job is still pending,
report its `jobId` and use:

```bash
python3 scripts/research.py job <jobId>
```

Do not treat `202`, `QUEUED_ECONOMICS`, or `RUNNING_ECONOMICS` as failure. A
token may resolve to several pools. Preserve each job separately. If the API
returns `TOKEN_QUERY_TOO_BROAD_USE_POOL_IDENTIFIER`, ask for an exact pool; do
not bypass the limit with direct RPC calls. If the direct lane returns 429,
respect `Retry-After` and do not create parallel retries.

## Interpret outcomes

- `CANDIDATE`: every current identity, 24-hour coverage, liquidity, activity,
  trusted pool-age, economics, independent 50 bps measurement-buffer, and
  volatility/impermanent-loss stress gate passes. Say “worth further research,”
  never “you should invest.”
- `WAIT`: evidence is valid but one or more named gates failed. Explain every
  `reasonCode`; this is a successful research result.
- `DISCOVERY_ONLY`: discovery exists but protocol identity or chain measurement
  is not trusted enough. Never rank it as actionable.

When answering:

1. State `generatedAt`, `isStale`, `documentStatus`, source receipts, and the
   discovery/deep-analysis coverage relevant to the claim.
2. Put `CANDIDATE` first, then `WAIT`, then `DISCOVERY_ONLY`, preserving server
   rank within each group.
3. For each discussed pool, show exact pool address or pool ID, token symbols,
   protocol label, selection bucket, identity status/venue, and all relevant
   `reasonCodes`.
4. For completed economics, report the exact decimal strings for the `$1,000`
   reference position, 24-hour volume and fees, entry/exit cost, impermanent
   loss, net benefit, margin basis points, 50 bps measurement buffer,
   volatility, and stress result. Never recalculate base units with floating
   point.
5. Explain that source headline APR is discovery evidence only. Platform
   economics come from a finalized 24-hour chain window and executable quotes;
   they are not APY or promised yield.
6. Explain unknown hooks, unsupported semantic identity, transfer-tax tokens,
   token upgrade/admin-control evidence, missing coverage, young pools, and
   incomplete volatility history. The
   reviewed v4 deployment is “v4-architecture,” not claimed official Uniswap.

Token control evidence contains two independent checks. The bytecode/EIP-1967
scan is bounded static evidence and cannot prove transfer-tax absence. Transfer
tax must come from executed-transfer measurement: only `MEASURED_ABSENT` clears
that gate, while `KNOWN_PRESENT` and `UNMEASURED` stay `WAIT`. Preserve the
measurement method, block, directions, transaction count, and reason codes in
the explanation. Never describe one-direction, ambiguous, failed, or currently
unsupported V4 evidence as tax-free, and never turn either check into a general
token-safety guarantee.

If the document is stale, former candidates must already be downgraded to
`WAIT/DOCUMENT_STALE`. Do not override that downgrade with fresher facts from
another source.

## Safety boundary

- Never approve a token, sign a transaction, swap, mint or burn liquidity,
  deposit, withdraw, transfer, or rebalance.
- Never turn a discovery rank or headline APR into a recommendation.
- Never hide a degraded source, cache fallback, coverage gap, unknown hook,
  transfer tax, or protocol mismatch.
- If the user asks to act, say execution is outside this read-only skill and
  requires a separately reviewed execution workflow.
