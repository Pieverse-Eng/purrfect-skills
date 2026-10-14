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
