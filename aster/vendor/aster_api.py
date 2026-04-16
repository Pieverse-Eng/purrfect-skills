#!/usr/bin/env python3
"""
Aster FAPI v3 CLI client.

Unsigned (market data) commands call the API directly.
Signed commands use a two-step flow:
  1. `build-sign-request` — outputs EIP-712 typed data JSON for wallet_sign_typed_data
  2. `signed-request`    — takes --signature and calls the API

Based on: https://github.com/asterdex/aster-mcp (v3_client.py)

Usage:
  python3 aster_api.py ticker --symbol BTCUSDT
  python3 aster_api.py depth --symbol BTCUSDT --limit 5
  python3 aster_api.py klines --symbol BTCUSDT --interval 1h --limit 10
  python3 aster_api.py funding-rate --symbol BTCUSDT
  python3 aster_api.py premium-index --symbol BTCUSDT
  python3 aster_api.py ticker-24hr --symbol BTCUSDT
  python3 aster_api.py exchange-info
  python3 aster_api.py server-time

  # Step 1: build sign payload for wallet_sign_typed_data
  python3 aster_api.py build-sign-request --endpoint /fapi/v3/balance --user 0x... --signer 0x...

  # Step 2: call API with pre-computed signature
  python3 aster_api.py signed-request --method GET --endpoint /fapi/v3/balance \
    --user 0x... --signer 0x... --nonce 123456 --signature 0x...
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "https://fapi.asterdex.com"

EIP712_DOMAIN = {
	"name": "AsterSignTransaction",
	"version": "1",
	"chainId": 1666,
	"verifyingContract": "0x0000000000000000000000000000000000000000",
}


def _params_to_str(params):
	"""Sort keys ASCII and join as key=value&key=value (all values as strings)."""
	return "&".join(f"{k}={v}" for k, v in sorted(params.items()))


def _next_nonce():
	"""Monotonic nonce in the format expected by Aster (ms * 1_000_000)."""
	return int(time.time() * 1000) * 1_000_000


def _api_request(method, endpoint, params=None):
	"""Make an HTTP request to the Aster API. Returns parsed JSON."""
	url = f"{BASE_URL}{endpoint}"
	params = params or {}
	headers = {"User-Agent": "aster-api/0.1.0"}

	if method == "GET":
		if params:
			url = f"{url}?{urllib.parse.urlencode(params)}"
		req = urllib.request.Request(url, headers=headers)
	else:
		data = urllib.parse.urlencode(params).encode()
		headers["Content-Type"] = "application/x-www-form-urlencoded"
		req = urllib.request.Request(url, data=data, headers=headers, method=method)

	try:
		with urllib.request.urlopen(req, timeout=30) as resp:
			return json.loads(resp.read().decode())
	except urllib.error.HTTPError as e:
		body = e.read().decode() if e.fp else ""
		print(json.dumps({"error": f"HTTP {e.code}", "body": body}))
		sys.exit(1)


# ---------- Unsigned (public) commands ----------

def cmd_ticker(args):
	params = {}
	if args.symbol:
		params["symbol"] = args.symbol
	print(json.dumps(_api_request("GET", "/fapi/v3/ticker/price", params)))

def cmd_ticker_24hr(args):
	params = {}
	if args.symbol:
		params["symbol"] = args.symbol
	print(json.dumps(_api_request("GET", "/fapi/v3/ticker/24hr", params)))

def cmd_depth(args):
	params = {"symbol": args.symbol, "limit": args.limit}
	print(json.dumps(_api_request("GET", "/fapi/v3/depth", params)))

def cmd_klines(args):
	params = {"symbol": args.symbol, "interval": args.interval, "limit": args.limit}
	print(json.dumps(_api_request("GET", "/fapi/v3/klines", params)))

def cmd_premium_index(args):
	params = {}
	if args.symbol:
		params["symbol"] = args.symbol
	print(json.dumps(_api_request("GET", "/fapi/v3/premiumIndex", params)))

def cmd_funding_rate(args):
	params = {"limit": args.limit}
	if args.symbol:
		params["symbol"] = args.symbol
	print(json.dumps(_api_request("GET", "/fapi/v3/fundingRate", params)))

def cmd_funding_info(args):
	params = {}
	if args.symbol:
		params["symbol"] = args.symbol
	print(json.dumps(_api_request("GET", "/fapi/v3/fundingInfo", params)))

def cmd_trades(args):
	params = {"symbol": args.symbol, "limit": args.limit}
	print(json.dumps(_api_request("GET", "/fapi/v3/trades", params)))

def cmd_exchange_info(args):
	params = {}
	if args.symbol:
		params["symbol"] = args.symbol
	print(json.dumps(_api_request("GET", "/fapi/v3/exchangeInfo", params)))

def cmd_server_time(args):
	print(json.dumps(_api_request("GET", "/fapi/v3/time")))

def cmd_book_ticker(args):
	params = {}
	if args.symbol:
		params["symbol"] = args.symbol
	print(json.dumps(_api_request("GET", "/fapi/v3/ticker/bookTicker", params)))


# ---------- Signed request helpers ----------

def cmd_build_sign_request(args):
	"""Build the EIP-712 typed data payload for wallet_sign_typed_data.

	Outputs JSON with:
	  - typedData: pass directly to wallet_sign_typed_data
	  - callParams: use with signed-request after signing
	"""
	params = {}
	# Parse --param key=value pairs
	if args.param:
		for p in args.param:
			k, v = p.split("=", 1)
			params[k] = v

	# Add auth params
	timestamp = str(int(time.time() * 1000))
	nonce = str(_next_nonce())
	params["timestamp"] = timestamp
	params["nonce"] = nonce
	params["user"] = args.user
	params["signer"] = args.signer

	param_str = _params_to_str(params)

	typed_data = {
		"domain": EIP712_DOMAIN,
		"types": {
			"EIP712Domain": [
				{"name": "name", "type": "string"},
				{"name": "version", "type": "string"},
				{"name": "chainId", "type": "uint256"},
				{"name": "verifyingContract", "type": "address"},
			],
			"Message": [{"name": "msg", "type": "string"}],
		},
		"primaryType": "Message",
		"message": {"msg": param_str},
	}

	output = {
		"typedData": typed_data,
		"callParams": {
			"method": args.method,
			"endpoint": args.endpoint,
			"nonce": nonce,
			"timestamp": timestamp,
			"user": args.user,
			"signer": args.signer,
			"params": {k: v for k, v in params.items() if k not in ("nonce", "timestamp", "user", "signer")},
		},
	}
	print(json.dumps(output, indent=2))


def cmd_signed_request(args):
	"""Make a signed API request with a pre-computed signature."""
	params = {}
	if args.param:
		for p in args.param:
			k, v = p.split("=", 1)
			params[k] = v

	params["timestamp"] = args.timestamp or str(int(time.time() * 1000))
	params["nonce"] = args.nonce
	params["user"] = args.user
	params["signer"] = args.signer
	params["signature"] = args.signature

	print(json.dumps(_api_request(args.method, args.endpoint, params)))


# ---------- CLI ----------

def main():
	parser = argparse.ArgumentParser(description="Aster DEX FAPI v3 CLI")
	sub = parser.add_subparsers(dest="command", required=True)

	# Market data (unsigned)
	p = sub.add_parser("ticker", help="Latest price")
	p.add_argument("--symbol")
	p.set_defaults(func=cmd_ticker)

	p = sub.add_parser("ticker-24hr", help="24h ticker stats")
	p.add_argument("--symbol")
	p.set_defaults(func=cmd_ticker_24hr)

	p = sub.add_parser("depth", help="Order book")
	p.add_argument("--symbol", required=True)
	p.add_argument("--limit", type=int, default=20)
	p.set_defaults(func=cmd_depth)

	p = sub.add_parser("klines", help="Candlestick data")
	p.add_argument("--symbol", required=True)
	p.add_argument("--interval", required=True)
	p.add_argument("--limit", type=int, default=100)
	p.set_defaults(func=cmd_klines)

	p = sub.add_parser("premium-index", help="Mark price and funding rate")
	p.add_argument("--symbol")
	p.set_defaults(func=cmd_premium_index)

	p = sub.add_parser("funding-rate", help="Funding rate history")
	p.add_argument("--symbol")
	p.add_argument("--limit", type=int, default=100)
	p.set_defaults(func=cmd_funding_rate)

	p = sub.add_parser("funding-info", help="Funding info (intervals, caps)")
	p.add_argument("--symbol")
	p.set_defaults(func=cmd_funding_info)

	p = sub.add_parser("trades", help="Recent trades")
	p.add_argument("--symbol", required=True)
	p.add_argument("--limit", type=int, default=100)
	p.set_defaults(func=cmd_trades)

	p = sub.add_parser("exchange-info", help="Trading rules and symbol info")
	p.add_argument("--symbol")
	p.set_defaults(func=cmd_exchange_info)

	p = sub.add_parser("server-time", help="Server time")
	p.set_defaults(func=cmd_server_time)

	p = sub.add_parser("book-ticker", help="Best bid/ask")
	p.add_argument("--symbol")
	p.set_defaults(func=cmd_book_ticker)

	# Signed request helpers
	p = sub.add_parser("build-sign-request", help="Build EIP-712 typed data for wallet_sign_typed_data")
	p.add_argument("--method", default="GET", help="HTTP method (GET, POST, DELETE)")
	p.add_argument("--endpoint", required=True, help="API endpoint (e.g. /fapi/v3/balance)")
	p.add_argument("--user", required=True, help="Wallet address (user)")
	p.add_argument("--signer", required=True, help="Wallet address (signer)")
	p.add_argument("--param", action="append", help="key=value params (repeatable)")
	p.set_defaults(func=cmd_build_sign_request)

	p = sub.add_parser("signed-request", help="Make signed API call with pre-computed signature")
	p.add_argument("--method", default="GET")
	p.add_argument("--endpoint", required=True)
	p.add_argument("--user", required=True)
	p.add_argument("--signer", required=True)
	p.add_argument("--nonce", required=True)
	p.add_argument("--timestamp")
	p.add_argument("--signature", required=True)
	p.add_argument("--param", action="append", help="key=value params (repeatable)")
	p.set_defaults(func=cmd_signed_request)

	args = parser.parse_args()
	args.func(args)


if __name__ == "__main__":
	main()
