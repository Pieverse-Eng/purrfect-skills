#!/usr/bin/env python3
"""
eip7702.py — EIP-7702 EOA delegation via platform wallet signing.

Reuses vendor's _serialize_7702_tx, _compute_auth_hash, _compute_data_hash,
_encode_batch_calldata for RLP/ABI encoding. Replaces local private-key
signing with HTTP calls to /wallet/sign-transaction (mode 3 raw hash).

Subcommands:
  authorize  — sign a 7702 authorization offline (no tx)
  send       — single delegated call (type 0x04 tx)
  batch      — atomic multi-call via delegation (type 0x04 tx)
  revoke     — revoke delegation (authorize address(0))

Env vars: WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'vendor', 'scripts'))
from morph_7702 import (  # noqa: E402
    _compute_auth_hash,
    _compute_data_hash,
    _encode_batch_calldata,
    _get_delegation_nonce,
    _serialize_7702_tx,
    _estimate_gas_7702,
    _keccak,
    GAS_FALLBACK_SEND,
    GAS_FALLBACK_BATCH,
    GAS_REVOKE,
    REVOKE_ADDR,
)
from morph_api import (  # noqa: E402
    CHAIN_ID,
    rpc_call,
    validate_address,
    to_wei,
    _hex_to_bytes,
)

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


def _sign_hash(hash_hex):
    """Sign a raw 32-byte hash via /wallet/sign-transaction mode 3."""
    body = {"txs": [{"msgs": [{"signType": "eth_sign", "hash": hash_hex}]}]}
    r = http.post(
        f"{API_URL}/v1/instances/{INSTANCE_ID}/wallet/sign-transaction",
        headers=_api_headers(), json=body, timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        sys.exit(f"sign-transaction failed: {data.get('error', 'unknown')}")
    return data["data"]["txs"][0]["msgs"][0]["sig"]


def _parse_sig(sig_hex):
    """Parse 65-byte hex signature into (y_parity, r, s) for RLP fields."""
    raw = sig_hex[2:] if sig_hex.startswith("0x") else sig_hex
    sig_bytes = bytes.fromhex(raw)
    r = int.from_bytes(sig_bytes[:32], "big")
    s = int.from_bytes(sig_bytes[32:64], "big")
    v = sig_bytes[64]
    y_parity = v - 27 if v >= 27 else v
    return y_parity, r, s


def _sign_auth_remote(chain_id, contract_addr, nonce):
    """Sign EIP-7702 authorization hash via platform and return auth dict."""
    auth_hash = _compute_auth_hash(chain_id, contract_addr, nonce)
    sig_hex = _sign_hash("0x" + auth_hash.hex())
    y, r, s = _parse_sig(sig_hex)
    return {"chainId": chain_id, "contract": contract_addr, "nonce": nonce, "y_parity": y, "r": r, "s": s}


def _sign_eip191_hash_remote(data_hash_bytes):
    """Sign keccak256(EIP-191 prefix + data_hash) — matches encode_defunct(primitive=...)."""
    prefix = b'\x19Ethereum Signed Message:\n32'
    final_hash = _keccak(prefix + data_hash_bytes)
    return bytes.fromhex(_sign_hash("0x" + final_hash.hex())[2:])


def _sign_7702_tx_remote(tx, auth_list):
    """Serialize, hash, sign, and reconstruct a type 0x04 tx."""
    unsigned = _serialize_7702_tx(tx, auth_list)
    msg_hash = _keccak(unsigned)
    sig_hex = _sign_hash("0x" + msg_hash.hex())
    y, r, s = _parse_sig(sig_hex)
    signed = _serialize_7702_tx(tx, auth_list, (y, r, s))
    return "0x" + signed.hex()


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_authorize(args):
    validate_address(args.delegate)
    address = _get_address()
    tx_nonce = int(rpc_call("eth_getTransactionCount", [address, "latest"]), 16)
    auth_nonce = tx_nonce + 1
    auth = _sign_auth_remote(CHAIN_ID, args.delegate, auth_nonce)
    print(json.dumps({
        "chainId": CHAIN_ID,
        "contractAddress": args.delegate,
        "nonce": auth_nonce,
        "yParity": hex(auth["y_parity"]),
        "r": hex(auth["r"]),
        "s": hex(auth["s"]),
    }))


def cmd_send(args):
    validate_address(args.to)
    validate_address(args.delegate)
    address = _get_address()
    value_wei = to_wei(args.value) if args.value else 0
    data_hex = args.data or "0x"
    call = (args.to, value_wei, _hex_to_bytes(data_hex))
    _do_delegated_execute(address, args.delegate, [call], args.gas_limit, GAS_FALLBACK_SEND)


def cmd_batch(args):
    validate_address(args.delegate)
    try:
        raw_calls = json.loads(args.calls)
    except (json.JSONDecodeError, TypeError) as e:
        sys.exit(f"Invalid --calls JSON: {e}")
    if not isinstance(raw_calls, list) or len(raw_calls) == 0:
        sys.exit("--calls must be a non-empty JSON array")

    address = _get_address()
    calls_tuples = []
    for i, c in enumerate(raw_calls):
        if "to" not in c:
            sys.exit(f"call[{i}] missing 'to' field")
        validate_address(c["to"])
        v = to_wei(str(c.get("value", "0")))
        d = _hex_to_bytes(c.get("data", "0x"))
        calls_tuples.append((c["to"], v, d))
    _do_delegated_execute(address, args.delegate, calls_tuples, args.gas_limit, GAS_FALLBACK_BATCH)


def cmd_revoke(_args):
    address = _get_address()
    tx_nonce = int(rpc_call("eth_getTransactionCount", [address, "latest"]), 16)
    auth_nonce = tx_nonce + 1
    auth = _sign_auth_remote(CHAIN_ID, REVOKE_ADDR, auth_nonce)
    gas_price = int(rpc_call("eth_gasPrice", []), 16)
    tx = {"chainId": CHAIN_ID, "nonce": tx_nonce, "maxFeePerGas": gas_price, "gas": GAS_REVOKE, "to": address, "value": 0, "data": "0x"}
    raw_tx = _sign_7702_tx_remote(tx, [auth])
    tx_hash = rpc_call("eth_sendRawTransaction", [raw_tx])
    print(json.dumps({"tx_hash": tx_hash, "revoked": True}))


def _do_delegated_execute(eoa, delegate_addr, calls_tuples, gas_override, gas_fallback):
    """Shared logic for send + batch: sign execute data → sign auth → sign tx → broadcast."""
    tx_nonce = int(rpc_call("eth_getTransactionCount", [eoa, "latest"]), 16)
    auth_nonce = tx_nonce + 1

    # 1. Sign delegate execute() data hash (EIP-191 over raw bytes)
    delegation_nonce = _get_delegation_nonce(eoa)
    data_hash = _compute_data_hash(calls_tuples, delegation_nonce, CHAIN_ID, eoa)
    execute_sig = _sign_eip191_hash_remote(data_hash)
    execute_calldata = _encode_batch_calldata(calls_tuples, delegation_nonce, execute_sig)

    # 2. Sign EIP-7702 authorization
    auth = _sign_auth_remote(CHAIN_ID, delegate_addr, auth_nonce)

    # 3. Build + sign + broadcast the 0x04 tx
    gas_price = int(rpc_call("eth_gasPrice", []), 16)
    gas_limit = gas_override or _estimate_gas_7702(eoa, eoa, 0, execute_calldata, gas_fallback)
    tx = {"chainId": CHAIN_ID, "nonce": tx_nonce, "maxFeePerGas": gas_price, "gas": gas_limit, "to": eoa, "value": 0, "data": execute_calldata}
    raw_tx = _sign_7702_tx_remote(tx, [auth])
    tx_hash = rpc_call("eth_sendRawTransaction", [raw_tx])
    print(json.dumps({"tx_hash": tx_hash, "calls_count": len(calls_tuples)}))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if not API_URL or not API_TOKEN or not INSTANCE_ID:
        sys.exit("Missing env: WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID")

    parser = argparse.ArgumentParser(description="EIP-7702 via platform wallet")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("authorize", help="Sign a 7702 authorization offline (no tx)")
    p.add_argument("--delegate", required=True, help="Delegate contract address")

    p = sub.add_parser("send", help="Single delegated call (type 0x04)")
    p.add_argument("--delegate", required=True, help="Delegate contract address")
    p.add_argument("--to", required=True, help="Call target address")
    p.add_argument("--value", default=None, help="ETH value (default: 0)")
    p.add_argument("--data", default=None, help="Calldata hex (default: 0x)")
    p.add_argument("--gas-limit", type=int, default=None, help="Gas limit (auto if omitted)")

    p = sub.add_parser("batch", help="Atomic multi-call via delegation (type 0x04)")
    p.add_argument("--delegate", required=True, help="Delegate contract address")
    p.add_argument("--calls", required=True, help='JSON array of {to, value, data}')
    p.add_argument("--gas-limit", type=int, default=None, help="Gas limit (auto if omitted)")

    sub.add_parser("revoke", help="Revoke delegation (authorize address(0))")

    args = parser.parse_args()
    {"authorize": cmd_authorize, "send": cmd_send, "batch": cmd_batch, "revoke": cmd_revoke}[args.command](args)


if __name__ == "__main__":
    try:
        main()
    except http.RequestException as e:
        sys.exit(f"API request failed: {e}")
    except (KeyError, ValueError, RuntimeError) as e:
        sys.exit(f"Unexpected response: {e}")
