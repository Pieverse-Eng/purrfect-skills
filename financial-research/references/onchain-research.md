# Chain activity and token narratives

Research what is attracting attention on a chain, what a token/project claims
to represent, and which recent events and market observations support that
account. Do not turn an ordinary narrative question into a holder-distribution,
fund-flow or contract audit unless the user's question requires it.

## Identify the research subjects

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

## Choose evidence and tools

Keep the discovery results as the starting context; reuse their links and market
data rather than looking up the same information again. Use AgentKey for the
additional external evidence:

| Need | Starting tool or discovery approach | Scope and limitations |
| --- | --- | --- |
| Read a known project website, document or linked article | `Tavily/post_extract` | Extract the passages about the narrative or event. A failed or empty extraction is not evidence about the project. |
| Locate project background or an event's original source | `Tavily/post_search` | Use known official domains, project identifiers and relevant dates in the search parameters; check identity before attributing results. |
| Read X/social posts or investigate a discussion | Browse `social/twitter` for X, or discover the requested platform's directory | Describe the chosen social operation, then query known accounts, post URLs/IDs or the specific topic. Do not invent handles or endpoint names; search snippets alone do not establish what a post says. |
| Fill missing price-performance, volume or liquidity evidence | Browse `crypto/market` for prices/history or `crypto/dex` for pool/pair data | Reuse existing metrics first; query the exact chain and CA with the required time window. Do not substitute same-name assets. |

These are alternatives selected by the question, not a sequence of mandatory
calls. Browse with `purr agentkey discover --prefix <directory>`; if a listed
directory is unavailable, refresh the root catalog rather than guessing paths.
Follow the main skill's access rules. See [tool parameters](tool-parameters.md)
for provider mappings, field types and identifier semantics.

Explain the core narrative and recent developments using project websites,
social posts and relevant original sources. Attribute narratives to their
sources; distinguish project claims, recent events and independently verified
facts. Do not infer legitimacy, ownership rights or backing from a token name
or pair, or treat repeated promotional posts as independent confirmation.

When the question needs market evidence, obtain price performance, volume and
liquidity for the exact asset, preserving provider, pool/venue, observation time
and window. Do not sum overlapping samples or treat displayed liquidity as an
amount-specific executable quote. Skip market queries for narrative-only asks.

For an overview, summarize the returned tokens' narratives and relevant market
observations with names, symbols, exact CAs, source links and observation times.
For a single-token question, answer directly without forcing a chain overview.
Explain evidence gaps without converting popularity into an investment verdict.
