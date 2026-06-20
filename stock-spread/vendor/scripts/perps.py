#!/usr/bin/env python3
"""
stock-spread on-chain equity-PERP reads + spot-vs-perp BASIS (READ-ONLY).

Reads keyless equity-perp marks + funding from Hyperliquid's `xyz` builder dex
(trade.xyz HIP-3) and computes the spot-vs-perp basis against the existing spot
pipeline (adapters.py + spread.py). This is the arbitrage *signal* (cash-and-carry:
long spot / short perp, harvest funding) — NOT a capturable trade.

Honesty rails (carried from the brainstorm's adversarial review):
  - The perp is a 24/7 oracle MARK; spot is a mid/executable price during market
    hours. The basis is INDICATIVE; off-hours/weekends it is distorted.
  - Convergence is funding-driven and NOT capturable by an anonymous wallet
    (no physical redemption) — always surfaced.

Usage:
    python3 perps.py --live <UNDERLYING>     # perp mark/funding for one underlying
    python3 perps.py --basis <UNDERLYING>    # spot (adapters|spread) vs perp -> basis + funding APR
    python3 perps.py --selftest              # offline fixture checks (exit 0/1)

Standard library only. Read-only; no keys.
"""
import json
import os
import sys
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters  # noqa: E402  (spot reads)
import spread    # noqa: E402  (normalize + compare)

HL_INFO = "https://api.hyperliquid.xyz/info"
DEX = "xyz"
DEX_PREFIX = "xyz:"


def _post(body, timeout=15):
    req = Request(HL_INFO, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "User-Agent": "stock-spread/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_perp(meta, ctxs, underlying):
    """Pure: pull one underlying's perp ctx out of metaAndAssetCtxs. None if not listed."""
    name = DEX_PREFIX + underlying.upper()
    for i, u in enumerate(meta["universe"]):
        if u["name"] == name:
            c = ctxs[i]
            mark = float(c["markPx"])
            fhr = float(c.get("funding", 0.0))
            return {
                "venue": "hyperliquid_xyz",
                "underlying": underlying.upper(),
                "symbol": name,
                "mark": mark,
                "oracle": float(c.get("oraclePx", mark)),
                "funding_hourly": fhr,
                "funding_apr_pct": round(fhr * 24 * 365 * 100, 3),
                "open_interest": float(c.get("openInterest", 0.0)),
                "settlement": "USDC",
                "price_type": "perp_mark",
            }
    return None


def median(xs):
    s = sorted(xs)
    n = len(s)
    if not n:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def basis(spot_ref, perp):
    b = (perp["mark"] - spot_ref) / spot_ref * 100.0
    return {
        "basis_pct": round(b, 4),
        "funding_apr_pct": perp["funding_apr_pct"],
        "direction": "perp rich (>spot)" if b > 0 else "perp cheap (<spot)",
        "warnings": [
            "perp is a 24/7 oracle MARK vs spot mid/executable — basis is INDICATIVE, distorted off US market hours / weekends",
            "convergence is funding-driven and NOT capturable by an anonymous wallet (no physical redemption) — treat as a signal",
        ],
    }


def fetch_perps():
    return _post({"type": "metaAndAssetCtxs", "dex": DEX})


def perp_for(underlying):
    meta, ctxs = fetch_perps()
    return parse_perp(meta, ctxs, underlying)


# --- recorded real fixture (probe 2026-06-20) ---
_FX_META = {"universe": [{"name": "xyz:XYZ100"}, {"name": "xyz:TSLA"}, {"name": "xyz:NVDA"}]}
_FX_CTXS = [
    {"markPx": "1000.0", "oraclePx": "1000.0", "funding": "0.0", "openInterest": "1.0"},
    {"markPx": "402.12", "oraclePx": "402.18", "funding": "0.00000625", "openInterest": "71796.528"},
    {"markPx": "209.9", "oraclePx": "209.85", "funding": "0.00000625", "openInterest": "849319.78"},
]


def _selftest():
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    p = parse_perp(_FX_META, _FX_CTXS, "TSLA")
    check("parse TSLA mark = 402.12", p and abs(p["mark"] - 402.12) < 1e-6)
    check("funding APR ~5.479%", p and abs(p["funding_apr_pct"] - 5.479) < 0.01)
    check("perp_mark price_type + USDC", p["price_type"] == "perp_mark" and p["settlement"] == "USDC")
    check("not-listed underlying -> None", parse_perp(_FX_META, _FX_CTXS, "FAKE") is None)

    check("median odd", median([1, 3, 2]) == 2)
    check("median even", median([1, 2, 3, 4]) == 2.5)

    bz = basis(400.0, p)
    check("basis vs 400 = 0.53%", abs(bz["basis_pct"] - 0.53) < 0.01)
    check("basis carries not-capturable warning", any("NOT capturable" in w for w in bz["warnings"]))
    check("basis carries market-hours warning", any("market hours" in w for w in bz["warnings"]))

    failed = [n for n, ok in checks if not ok]
    print(json.dumps({"selftest": "PASS" if not failed else "FAIL", "total": len(checks),
                      "passed": len(checks) - len(failed), "failed": failed}, indent=2))
    return 0 if not failed else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()

    if "--live" in argv:
        u = argv[argv.index("--live") + 1]
        p = perp_for(u)
        print(json.dumps(p or {"error": f"no equity perp for {u.upper()} on {DEX} dex"}, indent=2))
        return 0

    if "--basis" in argv:
        u = argv[argv.index("--basis") + 1].upper()
        perp = perp_for(u)
        if not perp:
            print(json.dumps({"underlying": u, "error": f"no equity perp on {DEX} dex — basis unavailable"}, indent=2))
            return 0
        sres = spread.compare(adapters.live_payload(u))
        spot_prices = [n["price_usd"] for n in sres.get("normalized", [])]
        spot_ref = median(spot_prices)
        if spot_ref is None:
            print(json.dumps({"underlying": u, "perp": perp, "error": "no comparable spot quotes for basis"}, indent=2))
            return 0
        out = {
            "underlying": u,
            "spot_ref_usd": round(spot_ref, 6),
            "spot_venues": [n["venue"] for n in sres["normalized"]],
            "spot_reliable": sres.get("reliable"),
            "perp_mark": perp["mark"],
            "perp_venue": perp["venue"],
            "basis": basis(spot_ref, perp),
        }
        print(json.dumps(out, indent=2))
        return 0

    print(json.dumps({"error": "usage: perps.py --live <U> | --basis <U> | --selftest"}), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
