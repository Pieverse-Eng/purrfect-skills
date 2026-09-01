#!/usr/bin/env python3
"""POST one MiniMax H3 Max generate to the Pieverse platform proxy.

Prompt arrives through --prompt-file (data channel), never through shell
syntax. Duration, resolution, and other fal fields are not sent.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ENDPOINT_SUFFIX = "/media/minimax-h3-max"
FORBIDDEN_BODY_KEYS = (
    "duration",
    "resolution",
    "seed",
    "sync_mode",
    "prompt_expansion_mode",
    "aspect_ratio",
)
TIMEOUT_SECONDS = 60


def die(message: str, code: int = 2) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def parse_iso8601(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError("urlExpiresAt must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def fal_media_https(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    return (
        parsed.scheme == "https"
        and not parsed.username
        and not parsed.password
        and (host == "fal.media" or host.endswith(".fal.media"))
        and bool(parsed.path)
    )


def validate_success(payload: Any, *, now: datetime | None = None) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise ValueError("response is not ok")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("missing data")
    url = data.get("url")
    expires = data.get("urlExpiresAt")
    billed = data.get("secondsBilled")
    if not isinstance(url, str) or not fal_media_https(url):
        raise ValueError("url must be https on fal.media")
    if not isinstance(expires, str):
        raise ValueError("urlExpiresAt missing")
    expiry = parse_iso8601(expires)
    current = now or datetime.now(timezone.utc)
    if expiry <= current:
        raise ValueError("urlExpiresAt is not in the future")
    if billed != 5:
        raise ValueError("secondsBilled must be 5")
    extra = [key for key in data if key in FORBIDDEN_BODY_KEYS]
    if extra:
        raise ValueError("response echoed forbidden billing fields")
    return {
        "url": url,
        "urlExpiresAt": expires,
        "secondsBilled": 5,
    }


def request_body(prompt_file: str | None, template_id: str | None) -> dict[str, str]:
    if bool(prompt_file) == bool(template_id):
        die("exactly one of --prompt-file or --template-id")
    if template_id:
        body: dict[str, str] = {"templateId": template_id}
    else:
        text = Path(prompt_file).read_text(encoding="utf-8").rstrip("\n")
        if not text.strip():
            die("empty prompt")
        body = {"prompt": text}
    leaked = [key for key in FORBIDDEN_BODY_KEYS if key in body]
    if leaked:
        die(f"forbidden field: {leaked[0]}")
    return body


def post(url: str, token: str, idempotency_key: str, body: dict[str, str]) -> tuple[int, bytes]:
    request = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
        },
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return int(response.status), response.read()
    except HTTPError as error:
        return int(error.code), error.read()
    except URLError:
        return 0, b""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file")
    parser.add_argument("--template-id")
    parser.add_argument("--idempotency-key", required=True)
    args = parser.parse_args(argv)

    base = os.environ.get("WALLET_API_URL")
    token = os.environ.get("WALLET_API_TOKEN")
    instance_id = os.environ.get("INSTANCE_ID")
    if not base or not token or not instance_id:
        die("missing WALLET_API_URL, WALLET_API_TOKEN, or INSTANCE_ID")

    body = request_body(args.prompt_file, args.template_id)
    url = f"{base.rstrip('/')}/v1/instances/{instance_id}{ENDPOINT_SUFFIX}"
    status, raw = post(url, token, args.idempotency_key, body)
    print(f"HTTP_STATUS: {status}")
    if status == 0:
        return 1
    if status != 200:
        sys.stdout.write(raw.decode("utf-8", errors="replace"))
        if raw and not raw.endswith(b"\n"):
            sys.stdout.write("\n")
        if status >= 500:
            return 5
        if status >= 400:
            return 4
        return 1
    try:
        payload = json.loads(raw.decode("utf-8"))
        clip = validate_success(payload)
    except (ValueError, json.JSONDecodeError) as error:
        print(f"INVALID_SUCCESS: {error}", file=sys.stderr)
        return 1
    print(json.dumps(clip, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
