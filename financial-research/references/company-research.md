# Company and earnings research

Resolve the issuer and reporting period; identify its listing only when market
data is needed. Company research does not require selecting a tokenized or
perpetual instrument.

Start with official filings, earnings releases and investor-relations materials.
For changes in a financial metric, establish the comparison and management's
explanation; add structured data only for needed figures or calculations.
Select tools below for the question, not as a mandatory sequence. Follow the
main skill's access, result-processing and completion rules.

## Locate sources: `Tavily/post_search`

Search the issuer, period and subject, preferring official domains.

| Parameter | Type / meaning |
| --- | --- |
| `query` | Required string: research query. |
| `include_domains`, `exclude_domains` | Arrays of domain strings. |
| `max_results` | Integer 0–20; default 5. |
| `topic` | `general` (default), `news` or `finance`. |
| `search_depth` | `basic`, `advanced`, `fast` or `ultra-fast`. |
| `start_date`, `end_date` | `YYYY-MM-DD` strings. |
| `chunks_per_source` | Integer 1–3, default 3; snippets for advanced search. |

## Read sources: `Tavily/post_extract`

| Parameter | Type / meaning |
| --- | --- |
| `urls` | Required string: **one complete URL**, never joined URLs or a string-encoded array. Use an array of 1–20 URLs only if the live AgentKey schema supports it. |
| `query` | Optional string for relevant excerpts. Omit for full-content extraction; save and filter large results locally. |
| `chunks_per_source` | Integer 1–5, default 3; with `query`, at most 500 characters per excerpt. |
| `extract_depth` | `basic` (default) or `advanced`; advanced can help with tables but does not remove excerpt limits or guarantee completeness. |
| `format` | `markdown` (default) or `text`. |
| `timeout` | Number, 1–60 seconds. |

Choose passage or full-content extraction according to the evidence needed.
If excerpts omit a required table/section, change the extraction mode rather
than repeatedly rewriting the query. Check `results` and `failed_results`;
a successful request does not prove a complete filing was retrieved.

Sources: [Tavily Search](https://docs.tavily.com/documentation/api-reference/endpoint/search),
[Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract).

## Company data: Finnhub

| Need / tool | Parameters | Semantics |
| --- | --- | --- |
| Financial figures: `Finnhub/financialsReported` | Optional strings: `symbol`, `cik`, `accessNumber`, `freq`, `from`, `to`. | Supply an issuer or filing identifier. `freq`: `annual` (default) or `quarterly`. Dates filter report **endDate**, not publication date. |
| Filing links: `Finnhub/filings` | Optional strings: `symbol`, `cik`, `accessNumber`, `form`, `from`, `to`. | Without an issuer/filing identifier, returns filings across issuers. `form` filters filing type. |
| EPS surprises: `Finnhub/companyEarnings` | Required `symbol: string`; optional `limit: integer`. | `limit` counts periods; omission returns full history. Not revenue attribution. |
| Company news: `Finnhub/companyNews` | Required strings: `symbol`, `from`, `to`. | Coverage of events, not a substitute for original disclosures. |

Dates use `YYYY-MM-DD`. Request the relevant periods and select needed statement
fields locally, retaining filing identifiers and units.

Source: [Finnhub parameters](https://github.com/Finnhub-Stock-API/finnhub-go/blob/master/docs/DefaultApi.md).

## Interpret comparisons

Compare consistent fiscal/calendar periods, quarterly/cumulative/annual/TTM
figures, reported/adjusted metrics, basic/diluted EPS and currencies. Separate
actual results from guidance and forecasts; an earnings surprise requires a
comparable expectations baseline. Explain material changes with sourced
drivers and label calculations. Disclose unavailable filings or tables instead
of reconstructing them from snippets.
