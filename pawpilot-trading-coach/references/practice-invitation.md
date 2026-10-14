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
