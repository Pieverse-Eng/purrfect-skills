# Discuss and confirm a trading style

If terminal_read is available, first read operation=playbook. Existing answers
and user-provided context count: do not ask again. If the profile cannot be
read, say so rather than claiming there is no confirmed profile.

Ask about one missing dimension at a time, usually about three short questions:
holding rhythm, preferred decision style, and comfort with losses. Accept a
skip/null, free text or a changed mind. Ask another only when clarification is
needed, usually no more than five. If enough was already said, summarise now.
Do not prescribe a fixed strategy or infer that a percentage means balance,
notional or risk budget. Distinguish preferences from proposed principles.

Publish an editable playbook_proposal card: version=1, title, expectedVersion
(the read confirmed version, or 0 when the host confirmed none), and profile:
summary, holdingStyle, decisionStyle, riskComfort (nullable strings), principles
(array of explicit proposed rules). Do not invent expectedVersion after a read
failure. Without the read capability, discuss a text draft and explain that
confirmation needs the account's Coach surface.

The user edits and explicitly confirms in the web UI; only then is a new version
saved. A conversational yes does not itself create confirmed rules. Revisions
use the latest version and original human confirmation flow. No compulsory
first-use interview, automatic saving or interruption of ordinary trading.
