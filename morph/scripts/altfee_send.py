#!/usr/bin/env python3
"""
altfee_send.py — Morph alt-fee (0x7f) transaction via platform wallet signing.

Reuses vendor's _serialize_altfee_tx for RLP encoding. Replaces local
private-key signing with an HTTP call to /wallet/sign-transaction (mode 3).

Usage:
  python3 skills/morph/scripts/altfee_send.py \
    --to 0xRecipient --value 0.01 --fee-token-id 5 \
    [--data 0x...] [--fee-limit 500000] [--gas-limit 21000]

Env vars (set on pod by default):
  WALLET_API_URL   — platform API base URL
  WALLET_API_TOKEN — Bearer token
  INSTANCE_ID      — instance ID
"""

import argparse
import json
import os
import sys

# Import vendor helpers for RLP encoding + RPC
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vendor', 'scripts'))
from morph_altfee import _serialize_altfee_tx  # noqa: E402
from morph_api import rpc_call, validate_address, to_wei, CHAIN_ID  # noqa: E402

try:
    from eth_hash.auto import keccak
except ImportError:
    sys.exit("Missing dependency: pip install eth_hash")

import requests  # noqa: E402

# ---------------------------------------------------------------------------
# Platform wallet helpers
# ---------------------------------------------------------------------------

API_URL = os.environ.get("WALLET_API_URL", "")
API_TOKEN = os.environ.get("WALLET_API_TOKEN", "")
INSTANCE_ID = os.environ.get("INSTANCE_ID", "")


def _api_headers():
    return {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


def _get_address():
    """Get instance EVM wallet address from platform API."""
    r = requests.get(f"{API_URL}/v1/instances/{INSTANCE_ID}/wallet", headers=_api_headers(), timeout=15)
    r.raise_for_status()
    for w in r.json().get("data", []):
        if w.get("chainType") == "ethereum":
            return w["address"]
    raise RuntimeError("No EVM wallet found for this instance")


def _sign_hash(hash_hex):
    """Sign a raw 32-byte hash via platform /wallet/sign-transaction mode 3."""
    body = {"txs": [{"msgs": [{"signType": "eth_sign", "hash": hash_hex}]}]}
    r = requests.post(
        f"{API_URL}/v1/instances/{INSTANCE_ID}/wallet/sign-transaction",
        headers=_api_headers(),
        json=body,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        sys.exit(f"sign-transaction failed: {data.get('error', 'unknown')}")
    return data["data"]["txs"][0]["msgs"][0]["sig"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Morph alt-fee (0x7f) send via platform wallet")
    parser.add_argument("--to", required=True, help="Recipient/contract address")
    parser.add_argument("--value", default=None, help="ETH value to send (human-readable, default: 0)")
    parser.add_argument("--data", default=None, help="Transaction calldata hex (default: 0x)")
    parser.add_argument("--fee-token-id", type=int, required=True, help="Fee token ID (1-6)")
    parser.add_argument("--fee-limit", type=int, default=0, help="Max fee token amount (default: 0 = no limit)")
    parser.add_argument("--gas-limit", type=int, default=None, help="Gas limit (auto-estimated if omitted)")
    args = parser.parse_args()

    if not API_URL or not API_TOKEN or not INSTANCE_ID:
        sys.exit("Missing env: WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID")

    validate_address(args.to)
    value_wei = to_wei(args.value) if args.value else 0
    data_hex = args.data or "0x"

    # ① Get wallet address
    address = _get_address()

    # ② Read chain state
    nonce = int(rpc_call("eth_getTransactionCount", [address, "latest"]), 16)
    max_fee_per_gas = int(rpc_call("eth_gasPrice", []), 16)

    if args.gas_limit:
        gas_limit = args.gas_limit
    else:
        tx_for_estimate = {"from": address, "to": args.to}
        if data_hex != "0x":
            tx_for_estimate["data"] = data_hex
        if value_wei > 0:
            tx_for_estimate["value"] = hex(value_wei)
        gas_limit = int(rpc_call("eth_estimateGas", [tx_for_estimate]), 16)

    # ③ Build tx dict
    tx = {
        "chainId": CHAIN_ID,
        "nonce": nonce,
        "maxPriorityFeePerGas": 0,
        "maxFeePerGas": max_fee_per_gas,
        "gas": gas_limit,
        "to": args.to,
        "value": value_wei,
        "data": data_hex,
        "feeTokenID": args.fee_token_id,
        "feeLimit": args.fee_limit,
    }

    # ④ Serialize unsigned → hash
    unsigned_bytes = _serialize_altfee_tx(tx)
    msg_hash = "0x" + keccak(unsigned_bytes).hex()

    # ⑤ Sign hash via platform API
    sig_hex = _sign_hash(msg_hash)

    # ⑥ Parse r, s, v from 65-byte signature
    sig_bytes = bytes.fromhex(sig_hex[2:] if sig_hex.startswith("0x") else sig_hex)
    r = int.from_bytes(sig_bytes[:32], "big")
    s = int.from_bytes(sig_bytes[32:64], "big")
    v = sig_bytes[64]
    y_parity = v - 27 if v >= 27 else v

    # ⑦ Serialize signed tx
    signed_bytes = _serialize_altfee_tx(tx, (y_parity, r, s))
    raw_tx = "0x" + signed_bytes.hex()

    # ⑧ Broadcast
    tx_hash = rpc_call("eth_sendRawTransaction", [raw_tx])

    print(json.dumps({
        "tx_hash": tx_hash,
        "from": address,
        "to": args.to,
        "value_eth": args.value or "0",
        "fee_token_id": args.fee_token_id,
        "fee_limit": args.fee_limit,
        "gas": gas_limit,
        "type": "0x7f",
    }))


if __name__ == "__main__":
    try:
        main()
    except http.RequestException as e:
        sys.exit(f"API request failed: {e}")
    except (KeyError, ValueError, RuntimeError) as e:
        sys.exit(f"Unexpected response: {e}")
