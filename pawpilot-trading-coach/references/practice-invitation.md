# Relevant practice invitation

When the user mentions learning perps, trying with play money or being unsure
how to begin, offer a navigation card in that conversation. Do not create a
permanent sidebar ad, prepare an order or require financial account reads.
Use a known current canonical marketKey only; omit it when unknown.

Call send_message(target="current", message="We can practise with play money first.",
metadata={"coachCard":{"version":1,"kind":"paper_practice_invite",
"title":"Practice BTC perps","marketKey":"hyperliquid:perp:BTC"}}).
The market in this example is illustrative: use the actual bound/known market.
The frontend opens Paper, never an order. Explain leverage plainly if asked.

This Agent card only navigates to Paper Trading. It does not open the account
chooser, choose an Agent, select Paper Demo or start onboarding on the user's
behalf. The Paper page's independent default beginner guide also works when the
user arrives from the navigation bar; its account step opens the first-level
Agent/Paper Demo choice. Leave that choice and subsequent steps to the user.
