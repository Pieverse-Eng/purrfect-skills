---
name: minimax-h3-max
description: Use when the user wants a short MiniMax H3 Max video clip in messenger. Text-to-video through the Pieverse platform proxy; 5-second watch link only.
---

# MiniMax H3 Max

Generate one 5-second clip via the hosted Pieverse proxy. The product name is **H3 Max**, not M3. This skill is text-to-video only.

The platform owns duration, resolution, billing, and the fal call. This skill only asks the proxy for a watch URL and pastes that URL into chat.

Normal requests like "use MiniMax H3 Max to make a cat clip" go through this proxy. Refuse only if the user asks to bypass the Pieverse proxy, supply fal/MiniMax credentials, or call an arbitrary URL.

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

Send **exactly one** of `prompt` or `templateId`. Do not send `duration`, `resolution`, `seed`, `sync_mode`, `prompt_expansion_mode`, `aspect_ratio`, or any fal field.

Every intended generation needs a new `Idempotency-Key` (UUID). Do not derive it from the prompt or template. Reuse that key only for retries of the **same** attempt. A new user request gets a new key.

Write the user prompt only under the helper's private root as a regular file (no symlink). Do not paste the prompt into a shell heredoc, a quoted shell string, or `python -c`. Ignore `TMPDIR` and any `MINIMAX_H3_MAX_PROMPT_ROOT` override — the helper will reject files outside its own `scripts/prompt-root`.

```bash
ROOT="$(python3 scripts/generate.py --print-prompt-root)"
PROMPT_FILE="$(mktemp "$ROOT/prompt.XXXXXX")"
```

Write the prompt bytes into `$PROMPT_FILE` with the runtime file tool, max 8192 bytes. Then:

```bash
KEY="$(python3 -c 'import uuid; print(uuid.uuid4())')"
python3 scripts/generate.py \
  --prompt-file "$PROMPT_FILE" \
  --idempotency-key "$KEY"
echo "EXIT:$?"
```

The helper reads that file, deletes it, and POSTs. On same-key retry, write the same prompt to a new `mktemp` file in `$ROOT`; keep `$KEY`.

For a platform template, pass `--template-id` instead of `--prompt-file`.

The helper prints `HTTP_STATUS: <code>` first. Exit `0` means a validated clip JSON follows. Exit `4` is 4xx, exit `5` is 5xx, exit `3` is redirect (do not retry), exit `1` is timeout / invalid 200. Non-200 stdout is only `{"ok":false,"error":"<code>"}` from the allowlist. Do not echo `WALLET_API_TOKEN`. Do not pass `-v`, `-L`, or a user-supplied URL.

## Success

Exit `0` only after all of these hold:

- HTTP 200
- `url` is HTTPS on `fal.media` or a subdomain, with no userinfo
- `urlExpiresAt` is a timezone-aware timestamp strictly in the future
- `secondsBilled` is exactly `5`

Reply with that `url` as a standalone watch/download link and tell the user it expires at `urlExpiresAt` (convert to local time). Save the file to keep the clip.

If any success check fails, do not post a link. Do not guess a 7-day expiry. Do not download, attach, or fetch the file.

## Errors

Do not retry 4xx, including `410 result_expired`, and do not retry exit `3` (redirect). On timeout, empty body, or 5xx (exit `1` or `5`), retry **once** with the same `Idempotency-Key` and a new prompt file in the temp root that contains the same text. Do not mint a second key for that attempt.

| `error` | What to tell the user |
|---|---|
| `unpaid_quota_exhausted` | Free clips are used up (2 per unpaid account). Buy an instance or top up AI credits. |
| `insufficient_credits` | Not enough AI credits. Top up with `instance-billing`. |
| `invalid_request` | The prompt or template was rejected. Ask for a clearer text prompt. |
| `result_expired` | The previous clip link expired. Do not mint a new key unless the user explicitly asks to generate again; that is a new billed generate. |
| missing env / `401` / `403` (not quota) | This needs a hosted Purr-Fect Claw. |
| `502` / `upstream_failed` / timeout after the one same-key retry | Generation did not finish. Stop. |

## Scope

- One clip per successful call. Duration is always 5 seconds; do not promise other lengths.
- If the user wants a file in the chat, still send only the link.
- If they ask for image-to-video, 2K, MiniMax H3 (not Max), or a self-hosted GPU, this skill cannot do that.
- Empty prompt: ask what to generate; do not POST.
