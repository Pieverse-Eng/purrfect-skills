#!/usr/bin/env python3
"""
agent_set_wallet.py — Bind an operational wallet to an EIP-8004 agent.

Replaces the vendor's --private-key (owner) with platform wallet signing.
The new wallet's private key is still passed via --new-wallet-key, same as vendor.
EIP-712 consent is signed locally with the new wallet key.
The owner tx is submitted via the platform wallet API.

Usage:
  python3 skills/morph/scripts/agent_set_wallet.py \
    --agent-id 42 --new-wallet-key 0xNewWalletPrivateKey

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
from morph_api import CHAIN_ID, rpc_call  # noqa: E402

import requests as http  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IDENTITY_REGISTRY = "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432"
DOMAIN_NAME = "ERC8004IdentityRegistry"
DOMAIN_VERSION = "1"
MAX_DEADLINE_DELAY = 300  # 5 minutes

# ---------------------------------------------------------------------------
# Platform wallet helpers
# ---------------------------------------------------------------------------

API_URL = os.environ.get("WALLET_API_URL", "")
API_TOKEN = os.environ.get("WALLET_API_TOKEN", "")
INSTANCE_ID = os.environ.get("INSTANCE_ID", "")


def _api_headers():
    return {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


def _get_owner_address():
    r = http.get(f"{API_URL}/v1/instances/{INSTANCE_ID}/wallet", headers=_api_headers(), timeout=15)
    r.raise_for_status()
    for w in r.json().get("data", []):
        if w.get("chainType") == "ethereum":
            return w["address"]
    raise RuntimeError("No EVM wallet found for this instance")


def _submit_tx(to, signature_str, args_json):
    """Submit a contract call via /wallet/execute with ABI encoding."""
    body = {
        "to": to,
        "abi": [f"function {signature_str}"],
        "functionName": signature_str.split("(")[0],
        "args": args_json,
        "chainId": CHAIN_ID,
    }
    r = http.post(
        f"{API_URL}/v1/instances/{INSTANCE_ID}/wallet/execute",
        headers=_api_headers(), json=body, timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        sys.exit(f"execute failed: {data.get('error', 'unknown')}")
    return data["data"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Bind operational wallet to EIP-8004 agent")
    parser.add_argument("--agent-id", type=int, required=True, help="Agent NFT token ID")
    parser.add_argument("--new-wallet-key", required=True, help="Private key of the wallet to bind as operational")
    args = parser.parse_args()

    if not API_URL or not API_TOKEN or not INSTANCE_ID:
        sys.exit("Missing env: WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID")

    try:
        from eth_account import Account
    except ImportError:
        sys.exit("Missing dependency: pip install eth_account")

    # Load new wallet locally — same as vendor
    new_wallet_acct = Account.from_key(args.new_wallet_key)
    new_wallet_address = new_wallet_acct.address

    # Get owner address from platform wallet
    owner_address = _get_owner_address()

    # Read block timestamp → deadline
    block = rpc_call("eth_getBlockByNumber", ["latest", False])
    current_ts = int(block["timestamp"], 16)
    deadline = current_ts + MAX_DEADLINE_DELAY

    # Sign EIP-712 consent locally with new wallet key — same as vendor
    signed = new_wallet_acct.sign_typed_data(
        domain_data={
            "name": DOMAIN_NAME,
            "version": DOMAIN_VERSION,
            "chainId": CHAIN_ID,
            "verifyingContract": IDENTITY_REGISTRY,
        },
        message_types={
            "AgentWalletSet": [
                {"name": "agentId", "type": "uint256"},
                {"name": "newWallet", "type": "address"},
                {"name": "owner", "type": "address"},
                {"name": "deadline", "type": "uint256"},
            ],
        },
        message_data={
            "agentId": args.agent_id,
            "newWallet": new_wallet_address,
            "owner": owner_address,
            "deadline": deadline,
        },
    )
    sig_hex = "0x" + signed.signature.hex() if isinstance(signed.signature, bytes) else str(signed.signature)

    # Submit tx as owner via platform wallet (replaces vendor's local --private-key signing)
    result = _submit_tx(
        IDENTITY_REGISTRY,
        "setAgentWallet(uint256,address,uint256,bytes)",
        [args.agent_id, new_wallet_address, deadline, sig_hex],
    )

    print(json.dumps({
        "tx_hash": result.get("hash"),
        "from": owner_address,
        "agent_id": args.agent_id,
        "new_wallet": new_wallet_address,
        "deadline": deadline,
    }))


if __name__ == "__main__":
    try:
        main()
    except http.RequestException as e:
        sys.exit(f"API request failed: {e}")
    except (KeyError, ValueError, RuntimeError) as e:
        sys.exit(f"Unexpected response: {e}")
