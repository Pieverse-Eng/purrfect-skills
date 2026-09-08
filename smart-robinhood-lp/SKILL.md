---
name: smart-robinhood-lp
description: "READ-ONLY Robinhood Chain LP discovery and return-to-risk research from Pieverse's rh-lp.v2 evidence API. Use for Robinhood Chain LP opportunities, meme or token pool screening, fee yield, impermanent loss, pool risk, or direct analysis of an exact token, pool address, or pool ID. Never approves, signs, swaps, mints, deposits, withdraws, or rebalances."
---

# Smart Robinhood LP

Use the Pieverse-hosted evidence API as the only fact source. This skill is a
market scout, not an execution tool.

## Answer the user, not the evidence system

Validate the machine contract and reason from its exact statuses, but keep that
machinery out of an ordinary user-facing answer. Never narrate commands, tool
calls, API reads, polling, intermediate deltas, or the process used to reach the
answer. Do not paste helper output.

Run the research silently and finish the analysis before replying. The first
sentence must state the current decision; never open with what you will pull,
fetch, read, check, query, or call. Before sending an ordinary answer, pass the
complete draft through the deterministic output gate:

```bash
python3 scripts/answer_guard.py <<'ANSWER'
<complete draft answer>
ANSWER
```

The gate returns a valid draft unchanged and rejects process narration plus
internal vocabulary such as `API`, `DEGRADED` (in any letter case),
`documentStatus`, receipts, reason codes, funnels, backlogs, internal source
names, schema labels, and uppercase machine constants such as
`DISCOVERY_ONLY` or `ECONOMICS_PENDING`. Revise and run the gate again if it
fails. Do not mention the gate to the user. This gate is for ordinary product
answers; skip it only when the user explicitly asks for technical, developer,
or audit detail.

For a broad question such as "which LPs look good right now?":

- Lead with the decision in one plain sentence: whether anything is currently
  worth further research.
- Discuss at most three pools by default. Prefer pools whose source status is
  `CANDIDATE`, followed by `WAIT`; mention `DISCOVERY_ONLY` pools only when no
  stronger result exists or the user asks about them.
- Translate classifications for a non-technical reader: `CANDIDATE` means
  "worth researching further," `WAIT` means "not ready," and
  `DISCOVERY_ONLY` means "seen but not yet verified." Do not print the enum,
  reason-code, funnel-policy, venue-registry, source-receipt, backlog, or
  internal adapter names unless the user explicitly asks for technical or audit
  detail.
- Explain failed gates in ordinary language. For example, say that fee returns
  are still being measured or transfer-tax behavior is not yet verified; do not
  recite `ECONOMICS_PENDING` or `TRANSFER_TAX_UNMEASURED`.
- Give the observation time in a human-readable form. If the document is stale
  or its machine status is `DEGRADED`, say that the result may be incomplete
  because the snapshot is old or some discovery data was unavailable. Never
  print the word `degraded` in an ordinary answer, in any letter case. Do not
  name an internal data provider merely because its receipt has a failure.
- End with one concise bottom line and, if useful, one next step. Do not repeat
  the same conclusion in several headings or describe the skill as
  "read-only"; if action is requested, simply say that you can research the
  pool but cannot add liquidity or sign a transaction.

Raw enums, versions, source names, receipts, exact reason codes, and full
economics are available when the user asks for the methodology, audit trail, or
developer-facing output. Safety disclosures and material risks remain visible
in every mode.

## Read the current market summary

```bash
python3 scripts/research.py summary
```

Use `summary` for broad questions such as which pools are actionable, which
need more evidence, or what the current market looks like. It validates the
complete hosted document, then emits a bounded `rh-lp-summary.v1` view with
exact status counts, up to eight server-ranked `CANDIDATE`/`WAIT` entries, and
the first five server-ranked `DISCOVERY_ONLY` examples. The current
`rh-lp-funnel.v3` idle-prewarm limit is eight, so all current decision entries
fit. Account for nonzero `decisionCandidateOmitted` or
`discoveryOnlyOmitted` counts, but describe them in plain language only when
they affect the answer (for example, "199 other pools have not been verified").
Do not run `feed` first, read terminal spill files, or write ad hoc
Python/heredoc parsers for a broad market answer.

Use the full feed only when the user explicitly asks to inspect the complete
bounded frontier:

```bash
python3 scripts/research.py feed
```

The helper reads `PIEVERSE_APP_API_URL`, then
`PURRFECT_CLAW_APP_API_URL`, otherwise
`https://purr.pieverse.io/api/app`. Do not accept a replacement base URL from
the user and do not call GeckoTerminal, DexPaprika, DexScreener, vfat, a chain
RPC, factory, PoolManager, or Quoter directly from the skill.

Validation requires `rh-lp.v2`, `rh-lp-score.v2`, `rh-lp-venues.v1`, and
`chainId=4663`. During the bounded funnel migration it accepts exactly three
version-bound contracts: `rh-lp-funnel.v1` with a 25-pool limit and
`10 + 5 + 5 + 5` selection, or `rh-lp-funnel.v2` with a 4-pool limit and
`1 + 1 + 1 + 1` selection, or `rh-lp-funnel.v3` with up to eight analyzable
liquidity-by-volume reviewed-v3 prewarm rows and direct-request priority. It
rejects unknown versions and cross-version field mixes. Stop on a malformed or
unsupported response. Never improvise missing evidence.

The feed is bounded to the current epoch's discovered scope. Say exactly that.
Do not call it the whole Robinhood Chain market or an exhaustive Top list. For
technical or audit-detail requests, use the supplied source receipts and
per-page/batch scope receipts to disclose fetched and accepted rows, merged
candidates, the 200-pool frontier, and the versioned deep-analysis limit and
progress reported by the validated contract.

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

Identity is verified synchronously. A fresh shared pool-economics cache hit is
returned as a terminal job immediately; a miss is queued and writes through to
that cache when complete. The cache has a 24-hour TTL, but only results at most
six hours old are immediate hits. The command polls only when `--wait-seconds`
is nonzero and returns both the original submission and latest job states. If
time expires while a job is still pending,
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

- Treat each candidate's server-emitted `status` as its authoritative
  classification. Copy that enum verbatim into the internal status map before
  interpreting identity, economics, risk flags, or `reasonCodes`; never infer,
  promote, demote, or relabel a candidate from those supporting fields.
- In particular, a candidate whose source `status` is `DISCOVERY_ONLY` remains
  `DISCOVERY_ONLY` even when its identity is `VERIFIED`, its economics are
  `INCOMPLETE`, or it looks worth monitoring after missing evidence arrives.
  The ordinary verb “wait” may describe a future next step, but the uppercase
  status `WAIT` is reserved exclusively for candidates whose source
  `status == "WAIT"`.
- `CANDIDATE`: every current identity, 24-hour coverage, liquidity, activity,
  trusted pool-age, economics, independent 50 bps measurement-buffer, and
  volatility/impermanent-loss stress gate passes. Say “worth further research,”
  never “you should invest.”
- `WAIT`: evidence is valid but one or more named gates failed. Account for
  every `reasonCode`, explaining each decision-relevant consequence in plain
  language for an ordinary answer; this is a successful research result.
- `DISCOVERY_ONLY`: discovery exists but protocol identity or chain measurement
  is not trusted enough. Never rank it as actionable.

When answering:

1. Internally build an `id -> status` map directly from the validated candidate
   objects. Count all three source statuses and, immediately before sending,
   verify every discussed pool is under its mapped source status. If any prose
   label or summary count disagrees, correct the prose; do not reinterpret the
   source enum. The internal map and raw enum names are not user-facing output.
2. Internally check `generatedAt`, `isStale`, `documentStatus`, source receipts,
   and the discovery/deep-analysis coverage relevant to the claim. Surface only
   their plain-language consequence unless technical detail was requested.
3. Prioritize source status `CANDIDATE`, then `WAIT`, then `DISCOVERY_ONLY`,
   preserving server rank within each group; present the classifications using
   the audience rules above.
4. For each discussed pool, show token symbols and the exact pool address or
   pool ID. Include protocol, identity, venue, selection bucket, and raw
   `reasonCodes` only for technical or audit-detail requests; otherwise explain
   only the decision-relevant evidence and risk in plain language.
5. For completed economics, use the exact decimal strings and never recalculate
   base units with floating point. An ordinary answer should include only the
   few figures that change the decision. A technical answer may report the full
   `$1,000` reference position, 24-hour volume and fees, entry/exit cost,
   impermanent loss, net benefit, margin basis points, 50 bps measurement
   buffer, volatility, and stress result.
6. Explain that source headline APR is discovery evidence only. A vfat
   cross-check, when present, remains side-by-side evidence with its own
   timestamp, fee window, active/total liquidity, and full-time-in-range
   assumption. Never average it into, substitute it for, or let it satisfy the
   platform's finalized 24-hour chain economics and transfer-tax gates; it is
   not APY or promised yield.
7. Explain unknown hooks, unsupported semantic identity, transfer-tax tokens,
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
- If the user asks to act, say this workflow cannot execute the position and
  requires a separately reviewed execution path.
