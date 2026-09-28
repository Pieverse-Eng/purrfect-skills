# Company and earnings research

Resolve the issuer and reporting period; a listing matters only for market
data. Start with official filings, earnings releases and investor-relations
materials; find them with `Tavily/post_search` and `include_domains`, and read
them with `Tavily/post_extract`. Use structured data only for needed figures.

Filings for a US issuer (without `symbol`, `cik` or `accessNumber` it returns
every issuer):

```bash
purr agentkey execute Finnhub/filings --params '{"symbol":"<TICKER>","from":"YYYY-MM-DD","to":"YYYY-MM-DD"}' --max-credits 0.1 > /tmp/ak-filings.json
jq -c '[.result.data[] | {form, filedDate, reportUrl}]' /tmp/ak-filings.json
```

Reported financials (the response holds every period, often over 800 KB; the
latest filing may not be included yet, so check `filings`):

```bash
purr agentkey execute Finnhub/financialsReported --params '{"symbol":"<TICKER>","freq":"quarterly"}' --max-credits 0.1 > /tmp/ak-fin.json
jq -c '[.result.data.data[] | {year, quarter, form, endDate}] | sort_by(.endDate) | reverse | .[:6]' /tmp/ak-fin.json
jq -c '.result.data.data | sort_by(.endDate) | last | [.report.ic[] | select(.concept | test("Revenue|NetIncomeLoss|EarningsPerShareDiluted")) | {label: .label, value: .value, unit: .unit}]' /tmp/ak-fin.json
```

In jq 1.6, `label` is a keyword: write `label: .label`, not `{label}`. Statements
are `ic`, `bs` and `cf`.

`Finnhub/companyEarnings` gives EPS surprises only. `Finnhub/companyNews` covers
North American issuers, returns more than 100 items a day and mostly unrelated
market roundups; prefer news search.

Compare consistent periods (quarterly, cumulative, annual or TTM), reported vs
adjusted metrics, basic vs diluted EPS and currencies. Separate results from
guidance; a surprise needs a comparable expectation. Explain changes with
sourced drivers, label calculations, and disclose missing filings instead of
reconstructing them from snippets.
