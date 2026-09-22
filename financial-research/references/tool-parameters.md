# Research tool parameters

Read only the selected tool's section. Use the live AgentKey schema for accepted
fields and types; provider documentation explains semantics but does not imply
AgentKey supports additional fields or encodings. Omit optional parameters whose
encoding is unclear; do not guess required ones.

## Tavily: source search and extraction

### `Tavily/post_search`

| Parameter | Type / constraint | Use |
| --- | --- | --- |
| `query` | string, required | Actual research question, issuer/project and period. |
| `include_domains`, `exclude_domains` | array of strings | Domain filters; do not comma-join them. |
| `max_results` | integer, 0–20; default 5 | Bound the source list to the question. |
| `topic` | `general`, `news`, `finance`; default `general` | Select the appropriate source category. |
| `search_depth` | `basic`, `advanced`, `fast`, `ultra-fast` | Choose the needed coverage; advanced is not mandatory. |
| `start_date`, `end_date` | string, `YYYY-MM-DD` | Date filters. |
| `chunks_per_source` | integer, 1–3; default 3 | Relevant snippets per result for advanced search. |
| `include_answer` | provider: boolean or `basic` / `advanced` | Hosted schema omits the type. Usually omit; provider-generated answers are not primary evidence. |
| `include_raw_content` | provider: boolean or `markdown` / `text` | Hosted schema omits the type. Usually omit and extract selected sources. |

### `Tavily/post_extract`

| Parameter | Type / constraint | Use |
| --- | --- | --- |
| `urls` | AgentKey: string, required | One complete source URL; see batch constraints below. |
| `query` | string, optional | Reranks and returns relevant excerpts, not the full extracted page. |
| `chunks_per_source` | integer, 1–5; default 3 | With `query`, each excerpt is at most 500 characters. |
| `extract_depth` | `basic` or `advanced`; default `basic` | Advanced can improve extraction of tables and embedded content; it does not guarantee completeness. |
| `format` | `markdown` or `text`; default `markdown` | Output representation. |
| `timeout` | number, 1–60 seconds | Optional per-request extraction timeout. |

For a string schema, send one URL per call. The provider also accepts arrays of
1–20 URLs; use a JSON array only if the live AgentKey schema supports it. Never
join URLs with commas, spaces or newlines, or encode an array inside a string.

Use `query` for passages; omit it when its excerpt limit would cut off a required
table or section, then filter the extracted content locally. Extraction does not
guarantee a complete report. Inspect `results`, `failed_results` and content;
a `Not Found` or cookie page is not evidence.

Sources: [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search),
[Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract),
[official OpenAPI](https://docs.tavily.com/documentation/api-reference/openapi.json).

## Finnhub: filings and company data

| Tool | Parameters | Important semantics |
| --- | --- | --- |
| `Finnhub/financialsReported` | Optional strings: `symbol`, `cik`, `accessNumber`, `freq`, `from`, `to`. | Supply an issuer or filing identifier for company research. `freq`: `annual` (default) or `quarterly`. Dates: `YYYY-MM-DD`, filtering report **endDate**, not publication date. |
| `Finnhub/filings` | Optional strings: `symbol`, `cik`, `accessNumber`, `form`, `from`, `to`. | Without an issuer/filing identifier, lists latest filings across issuers. `form`: filing type; dates: `YYYY-MM-DD`. |
| `Finnhub/companyEarnings` | Required `symbol: string`; optional `limit: integer`. | `limit` counts reporting periods; omission returns full history. EPS surprises, not revenue attribution. |
| `Finnhub/companyNews` | Required strings: `symbol`, `from`, `to`. | Dates use `YYYY-MM-DD`; narrow the window to relevant events. |

Source: [Finnhub official SDK parameter documentation](https://github.com/Finnhub-Stock-API/finnhub-go/blob/master/docs/DefaultApi.md).

## Social and on-chain evidence

Use these directory-to-provider mappings to select an operation.

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
[Sorsa official endpoint reference](https://github.com/Sorsa-io/sorsa-x-api-skill/blob/main/references/api-reference.md),
[Chainbase historical-price example](https://platform.chainbase.com/blog/article/how-to-get-historical-erc-20-token-price),
[CoinMarketCap token endpoints](https://coinmarketcap.com/api/documentation/pro-api-reference/token),
[CoinMarketCap pool-address example](https://coinmarketcap.com/api/documentation/pro-api-reference/keyless-public-api).
