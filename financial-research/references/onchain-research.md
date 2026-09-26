# Chain activity and token narratives

Explain the requested chain activity, project narrative or token developments.
Choose evidence for that question; holder analysis, fund flows and contract
audits are separate investigations only when relevant to the request. Follow
the main skill's access, result-processing and completion rules.

## Identify subjects

For CLI lookups, chain values are `robinhood`, `bnb` and `solana`. This lookup
coverage does not limit broader AgentKey research.

```bash
purr market trending --chain <chain>
purr market token --chain <chain> <ca>
```

Use trending for a chain overview; for a specific token, reuse known identity
and evidence or use the token lookup. Never guess a chain or contract address.
Both return `chain` and `candidates`; token lookup returns at most one candidate.
An empty result means no provider match, not nonexistence; an error is a failed
lookup. Trending is a sample, not a chain-wide ranking or safety endorsement.
For an overview, cover returned candidates within the user's scope and disclose
evidence gaps. Reuse returned links and metrics.

## Web sources: Tavily

Use search to locate original sources and extract to read a known project page,
document or article. Preserve project identity when selecting results.

| Tool | Parameters and semantics |
| --- | --- |
| `Tavily/post_search` | Required `query: string`. Optional `include_domains` / `exclude_domains`: arrays of domain strings; `max_results`: integer 0–20 (default 5); `topic`: `general` (default), `news` or `finance`; `search_depth`: `basic`, `advanced`, `fast` or `ultra-fast`; `start_date` / `end_date`: `YYYY-MM-DD` strings; `chunks_per_source`: integer 1–3 (default 3), for advanced search. |
| `Tavily/post_extract` | Required `urls: string`: **one complete URL**, never joined URLs or a string-encoded array. Use an array of 1–20 URLs only if the live schema supports it. Optional `query: string` selects excerpts, not full content; `chunks_per_source`: integer 1–5 (default 3), at most 500 characters each with `query`; `extract_depth`: `basic` (default) or `advanced`; `format`: `markdown` (default) or `text`; `timeout`: number, 1–60 seconds. |

If excerpts omit a required section, omit `query` and filter the full-content
response locally rather than repeatedly rewriting queries. Advanced extraction
does not remove excerpt limits or guarantee completeness. Check `results` and
`failed_results` before using the content.

Sources: [Tavily Search](https://docs.tavily.com/documentation/api-reference/endpoint/search),
[Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract).

## Social and market evidence

Use social tools for known posts/accounts or a relevant discussion; use market
tools only for missing price, volume or liquidity evidence. Describe the selected
operation directly. If none fits, discover within `social/twitter`,
`crypto/market`, `crypto/dex` or the requested platform's returned directory.

| Discovery path → execution name | Parameters | Semantics |
| --- | --- | --- |
| `social/twitter/post_search_tweets` → `Sorsa/post_search_tweets` | Required by provider: `query: string`; optional `order: string`, `next_cursor: string`. | `order`: `popular` or `latest`; supports X search operators. |
| `social/twitter/post_tweet_info` → `Sorsa/post_tweet_info` | `tweet_link: string`. | Known complete tweet URL or ID, not a profile URL. |
| `social/twitter/post_user_tweets` → `Sorsa/post_user_tweets` | A known user identifier: `username`, `user_link` or `user_id`, each string; optional `next_cursor: string`, `with_replies: boolean`. | Profile URL field is `user_link`, not `link`. Numeric IDs remain strings. |
| `crypto/market/GetTokenPriceHistory` → `Chainbase/GetTokenPriceHistory` | Required `chain_id: string`, `contract_address: string`, `from_timestamp: integer`, `end_timestamp: integer`. | Unix **seconds**; inclusive interval at most 90 days. |
| `crypto/dex/getDexTokenLiquidity` → `CoinMarketCap/getDexTokenLiquidity` | `platform: string`, `address: string`. | Provider platform name and **token contract address**. |
| `crypto/dex/getDexPairsQuotesLatest` → `CoinMarketCap/getDexPairsQuotesLatest` | Strings: `network_id`, `network_slug`, `contract_address`, `convert`, `convert_id`, `aux`, `reverse_order`; `skip_invalid: boolean`. | `contract_address` is the **pair/pool**, not the token. |

Confirm provider-specific chain coverage and identifier formats. Use pagination
cursors verbatim; omit optional switches whose encoding is unknown.

Sources: [Sorsa](https://github.com/Sorsa-io/sorsa-x-api-skill/blob/main/references/api-reference.md),
[Chainbase historical prices](https://platform.chainbase.com/blog/article/how-to-get-historical-erc-20-token-price),
[CoinMarketCap tokens](https://coinmarketcap.com/api/documentation/pro-api-reference/token),
[CoinMarketCap pools](https://coinmarketcap.com/api/documentation/pro-api-reference/keyless-public-api).

## Interpret and report

Attribute project claims and social narratives; repeated promotion is not
independent confirmation of legitimacy or backing. Preserve token names,
symbols, exact chains/CAs, source links and observation times. For market data,
retain the provider, pool/venue and window; do not sum overlapping samples or
treat displayed liquidity as a size-specific executable quote. Answer the
requested scope without turning popularity into an investment recommendation.
