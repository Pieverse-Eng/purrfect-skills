# User-triggered position research

The Positions row AI icon starts research for that exact Paper or Live position.
Explain that it starts work, not merely a help panel. It preserves the selected
market, order draft and unsent chat. The Live Positions toolbar's AI analysis
button opens a dialog: choose one venue, then Analyze all positions. This covers
that venue's positions and spot balances, reported separately. It is independent
of the list filter. There is no Paper all-account research entry in this version.
The feature works regardless of the Coach hint switch.

Only the user's deliberate research action starts a new research task. A hint,
ordinary discussion or explanation of an existing report must not start search.
If asked only how to use it, describe the row icon without invoking tools or
fabricating a new web_action. If the entry is unavailable, explain the actual
runtime/account limitation instead of claiming the user can click a missing UI.

The host prepares scoped facts, existing news and, when needed, a permitted
external search. In a scoped research Run use these supplied sources and the
native financial-analysis Skill; do not start another external search from a
shell, another Agent or financial-research. The host's current-Run read tools
are the only available account reads. Do not prepare trades, save plans or
change Playbooks in the read-only research Run.

The UI reports a user-wide daily allowance (default 3, configurable), shared
across Agents, Paper/Live and both entries; reset is 00:00 UTC. Starting reserves
a slot; only a report confirmed saved consumes it. Definite failure/cancellation
releases it. Do not claim zero cost: existing Credits rules still apply. Do not
invent the user's remaining allowance; use the returned value.

A timeout, delivery_unknown or indeterminate search receipt is not failure.
Recover the original task through its original research entry/chat recovery,
retaining original session, Run, client request and target. The frontend/host
owns this operation: there is no model research-retry tool. Never tell the user
to open a new chat, change Agent or make another search to bypass uncertainty.
Later stored-news coverage cannot resolve the original uncertain search receipt
or bypass its report completion/persistence gate. Explain available news only as
provisional evidence; the host must resolve the original receipt first.
Viewing/recovering/explaining the original report does not start a new task;
explicitly updating sources is a new task and may use another daily slot.

Reports state exact mode/account/venue/position scope, source publication and
collection times, coverage, supporting and opposing evidence, assumptions and
missing information. Stored news is not an external search; empty search results
are not a failed tool and are not proof that no relevant event occurred.
