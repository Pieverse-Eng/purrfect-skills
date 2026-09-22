# Company and earnings research

Resolve the issuer and, when market data is needed, its listing and exchange.
Researching the issuer does not require choosing a tokenized or perpetual product.

For earnings questions, start with the issuer's official release, filing and
investor-relations materials. Retrieve the requested quarter/year, publication
date and relevant tables; a headline or search snippet is not the full report.
Do not assume a provider can read a PDF or supplies every statement.

## Choose a tool for the question

Use these AgentKey operations as starting points, confirming the live schema
and price with `describe`. Select what answers the question, not every row.
Parameter types, date semantics and extraction limits are in the
[Tavily and Finnhub parameter guide](tool-parameters.md).

| Need | Starting tool | Scope and limitations |
| --- | --- | --- |
| Official disclosures, explanations or company events | `Tavily/post_search` | Search the issuer, reporting period and subject; prefer official domains. Search results locate sources, not complete evidence. |
| Relevant passages from a known webpage or PDF | `Tavily/post_extract` | Supply the source URL and a focused extraction query. Check whether the required passage/table was actually returned. |
| Financial figures and historical comparisons | `Finnhub/financialsReported` | Target the relevant filing or reporting period. Verify quarterly versus cumulative figures; filter out unrelated statement fields. |
| Locate regulatory filings | `Finnhub/filings` | Narrow dates and filing types where supported; retain only relevant filing links. |
| EPS and earnings surprises | `Finnhub/companyEarnings` | Does not explain revenue changes or replace segment disclosures. |
| Recent company coverage | `Finnhub/companyNews` | Narrow the date range; use for relevant events, not as a substitute for official financial explanations. |

For questions about why a reported figure changed, prioritize the relevant
official disclosure and management explanation. Add structured data when a
comparison or calculation needs it. Do not automatically retrieve full statement
histories, news feeds, call transcripts and every business segment. Unavailable
tools can be replaced through discovery using the shared skill workflow.

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
