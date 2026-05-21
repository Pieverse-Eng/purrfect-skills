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
- Leaderboard returns at most Top 50

For a one-day window, `window_end` is the next UTC date. Example for
2026-05-21: `window_start=2026-05-21&window_end=2026-05-22`.

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

| Intent | Period | Endpoint |
| --- | --- | --- |
| Leaderboard | Today (default) | `GET /v2/redpacket-race/leaderboard` |
| Leaderboard | Specific UTC day | same + `window_start` and `window_end` |
| Leaderboard | Total campaign | same + `window_start=2026-05-21` (omit `window_end`) |
| My rank | Today (default) | `GET /v2/instances/$INSTANCE_ID/redpacket-race/my-rank` |
| My rank | Specific UTC day | same + `window_start` and `window_end` |
| My rank | Total campaign | same + `window_start=2026-05-21` (omit `window_end`) |
| Audit | Today (default) | `GET /v2/instances/$INSTANCE_ID/redpacket-race/audit-log` |
| Audit | Specific UTC day | same + `window_date_utc=YYYY-MM-DD` |

Every endpoint takes `token=usdt0`. Audit uses `window_date_utc`, not the
start/end pair. For the total campaign, omitting `window_end` lets the server
read activity-to-date through the current UTC window end. Passing `window_end`
scopes the result to an explicit window; it is a one-day window only when
`window_end` is the next UTC date after `window_start`.

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

Show a compact ranked list. Per entry include:

- rank
- rendered handle
- sends count
- total amount
- `rank_delta_vs_prev_day` when not null
- rewards as `<rewards_pieverse> PIEVERSE (~$<rewards_usdt_equiv>)` when both fields are present

Never label `rewards_usdt_equiv` as a PIEVERSE amount. Do not editorialize
about reward multipliers, generosity, or bugs unless the user asks.

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
- `no_rank` with `reason=handle_not_found` — the instance needs a `.pie` handle.
- `no_rank` with `reason=not_ranked_current_window` — no eligible race activity in this window yet.
- `no_rank` with `reason=no_current_window_snapshot` — leaderboard data is warming up.

## Audit Details

Use when the user asks why they are not ranked, why activity is not counting,
or for their race transfer details. Audit is per-day.

Today:

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpacket-race/audit-log?direction=all&channel=telegram&limit=50&token=usdt0" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Specific UTC day (example 2026-05-21):

```bash
curl -sS "$WALLET_API_URL/v2/instances/$INSTANCE_ID/redpacket-race/audit-log?window_date_utc=2026-05-21&direction=all&channel=telegram&limit=50&token=usdt0" \
  -H "Authorization: Bearer $WALLET_API_TOKEN"
```

Query options:

- `direction`: `all` (default), `sent`, or `received`.
- `channel`: `telegram`, `line`, or `all`. Detect from runtime context —
  Hermes uses `Current Session Context` / `Source`; OpenClaw/PurrfectClaw uses
  `Inbound Context (trusted metadata)` `channel`/`provider`/`surface`. Use
  `all` only when the user explicitly asks for all or unfiltered channel
  activity. API default when the parameter is omitted is `all`.
- `limit`: 1-100, default 50.
- `offset`: paginate when the response has `has_more=true`.

Output:

1. Summarize `summary.race_credit`.
2. List recent entries with direction, counterparty, status, amount, channel,
   `counted_for_race`, and any non-zero race credit.
3. If an entry is not counted, point out observable facts only: unclaimed
   status, wrong channel, tiny amount, zero race credit, missing `.pie`
   handle. If none apply, say it may be due to race caps, qualification gates,
   risk filters, or snapshot timing — do not invent a precise backend reason.

## Errors

- HTTP 400 with window parameters: the date window is invalid, or the windowed leaderboard API may not be deployed yet.
- HTTP 401 or 403 on personal endpoints: hosted instance authorization is missing or expired.
- Empty `leaderboard`: no ranked participants are available for this window.
- Empty audit entries: no race activity was found for that day/channel.
