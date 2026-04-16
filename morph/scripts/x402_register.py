#!/usr/bin/env python3
"""
x402_register.py — Register with x402 Facilitator via platform wallet signing.

Based on vendor cmd_x402_register. Replaces local --private-key (EIP-191)
with platform /wallet/sign.

Usage:
  python3 skills/morph/scripts/x402_register.py [--save --name myagent]

Env vars:
  WALLET_API_URL   — platform API base URL
  WALLET_API_TOKEN — Bearer token
  INSTANCE_ID      — instance ID
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vendor', 'scripts'))
from morph_x402 import X402_FACILITATOR_BASE, _save_credentials  # noqa: E402

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
    parser = argparse.ArgumentParser(description="Register with x402 Facilitator")
    parser.add_argument("--save", action="store_true", help="Save credentials locally (encrypted)")
    parser.add_argument("--name", default=None, help="Credential name for --save")
    args = parser.parse_args()

    if not API_URL or not API_TOKEN or not INSTANCE_ID:
        sys.exit("Missing env: WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID")

    # ① Get address (replaces _load_account)
    address = _get_address()

    # ② Get nonce from facilitator
    try:
        r = http.get(f"{X402_FACILITATOR_BASE}/auth/nonce", params={"address": address}, timeout=15)
        r.raise_for_status()
        nonce_data = r.json()
    except http.RequestException as e:
        sys.exit(f"Failed to get nonce: {e}")

    if nonce_data.get("code", 0) != 0:
        sys.exit(f"Nonce error: {nonce_data.get('message', str(nonce_data))}")
    nonce_info = nonce_data.get("data", nonce_data)
    message = nonce_info["message"]
    nonce = nonce_info["nonce"]

    # ③ Sign challenge via platform API (replaces acct.sign_message)
    signature = _sign_message(message)

    # ④ Login → JWT
    try:
        r = http.post(
            f"{X402_FACILITATOR_BASE}/auth/login",
            json={"address": address, "signature": signature, "nonce": nonce},
            timeout=15,
        )
        r.raise_for_status()
        login_data = r.json()
    except http.RequestException as e:
        sys.exit(f"Login failed: {e}")

    if login_data.get("code", 0) != 0:
        sys.exit(f"Login error: {login_data.get('message', str(login_data))}")
    token = login_data.get("data", login_data).get("token")
    if not token:
        sys.exit("Login succeeded but no token returned")

    # ⑤ Create API key
    auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = http.post(f"{X402_FACILITATOR_BASE}/api-keys/create", headers=auth_headers, json={}, timeout=15)
        key_data = r.json()
    except http.RequestException as e:
        sys.exit(f"Failed to create API key: {e}")

    is_new = True
    if key_data.get("code") == 40005:
        is_new = False
        try:
            r = http.get(f"{X402_FACILITATOR_BASE}/api-keys/detail", headers=auth_headers, timeout=15)
            r.raise_for_status()
            key_info = r.json().get("data", r.json())
        except http.RequestException as e:
            sys.exit(f"Key exists but failed to fetch details: {e}")
    elif key_data.get("code", 0) != 0:
        sys.exit(f"Create key error: {key_data.get('message', str(key_data))}")
    else:
        key_info = key_data.get("data", key_data)

    access_key = key_info.get("accessKey", "")
    secret_key = key_info.get("secretKey", "")

    # ⑥ Optionally save credentials
    saved = False
    if args.save and not args.name:
        sys.exit("--save requires --name")
    if args.save and args.name:
        if not secret_key:
            sys.exit("Cannot save: secretKey not available (key was previously created)")
        _save_credentials(args.name, address, access_key, secret_key)
        saved = True

    result = {"access_key": access_key, "address": address, "is_new": is_new}
    if secret_key:
        result["secret_key"] = secret_key
    else:
        result["secret_key_note"] = "not available — only shown on first creation"
    if saved:
        result["saved"] = True
        result["name"] = args.name

    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except http.RequestException as e:
        sys.exit(f"API request failed: {e}")
    except (KeyError, ValueError, RuntimeError) as e:
        sys.exit(f"Error: {e}")
