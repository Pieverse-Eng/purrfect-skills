---
name: red-packet-race
description: Use when the user wants to view the Pieverse OKX Red Packet Race leaderboard (today, a specific UTC day, or total campaign), their own rank, or their race audit details.
---

# Red Packet Race

Read-only helper for the Pieverse OKX Red Packet Race campaign. Use when the
user asks for:

- Today's, a specific UTC day's, or the total campaign leaderboard
- Their own daily, total, or specific-day rank
- Their race activity audit, or why they are not ranked

Do not use this skill to send, claim, or list pending redpackets. Defer to
`red-packet-send` / `red-packet-claim` for those.

## Constants

- API base: `$WALLET_API_URL` (prod: `https://purr.pieverse.io`)
- Race token: `usdt0`
- Campaign start (UTC): `2026-05-21`
- Dates are UTC `YYYY-MM-DD`; `window_start` is inclusive, `window_end` is exclusive
- Leaderboard returns Top 10 by default; pass `limit` up to 20 for more rows

## Requirements

Public leaderboard needs only `WALLET_API_URL`:

```bash
test -n "${WALLET_API_URL:-}"
```

My-rank and audit-log require hosted instance credentials:

```bash
test -n "${WALLET_API_URL:-}" && test -n "${WALLET_API_TOKEN:-}" && test -n "${INSTANCE_ID:-}"
```

If anything is missing, say hosted Pieverse instance credentials are required
for this query. Never ask for private keys or wallet secrets. Never echo raw
tokens or env values in replies.

## Pick the endpoint

| Intent | Endpoint |
| --- | --- |
| Leaderboard | `GET /v2/redpacket-race/leaderboard` |
| My rank | `GET /v2/instances/$INSTANCE_ID/redpacket-race/my-rank` |
| Audit | `GET /v2/instances/$INSTANCE_ID/redpacket-race/audit-log` |

Start every request with `token=usdt0`, then add the needed query pattern:

| Period / option | Query pattern |
| --- | --- |
| Today (default) | no window params |
| Specific UTC day for leaderboard/my-rank | `window_start=YYYY-MM-DD&window_end=NEXT-YYYY-MM-DD` |
| Specific UTC day for audit | `window_date_utc=YYYY-MM-DD` |
| Explicit date range | `window_start=YYYY-MM-DD&window_end=YYYY-MM-DD` |
| Total campaign/history | `window_start=2026-05-21` (omit `window_end`) |
| More leaderboard rows | `limit=N`, max `20` |

For one-day `window_start` / `window_end` queries, `window_end` is the next UTC
date. Audit supports either `window_date_utc` or `window_start` / `window_end`;
never combine them. Omitting `window_end` with `window_start` reads through the
current UTC window end. `limit` is leaderboard-only, but it can be combined with
leaderboard window params.

If the user asks for the current or latest leaderboard without saying total,
overall, campaign-to-date, or a specific date, use the Today endpoint only. Do
not probe total/window endpoints for that intent.

## Leaderboard

Today:

```bash
curl -sS "$WALLET_API_URL/v2/redpacket-race/leaderboard?token=usdt0"
```

Specific UTC day (example 2026-05-21):

```bash
curl -sS "$WALLET_API_URL/v2/redpacket-race/leaderboard?token=usdt0&window_start=2026-05-21&window_end=2026-05-22"
```

Total campaign (since launch):

```bash
curl -sS "$WALLET_API_URL/v2/redpacket-race/leaderboard?token=usdt0&window_start=2026-05-21"
```

More rows:

```bash
curl -sS "$WALLET_API_URL/v2/redpacket-race/leaderboard?token=usdt0&limit=20"
```

Show a compact ranked list. Per entry include:

- rank
- rendered handle
- sends count
- total amount
- `rank_delta_vs_prev_day` when not null
- rewards as `<rewards_pieverse> PIEVERSE (~$<rewards_usdt_equiv>)` when both fields are present

Use `rendered_handle` exactly as returned; do not shorten handles, drop `.pie`,
or replace them with raw `handle`.

Label `pieverse_usd_price` as PIEVERSE USD price and `rewards_usdt_equiv` as
rewards USD equivalent.

## My Rank

Never pass a handle. The platform resolves the instance's `.pie` handle
server-side from `$INSTANCE_ID`.

Today:

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpacket-race/my-rank?token=usdt0" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Specific UTC day:

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpacket-race/my-rank?token=usdt0&window_start=2026-05-21&window_end=2026-05-22" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Total campaign:

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpacket-race/my-rank?token=usdt0&window_start=2026-05-21" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Branch on `state`:

- `ranked` — show the resolved handle and the user's leaderboard entry.
  Include rank, rendered handle, sent/received counts and amounts, score,
  rewards, and `rank_delta_vs_prev_day` when present.
  Label `*_count` fields as counts and `*_amount` fields as amounts, e.g.
  "Total received count" vs. "Total received amount".
- `no_rank` with `reason=handle_not_found` — the instance needs a `.pie` handle.
- `no_rank` with `reason=not_ranked_current_window` — no eligible race activity in this window yet.
- `no_rank` with `reason=no_current_window_snapshot` — leaderboard data is warming up.

## Audit Details

Use when the user asks why they are not ranked, why activity is not counting,
or for their race transfer details. Audit can be per-day or a UTC date range.

Today:

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpacket-race/audit-log?direction=all&channel=telegram&limit=50&token=usdt0" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Specific UTC day:

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpacket-race/audit-log?window_date_utc=YYYY-MM-DD&direction=all&channel=telegram&limit=50&token=usdt0" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Explicit date range:

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpacket-race/audit-log?window_start=YYYY-MM-DD&window_end=YYYY-MM-DD&direction=all&channel=telegram&limit=50&token=usdt0" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Campaign history:

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpacket-race/audit-log?window_start=2026-05-21&direction=all&channel=telegram&limit=50&token=usdt0" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Query options:

- Window params: use the query patterns above.
- `direction`: `all` (default), `sent`, or `received`.
- `channel`: `telegram`, `line`, or `all`. Detect from runtime context —
  Hermes uses `Current Session Context` / `Source`; OpenClaw/PurrfectClaw uses
  `Inbound Context (trusted metadata)` `channel`/`provider`/`surface`. Use
  `all` only when the user explicitly asks for all or unfiltered channel
  activity. API default when the parameter is omitted is `all`.
- `limit`: 1-100, default 50.
- `offset`: paginate when the response has `has_more=true`.

Output:

1. Summarize `summary.race_credit`; label `*_count_credit` as count credit,
   `*_amount` as amount, and only `score_credit` as score credit.
2. List recent entries with direction, counterparty, status, amount, channel,
   `counted_for_race`, and any non-zero race credit, using the same count /
   amount / score label split.
   Format `amount_base_units` with `token.decimals` and `token.symbol`; do not
   display base units directly.
3. If an entry is not counted, point out observable facts only: unclaimed
   status, wrong channel, tiny amount, zero race credit, missing `.pie`
   handle. If none apply, say it may be due to race caps, qualification gates,
   risk filters, or snapshot timing — do not invent a precise backend reason.

## Errors

- HTTP 400 with window parameters: the date window is invalid.
- HTTP 401 or 403 on personal endpoints: hosted instance authorization is missing or expired.
- Empty `leaderboard`: no ranked participants are available for this window.
- Empty audit entries: no race activity was found for that day/channel.
