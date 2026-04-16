#!/usr/bin/env python3
"""
bridge_swap.py — One-step cross-chain swap via platform wallet signing.

Based on vendor cmd_bridge_swap. Replaces local --private-key signing
with platform /wallet/sign-transaction. Bulbaswap's nested tx shape
{chainId, data: {nonce, to, value, gasLimit, gasPrice, calldata}} is
flattened to the flat shape that signSingleTxItem expects.

Usage:
  python3 skills/morph/scripts/bridge_swap.py \
    --jwt <JWT from bridge_login.py> \
    --from-chain morph --from-contract USDT --from-amount 5 \
    --to-chain base --to-contract USDC \
    --market stargate \
    [--to-address 0x...] [--slippage 0.5] [--feature no_gas]

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
from morph_bridge import (  # noqa: E402
    _resolve_bridge_token,
    bridge_post_auth,
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


def _sign_txs(txs):
    """Sign unsigned bridge txs via /wallet/sign-transaction.

    Flattens Bulbaswap's nested shape to the flat shape signSingleTxItem expects.
    """
    flat_txs = []
    for tx_info in txs:
        d = tx_info["data"]
        flat_txs.append({
            "chainId": int(tx_info["chainId"]),
            "nonce": int(d["nonce"]),
            "to": d["to"],
            "value": str(d["value"]),
            "gasLimit": str(d["gasLimit"]),
            "gasPrice": str(d["gasPrice"]),
            "data": d["calldata"],
        })

    r = http.post(
        f"{API_URL}/v1/instances/{INSTANCE_ID}/wallet/sign-transaction",
        headers=_api_headers(),
        json={"txs": flat_txs},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        sys.exit(f"sign-transaction failed: {data.get('error', 'unknown')}")
    return [tx["sig"] for tx in data["data"]["txs"]]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Cross-chain swap via platform wallet")
    parser.add_argument("--jwt", required=True, help="JWT from bridge_login.py")
    parser.add_argument("--from-chain", required=True, help="Source chain (e.g. morph, eth, base)")
    parser.add_argument("--from-contract", required=True, help="Source token address or symbol")
    parser.add_argument("--from-amount", required=True, help="Amount to swap (human-readable)")
    parser.add_argument("--to-chain", required=True, help="Destination chain")
    parser.add_argument("--to-contract", required=True, help="Destination token address or symbol")
    parser.add_argument("--market", required=True, help="Market/protocol from quote (e.g. stargate)")
    parser.add_argument("--to-address", default=None, help="Recipient (default: sender)")
    parser.add_argument("--slippage", type=float, default=None, help="Slippage tolerance %%")
    parser.add_argument("--feature", default=None, help="Feature flag (e.g. no_gas)")
    args = parser.parse_args()

    if not API_URL or not API_TOKEN or not INSTANCE_ID:
        sys.exit("Missing env: WALLET_API_URL, WALLET_API_TOKEN, INSTANCE_ID")

    address = _get_address()
    to_address = args.to_address or address

    # Step 1: make order
    from_contract = _resolve_bridge_token(args.from_contract, chain=args.from_chain)
    to_contract = _resolve_bridge_token(args.to_contract, chain=args.to_chain)
    body = {
        "fromChain": args.from_chain,
        "fromContract": from_contract,
        "fromAmount": str(args.from_amount),
        "toChain": args.to_chain,
        "toContract": to_contract,
        "toAddress": to_address,
        "market": args.market,
    }
    if args.slippage is not None:
        body["slippage"] = str(args.slippage)
    if args.feature:
        body["feature"] = args.feature

    order = bridge_post_auth("/v2/order/makeSwapOrder", body, args.jwt)

    # Step 2: sign txs via platform wallet
    signed_list = _sign_txs(order.get("txs", []))

    # Step 3: submit
    order_id = order["orderId"]
    bridge_post_auth(
        "/v2/order/submitSwapOrder",
        {"orderId": order_id, "signedTxs": signed_list},
        args.jwt,
    )

    print(json.dumps({
        "orderId": order_id,
        "fromChain": args.from_chain,
        "toChain": args.to_chain,
        "fromAmount": str(args.from_amount),
        "toMinAmount": order.get("toMinAmount"),
        "txCount": len(signed_list),
        "status": "submitted",
    }))


if __name__ == "__main__":
    try:
        main()
    except http.RequestException as e:
        sys.exit(f"API request failed: {e}")
    except (KeyError, ValueError, RuntimeError) as e:
        sys.exit(f"Unexpected response: {e}")
