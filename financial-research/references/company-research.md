# Company and stock research

Identify the company, question and relevant period; resolve the exchange and
listing when market data is needed. Research does not require selecting a
tokenized or perpetual instrument.

Choose evidence for the question: company disclosures for reported performance
and strategy, industry or regulatory sources for context, and structured data
for numerical comparisons. Attribute management's explanations rather than
treating them as independent conclusions. Use the tools below as defaults when
they fit, not a mandatory sequence. Follow the main skill's access,
result-processing and completion rules.

## Locate sources: `Serper/search`

Search the company and subject, adding dates or `site:` filters when useful.
Prefer original sources; use search results to locate evidence, not replace it.

| Parameter | Type / meaning |
| --- | --- |
| `q` | Required string: search query. |
| `num`, `page` | Integers: result count and page. |
| `gl`, `hl` | Strings: country and language codes. |
| `tbs` | Optional string: time filter, such as `qdr:m` for the past month. |

## Read sources: `Firecrawl/scrape`

Read a known source URL directly. Select relevant sections from the saved
response before returning content to the model, keeping table headers and units.

| Parameter | Type / meaning |
| --- | --- |
| `url` | Required string: one complete source URL. |
| `formats` | Array; use `["markdown"]` for readable text and tables. |
| `onlyMainContent` | Boolean; use `true` to reduce navigation and footer content. |
| `includeTags`, `excludeTags` | Optional arrays of CSS selectors for known page sections. |
| `maxAge` | Integer milliseconds of acceptable cache age; use `0` when a fresh fetch is needed. |
| `skipTlsVerification` | Boolean; set `false` to retain certificate verification. |

If extraction fails or omits necessary content, `Jina/readUrlPost` is an
alternative: required `url: string`; use `x-return-format: "markdown"`, optional
`x-target-selector: string` for a known section and `x-no-cache: boolean` for
fresh retrieval. Its `x-token-budget: integer` rejects oversized responses; it
does not truncate them. Check that extracted tables retain their row/column
relationships before using the numbers.

## Numerical comparisons: `yfinance/getFundamentalTimeSeries`

Use for selected financial metrics across periods, not explanations of their
causes. Request only needed metrics and periods.

| Parameter | Type / meaning |
| --- | --- |
| `symbol` | Required string: provider ticker for the selected listing. |
| `type` | Required string: frequency-prefixed metric names, comma-separated; e.g. `quarterlyTotalRevenue` or `annualNetIncome`. |
| `period1`, `period2` | Optional integers: Unix seconds bounding the requested date range. |

Retain currency and period type. Provider period labels may normalize dates;
check the original disclosure for exact fiscal dates and material figures.
An empty or partial series does not establish that a metric or period is absent.

## Other company data: Finnhub

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
