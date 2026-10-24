# Errors and partial data

| Observation | Action |
| --- | --- |
| `Unknown group: injective` | Installed CLI lacks the capability. Report the upgrade requirement; no invented version or raw fallback. |
| `INJECTIVE_CAPABILITY_UNAVAILABLE` | Backend lacks the routes. Report backend rollout/version mismatch. |
| `INJECTIVE_READ_ONLY` | Execution is unavailable in this phase. Stop; no signing or alternative write path. |
| Missing credentials / wallet unavailable | Report current Agent configuration/identity unavailable. Never ask for a private key. |
| `MARKET_NOT_FOUND` | Resolve exact native hash plus product again; do not substitute a ticker or venue. |
| 429 / retry metadata | Respect `Retry-After` or `retryAfterMs`; no rapid loop or bypass to native endpoints. |
| Timeout / upstream unavailable / not indexed | State unavailable. Keep historical data labelled stale; failure is not a zero balance. |
| Invalid/expired cursor / changed identity | Restart the query under current identity; do not repair or decode the cursor. |

Inspect component `meta.status`, `completeness`, `asOf`, `retryAfterMs`, and
`reason`, plus page coverage and nextCursor. A successful HTTP response can
still contain unavailable components. Partial balances do not establish a
portfolio total; a partial page does not establish no other orders or positions.
Preserve available components when another is unavailable. Do not upgrade old
data to current by refreshing its display timestamp.

Report the useful result, its scope/time and the unresolved gap. No exchange
transaction or gas deduction occurs in these read commands. Public endpoints
still have availability and request-budget limits.
