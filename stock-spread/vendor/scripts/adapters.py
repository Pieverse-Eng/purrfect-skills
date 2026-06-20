#!/usr/bin/env python3
"""
stock-spread venue read adapters (READ-ONLY, keyless public market data).

Per-venue `parse_*` (pure, fixture-tested) is separated from `fetch_*` (network),
so the gate (`--selftest`) is deterministic over recorded real responses while
`--live` exercises the actual public endpoints. Output of `--live` is a payload
ready to pipe into `spread.py`.

Live keyless venues (probe-verified 2026-06-20): gate, bybit, binance_bstocks, solana_jupiter.
Deferred (no keyless public read): kraken (xStocks not on public AssetPairs), bitget (keyed wallet API).

Usage:
    python3 adapters.py --live <UNDERLYING>     # fetch live venues -> spread.py payload (stdout)
    python3 adapters.py --live <UNDERLYING> | python3 spread.py    # full read pipeline
    python3 adapters.py --selftest               # offline parse checks vs recorded fixtures (exit 0/1)

No API keys. Standard library only.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

try:
    from zoneinfo import ZoneInfo
    _ET = ZoneInfo("America/New_York")
except Exception:  # tzdata unavailable -> market state unknown (fail-safe to unreliable)
    _ET = None

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "symbology.json")
LIVE_VENUES = ("gate", "bybit", "binance_bstocks", "solana_jupiter")


def us_equity_market_open(now_ms):
    """Best-effort US-equity regular-session check (Mon-Fri 09:30-16:00 ET).
    Returns True/False, or None when the tz db is unavailable. Does NOT handle
    market holidays/half-days (documented limitation). Tokenized stocks trade 24/7;
    this flags whether the *underlying* equity market is open so spread.py can decide
    whether to certify the cross-venue spread."""
    if _ET is None:
        return None
    t = datetime.fromtimestamp(now_ms / 1000, _ET)
    if t.weekday() >= 5:  # Sat/Sun
        return False
    mins = t.hour * 60 + t.minute
    return 570 <= mins < 960  # 09:30 .. 16:00 ET


def _load():
    with open(DATA, "r") as f:
        return json.load(f)


def _get(url, timeout=12):
    req = Request(url, headers={"User-Agent": "stock-spread/1.0 (read-only)"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


# --- pure parsers: (raw, ctx) -> normalized quote (no timestamp; caller stamps) ---

def parse_gate(raw):
    row = raw[0]
    bid, ask = float(row["highest_bid"]), float(row["lowest_ask"])
    if bid <= 0 or ask <= 0:
        raise ValueError("gate one-sided/empty book (non-positive bid or ask)")
    return {"venue": "gate", "price": round((bid + ask) / 2, 6), "bid": bid, "ask": ask,
            "settlement": "USDT", "price_type": "mid"}


def parse_bybit(raw):
    row = raw["result"]["list"][0]
    bid, ask = float(row["bid1Price"]), float(row["ask1Price"])
    if bid <= 0 or ask <= 0:
        raise ValueError("bybit one-sided/empty book (non-positive bid or ask)")
    return {"venue": "bybit", "price": round((bid + ask) / 2, 6), "bid": bid, "ask": ask,
            "settlement": "USDT", "price_type": "mid"}


def parse_binance(raw):
    return {"venue": "binance_bstocks", "price": float(raw["price"]),
            "settlement": "USDT", "price_type": "mid", "note": "last-trade price (no bid/ask via this endpoint)"}


def parse_jupiter(raw, decimals_in, usdc_mint, usdc_decimals=6):
    # guard against a route/units change silently mis-scaling the price by orders of magnitude
    if raw.get("outputMint") != usdc_mint:
        raise ValueError(f"jupiter outputMint {raw.get('outputMint')!r} != expected USDC {usdc_mint!r}")
    in_amt, out_amt = int(raw["inAmount"]), int(raw["outAmount"])
    if in_amt <= 0 or out_amt <= 0:
        raise ValueError("jupiter non-positive in/out amount")
    units_in = in_amt / (10 ** decimals_in)
    usd = out_amt / (10 ** usdc_decimals)
    return {"venue": "solana_jupiter", "price": round(usd / units_in, 6),
            "settlement": "USDC", "price_type": "executable",
            "size_usd": round(float(raw.get("swapUsdValue", usd)), 2),
            "price_impact_pct": round(float(raw.get("priceImpactPct", 0.0)), 6)}


# --- fetchers: network ---

def fetch_gate(sym):
    return parse_gate(_get(f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={sym}"))


def fetch_bybit(sym):
    return parse_bybit(_get(f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={sym}"))


def fetch_binance(sym):
    return parse_binance(_get(f"https://api.binance.com/api/v3/ticker/price?symbol={sym}"))


def fetch_jupiter(mint, decimals, usdc_mint, usdc_decimals):
    amount = 10 ** decimals  # quote 1.0 token
    raw = _get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={usdc_mint}"
               f"&amount={amount}&slippageBps=50")
    return parse_jupiter(raw, decimals, usdc_mint, usdc_decimals)


def live_payload(underlying):
    data = _load()
    key = underlying.strip().upper()
    if key not in data["underlyings"]:
        return {"error": f"unknown underlying '{underlying}' — not in symbology map; refusing to guess"}
    venues = data["underlyings"][key]["venues"]
    usdc = data["quote_mints"]["USDC"]
    now_ms = int(time.time() * 1000)
    market_open = us_equity_market_open(now_ms)
    quotes, errors, skipped = [], [], []
    for v in LIVE_VENUES:
        info = venues.get(v)
        if not info or not info.get("live") or info.get("id") is None:
            skipped.append({"venue": v, "reason": (info.get("live_note") or info.get("source") or "no keyless public read") if info else "not covered"})
            continue
        try:
            if v == "gate":
                q = fetch_gate(info["id"])
            elif v == "bybit":
                q = fetch_bybit(info["id"])
            elif v == "binance_bstocks":
                q = fetch_binance(info["id"])
            elif v == "solana_jupiter":
                q = fetch_jupiter(info["id"], info["decimals"], usdc["mint"], usdc["decimals"])
            q.update({"timestamp_ms": now_ms, "verified": info.get("verified", False), "market_open": market_open})
            quotes.append(q)
        except (URLError, HTTPError, KeyError, ValueError, IndexError) as e:
            errors.append({"venue": v, "error": str(e)})
    # deferred venues surfaced (no silent caps)
    for v, info in venues.items():
        if v not in LIVE_VENUES or not info.get("live"):
            if not any(s["venue"] == v for s in skipped):
                skipped.append({"venue": v, "reason": info.get("live_note") or info.get("source") or "no keyless public read"})
    return {
        "underlying": key,
        "now_ms": now_ms,
        "pegs": {"USD": 1.0, "USDT": 1.0, "USDC": 1.0},
        "_peg_note": "default 1.0 pegs — live stablecoin peg source is a deferred enhancement",
        "_market_hours_note": "market_open = US-equity regular session (Mon-Fri 09:30-16:00 ET); holidays/half-days not handled; tokens trade 24/7 so off-hours legs are shown but the spread is not certified reliable",
        "quotes": quotes,
        "skipped": skipped,
        "errors": errors,
    }


# --- recorded real fixtures (probe 2026-06-20) for the deterministic gate ---

_FIX_GATE = [{"currency_pair": "TSLAX_USDT", "last": "402.68", "lowest_ask": "402.78",
              "highest_bid": "402.65", "base_volume": "180.344", "high_24h": "403.47", "low_24h": "398.83"}]
_FIX_BYBIT = {"retCode": 0, "result": {"category": "spot", "list": [
    {"symbol": "TSLAXUSDT", "bid1Price": "402.6", "ask1Price": "402.7", "lastPrice": "402.55"}]}}
_FIX_BINANCE = {"symbol": "TSLABUSDT", "price": "402.43000000"}
_FIX_JUPITER = {"inputMint": "XsDoVfqeBukxuZHWhdvWHBhgEHjGNst4MLodqsJHzoB", "inAmount": "100000000",
                "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "outAmount": "401273174",
                "swapMode": "ExactIn", "slippageBps": 50, "priceImpactPct": "0.000735096", "swapUsdValue": "401.273174"}


def _selftest():
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    g = parse_gate(_FIX_GATE)
    check("gate price = mid(bid,ask) = 402.715", abs(g["price"] - 402.715) < 1e-6)
    check("gate settlement USDT / mid", g["settlement"] == "USDT" and g["price_type"] == "mid")

    b = parse_bybit(_FIX_BYBIT)
    check("bybit price = mid = 402.65", abs(b["price"] - 402.65) < 1e-6)

    bn = parse_binance(_FIX_BINANCE)
    check("binance price = 402.43", abs(bn["price"] - 402.43) < 1e-6)
    check("binance settlement USDT", bn["settlement"] == "USDT")

    USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    j = parse_jupiter(_FIX_JUPITER, 8, USDC)
    check("jupiter price = 401.273174 (8dec in, 6dec usdc)", abs(j["price"] - 401.273174) < 1e-6)
    check("jupiter executable + size_usd ~401.27", j["price_type"] == "executable" and abs(j["size_usd"] - 401.27) < 0.01)

    # review repros: reject zero-book and a routed/mis-scaled Jupiter output
    try:
        parse_gate([{"highest_bid": "0", "lowest_ask": "201.39"}])
        check("gate zero-bid rejected", False)
    except ValueError:
        check("gate zero-bid rejected", True)
    try:
        parse_jupiter({"outputMint": "WRONGMINT", "inAmount": "100000000", "outAmount": "401273174"}, 8, USDC)
        check("jupiter outputMint-mismatch rejected", False)
    except ValueError:
        check("jupiter outputMint-mismatch rejected", True)

    # market-hours helper (robust to missing tzdata -> None)
    sat_ms = int(datetime(2022, 1, 1, 12, 0, tzinfo=timezone.utc).timestamp() * 1000)  # Saturday
    wed_ms = int(datetime(2022, 1, 5, 15, 0, tzinfo=timezone.utc).timestamp() * 1000)  # Wed 10:00 ET
    check("market closed on Saturday", us_equity_market_open(sat_ms) in (False, None))
    check("market open Wed 10:00 ET", us_equity_market_open(wed_ms) in (True, None))

    failed = [n for n, ok in checks if not ok]
    print(json.dumps({"selftest": "PASS" if not failed else "FAIL", "total": len(checks),
                      "passed": len(checks) - len(failed), "failed": failed}, indent=2))
    return 0 if not failed else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--live" in argv:
        i = argv.index("--live")
        if i + 1 >= len(argv):
            print(json.dumps({"error": "--live requires an underlying, e.g. --live TSLA"}), file=sys.stderr)
            return 1
        print(json.dumps(live_payload(argv[i + 1]), indent=2))
        return 0
    print(json.dumps({"error": "usage: adapters.py --live <UNDERLYING> | --selftest"}), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
