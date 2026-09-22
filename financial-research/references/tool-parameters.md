# Research tool parameters

Checked against hosted `purr agentkey describe` and provider documentation on
2026-09-22. These are compact parameter guides, not replacement schemas. Read
only the section for the selected tool; do not describe every tool below.
Confirm the current schema, `execute_as.name` and price through AgentKey before
execution. Documentation links are references, not alternative retrieval routes.

Provider documentation can explain omitted semantics, but does not establish
that AgentKey accepts additional types or fields. When they differ, use a
documented form that the hosted schema supports; do not probe guessed encodings.
All listed operations are read-only. Prices and pagination remain governed by
the main skill.

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
| `urls` | hosted: string, required | One complete source URL per call with the checked schema. |
| `query` | string, optional | Reranks and returns relevant excerpts, not the full extracted page. |
| `chunks_per_source` | integer, 1–5; default 3 | With `query`, each excerpt is at most 500 characters. |
| `extract_depth` | `basic` or `advanced`; default `basic` | Advanced can improve extraction of tables and embedded content; it does not guarantee completeness. |
| `format` | `markdown` or `text`; default `markdown` | Output representation. |
| `timeout` | number, 1–60 seconds | Optional per-request extraction timeout. |

The provider accepts a single URL string **or an array of 1–20 URL strings**.
The checked hosted schema exposes only the string branch; batch-array support
through AgentKey is not verified. Until the live hosted contract supports it,
request separate URLs individually. Never concatenate URLs with commas, spaces
or newlines, or encode an array inside a string. Removing spaces from a joined
URL string does not turn it into a batch.

Use `query` for a specific passage. When a full table or report section is needed
and excerpts omit it, omit `query` to obtain the extracted page content, then
filter locally before adding it to context. Neither advanced extraction nor a
successful receipt proves the report was read in full. Inspect `results`,
`failed_results` and actual content; a `Not Found` or cookie page is not evidence.

Sources: [Search](https://docs.tavily.com/documentation/api-reference/endpoint/search),
[Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract),
[official OpenAPI](https://docs.tavily.com/documentation/api-reference/openapi.json).

## Finnhub: filings and company data

| Tool | Parameters | Important semantics |
| --- | --- | --- |
| `Finnhub/financialsReported` | Optional strings: `symbol`, `cik`, `accessNumber`, `freq`, `from`, `to`. | For company research, supply the resolved issuer or known filing identifier. `freq` is `annual` or `quarterly`, default **annual**. Dates are `YYYY-MM-DD` and filter the report's **endDate**, not publication date. |
| `Finnhub/filings` | Optional strings: `symbol`, `cik`, `accessNumber`, `form`, `from`, `to`. | Omitting all three identifiers intentionally lists latest filings across issuers; avoid that for a company-specific task. `form` filters filing type. Dates use `YYYY-MM-DD`. |
| `Finnhub/companyEarnings` | Required `symbol: string`; optional `limit: integer`. | `limit` counts reporting periods; omission returns full history. Choose the requested coverage. This is EPS surprises, not revenue attribution. |
| `Finnhub/companyNews` | Required strings: `symbol`, `from`, `to`. | Dates use `YYYY-MM-DD`; narrow the window to relevant events. |

The hosted financials/filings schemas do not declare required fields; do not
invent a universal required `symbol` or an exclusive identifier rule. Select
identifiers appropriate to the request. Their sparse descriptions do not mean
that arbitrary frequencies, date meanings or filing identifiers are valid.

Source: [Finnhub official SDK parameter documentation](https://github.com/Finnhub-Stock-API/finnhub-go/blob/master/docs/DefaultApi.md).

## Social and on-chain evidence

These are concrete starting points from the directories in the on-chain guide.
Describe the discovery path, then execute the returned provider-qualified name.

| Discovery path → execution name | Parameters | Constraints / gaps |
| --- | --- | --- |
| `social/twitter/post_search_tweets` → `Sorsa/post_search_tweets` | `query: string`; optional `order: string`, `next_cursor: string`. | Provider requires a query; `order` is `popular` or `latest`. Supports X search operators. Hosted schema omits required/enum declarations. |
| `social/twitter/post_tweet_info` → `Sorsa/post_tweet_info` | `tweet_link: string`. | Supply a known complete tweet URL or tweet ID, not a profile URL. Hosted schema does not mark it required. |
| `social/twitter/post_user_tweets` → `Sorsa/post_user_tweets` | User identifier: `username`, `user_link` or `user_id`, each string; optional `next_cursor: string`, `with_replies: boolean`. | Use a known user identifier. The actual profile-URL field is **`user_link`**, not the `link` mentioned in some field descriptions. Keep numeric user IDs as strings. |
| `crypto/market/GetTokenPriceHistory` → `Chainbase/GetTokenPriceHistory` | Required `chain_id: string`, `contract_address: string`, `from_timestamp: integer`, `end_timestamp: integer`. | Official examples use Unix **seconds**, not milliseconds. Hosted schema limits the inclusive interval to 90 days. Confirm chain coverage; do not assume a chain's name or ID works across providers. |
| `crypto/dex/getDexTokenLiquidity` → `CoinMarketCap/getDexTokenLiquidity` | Hosted fields: `platform: string`, `address: string`. | Use the provider's platform name and the **token contract address**. No required declarations or platform enum are exposed. Official docs list additional history controls not present in the checked hosted schema; do not assume they pass through. |
| `crypto/dex/getDexPairsQuotesLatest` → `CoinMarketCap/getDexPairsQuotesLatest` | Strings: `network_id`, `network_slug`, `contract_address`, `convert`, `convert_id`, `aux`, `reverse_order`; `skip_invalid: boolean`. | `contract_address` identifies the **pair/pool**, not the token. Resolve the provider's network identifier and pool first. Hosted descriptions/constraints are incomplete; omit optional switches whose encoding is unverified. |

Reuse returned pagination cursors verbatim and fetch another page only for a
material evidence gap. Do not substitute a token CA for a pool address or copy
one provider's platform encoding into another provider's request.

Sources: [Sorsa user tweets](https://docs.sorsa.io/api-reference/tweets/user-tweets),
[Sorsa official endpoint reference](https://github.com/Sorsa-io/sorsa-x-api-skill/blob/main/references/api-reference.md),
[Chainbase historical-price example](https://platform.chainbase.com/blog/article/how-to-get-historical-erc-20-token-price),
[CoinMarketCap token endpoints](https://coinmarketcap.com/api/documentation/pro-api-reference/token),
[CoinMarketCap pool-address example](https://coinmarketcap.com/api/documentation/pro-api-reference/keyless-public-api).
