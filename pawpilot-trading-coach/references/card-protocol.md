# Versioned conversational card protocol

Publish with send_message target=current. The native tool argument `message`
is the visible text; `metadata.coachCard` contains the proposal below. Copy
prepared tool `data.message.text`, optional `reply_markup` and `data.metadata`
unchanged when publishing an order. Never invent an actionId or callback.
The server binds current user/instance/session/Run, stores a canonical card,
and returns an opaque version/id/kind reference for stream and history.

All cards have version=1, kind, title (<=200 characters).

| kind | Additional required fields |
| --- | --- |
| paper_practice_invite | optional known canonical marketKey |
| web_actions | actions array (one to four), see below |
| playbook_proposal | expectedVersion, complete profile; use update.kind=patch for revisions |
| before_trade | actionId, explanation, facts (may be empty) |
| holding | positionId, explanation, facts; optional registered actionId |
| trade_review | cycleId, explanation, facts; optional lesson (string, proposed and unconfirmed) |
| trade_patterns | explanation, facts |
| live_readiness | explanation, facts, five topics |

## Playbook proposal shape

Use the literal field `profile`, containing summary, holdingStyle, decisionStyle,
riskComfort and principles. Unknown style/comfort values are null. For an existing
profile, read its current expectedVersion and preserve every unrelated field and
principle. Describe the requested change in `update:{kind:"patch",set?,appendPrinciples?,removePrinciples?}`;
the host applies it to that immutable version and computes the complete saved profile
and added/removed diff. Omit unchanged `set` fields. Exact duplicate additions are
deduplicated; overflow is a blocker rather than permission to discard old rules.

Example only: the read returned version 1, the summary and one existing principle
below, and null style/comfort answers. The user explicitly asks to append the four
Paper practice rules while retaining the old principle:

```json
{"version":1,"kind":"playbook_proposal","title":"Paper practice rules","expectedVersion":1,"profile":{"summary":"The user's confirmed trading preferences","holdingStyle":null,"decisionStyle":null,"riskComfort":null,"principles":["Review the agreed thesis before each decision","This Paper practice uses small positions","This Paper practice uses at most 3x leverage","This Paper practice does not add after a loss","This Paper practice defines exits before entry"]},"update":{"kind":"patch","appendPrinciples":["This Paper practice uses small positions","This Paper practice uses at most 3x leverage","This Paper practice does not add after a loss","This Paper practice defines exits before entry"]}}
```

These are user-requested example rules, not account facts or default trading limits.
Adapt the profile and expectedVersion from the successful read and the user's request.
The first profile uses expectedVersion 0, all five profile fields and
`update:{kind:"replace"}`. A legacy complete `profile` without update is accepted as
a replacement, but omitting old principles requires explicitly requested removals
in `update.removePrinciples`. The field `proposed` is unsupported. Never remove
`kind` to repair a rejected proposal. Read the trading preferences reference for
same-Run consent and save receipts.

## Analysis cards

Analysis cards may include questions (up to three). `facts` is an array of
{callId,queryId} from completed same-Run native facts results, not copied model
numbers. A v3 pawpilot_paper_trade_review citation copies the successful response's
top-level `callId` and `data.facts.queryId`, not the assistant's function/tool-call
ID (bounded perpetual candidate-list trades or exact-cycle
timeline). Legacy paper_read/terminal_read query receipts remain supported.
Analysis panels require your send_message publication; preparation and practice
invite proxies publish only their own original draft/invite cards.
holding requires the cited owned position; trade_review
requires the cited cycle/history record. Read facts first; other than an order
card, numeric cards cannot cite an empty array. Keep explanations <=2000 chars.

live_readiness topics are exactly practice, stop_use, leverage, result,
plan_exits; each has status supported/discuss/unknown, criteria and explanation.
Coach chooses and explains criteria from actual facts and discussion. These are
suggestions, not backend gates. Missing denominators remain unknown. Do not
pretend a checklist has passed or offer an invented order button.

A proposal is not authoritative until the host returns its opaque reference.
If publication cannot be confirmed, retain the visible answer and original
scope; do not create another order or silently claim the card was saved.

## Publication outcome and recovery

On an acknowledgement-capable Hermes Run, send_message returns success plus
publication status, original message_id, sessionId, runId and hash. Only
success=true after registration/delivery means the usable card was delivered.
Registered alone with success=false means delivery is uncertain, not success.
A rejected card/action reference is not a plain-text substitute for a Review UI.
Explain the specific blocker; do not claim Edit/Review is available.

If retrySameInput=false, do not repeat identical failing inputs. For a transient
unknown publication with retrySameInput=true, at most one retry of the identical
structured message in the same Run can recover its original publication identity.
Do not prepare a new order, change its action ID, or repeatedly publish explanations.
If still uncertain, preserve the original card/action and tell the user what is
unconfirmed. Older runtimes without acknowledgement must not be presented as
having confirmed durable delivery. Reopening reads the original receipt.

## Web actions versus answers

Use clarify for a missing answer, not for invented executable callbacks. A
web_actions card may carry these exact typed actions (each also has label):
- kind=navigate, view=paper|positions|reviews|lessons, optional canonical marketKey.
- kind=focus_order, field=amount|leverage|protection.
- kind=review_draft, actionId from a registered current-Run draft.
No arbitrary URL, script, trading parameter or submission is allowed. A focus or
navigation button never trades. Review/Edit requires a new manual preview and
confirmation. If the web operation is unavailable or another task is busy, keep
the original scope and explain the actual state; do not invent successful action.

## Correct a rejected request

Pass metadata as an actual JSON object. The minimal navigation publication is:

```json
{"target":"current","message":"You can practise with simulated funds.","metadata":{"coachCard":{"version":1,"kind":"paper_practice_invite","title":"Try Paper Trading"}}}
```

It needs neither a marketKey nor a financial read. When the full protocol is not
yet loaded, read it before constructing a card. A failure's allowedValues shows
valid enum choices, not every required field. Use failure.fields.path and
unknownKeys to fix arguments, then validate against this reference/tool schema.
An encoded or malformed metadata string is not a card. A plain-text message
claiming an “entry” is not a clickable navigation card. After rejection do not
claim the card exists or direct the user to a nonexistent preferences page.
