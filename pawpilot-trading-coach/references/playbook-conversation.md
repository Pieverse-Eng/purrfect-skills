# Trading preferences and principles

Call these “交易偏好与原则” or “trading preferences and principles” to the user.
The stored protocol still calls them Playbook. This is a shared user profile for
Paper and Live, not a fixed trading strategy or a separate web page.

1. Read terminal_read operation=playbook when available. Retain existing answers.
   A successful null profile means expectedVersion=0; otherwise use the returned version.
   A failed read does not establish version 0 or an empty profile. Without a
   readable version, discuss a draft and explain that persistence is unavailable.
2. Ask one missing dimension at a time: holding rhythm, decision style, loss
   comfort. Usually three questions, at most five when clarification is needed.
   If clarify is available, use a few neutral choices, Skip and free-form input.
   Otherwise ask the single question in ordinary text and wait for the reply. Finish the
   question text before calling clarify, then wait for that answer. Do not ask
   the next question in the same turn or pack three dimensions into multi_select.
3. Summarize “you mentioned”, proposed principles and unanswered/null fields
   separately. Read card-protocol, then publish one playbook_proposal with the
   confirmed current expectedVersion and profile. All profile fields must be
   present: summary is a nonempty string, principles is an array; holdingStyle,
   decisionStyle and riskComfort are nullable strings.
4. After registered publication, ask for explicit confirmation: “确认保存” or
   “Save these preferences”. A description, skip, “sounds like me” or a request
   to explain a term is still discussion. It must not create rules.
5. When terminal_save_preferences is available and the user's new turn explicitly
   confirms, pass confirmed=true, that exact authorizingMessage, registered
   cardId and expectedVersion. The host reads the original profile: do not send
   replacement fields. Say “saved, version N” only after status=ready and the
   returned version. A proposal/card or successful send_message is not a save.

For a revision discuss edits, read the current version, register a revised
proposal and get a new explicit confirmation. Keep prior confirmed versions.
If the user asks to edit after seeing the summary, continue the conversation;
no page search or mandatory form is needed. When the runtime lacks the save tool,
explain that saving is unavailable there; do not invent a Coach/Playbook page or
promise a fake Edit/Confirm control. Readonly trade-research Runs cannot save
preferences: end that discussion context before a new ordinary confirmation.

The profile is a note. It grants no order execution permission, sets no new Live
unlock requirement, and never turns observed performance into a user rule.
