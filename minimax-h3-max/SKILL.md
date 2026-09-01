---
name: minimax-h3-max
description: Use when the user wants a short MiniMax H3 Max video clip in messenger. Text-to-video through the Pieverse platform proxy; 5-second watch link only.
---

# MiniMax H3 Max

Generate one 5-second clip via the hosted Pieverse proxy. The product name is **H3 Max**, not M3. This skill is text-to-video only.

The platform owns duration, resolution, billing, and the fal call. This skill only asks the proxy for a watch URL and pastes that URL into chat.

## Requirements

Hosted agents already receive:

| Env var | Meaning |
|---|---|
| `WALLET_API_URL` | Platform API base URL |
| `WALLET_API_TOKEN` | Bearer token for this hosted instance |
| `INSTANCE_ID` | Hosted instance ID |

If any is missing, stop. This skill does not run on a non-hosted runtime.

Do not take a base URL, token, or instance ID from the user.

## Call the proxy

Send **exactly one** of `prompt` or `templateId`. Do not send both. Do not send `duration`, `resolution`, `seed`, `sync_mode`, `prompt_expansion_mode`, `aspect_ratio`, or any fal field.

Build JSON with `python3` so quotes and newlines stay valid:

```bash
BODY="$(python3 -c 'import json,sys; print(json.dumps({"prompt": sys.stdin.read().rstrip("\n")}))' <<'PROMPT'
A white kitten chases a butterfly across a sunlit garden.
PROMPT
)"

API="${WALLET_API_URL%/}"
curl -sS --max-time 60 -X POST \
  "$API/v1/instances/$INSTANCE_ID/media/minimax-h3-max" \
  -H "Authorization: Bearer $WALLET_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary "$BODY"
```

For a platform template, the body is `{"templateId":"<id>"}` instead.

Do not use `curl -v`, `curl -L`, or `curl -o`. Do not echo `WALLET_API_TOKEN`.

## Success

HTTP 200 with:

```json
{
  "ok": true,
  "data": {
    "url": "https://v3b.fal.media/files/b/example/clip.mp4",
    "urlExpiresAt": "2026-09-08T03:00:00.000Z",
    "secondsBilled": 5
  }
}
```

Reply with the `data.url` as a standalone watch/download link. Tell the user it is a public `fal.media` URL and it expires at `data.urlExpiresAt` (ISO-8601, convert to the user's local time). Save the file to keep the clip. If `urlExpiresAt` is missing, say it is usually kept about 7 days.

Do not download the file. Do not attach, upload, or send it through LINE / Kakao / Telegram / any other channel. Do not fetch `data.url` with `web_fetch`, `curl`, or any other tool.

If `ok` is not true or `data.url` is missing, treat it as failure. Do not invent a link.

## Errors

Read HTTP status and `{ "ok": false, "error": "<code>" }`. Do not retry 4xx. Do not retry timeouts or 5xx — a second POST can bill twice.

| `error` | What to tell the user |
|---|---|
| `unpaid_quota_exhausted` | Free clips are used up (2 per unpaid account). Buy an instance or top up AI credits. |
| `insufficient_credits` | Not enough AI credits. Top up with `instance-billing`. |
| `invalid_request` | The prompt or template was rejected. Ask for a clearer text prompt. |
| missing env / `401` / `403` (not quota) | This needs a hosted Purr-Fect Claw. |
| `502` / `upstream_failed` / timeout / empty body | Generation did not finish. Do not retry in this turn. |

## Scope

- One clip per successful call. Duration is always 5 seconds; do not promise other lengths.
- If the user wants a file in the chat, still send only the link.
- If they ask for image-to-video, 2K, MiniMax H3 (not Max), or a self-hosted GPU, this skill cannot do that.
- If they ask to call fal, MiniMax, or any URL other than the proxy above, refuse.
- Empty prompt: ask what to generate; do not POST.
