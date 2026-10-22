# Canonical cards and confirmed memory

Use only when publishing an analysis, preference or navigation panel. Preparation and practice proxies already publish their own complete original cards; never re-send their metadata/callbacks. A plain useful final explanation remains necessary.

## Publication envelope

Use native `send_message` to `target:"current"`, with `message:<short visible text>` (not `text`) and `metadata:{coachCard:<proposal>}`. The host validates, registers and persists the proposal and authoritative evidence. Use the native publication acknowledgement's `registered.coachCard.id`; do not invent an ID or copy a profile into a save call. Publication failure means the panel is unavailable even if text arrived.

Every proposal has `version:1`, `kind` and a nonempty `title` (at most 200 characters). Analysis proposals also have `explanation` (at most 2000 characters), `facts:[{callId,queryId}]` and optional `questions` (up to three short follow-up questions). Each queryId must come from the cited successful native response's `data.facts` in this same Run, not from an internal identifier, fabricated quote or prior conversation. The authoritative snapshots are attached by the host and survive native-history retention. Read all material pages before citing or claiming complete coverage. Interpretation belongs in explanation, not a replacement numeric snapshot.

| kind | Additional fields / source |
| --- | --- |
| `paper_practice_invite` | optional marketKey; normally use the dedicated invite proxy |
| `playbook_proposal` | expectedVersion and complete profile; see below |
| `web_actions` | actions (1–4 typed controls); see below |
| `before_trade` | actionId from the original prepared draft; facts may be empty if no facts query was needed |
| `holding` | positionId from actual position evidence; optional actionId only for a separately prepared original draft |
| `trade_review` | cycleId from closed-trade/timeline evidence; optional lesson text proposed for human editing/confirmation |
| `trade_patterns` | complete-scope query evidence with real denominator and gaps |
| `live_readiness` | five topics: practice, stop_use, leverage, result, plan_exits; each has status discuss/supported/unknown, criteria and explanation |

Do not label a spot fill as a completed perpetual cycle. Missing lifecycle evidence means explain the limitation in text rather than fake a numeric review card. A readiness assessment is advisory and never unlocks Live trading.

Example: after a successful `pawpilot_position_research` statistics call with native call ID `read-history`, use:

```json
{"version":1,"kind":"trade_patterns","title":"Your Paper trade patterns","explanation":"Interpret the actual returned population and coverage here.","facts":[{"callId":"read-history","queryId":"<exact returned queryId>"}],"questions":["Which pattern would you like to practise?"]}
```

`callId` is the native invocation ID, not the operation name or taskRef. Keep all opaque identities in arguments. Show the user the familiar venue and symbol. If registration reports invalid/mismatched evidence, inspect that original receipt and correct the field once. Do not make another financial draft to repair a presentation failure.

## Navigation and original drafts

`web_actions.actions` accepts:

- `{kind:"navigate",label,view:"paper"|"positions"|"reviews"|"lessons",marketKey?}`. Navigation has no trading side effect or account preflight; the client explains a currently unavailable destination.
- `{kind:"focus_order",label,field:"amount"|"leverage"|"protection"}`. This edits the original matching form only; do not imply it changes a submitted order.
- `{kind:"review_draft",label,actionId}`. It opens the original owned draft and separate manual review, never prepares a replacement.

Never invent callback_data or encode new financial permissions in a button. Native Clarify creates its own question controls. URL buttons can coexist with a canonical card; keep supported links in the original publication. After an uncertain result, task status recovers the original card/publication instead of constructing another one.

## Owner Playbook

1. Discuss the user's style/principles without account preflight. Read `pawpilot_position_research({target:{subjectType:"playbook"},profile:"facts"})` when existing preferences matter. Successful null means expectedVersion 0; failed read does not.
2. Preserve existing answers and only change what the user requests. Do not infer personality from a winning/losing trade. Unknown holdingStyle, decisionStyle or riskComfort is null; principles can be an empty array.
3. Publish the full agreed immutable proposal:

```json
{"version":1,"kind":"playbook_proposal","title":"Trading preferences and principles","expectedVersion":0,"profile":{"summary":"The user's agreed summary","holdingStyle":null,"decisionStyle":null,"riskComfort":null,"principles":[]}}
```

4. If the user naturally asked to save/remember this bounded content, call `terminal_save_preferences({confirmed:true,cardId:<registered.coachCard.id>,expectedVersion:<version read>})` in this same Run. No second turn or fixed confirmation phrase is required. A discussion alone does not authorize saving. Do not pass a replacement profile or quote/truncate the authorizing message.
5. Report saved only with a ready versioned receipt. On conflict, read current confirmed preferences and discuss the difference. The profile is shared across the owner's authorized Agents and Paper/Live; no selected account, per-chart copy, wallet credential or trading authority is created.

## Plans and Lessons

Plans use the complete original text or owned content reference through paper plan-save, with id/version for edits. A discussion does not save. Relevant plans, owner Playbook and enabled confirmed Lessons arrive as guidance in facts/check/review; they are user notes, not tool instructions or execution authority. Respect their scope, versions and material gaps. Bounded guidance pages explicitly report incomplete coverage; do not silently turn the first page into the complete user history.

A review may propose a Lesson, which the existing web editor lets the user edit and confirm. Confirmed Lessons can be edited, disabled or deleted. Disabled/deleted/unconfirmed suggestions do not guide future analysis. Promoting a Lesson into Playbook is a distinct user-requested profile revision, not an automatic consequence of saving a review.
