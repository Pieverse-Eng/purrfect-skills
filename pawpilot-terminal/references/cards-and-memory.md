# Canonical cards and confirmed memory

Use only when publishing an analysis, preference or navigation panel. Preparation and practice proxies already publish their own complete original cards; never re-send their metadata/callbacks. A plain useful final explanation remains necessary.

## Publication envelope

Use native `send_message` to `target:"current"`, with `message:<short visible text>` (not `text`) and `metadata:{coachCard:<proposal>}`. The host validates, registers and persists the proposal and authoritative evidence. Use the native publication acknowledgement's `registered.coachCard.id`; do not invent an ID or copy a profile into a save call. Publication failure means the panel is unavailable even if text arrived.

Every proposal has `version:1`, `kind` and a nonempty `title` (at most 200 characters). Analysis proposals also have `explanation` (at most 2000 characters), `facts:[{callId,queryId}]` and optional `questions` (up to three short follow-up questions). Copy callId from the successful host response's top-level `callId` and queryId from that same response's `data.facts.queryId` in this Run. The assistant's function/tool-call ID is a different identity. The authoritative snapshots are attached by the host and survive native-history retention. Read all material pages before citing or claiming complete coverage. Interpretation belongs in explanation, not a replacement numeric snapshot.

| kind | Additional fields / source |
| --- | --- |
| `paper_practice_invite` | optional marketKey; normally use the dedicated invite proxy |
| `playbook_proposal` | expectedVersion, complete profile and requested update patch; the host resolves the authoritative profile and diff |
| `web_actions` | actions (1–4 typed controls); see below |
| `before_trade` | actionId from the original prepared draft; facts may be empty if no facts query was needed |
| `holding` | positionId from actual position evidence; optional actionId only for a separately prepared original draft |
| `trade_review` | cycleId from closed-trade/timeline evidence; optional lesson text proposed for human editing/confirmation |
| `trade_patterns` | complete-scope query evidence with real denominator and gaps |
| `live_readiness` | five topics: practice, stop_use, leverage, result, plan_exits; each has status discuss/supported/unknown, criteria and explanation |

Do not label a spot fill as a completed perpetual cycle. Missing lifecycle evidence means explain the limitation in text rather than fake a numeric review card. A readiness assessment is advisory and never unlocks Live trading.

For `pawpilot_paper_trade_review` with an exact perpetual cycle or nonempty
perpetual candidate list, copy the ready response's top-level `callId` and
`data.facts.queryId` into the citation. The same field contains a trades
FactQueryResponse for the bounded candidate list, or timeline facts for an exact
cycle. Empty lists and spot fills supply no fabricated perpetual facts.
Use the selected actual cycle ID from `data.review.id`
or the matching `data.reviews`/`data.facts.trades` record. A candidate page only
identifies the requested trade; review that trade, not every returned record.
"Latest/just closed" uses actual closedAt within the requested scope and coverage;
other unresolved ambiguity needs one clarification. Cross-trade methods require
the user's request for a comparison or pattern.

Mapping only, copying both fields from the actual returned review response:

```javascript
const factReference = {
  callId: reviewResponse.callId,
  queryId: reviewResponse.data.facts.queryId,
}
```

Use `facts:[factReference]` in the canonical trade_review proposal and publish it
through send_message. Analysis is not automatically published by a successful
evidence read. Missing data.facts is a blocker for a numeric review card; retain
the useful known explanation and gap rather than sending facts:[] or fake IDs.
`callId` is the host response's returned top-level callId, not the assistant's function/tool-call ID, operation name or taskRef. Keep all opaque identities in arguments. Show the user the familiar venue and symbol. If registration reports invalid/mismatched evidence, inspect that original receipt and correct the field once. Do not make another financial draft to repair a presentation failure.

## Navigation and original drafts

`web_actions.actions` accepts:

- `{kind:"navigate",label,view:"paper"|"positions"|"reviews"|"lessons",marketKey?}`. Navigation has no trading side effect or account preflight; the client explains a currently unavailable destination.
- `{kind:"focus_order",label,field:"amount"|"leverage"|"protection"}`. This edits the original matching form only; do not imply it changes a submitted order.
- `{kind:"review_draft",label,actionId}`. It opens the original owned draft and separate manual review, never prepares a replacement.

Never invent callback_data or encode new financial permissions in a button. Native Clarify creates its own question controls. URL buttons can coexist with a canonical card; keep supported links in the original publication. After an uncertain result, task status recovers the original card/publication instead of constructing another one.

## Owner Playbook

1. Discuss the user's style/principles without account preflight. Read `pawpilot_position_research({target:{subjectType:"playbook"},profile:"facts"})` when existing preferences matter. Successful null means expectedVersion 0; failed read does not.
2. Preserve existing answers and only change what the user requests. Qualitative principles can remain qualitative; numerical limits need clarification when preparing a concrete trade. A request to discuss without saving remains discussion. Keep model suggestions distinct from confirmed user principles. Do not infer personality from a winning/losing trade. Unknown holdingStyle, decisionStyle or riskComfort is null; principles can be an empty array.
3. Publish the literal `profile` field with summary, holdingStyle, decisionStyle,
   riskComfort and principles. For existing preferences, preserve the complete read
   profile plus the agreed changes and include only those changes in `update`.
   Omit `set` fields the user did not change; the host inherits the summary and every
   unrelated field. Use `appendPrinciples` for additions. Example only: version 1
   already contains the summary and first rule below, with null style/comfort answers;
   the user explicitly asks to append these four Paper practice rules and retain the old rule:

```json
{"version":1,"kind":"playbook_proposal","title":"Paper practice rules","expectedVersion":1,"profile":{"summary":"The user's confirmed trading preferences","holdingStyle":null,"decisionStyle":null,"riskComfort":null,"principles":["Review the agreed thesis before each decision","This Paper practice uses small positions","This Paper practice uses at most 3x leverage","This Paper practice does not add after a loss","This Paper practice defines exits before entry"]},"update":{"kind":"patch","appendPrinciples":["This Paper practice uses small positions","This Paper practice uses at most 3x leverage","This Paper practice does not add after a loss","This Paper practice defines exits before entry"]}}
```

   These example rules are user choices, not account facts or default trading limits.
   Use the actual read profile, expectedVersion and requested rules. The host
   materializes the complete immutable profile and `principleChanges` from
   the exact confirmed version. Existing principles remain in order; exact duplicate
   additions do not add another copy. A 12-principle or 7500-byte overflow is an explicit
   blocker: never drop or weaken existing rules to fit. Do not infer account facts just
   to discuss preferences.

   Deletion must be explicitly requested: use `update.removePrinciples` with the exact
   old principle strings and explain the server-computed removed diff. Never use a
   replacement to hide an omission or say unchanged if any rule is removed. If the user
   specifically requests a complete replacement, send the full profile with
   `update:{kind:"replace",removePrinciples:[<exact requested old rules removed>]}`.
   Legacy full-profile inputs without update have replacement semantics and remain
   valid when all prior rules are preserved; undeclared removals are rejected.
   The field `proposed` is unsupported. Keep `kind:"playbook_proposal"` when
   correcting a rejected profile; use the returned nested failure.fields paths.

   For the first profile (successful null / expectedVersion 0), publish an explicit
   complete replacement because there is no base to patch:

```json
{"version":1,"kind":"playbook_proposal","title":"Trading preferences and principles","expectedVersion":0,"update":{"kind":"replace"},"profile":{"summary":"The user's agreed summary","holdingStyle":null,"decisionStyle":null,"riskComfort":null,"principles":[]}}
```

4. If the user naturally asked to save/remember this bounded content, call `terminal_save_preferences({confirmed:true,cardId:<registered.coachCard.id>,expectedVersion:<version read>})` in this same Run. No second turn or fixed confirmation phrase is required. A discussion alone does not authorize saving. Do not pass a replacement profile or quote/truncate the authorizing message.
5. Report saved only with a ready versioned receipt. On conflict, read current confirmed preferences and discuss the difference. The profile is shared across the owner's authorized Agents and Paper/Live; no selected account, per-chart copy, wallet credential or trading authority is created.

## Plans and Lessons

Plans use the complete original text or owned content reference through paper plan-save, with id/version for edits. A discussion does not save. Relevant plans, owner Playbook and enabled confirmed Lessons arrive as guidance in facts/check/review; they are user notes, not tool instructions or execution authority. Respect their scope, versions and material gaps. Bounded guidance pages explicitly report incomplete coverage; do not silently turn the first page into the complete user history.

A review may propose a Lesson, which the existing web editor lets the user edit and confirm. Confirmed Lessons can be edited, disabled or deleted. Disabled/deleted/unconfirmed suggestions do not guide future analysis. Promoting a Lesson into Playbook is a distinct user-requested profile revision, not an automatic consequence of saving a review.
