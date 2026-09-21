# Chain and project research

For the supported CLI discovery chains, map Robinhood Chain to `robinhood`,
BNB Chain to `bnb`, and Solana to `solana`. This lookup coverage is not a limit
on broader read-only research through AgentKey.

For a requested chain overview:

```bash
purr market trending --chain <chain>
```

For a specific token, reuse its known chain, contract address (CA), links and
evidence. If a lookup is needed:

```bash
purr market token --chain <chain> <ca>
```

The latter returns the same `chain` and `candidates` shape as trending, with at
most one candidate. Do not run trending to find an explicitly supplied CA.
Resolve ambiguous identities before lookup; never guess a CA or chain. Empty
candidates mean no match from this provider, not that the token does not exist.
Provider errors are lookup failures.

Preserve exact CAs, chains, pool names and project links. Trending is a discovery
sample, not a chain-wide ranking, safety endorsement or recommendation list.
For an overview, cover returned candidates unless the user narrows the scope;
acknowledge missing evidence rather than silently omitting candidates.

Use AgentKey to retrieve project documentation, websites, social posts and
relevant original sources. Attribute narratives to their sources; distinguish
project claims, recent events and independently verified facts. Do not infer
legitimacy, ownership rights or backing from a token name or pair.

When the question needs market evidence, obtain price performance, volume and
liquidity for the exact asset, preserving provider, pool/venue, observation time
and window. Do not sum overlapping samples or treat displayed liquidity as an
amount-specific executable quote. Skip market queries for narrative-only asks.

Explain the requested facts and evidence limitations without turning popularity
or price movement into a reason to buy, sell or wait for an entry.
