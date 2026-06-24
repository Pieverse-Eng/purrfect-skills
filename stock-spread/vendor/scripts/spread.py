#!/usr/bin/env python3
"""
stock-spread normalize-and-compare module (READ-ONLY).

Takes per-venue quotes for ONE underlying and produces a *trustworthy* cross-venue
comparison. The hard part is not the subtraction — it is refusing to report a
spread that is actually an artifact. This module:

  - normalizes settlement currency to USD-equivalent via supplied pegs
    (USDT/USDC are NOT assumed 1:1; a depeg beyond tolerance is applied + flagged);
  - refuses to mix incomparable legs silently: market-closed, stale, unverified,
    and structurally-offset (e.g. total-return) quotes are EXCLUDED with a reason;
  - flags mid-vs-executable mixing (a CEX mid is not a fillable price);
  - marks the spread UNRELIABLE on cross-venue timestamp skew.

Determinism: the caller passes `now_ms` in the payload — no wall-clock is read,
so output is reproducible and testable.

Usage:
    python3 spread.py --quotes <file.json>   # compute from a payload file
    echo '<payload>' | python3 spread.py     # ...or from stdin
    python3 spread.py --demo                  # run the fake-spread fixture
    python3 spread.py --selftest              # offline fixture checks (exit 0/1)

Payload: {"underlying","now_ms","pegs":{cur:rate},"params":{...},"quotes":[{...}]}
  quote = {venue, price, settlement, price_type("mid"|"executable"|"total_return"),
           size_usd?, timestamp_ms, market_open(bool), verified(bool)}
Output: JSON to stdout. Exit 0 on success; 1 on error / failed selftest.
No network. Standard library only.
"""
import json
import math
import sys

DEFAULT_PARAMS = {"freshness_ms": 60000, "skew_ms": 30000, "peg_tolerance_bps": 50}


def _normalize_quote(q, pegs, peg_tol_bps):
    settlement = q.get("settlement")
    peg = pegs.get(settlement)
    warnings = []
    if peg is None:
        return None, [f"venue '{q['venue']}': unknown settlement currency {settlement!r}; cannot normalize"]
    price_usd = q["price"] * peg
    dev_bps = abs(peg - 1.0) * 10000.0
    if dev_bps > peg_tol_bps:
        warnings.append(
            f"venue '{q['venue']}': {settlement} peg off by {dev_bps:.0f}bps — normalization applied "
            f"(naive same-number comparison would be wrong)"
        )
    return price_usd, warnings


def compare(payload):
    underlying = payload["underlying"]
    pegs = payload.get("pegs", {"USD": 1.0, "USDT": 1.0, "USDC": 1.0})
    params = {**DEFAULT_PARAMS, **payload.get("params", {})}
    now = payload.get("now_ms")
    quotes = payload["quotes"]

    normalized, warnings, excluded = [], [], []
    price_types, timestamps = set(), []
    freshness_unknown = market_unknown = False

    for q in quotes:
        venue = q["venue"]
        if q.get("price_type") == "total_return" or q.get("offset"):
            excluded.append({"venue": venue, "reason": "structurally-offset feed (e.g. total-return) — not comparable to a raw price"})
            continue
        if not q.get("verified", True):
            excluded.append({"venue": venue, "reason": "unverified identifier — confirm vs issuer source before trusting"})
            warnings.append(f"venue '{venue}': UNVERIFIED identifier — excluded from spread")
            continue
        ts = q.get("timestamp_ms")
        if ts is not None and now is not None and (now - ts) > params["freshness_ms"]:
            excluded.append({"venue": venue, "reason": f"stale quote ({now - ts} ms old)"})
            warnings.append(f"venue '{venue}': quote stale ({now - ts} ms > {params['freshness_ms']} ms) — excluded")
            continue
        price_usd, w = _normalize_quote(q, pegs, params["peg_tolerance_bps"])
        warnings.extend(w)
        if price_usd is None:
            excluded.append({"venue": venue, "reason": "unnormalizable settlement currency"})
            continue
        # price sanity: a 0 / negative / NaN / Inf feed must never become a spread
        if not (isinstance(price_usd, (int, float)) and math.isfinite(price_usd) and price_usd > 0):
            excluded.append({"venue": venue, "reason": "non-positive or non-finite price"})
            warnings.append(f"venue '{venue}': non-positive/invalid price ({q.get('price')!r}) — excluded")
            continue
        # fail-safe: if freshness or market state can't be verified, we must NOT certify reliable
        if ts is None or now is None:
            freshness_unknown = True
        else:
            timestamps.append(ts)
        if q.get("market_open") is not True:
            market_unknown = True
        price_types.add(q.get("price_type", "mid"))
        normalized.append({
            "venue": venue,
            "price_usd": round(price_usd, 6),
            "raw_price": q["price"],
            "settlement": q.get("settlement"),
            "price_type": q.get("price_type", "mid"),
            "size_usd": q.get("size_usd"),
            "price_impact_pct": q.get("price_impact_pct"),
        })

    result = {"underlying": underlying, "normalized": normalized, "excluded": excluded, "warnings": warnings}

    if len(normalized) < 2:
        result.update({"reliable": False, "reason": "fewer than 2 comparable venues after filtering", "spread_pct": None})
        return result

    reliable = True
    if len(price_types) > 1:
        warnings.append(
            "comparison mixes mid and executable prices — spread is INDICATIVE, not directly capturable; "
            "compare executable-at-size for actionable edge"
        )
    if timestamps and (max(timestamps) - min(timestamps)) > params["skew_ms"]:
        reliable = False
        warnings.append(
            f"cross-venue timestamp skew {max(timestamps) - min(timestamps)} ms exceeds {params['skew_ms']} ms — spread UNRELIABLE"
        )
    if freshness_unknown:
        reliable = False
        warnings.append(
            "at least one leg has no verifiable timestamp — freshness UNKNOWN; spread not certified reliable"
        )
    if market_unknown:
        reliable = False
        warnings.append(
            "market not confirmed open (closed/unknown) for at least one leg — tokens trade 24/7 but the spread is not certified reliable"
        )

    prices = [n["price_usd"] for n in normalized]
    cheapest = min(normalized, key=lambda n: n["price_usd"])
    dearest = max(normalized, key=lambda n: n["price_usd"])
    mid = (max(prices) + min(prices)) / 2.0
    spread_pct = (dearest["price_usd"] - cheapest["price_usd"]) / mid * 100.0 if mid else None

    basis = "executable" if price_types == {"executable"} else ("mid" if price_types == {"mid"} else "mixed")
    result.update({
        "cheapest": {"venue": cheapest["venue"], "price_usd": cheapest["price_usd"]},
        "dearest": {"venue": dearest["venue"], "price_usd": dearest["price_usd"]},
        "spread_pct": round(spread_pct, 4) if spread_pct is not None else None,
        "price_basis": basis,
        "reliable": reliable,
    })
    return result


_FAKE_SPREAD_DEMO = {
    "underlying": "TSLA",
    "now_ms": 1750000000000,
    "pegs": {"USD": 1.0, "USDT": 0.97, "USDC": 1.0},
    "quotes": [
        {"venue": "gate", "price": 257.7320, "settlement": "USDT", "price_type": "mid", "timestamp_ms": 1750000000000, "verified": True, "market_open": True},
        {"venue": "kraken", "price": 250.0, "settlement": "USD", "price_type": "mid", "timestamp_ms": 1750000000000, "verified": True, "market_open": True},
    ],
}


def _selftest():
    NOW = 1750000000000
    ok_pegs = {"USD": 1.0, "USDT": 1.0, "USDC": 1.0}
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    # 1. clean comparable (two executable USDC, fresh) → reliable + correct spread
    r1 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "quotes": [
        {"venue": "solana_jupiter", "price": 250.0, "settlement": "USDC", "price_type": "executable", "size_usd": 10000, "timestamp_ms": NOW - 2000, "verified": True, "market_open": True},
        {"venue": "gate", "price": 252.5, "settlement": "USDC", "price_type": "executable", "size_usd": 10000, "timestamp_ms": NOW - 1000, "verified": True, "market_open": True},
    ]})
    check("clean: reliable", r1["reliable"] is True)
    check("clean: spread ~0.995%", abs(r1["spread_pct"] - 0.995024) < 0.01)
    check("clean: cheapest=solana", r1["cheapest"]["venue"] == "solana_jupiter")

    # 2. THE fake-spread case: USDT depeg → naive ~3% must normalize to ~0% + peg warning
    r2 = compare(_FAKE_SPREAD_DEMO)
    check("fake-spread: normalized ~0 (not naive ~3%)", r2["spread_pct"] < 0.1)
    check("fake-spread: peg warning", any("peg off" in w for w in r2["warnings"]))

    # 3. mid vs executable mixing → warned + basis=mixed
    r3 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "quotes": [
        {"venue": "kraken", "price": 250.0, "settlement": "USD", "price_type": "mid", "timestamp_ms": NOW, "verified": True, "market_open": True},
        {"venue": "solana_jupiter", "price": 251.0, "settlement": "USDC", "price_type": "executable", "size_usd": 10000, "timestamp_ms": NOW, "verified": True, "market_open": True},
    ]})
    check("mixing: warned", any("mid and executable" in w for w in r3["warnings"]))
    check("mixing: basis=mixed", r3["price_basis"] == "mixed")

    # 4. market-closed leg excluded → <2 comparable → unreliable
    r4 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "quotes": [
        {"venue": "kraken", "price": 250.0, "settlement": "USD", "price_type": "mid", "timestamp_ms": NOW, "verified": True, "market_open": False},
        {"venue": "solana_jupiter", "price": 251.0, "settlement": "USDC", "price_type": "executable", "timestamp_ms": NOW, "verified": True, "market_open": True},
    ]})
    check("closed leg: reliable False", r4["reliable"] is False)
    check("closed leg: kept (24/7 token), not excluded", any(n["venue"] == "kraken" for n in r4["normalized"]))
    check("closed leg: 'not confirmed open' warning", any("not confirmed open" in w for w in r4["warnings"]))

    # 5. timestamp skew beyond skew_ms → unreliable
    r5 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "params": {"freshness_ms": 60000, "skew_ms": 30000}, "quotes": [
        {"venue": "gate", "price": 250.0, "settlement": "USDC", "price_type": "executable", "timestamp_ms": NOW - 5000, "verified": True, "market_open": True},
        {"venue": "solana_jupiter", "price": 251.0, "settlement": "USDC", "price_type": "executable", "timestamp_ms": NOW - 45000, "verified": True, "market_open": True},
    ]})
    check("skew: reliable False", r5["reliable"] is False)
    check("skew: warned", any("skew" in w for w in r5["warnings"]))

    # 6. structurally-offset (total-return) feed excluded from spread
    r6 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "quotes": [
        {"venue": "ondo", "price": 300.0, "settlement": "USDC", "price_type": "total_return", "timestamp_ms": NOW, "verified": True, "market_open": True},
        {"venue": "gate", "price": 250.0, "settlement": "USDC", "price_type": "executable", "timestamp_ms": NOW, "verified": True, "market_open": True},
        {"venue": "solana_jupiter", "price": 251.0, "settlement": "USDC", "price_type": "executable", "timestamp_ms": NOW, "verified": True, "market_open": True},
    ]})
    check("offset: ondo excluded", any(e["venue"] == "ondo" for e in r6["excluded"]))
    check("offset: ondo not in normalized", all(n["venue"] != "ondo" for n in r6["normalized"]))

    # 7. unverified id excluded from spread
    r7 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "quotes": [
        {"venue": "bybit", "price": 250.0, "settlement": "USDT", "price_type": "mid", "timestamp_ms": NOW, "verified": False, "market_open": True},
        {"venue": "gate", "price": 250.5, "settlement": "USDC", "price_type": "executable", "timestamp_ms": NOW, "verified": True, "market_open": True},
        {"venue": "solana_jupiter", "price": 251.0, "settlement": "USDC", "price_type": "executable", "timestamp_ms": NOW, "verified": True, "market_open": True},
    ]})
    check("unverified: bybit excluded", any(e["venue"] == "bybit" for e in r7["excluded"]))

    # 8. non-positive price is excluded (never becomes a spread) — review repro
    r8 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "quotes": [
        {"venue": "a", "price": -5.0, "settlement": "USD", "price_type": "mid", "timestamp_ms": NOW, "verified": True, "market_open": True},
        {"venue": "b", "price": 250.0, "settlement": "USD", "price_type": "mid", "timestamp_ms": NOW, "verified": True, "market_open": True},
    ]})
    check("negative price excluded", any(e["venue"] == "a" for e in r8["excluded"]))
    check("negative price -> not reliable (no fake 208% spread)", r8["reliable"] is False)

    # 9. zero price excluded too
    r9 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "quotes": [
        {"venue": "a", "price": 0.0, "settlement": "USD", "price_type": "mid", "timestamp_ms": NOW, "verified": True, "market_open": True},
        {"venue": "b", "price": 250.0, "settlement": "USD", "price_type": "mid", "timestamp_ms": NOW, "verified": True, "market_open": True},
    ]})
    check("zero price excluded", any(e["venue"] == "a" for e in r9["excluded"]))

    # 10. unknown freshness (no timestamp on a leg) -> NOT certified reliable (live-path P0)
    r10 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "quotes": [
        {"venue": "a", "price": 250.0, "settlement": "USD", "price_type": "mid", "timestamp_ms": NOW, "verified": True, "market_open": True},
        {"venue": "b", "price": 252.0, "settlement": "USDC", "price_type": "executable", "verified": True, "market_open": True},
    ]})
    check("unknown freshness -> reliable False", r10["reliable"] is False)
    check("unknown freshness warned", any("freshness UNKNOWN" in w for w in r10["warnings"]))

    # 11. unknown market_open -> NOT certified reliable (the inert-guard P0)
    r11 = compare({"underlying": "TSLA", "now_ms": NOW, "pegs": ok_pegs, "quotes": [
        {"venue": "a", "price": 250.0, "settlement": "USD", "price_type": "mid", "timestamp_ms": NOW, "verified": True, "market_open": True},
        {"venue": "b", "price": 252.0, "settlement": "USDC", "price_type": "executable", "timestamp_ms": NOW, "verified": True},
    ]})
    check("unknown market_open -> reliable False", r11["reliable"] is False)
    check("unknown market_open warned", any("not confirmed open" in w for w in r11["warnings"]))

    failed = [n for n, passed in checks if not passed]
    print(json.dumps({
        "selftest": "PASS" if not failed else "FAIL",
        "total": len(checks),
        "passed": len(checks) - len(failed),
        "failed": failed,
    }, indent=2))
    return 0 if not failed else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--demo" in argv:
        print(json.dumps(compare(_FAKE_SPREAD_DEMO), indent=2))
        return 0
    payload = None
    if "--quotes" in argv:
        i = argv.index("--quotes")
        if i + 1 >= len(argv):
            print(json.dumps({"error": "--quotes requires a file path"}), file=sys.stderr)
            return 1
        with open(argv[i + 1], "r") as f:
            payload = json.load(f)
    else:
        data = sys.stdin.read().strip()
        if not data:
            print(json.dumps({"error": "no payload: pass --quotes <file>, pipe JSON via stdin, or use --demo/--selftest"}), file=sys.stderr)
            return 1
        payload = json.loads(data)
    try:
        print(json.dumps(compare(payload), indent=2))
    except (KeyError, TypeError) as e:
        print(json.dumps({"error": f"invalid payload: {e}"}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
