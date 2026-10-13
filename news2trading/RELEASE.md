# PawPilot News release handoff

Original publication handoff (historical):
[purrfect-skills #149](https://github.com/Pieverse-Eng/purrfect-skills/pull/149) and
[purrfect-claw-platform #2968](https://github.com/Pieverse-Eng/purrfect-claw-platform/pull/2968).
The multi-source active-analysis follow-up is linked in its PR descriptions;
those historical PR numbers are not the release identity for this change.

Use the final reviewed Skills commit, not the older `1116466` handoff snapshot.
The backend must pin that exact commit before rebuilding Tenant images. Local
working-tree fixes are not shipped by the existing submodule pin.

## Included workflows

- Subscriptions use the server Profile, optimistic version checks and verified
  write receipts. Independent Web/external preferences preserve legacy delivery
  settings unless explicitly changed. Item reads pin the queued item/version.
- Background batches may use authorized read-only market data, but do not
  prepare/execute trades or change accounts/integrations. Publication is attempted
  once; the final activation reply is always `NO_REPLY` after invocation.
- API `context_missing` failures retain validated top-level `target`,
  Web/external details and canonical text, including external-only errors that
  provide no Web/external wrapper. `external.status: accepted` is known channel
  acceptance with incomplete context, not complete success. Diagnostic IDs are
  nonblank, at most 512 characters and control-free; conflicting external targets
  and invalid additive fields are omitted without discarding other valid evidence.
  Unknown upstream fields are not copied into diagnostics. No resend or mirror
  is attempted without the successful runtime/session receipt.
- Hermes local mirror failures also retain the target, canonical text and any
  Web/external receipts. Repairs must not resend external messages.
- Explicit active holdings-news analysis is an ordinary chat report using the
  supplied account/holdings and last-24-hour platform news evidence (PANews plus
  the optional original X-post channel). X materials are source-provided post text,
  not Grok-generated summaries; context slices and search coverage remain partial.
  The Skill gains no search tools; the platform collector uses no model.
  X queries use the explicit request's actual holding tickers, not a fixed crypto
  allowlist; only asset identifiers/optional aliases are sent, not wallet addresses,
  quantities or direction. Cover stocks, stock-related derivatives and unfamiliar
  tokens too; preserve market identities and disclose unresolved identities,
  missing/omitted/stale evidence and query coverage. Ticker relevance does not
  establish issuer identity or ownership of shares.
  No-data requests still receive a readable answer, not only `NO_REPLY`. This mode
  does not invoke Profile/publication scripts, subscribe, search additional sources,
  send Telegram/LINE, or prepare/execute trades.

## Validation

From the Skills repository:

```bash
python3 -m unittest discover -s news2trading/scripts -p 'test_*.py'
node --test scripts/test-materialize-news2trading.mjs
bash scripts/check-skill-shadowing.sh
git diff --check
```

The API regression tests cover HTTP 502 partial publication for both runtimes
and Telegram/LINE, CLI diagnostics, a single POST, no Hermes mirror on API
failure, external-only targets, conflicting destinations, identifier bounds and
control characters, malformed additive fields, batch binding, and legacy errors.
The materialization tests check active-mode rules in both runtime artifacts; these
static contract assertions are not model-behavior evaluations.

The pinned-Hermes SessionDB integration is optional and requires
`NEWS2TRADING_HERMES_REAL=1` plus the matching Hermes runtime/PYTHONPATH. A skip
does not validate real SessionDB routing or readback.

## Rollout acceptance

1. Pin the final Skills commit in the matching backend; rebuild and deploy both
   runtime images, and verify the installed skill files rather than only the pin.
2. Follow the final backend's migration procedure and ledger. The current News
   prerequisites are `185_news_web_feed.sql` and `186_news_pointer_snapshots.sql`;
   the historical 169/174/175 handoff numbers are outdated. This XSearch/Skills
   follow-up adds no migration; do not reapply already-ledgered prerequisites.
3. Verify Web-only publication without a paired external recipient, mixed
   publication, and accepted-but-context-incomplete diagnostics without resending.
4. Verify real Telegram/LINE delivery and Hermes session routing/readback.
5. Verify explicit active reports for multiple assets, no relevant news, incomplete
   source coverage, and single-asset requests; page refresh is not analysis consent.
   Active analysis extends the original handoff; product-scope acceptance and
   frontend integration remain separate gates. Frontend #933 does not implement
   that action. Optional RSS sources and their opt-in flag have been removed
   from the companion backend pending publisher-permission review. Public/manual
   feed/item reads and background subscription matching remain PANews-only.
   The optional backend XSearch read runs only for an explicit holdings analysis,
   using that request's current assets; it is not a global scheduled collector;
   enable it only after real X API access/response/cost/permission validation and
   pinning this Skills release in the backend's tenant images. This Skills change
   adds no schema migration or publication protocol. Retaining PANews or using X API
   does not establish collection/storage/display/model rights; verify the
   applicable provider and source agreements separately.

Local tests and a merged Skills PR alone do not establish deployed image contents,
live source availability, production migration success, or external delivery.
