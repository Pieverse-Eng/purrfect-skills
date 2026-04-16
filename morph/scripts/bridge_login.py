#!/usr/bin/env python3
"""
bridge_login.py — Obtain a Bulbaswap bridge JWT via platform wallet signing.

Based on vendor cmd_bridge_login. Replaces local --private-key signing
with platform /wallet/sign (EIP-191).

Usage:
  JWT=$(python3 skills/morph/scripts/bridge_login.py | jq -r '.accessToken')
  python3 morph_api.py bridge-make-order --jwt "$JWT" ...

Env vars:
  WALLET_API_URL   — platform API base URL
  WALLET_API_TOKEN — Bearer token
  INSTANCE_ID      — instance ID
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vendor', 'scripts'))
from morph_api import _generate_auth_message, DEX_API  # noqa: E402

import requests as http  # noqa: E402

# ---------------------------------------------------------------------------
# Platform wallet helpers
# ---------------------------------------------------------------------------

API_URL = os.environ.get("WALLET_API_URL", "")
API_TOKEN = os.environ.get("WALLET_API_TOKEN", "")
INSTANCE_ID = os.environ.get("INSTANCE_ID", "")


def _api_headers():
    return {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


def _get_address():
    r = http.get(f"{API_URL}/v1/instances/{INSTANCE_ID}/wallet", headers=_api_headers(), timeout=15)
    r.raise_for_status()
    for w in r.json().get("data", []):
        if w.get("chainType") == "ethereum":
            return w["address"]
    raise RuntimeError("No EVM wallet found for this instance")


def _sign_message(message):
    """Sign a message via platform /wallet/sign (EIP-191)."""
    r = http.post(
        f"{API_URL}/v1/instances/{INSTANCE_ID}/wallet/sign",
        headers=_api_headers(),
        json={"message": message},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        sys.exit(f"sign failed: {data.get('error', 'unknown')}")
    return data["data"]["signature"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not API_URL or not API_TOKEN or not INSTANCE_ID:
        sys.exit("Missing env: WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID")

    # ① Get address from platform wallet (replaces _load_account)
    address = _get_address()

    # ② Fresh timestamp
    timestamp = int(time.time() * 1000)

    # ③ Build auth message (reuse vendor's exact format)
    message = _generate_auth_message(timestamp)

    # ④⑤ Sign via platform API (replaces acct.sign_message)
    signature = _sign_message(message)

    # ⑥ Exchange signature for JWT
    url = f"{DEX_API}/v1/auth/sign-in"
    try:
        r = http.post(url, json={"address": address, "signature": signature, "timestamp": timestamp}, timeout=30)
        r.raise_for_status()
        resp = r.json()
    except http.RequestException as e:
        sys.exit(f"Auth request failed: {e}")

    if resp.get("code") != 200:
        sys.exit(f"Auth error: {resp.get('msg', str(resp))}")

    # ⑦ Output JWT data
    print(json.dumps(resp.get("data")))


if __name__ == "__main__":
    try:
        main()
    except http.RequestException as e:
        sys.exit(f"API request failed: {e}")
    except (KeyError, ValueError, RuntimeError) as e:
        sys.exit(f"Error: {e}")
