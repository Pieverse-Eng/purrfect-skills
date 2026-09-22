# Company and earnings research

Resolve the issuer and, when market data is needed, its listing and exchange.
Researching the issuer does not require choosing a tokenized or perpetual product.

For earnings questions, start with the issuer's official release, filing and
investor-relations materials. Retrieve the requested quarter/year, publication
date and relevant tables; a headline or search snippet is not the full report.
Do not assume a provider can read a PDF or supplies every statement.

For questions about why a reported figure changed, prioritize the relevant
official disclosure and management explanation. Add structured data when a
comparison or calculation needs it. Do not automatically retrieve full statement
histories, news feeds, call transcripts and every business segment. Stop when
the requested change and its material drivers are supported; missing unrelated
segment figures do not require further retrieval.

## Tools and parameters

Select what answers the question, not every tool. Follow the main skill's access
rules: describe a listed tool directly, then execute with its accepted schema.

### Locate sources: `Tavily/post_search`

Search the issuer, reporting period and subject; prefer official domains.
Search results locate sources, not complete evidence.

| Parameter | Type and meaning |
| --- | --- |
| `query` | Required string: the research query. |
| `include_domains`, `exclude_domains` | Arrays of domain strings, not comma-joined strings. |
| `max_results` | Integer, 0–20; default 5. |
| `topic` | `general` (default), `news` or `finance`. |
| `search_depth` | `basic`, `advanced`, `fast` or `ultra-fast`. |
| `start_date`, `end_date` | Strings, `YYYY-MM-DD`. |
| `chunks_per_source` | Integer, 1–3; default 3. Snippets per result for advanced search. |

Usually omit `include_answer` and `include_raw_content`; extract selected sources
instead. Provider types are boolean or `basic`/`advanced` for `include_answer`,
and boolean or `markdown`/`text` for `include_raw_content`; do not assume these
unions are supported when the AgentKey schema omits their types.

### Read a source: `Tavily/post_extract`

| Parameter | Type and meaning |
| --- | --- |
| `urls` | Required string: one complete source URL per call with a string schema. Never comma-join URLs or encode an array inside a string. Use an array of 1–20 URLs only if the live AgentKey schema supports it. |
| `query` | Optional string: selects relevant excerpts, **not full-page content**. Omit for a required table or section that would exceed the excerpt limit. |
| `chunks_per_source` | Integer, 1–5; default 3. With `query`, each excerpt is at most 500 characters. |
| `extract_depth` | `basic` (default) or `advanced`; advanced can help with tables but does not remove excerpt limits or guarantee completeness. |
| `format` | `markdown` (default) or `text`. |
| `timeout` | Number, 1–60 seconds. |

For full-content extraction, save and filter the response locally before adding
the relevant passages to context. Missing material in query-selected excerpts
is not evidence that the source lacks it: change the extraction mode rather than
repeatedly rewriting the query. Inspect `results`, `failed_results` and actual
content; an error or cookie page is not evidence.

Sources: [Tavily Search](https://docs.tavily.com/documentation/api-reference/endpoint/search),
[Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract),
[OpenAPI](https://docs.tavily.com/documentation/api-reference/openapi.json).

### Company data: Finnhub

| Need / tool | Parameters | Key semantics |
| --- | --- | --- |
| Financial figures: `Finnhub/financialsReported` | Optional strings: `symbol`, `cik`, `accessNumber`, `freq`, `from`, `to`. | Supply an issuer or filing identifier. `freq`: `annual` (default) or `quarterly`. Dates: `YYYY-MM-DD`, filtering report **endDate**, not publication date. |
| Filing links: `Finnhub/filings` | Optional strings: `symbol`, `cik`, `accessNumber`, `form`, `from`, `to`. | Without an issuer/filing identifier, lists latest filings across issuers. `form`: filing type; dates: `YYYY-MM-DD`. |
| EPS surprises: `Finnhub/companyEarnings` | Required `symbol: string`; optional `limit: integer`. | `limit` counts reporting periods; omission returns full history. Does not explain revenue changes. |
| Company news: `Finnhub/companyNews` | Required strings: `symbol`, `from`, `to`. | Dates: `YYYY-MM-DD`. Relevant coverage, not a substitute for official financial explanations. |

Request only the periods needed for the comparison. Save large financial
responses locally and select the relevant statement fields before returning
them to context; retain filing identifiers, periods, units and billing/error
status. Do not print whole multi-period statements for a few figures.

Source: [Finnhub parameter documentation](https://github.com/Finnhub-Stock-API/finnhub-go/blob/master/docs/DefaultApi.md).

## Interpret the evidence

Select dimensions that answer the question: revenue and segment mix, margins,
earnings, cash flow, balance-sheet changes, guidance or management explanations.
Compare like periods and units. Keep fiscal versus calendar periods, quarterly
versus annual/TTM data, reported versus adjusted metrics, diluted versus basic
EPS, statement currency and quote currency distinct. Label forecasts and
management guidance separately from actual results. A claim that earnings
"beat expectations" requires a sourced, comparable expectations baseline.

Use structured data for coverage and comparisons, and original disclosures for
material explanations or discrepancies. Supplement only the gaps relevant to
the question; do not collect every available metric. If a requested filing or
table cannot be read, disclose that limit rather than reconstructing it.

Explain changes and competing explanations, cite the underlying evidence and
label your calculations.
