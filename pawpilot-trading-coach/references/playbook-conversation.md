# Trading preferences and principles

Call these "trading preferences and principles" to the user.
The stored protocol still calls them Playbook. This is a shared user profile for
Paper and Live, not a fixed trading strategy or a separate web page.

1. Read `pawpilot_position_research({target:{subjectType:"playbook"},profile:"facts"})`
   when available, or the advertised legacy terminal_read operation=playbook.
   Retain existing answers. No selected trading account is required.
   A successful null profile means expectedVersion=0; otherwise use the returned version.
   A failed read does not establish version 0 or an empty profile. Without a
   readable version, discuss a draft and explain that persistence is unavailable.
2. Discuss only what the user requests. Qualitative principles such as "small
   positions", "do not add after a loss" and "define exits before entry" can stay
   qualitative in discussion and the saved profile. An explicit "do not save yet"
   keeps the conversation unsaved. Ask for numerical limits only when a concrete
   trade configuration needs them. Reuse confirmed risk principles; model suggestions
   remain proposals until the user agrees and never become reported user facts.
   For a requested style interview, ask one missing dimension at a time: holding
   rhythm, decision style, loss comfort. Ask only when clarification is needed.
   If clarify is available, use a few neutral choices, Skip and free-form input.
   Otherwise ask the single question in ordinary text and wait for the reply. Finish the
   question text before calling clarify, then wait for that answer. Do not ask
   the next question in the same turn or pack three dimensions into multi_select.
3. Summarize “you mentioned”, proposed principles and unanswered/null fields
   separately. Read card-protocol, then publish one playbook_proposal with the
   confirmed current expectedVersion and the literal `profile` field. All profile fields must be
   present: summary is a nonempty string, principles is an array; holdingStyle,
   decisionStyle and riskComfort are nullable strings. For a revision, include
   `update:{kind:"patch",set?,appendPrinciples?,removePrinciples?}` with only the
   requested changes. Keep the complete profile consistent with the read plus that
   patch; the host materializes the immutable base and preserves unrelated answers.
   Use appendPrinciples to add rules. Only an explicit removal permits naming an
   exact existing rule in removePrinciples. See card-protocol's valid JSON example.
4. A natural request to save or remember this bounded content is sufficient consent;
   publish and save in that SAME Run. No fixed phrase or second turn is required.
   A description, skip, "sounds like me" or a request to explain a term remains discussion.
5. When terminal_save_preferences is available and saving is requested, pass
   confirmed=true, cardId from `send_message`'s `registered.coachCard.id` and the
   same expectedVersion. The host binds the authorizing Run; do not copy or shorten
   the user message or send replacement profile fields. Say "saved, version N" only after status=ready and the
   returned version. A proposal/card or successful send_message is not a save.

For a revision discuss edits, read the current version and register the requested
changes. An explicit save request authorizes saving those changes in the same Run.
Keep prior confirmed versions; reread and discuss differences on a version conflict.
If the user asks to edit after seeing the summary, continue the conversation;
no page search or mandatory form is needed. When the runtime lacks the save tool,
explain that saving is unavailable there; do not invent a Coach/Playbook page or
promise a fake Edit/Confirm control. Readonly trade-research Runs cannot save
preferences: continue saving in an ordinary conversation after the user's request.

The profile is a note. It grants no order execution permission, sets no new Live
unlock requirement, and never turns observed performance into a user rule.
