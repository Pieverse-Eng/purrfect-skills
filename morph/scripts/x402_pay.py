#!/usr/bin/env python3
"""
x402_pay.py — Pay for an x402-protected resource via platform wallet signing.

Based on vendor cmd_x402_pay. Replaces local --private-key (EIP-712
TransferWithAuthorization) with platform /wallet/sign-typed-data.

Usage:
  python3 skills/morph/scripts/x402_pay.py --url https://api.example.com/resource [--max-payment 1.0]

Env vars:
  WALLET_API_URL   — platform API base URL
  WALLET_API_TOKEN — Bearer token
  INSTANCE_ID      — instance ID
"""

import argparse
import base64
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vendor', 'scripts'))
from morph_x402 import (  # noqa: E402
    X402_USDC_ADDRESS,
    X402_DEFAULT_MAX_USDC,
    _parse_402_requirements,
    _required_amount_raw,
    _usdc_from_raw,
    _x402_nonce,
)
from morph_api import CHAIN_ID  # noqa: E402

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


def _sign_typed_data(typed_data):
    """Sign EIP-712 typed data via platform /wallet/sign-typed-data."""
    r = http.post(
        f"{API_URL}/v1/instances/{INSTANCE_ID}/wallet/sign-typed-data",
        headers=_api_headers(),
        json=typed_data,
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        sys.exit(f"sign-typed-data failed: {data.get('error', 'unknown')}")
    return data["data"]["signature"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Pay for an x402-protected resource")
    parser.add_argument("--url", required=True, help="x402-protected URL")
    parser.add_argument("--max-payment", type=float, default=X402_DEFAULT_MAX_USDC,
                        help=f"Max USDC to pay (default: {X402_DEFAULT_MAX_USDC})")
    args = parser.parse_args()

    if not API_URL or not API_TOKEN or not INSTANCE_ID:
        sys.exit("Missing env: WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID")

    address = _get_address()

    # ① Probe URL
    try:
        r = http.get(args.url, timeout=15, allow_redirects=True)
    except http.RequestException as e:
        sys.exit(f"Request failed: {e}")

    if r.status_code != 402:
        print(json.dumps({"status": r.status_code, "requires_payment": False, "content": r.text}))
        return

    # ② Parse requirements + check max_payment
    requirements = _parse_402_requirements(r)
    amount_raw = _required_amount_raw(requirements)
    amount_usdc = float(_usdc_from_raw(str(amount_raw)))

    if amount_usdc > args.max_payment:
        sys.exit(f"Payment required: {amount_usdc} USDC exceeds --max-payment {args.max_payment} USDC")

    # ③ Build EIP-712 TransferWithAuthorization + sign via platform API
    extra = requirements.get("extra", {})
    domain = {
        "name": extra.get("name", "USDC"),
        "version": extra.get("version", "2"),
        "chainId": CHAIN_ID,
        "verifyingContract": X402_USDC_ADDRESS,
    }
    valid_before = int(time.time()) + 3600
    nonce = "0x" + _x402_nonce(address).hex()

    typed_data = {
        "domain": domain,
        "types": {
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "primaryType": "TransferWithAuthorization",
        "message": {
            "from": address,
            "to": requirements["payTo"],
            "value": str(amount_raw),
            "validAfter": "0",
            "validBefore": str(valid_before),
            "nonce": nonce,
        },
    }

    signature = _sign_typed_data(typed_data)

    # ④ Build payment payload + replay
    payload = {
        "x402Version": 2,
        "payload": {
            "signature": signature,
            "authorization": {
                "from": address,
                "to": requirements["payTo"],
                "value": str(amount_raw),
                "validAfter": "0",
                "validBefore": str(valid_before),
                "nonce": nonce,
            },
        },
        "accepted": requirements,
        "resource": {"url": requirements.get("resource", "")},
    }

    header_value = base64.b64encode(json.dumps(payload).encode()).decode()
    try:
        r2 = http.get(args.url, headers={"PAYMENT-SIGNATURE": header_value}, timeout=30)
    except http.RequestException as e:
        sys.exit(f"Payment replay failed: {e}")

    if r2.status_code != 200:
        sys.exit(f"Payment rejected: HTTP {r2.status_code} — {r2.text[:500]}")

    try:
        content = r2.json()
    except Exception:
        content = r2.text

    print(json.dumps({
        "status": r2.status_code,
        "amount_paid_usdc": _usdc_from_raw(str(amount_raw)),
        "pay_to": requirements.get("payTo"),
        "content": content,
    }))


if __name__ == "__main__":
    try:
        main()
    except http.RequestException as e:
        sys.exit(f"API request failed: {e}")
    except (KeyError, ValueError, RuntimeError) as e:
        sys.exit(f"Error: {e}")
