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
| Read X/social posts or investigate a discussion | Select a social operation below | Query known accounts, post URLs/IDs or the specific topic. Do not invent handles; search snippets alone do not establish what a post says. |
| Fill missing price-performance, volume or liquidity evidence | Select a market or DEX operation below | Reuse existing metrics first; resolve the exact token or pool and time window. Do not substitute same-name assets. |

These are alternatives, not mandatory calls. Follow the main skill's access
rules and describe a listed operation directly. If none fits, discover within
`social/twitter`, `crypto/market` or `crypto/dex` as appropriate, or discover the
requested platform. If a directory is unavailable, refresh the root catalog
rather than guessing paths.

### Web sources: Tavily parameters

| Tool | Parameters and semantics |
| --- | --- |
| `Tavily/post_search` | Required `query: string`. Optional `include_domains` / `exclude_domains`: arrays of domain strings; `max_results`: integer 0–20 (default 5); `topic`: `general` (default), `news` or `finance`; `search_depth`: `basic`, `advanced`, `fast` or `ultra-fast`; `start_date` / `end_date`: `YYYY-MM-DD` strings; `chunks_per_source`: integer 1–3 (default 3), for advanced search. |
| `Tavily/post_extract` | Required `urls: string`: **one complete URL**, never comma-joined URLs or an array encoded as a string. Use an array of 1–20 URLs only if the live schema supports it. Optional `query: string`: selects excerpts, not full-page content; `chunks_per_source`: integer 1–5 (default 3), at most 500 characters each with `query`; `extract_depth`: `basic` (default) or `advanced`; `format`: `markdown` (default) or `text`; `timeout`: number, 1–60 seconds. |

Usually omit search's `include_answer` and `include_raw_content`; extract the
selected source instead. Their provider types are boolean or `basic`/`advanced`,
and boolean or `markdown`/`text`, respectively; do not assume union support when
the AgentKey schema omits their types.

Use extraction `query` for passages. If a required section exceeds the excerpt
limit, omit `query`, save the response and filter locally; do not repeatedly
rewrite queries to reconstruct a document. Advanced extraction does not remove
excerpt limits or guarantee completeness. Inspect `results`, `failed_results`
and actual content; an error or cookie page is not evidence.

Sources: [Tavily Search](https://docs.tavily.com/documentation/api-reference/endpoint/search),
[Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract),
[OpenAPI](https://docs.tavily.com/documentation/api-reference/openapi.json).

### Social and market parameters

| Discovery path → execution name | Parameters | Key semantics |
| --- | --- | --- |
| `social/twitter/post_search_tweets` → `Sorsa/post_search_tweets` | Required by provider: `query: string`; optional `order: string`, `next_cursor: string`. | `order`: `popular` or `latest`. Supports X search operators. |
| `social/twitter/post_tweet_info` → `Sorsa/post_tweet_info` | `tweet_link: string`. | Complete tweet URL or tweet ID, not a profile URL. |
| `social/twitter/post_user_tweets` → `Sorsa/post_user_tweets` | User identifier: `username`, `user_link` or `user_id`, each string; optional `next_cursor: string`, `with_replies: boolean`. | Profile URL field: `user_link`, not `link`. Keep numeric user IDs as strings. |
| `crypto/market/GetTokenPriceHistory` → `Chainbase/GetTokenPriceHistory` | Required `chain_id: string`, `contract_address: string`, `from_timestamp: integer`, `end_timestamp: integer`. | Unix **seconds**, not milliseconds; inclusive interval at most 90 days. |
| `crypto/dex/getDexTokenLiquidity` → `CoinMarketCap/getDexTokenLiquidity` | `platform: string`, `address: string`. | Provider platform name and **token contract address**. |
| `crypto/dex/getDexPairsQuotesLatest` → `CoinMarketCap/getDexPairsQuotesLatest` | Strings: `network_id`, `network_slug`, `contract_address`, `convert`, `convert_id`, `aux`, `reverse_order`; `skip_invalid: boolean`. | `contract_address` is the **pair/pool**, not the token. Resolve the provider's network identifier and pool first. |

Reuse pagination cursors verbatim. Confirm each provider's chain coverage and
identifier format; platform names and network IDs are not interchangeable.

Sources: [Sorsa user tweets](https://docs.sorsa.io/api-reference/tweets/user-tweets),
[Sorsa endpoint reference](https://github.com/Sorsa-io/sorsa-x-api-skill/blob/main/references/api-reference.md),
[Chainbase historical prices](https://platform.chainbase.com/blog/article/how-to-get-historical-erc-20-token-price),
[CoinMarketCap tokens](https://coinmarketcap.com/api/documentation/pro-api-reference/token),
[CoinMarketCap pool addresses](https://coinmarketcap.com/api/documentation/pro-api-reference/keyless-public-api).

## Interpret and report

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
