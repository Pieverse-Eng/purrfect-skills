#!/usr/bin/env python3
"""POST one MiniMax H3 Max generate to the Pieverse platform proxy.

Prompt arrives through a regular file under the skill temp root, never
through shell syntax. Duration, resolution, and other fal fields are not
sent. Redirects are rejected so bearer tokens never leave the platform
origin.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from datetime import datetime, timezone
from http.client import IncompleteRead
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ENDPOINT_SUFFIX = "/media/minimax-h3-max"
FORBIDDEN_BODY_KEYS = (
    "duration",
    "resolution",
    "seed",
    "sync_mode",
    "prompt_expansion_mode",
    "aspect_ratio",
)
ALLOWED_ERRORS = frozenset(
    {
        "unpaid_quota_exhausted",
        "insufficient_credits",
        "invalid_request",
        "result_expired",
        "upstream_failed",
        "redirect_not_allowed",
        "attempt_in_flight",
        "attempt_indeterminate",
        "idempotency_key_reused",
        "provider_output_invalid",
    }
)
TIMEOUT_SECONDS = 60
MAX_PROMPT_BYTES = 8192
MAX_RESPONSE_BYTES = 4096
READ_FAILURES = (OSError, IncompleteRead)


class FailClosedRedirects(HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        raise HTTPError(req.full_url, code, "redirect_not_allowed", headers, fp)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_300 = http_error_302


_OPENER = build_opener(FailClosedRedirects)


def open_url(request: Request, timeout: float):
    return _OPENER.open(request, timeout=timeout)


def die(message: str, code: int = 2) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def prompt_root() -> Path:
    here = Path(__file__).resolve().parent
    root = here / "prompt-root"
    if root.is_symlink():
        die("prompt root escaped")
    root.mkdir(mode=0o700, exist_ok=True)
    os.chmod(root, 0o700)
    info = os.lstat(root)
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        die("prompt root must be a directory")
    if info.st_uid != os.geteuid():
        die("prompt root owner")
    if info.st_mode & 0o077:
        die("prompt root mode")
    resolved = root.resolve()
    if resolved.parent != here:
        die("prompt root escaped")
    return resolved


def read_bounded(fp, limit: int = MAX_RESPONSE_BYTES) -> bytes:
    chunk = fp.read(limit + 1)
    if not chunk:
        return b""
    if isinstance(chunk, str):
        chunk = chunk.encode("utf-8")
    if len(chunk) > limit:
        raise ValueError("response too large")
    return chunk


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


def public_error(status: int, raw: bytes) -> dict[str, Any]:
    if 300 <= status < 400:
        return {"ok": False, "error": "redirect_not_allowed"}
    if len(raw) > MAX_RESPONSE_BYTES:
        return {"ok": False, "error": "unknown"}
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {"ok": False, "error": "unknown"}
    if not isinstance(payload, dict):
        return {"ok": False, "error": "unknown"}
    code = payload.get("error")
    if code not in ALLOWED_ERRORS:
        return {"ok": False, "error": "unknown"}
    return {"ok": False, "error": code}


def read_prompt_file(path_str: str) -> str:
    root = prompt_root().resolve()
    if not root.is_dir():
        die("prompt temp root missing")
    given = Path(path_str)
    if given.is_symlink():
        die("prompt file must be a regular file")
    resolved = given.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError:
        die("prompt file outside temp root")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(resolved, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            die("prompt file must be a regular file")
        if info.st_nlink != 1:
            die("prompt file must not be linked")
        if info.st_uid != os.geteuid():
            die("prompt file owner")
        if info.st_mode & 0o077:
            die("prompt file mode")
        if info.st_size > MAX_PROMPT_BYTES:
            die("prompt file too large")
        data = os.read(fd, info.st_size)
    finally:
        os.close(fd)
    try:
        os.unlink(resolved)
    except OSError:
        die("could not remove prompt file")
    text = data.decode("utf-8").rstrip("\n")
    if not text.strip():
        die("empty prompt")
    return text


def request_body(prompt_file: str | None, template_id: str | None) -> dict[str, str]:
    if bool(prompt_file) == bool(template_id):
        die("exactly one of --prompt-file or --template-id")
    if template_id:
        body: dict[str, str] = {"templateId": template_id}
    else:
        body = {"prompt": read_prompt_file(prompt_file)}
    leaked = [key for key in FORBIDDEN_BODY_KEYS if key in body]
    if leaked:
        die(f"forbidden field: {leaked[0]}")
    return body


def retry_after_seconds(headers) -> int | None:
    if headers is None:
        return None
    raw = headers.get("Retry-After")
    if raw is None:
        return None
    try:
        seconds = int(str(raw).strip())
    except ValueError:
        return None
    if seconds < 1:
        return None
    return min(seconds, 30)


def post(url: str, token: str, idempotency_key: str, body: dict[str, str]) -> tuple[int, bytes, int | None]:
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
        with open_url(request, timeout=TIMEOUT_SECONDS) as response:
            try:
                raw = read_bounded(response)
            except READ_FAILURES:
                return 0, b"", None
            except ValueError:
                return int(getattr(response, "status", 0) or 0), b"", None
            return int(response.status), raw, retry_after_seconds(getattr(response, "headers", None))
    except HTTPError as error:
        wait = retry_after_seconds(error.headers)
        try:
            raw = read_bounded(error)
        except READ_FAILURES:
            return int(error.code), b"", wait
        except ValueError:
            return int(error.code), b"", wait
        return int(error.code), raw, wait
    except (URLError, OSError, IncompleteRead):
        return 0, b"", None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file")
    parser.add_argument("--template-id")
    parser.add_argument("--idempotency-key")
    parser.add_argument("--print-prompt-root", action="store_true")
    args = parser.parse_args(argv)

    if args.print_prompt_root:
        print(prompt_root())
        return 0
    if not args.idempotency_key:
        die("missing --idempotency-key")

    base = os.environ.get("WALLET_API_URL")
    token = os.environ.get("WALLET_API_TOKEN")
    instance_id = os.environ.get("INSTANCE_ID")
    if not base or not token or not instance_id:
        die("missing WALLET_API_URL, WALLET_API_TOKEN, or INSTANCE_ID")

    body = request_body(args.prompt_file, args.template_id)
    url = f"{base.rstrip('/')}/v1/instances/{instance_id}{ENDPOINT_SUFFIX}"
    status, raw, wait = post(url, token, args.idempotency_key, body)
    print(f"HTTP_STATUS: {status}")
    if status == 0:
        return 1
    if status != 200:
        print(json.dumps(public_error(status, raw), ensure_ascii=False))
        if status == 409 and wait is not None:
            print(f"RETRY_AFTER: {wait}")
        if 300 <= status < 400:
            return 3
        if status >= 500:
            return 5
        if status >= 400:
            return 4
        return 1
    try:
        payload = json.loads(raw.decode("utf-8"))
        clip = validate_success(payload)
    except (ValueError, json.JSONDecodeError, TimeoutError) as error:
        print(f"INVALID_SUCCESS: {error}", file=sys.stderr)
        return 1
    print(json.dumps(clip, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
