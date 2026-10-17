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
| playbook_proposal | expectedVersion, editable profile; see Playbook reference |
| before_trade | actionId, explanation, facts (may be empty) |
| holding | positionId, explanation, facts; optional registered actionId |
| trade_review | cycleId, explanation, facts; optional lesson (string, proposed and unconfirmed) |
| trade_patterns | explanation, facts |
| live_readiness | explanation, facts, five topics |

Analysis cards may include questions (up to three). `facts` is an array of
{callId,queryId} from completed same-Run paper_read/terminal_read query results,
not copied model numbers. holding requires the cited owned position; trade_review
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
