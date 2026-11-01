# Errors and partial data

| Observation | Action |
| --- | --- |
| `Unknown group: injective` | Installed CLI lacks the capability. Report the upgrade requirement; no invented version or raw fallback. |
| `INJECTIVE_CAPABILITY_UNAVAILABLE` | Backend lacks the routes. Report backend rollout/version mismatch. |
| `INJECTIVE_READ_ONLY` / execution disabled | Installed candidate or backend does not permit the action. Stop; no alternative signing path. |
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

## Execution and RFQ recovery

- Execution `POLICY_DEFERRED` (202): retain the exact policy request, body,
  wallet generation and original business key. Report pending approval, not an
  order. Before continuing, GET the original request and verify that it is still
  that policy hold and that approval has been granted through the normal flow.
  Only for this verified, unbroadcast policy hold may the exact same operation,
  body, generation and original key be POSTed once to claim/resume approval.
  Do not reconstruct the body from new views or update its prices/expiry. A stale
  or expired approval requires a fresh user review; an uncertain resume returns
  to GET recovery, never another POST. This exception does not apply to unknown,
  submitted or signed/broadcast native transactions.
- Quote-only `rfq preview` 202 has no execution business key or journal. Report
  its policy hold and approval identifier if present. Do not run an execution
  request lookup, infer a transaction or automatically collect/accept a quote.
- Lost response, timeout or unknown execution: use `request --request-id
  ORIGINAL_KEY --by idempotency-key`. Preserve original transaction hash, key and
  body; follow that receipt until known. Never repeat a POST or swap quotes.
- Changed wallet generation, approval/state hash, native inventory or
  authorization: recover any previous request first. Only an explicitly unsent or
  terminal failed action may become a new reviewed intent. Refetch the minimum
  required view; never edit an old body to fit a new snapshot.
- Expired / partial / no RFQ quote: no acceptance. Explain coverage. Request a
  new quote only as a new review; do not increase size, price, fee or minimum fill.
- Missing INJ or insufficient settlement funds: report the exact user-funded
  shortfall. Do not sponsor gas, transfer automatically or enable an account.
- Receipt success without native order/fill observation: report inclusion only.
  Do not claim filled, closed, protected or a final PnL.

A native transaction can consume user INJ even if execution fails on-chain.
Read/quote APIs do not themselves consume chain gas, but are still rate limited.
